#!/usr/bin/env python3
"""Partition existing 1m CSVs into year/month folders.

This script scans `data/crypto/USDT/*/` for files named like
`crypto_<BASE>_USDT_1m.csv` and writes partitioned CSVs to
`data/crypto/USDT/<BASE>/1m/<YYYY>/<MM>/crypto_<BASE>_USDT_1m.csv`.

It reads the source CSV in chunks so it can handle large files.
Use --dry-run to only print planned writes.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import pandas as pd
import sys
from datetime import datetime
import math

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / 'data' / 'crypto' / 'USDT'


def infer_timestamp_col(df: pd.DataFrame) -> str | None:
    candidates = ['timestamp', 'datetime', 'open_time', 'openTime', 'open_time_ms']
    for c in candidates:
        if c in df.columns:
            return c
    # otherwise pick first numeric/int-like column
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]) or pd.api.types.is_float_dtype(df[c]):
            # heuristic: epoch ms if large numbers
            sample = df[c].dropna().iloc[0] if len(df[c].dropna())>0 else None
            if sample is None:
                continue
            if isinstance(sample, (int,)) and sample > 1e11:
                return c
    return None


def to_datetime_series(s: pd.Series) -> pd.Series:
    # if already datetime, return
    if pd.api.types.is_datetime64_any_dtype(s):
        return s.dt.tz_localize(None)
    # integers likely epoch ms
    if pd.api.types.is_integer_dtype(s) or pd.api.types.is_float_dtype(s):
        # treat as ms if >1e11 else seconds
        if s.dropna().empty:
            return pd.to_datetime(s, unit='ms', utc=True).dt.tz_localize(None)
        sample = float(s.dropna().iloc[0])
        unit = 'ms' if sample > 1e11 else 's'
        return pd.to_datetime(s, unit=unit, utc=True).dt.tz_localize(None)
    # otherwise try to parse strings
    return pd.to_datetime(s, utc=True).dt.tz_localize(None)


def partition_file(src: Path, dry_run: bool = True, chunksize: int = 100_000):
    print(f"Processing: {src}")
    basename = src.name
    parts = basename.split('_')
    # expect crypto_<BASE>_USDT_1m.csv -> symbol at index 1
    if len(parts) < 3:
        print(f"Skipping unexpected filename format: {basename}")
        return
    base = parts[1]
    dest_root = src.parent / '1m'

    reader = pd.read_csv(src, chunksize=chunksize)
    written = 0
    for chunk in reader:
        ts_col = infer_timestamp_col(chunk)
        if ts_col is None:
            print(f"Could not infer timestamp column for {src}; skipping chunk")
            continue
        chunk['_dt'] = to_datetime_series(chunk[ts_col])
        chunk['_year'] = chunk['_dt'].dt.year.astype(int)
        chunk['_month'] = chunk['_dt'].dt.month.astype(int)
        # iterate groups
        for (y, m), g in chunk.groupby(['_year', '_month']):
            year = int(y)
            month = int(m)
            dest_dir = dest_root / f"{year:04d}" / f"{month:02d}"
            dest_dir_parent = dest_dir
            dest_dir_parent.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir_parent / basename
            if dry_run:
                print(f"DRY RUN: would write {len(g)} rows to {dest_file}")
            else:
                # drop helper cols and append
                out = g.drop(columns=['_dt','_year','_month'])
                header = not dest_file.exists()
                out.to_csv(dest_file, mode='a', index=False, header=header)
                written += len(out)
    if not dry_run:
        print(f"Wrote {written} rows for {base}")


def main(argv=None):
    p = argparse.ArgumentParser(description='Partition existing 1m CSVs into year/month folders')
    p.add_argument('--data-root', default=str(DATA_ROOT), help='Root data folder for USDT')
    p.add_argument('--dry-run', action='store_true', help='Only print planned writes')
    p.add_argument('--symbol', help='Limit to single symbol (e.g. BTC)')
    args = p.parse_args(argv)

    data_root = Path(args.data_root)
    if not data_root.exists():
        print(f"Data root does not exist: {data_root}")
        return 1

    targets = []
    for sub in data_root.iterdir():
        if not sub.is_dir():
            continue
        if args.symbol and sub.name.upper() != args.symbol.upper():
            continue
        # look for canonical 1m csv
        src = sub / f"crypto_{sub.name}_USDT_1m.csv"
        if src.exists():
            targets.append(src)

    if not targets:
        print("No canonical 1m CSVs found to partition.")
        return 0

    for t in targets:
        partition_file(t, dry_run=args.dry_run)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
