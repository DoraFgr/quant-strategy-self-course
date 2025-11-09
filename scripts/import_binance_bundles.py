#!/usr/bin/env python3
"""Import Binance kline bundle files into canonical per-symbol CSVs.

This script expects a local bundle directory structured like:
  <bundle_dir>/<interval>/<SYMBOL>-<interval>-YYYY-MM-DD.csv  (or .zip)

It will find files for the requested symbols/timeframe, convert them to the
canonical format `data/crypto/USDT/<BASE>/crypto_<BASE>_USDT_<timeframe>.csv`,
append deduplicated rows, and update a simple YAML manifest `manifest_<timeframe>.yaml`.

Usage:
  python scripts/import_binance_bundles.py --bundle-dir ./bundles --timeframe 1m --symbols BTC ETH --dry-run

If --symbols is omitted, the script will inspect the bundle dir and import all symbols found.
"""
from pathlib import Path
import argparse
import zipfile
import csv
import io
import sys
import pandas as pd
import yaml
from datetime import datetime


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / 'data' / 'crypto' / 'USDT'


def find_bundle_files(bundle_dir: Path, timeframe: str, symbol: str):
    """Find bundle files for a symbol across daily and monthly bundle folders.

    Returns a list of Path objects. We search recursively so the downloader's
    layout (bundles/1m/ or bundles/monthly_1m/) is supported.
    """
    pattern = f"**/*{symbol.replace('/','')}-{timeframe}-*.csv"
    files = list(bundle_dir.glob(pattern))
    files += list(bundle_dir.glob(f"**/*{symbol.replace('/','')}-{timeframe}-*.zip"))
    return sorted(files)


def read_bundle_csv(path: Path) -> pd.DataFrame:
    """Read one bundle file (CSV or ZIP). If ZIP contains multiple CSVs, concatenate them.

    Returns a DataFrame indexed by datetime (UTC).
    """
    frames = []
    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path, 'r') as z:
            names = [n for n in z.namelist() if n.lower().endswith('.csv')]
            if not names:
                raise RuntimeError(f"No CSV found inside {path}")
            for name in names:
                with z.open(name) as fh:
                    text = io.TextIOWrapper(fh, encoding='utf8')
                    df = pd.read_csv(text, header=None)
                    frames.append(df)
    else:
        df = pd.read_csv(path, header=None)
        frames.append(df)

    if not frames:
        raise RuntimeError(f"No CSV frames in {path}")

    df = pd.concat(frames, axis=0, ignore_index=True)
    if df.shape[1] < 6:
        raise RuntimeError(f"Unexpected CSV format in {path}")
    df = df.iloc[:, :6]
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
    # coerce open_time to numeric and drop invalid rows
    df['open_time'] = pd.to_numeric(df['open_time'], errors='coerce')
    df = df.dropna(subset=['open_time'])
    # open_time may be in microseconds, milliseconds or seconds depending on bundle.
    df['open_time'] = df['open_time'].astype('int64')
    max_ot = df['open_time'].abs().max() if not df['open_time'].empty else 0
    if max_ot > 1e14:
        unit = 'us'
    elif max_ot > 1e11:
        unit = 'ms'
    else:
        unit = 's'
    df['datetime'] = pd.to_datetime(df['open_time'], unit=unit, utc=True, errors='coerce')
    df = df.dropna(subset=['datetime'])
    df = df.set_index('datetime')
    for c in ['open', 'high', 'low', 'close', 'volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df[['open', 'high', 'low', 'close', 'volume']]
    return df


def month_from_filename(path: Path):
    """Extract year-month string YYYY-MM from filename (daily or monthly)."""
    import re
    name = path.name
    m = re.search(r"(\d{4}-\d{2}(?:-\d{2})?)", name)
    if not m:
        return None
    date_part = m.group(1)
    if len(date_part) >= 7:
        return date_part[:7]
    return None


def sha256_of_df_csv_bytes(df: pd.DataFrame) -> str:
    import hashlib
    bio = io.BytesIO()
    df.to_csv(bio, index_label='datetime')
    bio.seek(0)
    h = hashlib.sha256(bio.read()).hexdigest()
    return h


def write_month_partition(df: pd.DataFrame, base: str, timeframe: str, year_month: str, bundle_path: Path, dry_run: bool = False, force: bool = False) -> dict:
    """Write a month's data to partition path: DATA_ROOT/<base>/<timeframe>/<YYYY>/<MM>/crypto_<base>_USDT_<timeframe>.csv

    Returns manifest info for the month.
    """
    year, month = year_month.split('-')
    symbol_dir = DATA_ROOT / base / timeframe / year / month
    symbol_dir.mkdir(parents=True, exist_ok=True)
    out_path = symbol_dir / f'crypto_{base}_USDT_{timeframe}.csv'

    # existing data for that month
    if out_path.exists() and not dry_run:
        existing = pd.read_csv(out_path, parse_dates=['datetime'], index_col='datetime')
    else:
        existing = pd.DataFrame(columns=['open','high','low','close','volume'])

    combined = pd.concat([existing, df]) if not existing.empty else df.copy()
    combined = combined[~combined.index.duplicated(keep='last')]
    combined = combined.sort_index()

    if not dry_run:
        if out_path.exists() and force:
            out_path.unlink()
        combined.to_csv(out_path, index_label='datetime')

    checksum = sha256_of_df_csv_bytes(combined) if not combined.empty else None
    info = {
        'filename': out_path.name,
        'rows': int(len(combined)),
        'start_date': str(combined.index.min()) if not combined.empty else None,
        'end_date': str(combined.index.max()) if not combined.empty else None,
        'bundle_source': str(bundle_path),
        'sha256': checksum,
    }
    # write per-month manifest
    # compute field-level stats similar to existing 1h/1d manifests
    mfile = symbol_dir / f'manifest_{timeframe}_{year_month}.yaml'
    mdata = {
        'symbol': f"{base}/USDT",
        'timeframe': timeframe,
        'rows': info['rows'],
        'start_date': info['start_date'],
        'end_date': info['end_date'],
        'sha256': info['sha256'],
        'updated': datetime.utcnow().isoformat(),
    }
    if not combined.empty:
        # per-field stats
        fields = {}
        for col in ['open','high','low','close','volume']:
            if col in combined.columns:
                ser = combined[col].dropna()
                fields[col] = {
                    'name': col,
                    'description': 'Open/High/Low/Close/Volume for the interval' if col!='volume' else 'Traded volume during the interval',
                    'min': float(ser.min()) if not ser.empty else None,
                    'max': float(ser.max()) if not ser.empty else None,
                    'mean': float(ser.mean()) if not ser.empty else None,
                    'median': float(ser.median()) if not ser.empty else None,
                    'std': float(ser.std()) if not ser.empty else None,
                    'nulls': int(len(combined) - len(ser)),
                }
        # last close and return
        first_close = float(combined['close'].iloc[0])
        last_close = float(combined['close'].iloc[-1])
        total_return_pct = (last_close / first_close - 1.0) * 100.0 if first_close != 0 else None

        mdata['fields'] = fields
        mdata['insights'] = {
            'price_range': {
                'min_close': float(combined['close'].min()),
                'max_close': float(combined['close'].max()),
            },
            'avg_volume': float(combined['volume'].mean()),
        }
        mdata['last_close'] = last_close
        mdata['total_return_pct'] = total_return_pct
    if not dry_run:
        with open(mfile, 'w', encoding='utf8') as fh:
            yaml.safe_dump(mdata, fh)

    return info


def write_manifest(symbol_dir: Path, timeframe: str, info: dict, dry_run: bool = False):
    mfile = symbol_dir / f'manifest_{timeframe}.yaml'
    data = {
        'rows': info.get('rows'),
        'start': info.get('start_date'),
        'end': info.get('end_date'),
        'updated': datetime.utcnow().isoformat(),
    }
    if not dry_run:
        with open(mfile, 'w', encoding='utf8') as fh:
            yaml.safe_dump(data, fh)


def main(argv=None):
    p = argparse.ArgumentParser(description='Import Binance bundle files to canonical CSV partitions')
    p.add_argument('--bundle-dir', required=True, help='Path to local bundle directory')
    p.add_argument('--timeframe', default='1m', help='Timeframe folder in bundles (e.g. 1m,1h)')
    p.add_argument('--symbols', nargs='*', help='Symbols to import (e.g. BTC ETH). If omitted, infer from bundle dir')
    p.add_argument('--dry-run', action='store_true', help='Do not write files; just show plan')
    p.add_argument('--force', action='store_true', help='Overwrite existing month partitions')
    args = p.parse_args(argv)

    bundle_dir = Path(args.bundle_dir)
    tf = args.timeframe

    if args.symbols:
        symbols = [s.upper() for s in args.symbols]
    else:
        # infer symbols from bundle dir
        tf_dir = bundle_dir / tf
        if not tf_dir.exists():
            print(f"Bundle timeframe dir not found: {tf_dir}")
            return 2
        symbols = []
        for f in tf_dir.iterdir():
            name = f.name
            if '-' in name:
                sym = name.split('-')[0]
                if sym not in symbols:
                    symbols.append(sym)

    plan = []
    for sym in symbols:
        base = sym.replace('USDT','') if sym.endswith('USDT') else sym
        files = find_bundle_files(bundle_dir, tf, sym)
        if not files:
            print(f"No bundle files found for {sym} in bundles under {bundle_dir}")
            continue

        # group files by month (YYYY-MM)
        months = {}
        for fpath in files:
            mon = month_from_filename(fpath)
            if mon is None:
                print(f"Skipping unknown filename pattern: {fpath}")
                continue
            months.setdefault(mon, []).append(fpath)

        # for each month, prefer monthly file (single .zip with YYYY-MM) if present
        month_infos = {}
        for mon, fps in sorted(months.items()):
            # detect any file whose stem ends with the month (YYYY-MM)
            monthly_file = next((f for f in fps if f.stem.endswith(mon)), None)
            try:
                if monthly_file:
                    df = read_bundle_csv(monthly_file)
                    info = write_month_partition(df, base, tf, mon, monthly_file, dry_run=args.dry_run, force=args.force)
                else:
                    # combine daily files for that month
                    dfs = []
                    for f in sorted(fps):
                        try:
                            dfs.append(read_bundle_csv(f))
                        except Exception as e:
                            print(f"Failed to read {f}: {e}")
                    if not dfs:
                        continue
                    big = pd.concat(dfs)
                    big = big[~big.index.duplicated(keep='last')]
                    info = write_month_partition(big, base, tf, mon, fps[0], dry_run=args.dry_run, force=args.force)
                month_infos[mon] = info
                plan.append((sym, mon, info))
            except Exception as e:
                print(f"Failed to import month {mon} for {sym}: {e}")

        # after processing months, write yearly manifest(s)
        if month_infos and not args.dry_run:
            # group by year
            years = {}
            for mon, info in month_infos.items():
                y = mon.split('-')[0]
                years.setdefault(y, {})[mon] = info
            for y, months_map in years.items():
                yfile = DATA_ROOT / base / tf / f'manifest_year_{y}.yaml'
                ydata = {
                    'year': y,
                    'months': {},
                    'updated': datetime.utcnow().isoformat(),
                }
                total_rows = 0
                for mon, info in months_map.items():
                    ydata['months'][mon] = {
                        'rows': info.get('rows'),
                        'start': info.get('start_date'),
                        'end': info.get('end_date'),
                        'sha256': info.get('sha256'),
                    }
                    total_rows += info.get('rows', 0) or 0
                ydata['rows'] = total_rows
                with open(yfile, 'w', encoding='utf8') as fh:
                    yaml.safe_dump(ydata, fh)

    # report
    for item in plan:
        if len(item) == 3:
            sym, mon, info = item
            print(f"{sym} {mon}: wrote {info.get('rows')} rows -> {info.get('filename')} (start={info.get('start_date')} end={info.get('end_date')})")
        else:
            # backward compatibility
            sym, info = item
            print(f"{sym}: wrote {info.get('rows')} rows -> {info.get('filename')} (start={info.get('start_date')} end={info.get('end_date')})")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
