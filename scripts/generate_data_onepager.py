#!/usr/bin/env python3
"""Generate a one-page markdown summary of all crypto manifests.

This script will look under `data/crypto/USDT/*` for per-symbol manifests
(`manifest_1d.yaml`, `manifest_1h.yaml`). If a manifest is missing or
incomplete it will fall back to reading the canonical CSV `crypto_<BASE>_USDT_<timeframe>.csv`.

Output: `results/data_onepager.md`

Emoticons are included in the generated report as requested.
"""
from pathlib import Path
import yaml
import pandas as pd
import textwrap
from datetime import datetime


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / 'data' / 'crypto' / 'USDT'
OUT_DIR = REPO_ROOT / 'results'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / 'data_onepager.md'


def read_manifest(symbol_dir: Path, timeframe: str) -> dict | None:
    mfile = symbol_dir / f'manifest_{timeframe}.yaml'
    if not mfile.exists():
        return None
    try:
        with open(mfile, 'r', encoding='utf8') as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return None


def read_csv_stats(symbol_dir: Path, base: str, timeframe: str) -> dict | None:
    csv_file = symbol_dir / f'crypto_{base}_USDT_{timeframe}.csv'
    if not csv_file.exists():
        return None
    try:
        df = pd.read_csv(csv_file, parse_dates=['datetime'], index_col='datetime')
    except Exception:
        return None

    if df.empty:
        return None

    stats = {
        'rows': int(len(df)),
        'start': str(df.index.min()),
        'end': str(df.index.max()),
        'last_close': float(df['close'].iloc[-1]) if 'close' in df.columns else None,
        'min_price': float(df['low'].min()) if 'low' in df.columns else None,
        'max_price': float(df['high'].max()) if 'high' in df.columns else None,
        'mean_volume': float(df['volume'].mean()) if 'volume' in df.columns else None,
    }
    return stats


def gather_symbol_summary(symbol_dir: Path) -> dict:
    base = symbol_dir.name
    out = {'symbol': f'{base}/USDT', 'base': base, 'timeframes': {}}
    for tf in ('1d', '1h'):
        manifest = read_manifest(symbol_dir, tf)
        if manifest:
            # Take commonly used fields if they exist, else fallback
            out_tf = {
                'rows': manifest.get('rows') or manifest.get('count') or None,
                'start': manifest.get('start') or manifest.get('first_date') or None,
                'end': manifest.get('end') or manifest.get('last_date') or None,
                'min_price': manifest.get('min') or manifest.get('min_price') or None,
                'max_price': manifest.get('max') or manifest.get('max_price') or None,
                'mean_volume': manifest.get('mean_volume') or manifest.get('avg_volume') or None,
            }

            # If any key is missing, try to read canonical CSV to fill values
            missing = any(v is None for v in out_tf.values())
            if missing:
                csv_stats = read_csv_stats(symbol_dir, base, tf)
                if csv_stats:
                    # prefer manifest values, but fill blanks from CSV
                    for k, v in csv_stats.items():
                        if out_tf.get(k) in (None, '—') and v is not None:
                            # map csv_stats keys to manifest keys when names differ
                            if k == 'last_close':
                                out_tf['last_close'] = v
                            else:
                                out_tf[k] = v

            out['timeframes'][tf] = out_tf
        else:
            csv_stats = read_csv_stats(symbol_dir, base, tf)
            if csv_stats:
                out['timeframes'][tf] = csv_stats
            else:
                out['timeframes'][tf] = None
    return out


def format_onepager(summaries: list[dict]) -> str:
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    header = f"# Data one-pager — crypto dataset 📊\n\nGenerated: {now}\n\n"

    overview_lines = [
        f"- Symbols scanned: {len(summaries)} 🔎",
        f"- Data root: `{DATA_ROOT.relative_to(REPO_ROOT)}`",
        "",
    ]
    body = []
    # Helper for formatting numbers
    def fmt(x, ndigits=4):
        if x is None:
            return '—'
        if isinstance(x, (int,)):
            return f"{x:,}"
        try:
            f = float(x)
        except Exception:
            return str(x)
        # large numbers use comma formatting
        if abs(f) >= 1_000:
            s = f"{f:,.{ndigits}f}"
            # strip trailing zeros and trailing dot
            s = s.rstrip('0').rstrip('.')
            return s
        # small numbers keep up to ndigits significant digits
        return f"{f:.{ndigits}f}".rstrip('0').rstrip('.')

    def fmt_vol(v):
        if v is None:
            return '—'
        try:
            v = float(v)
        except Exception:
            return str(v)
        # Human-readable SI-ish units
        abs_v = abs(v)
        if abs_v >= 1e9:
            return f"{v/1e9:.2f}B"
        if abs_v >= 1e6:
            return f"{v/1e6:.2f}M"
        if abs_v >= 1e3:
            return f"{v/1e3:.2f}K"
        return f"{v:.2f}"

    # Build two aggregated tables: 1h and 1d. Each table has one row per symbol.
    def build_table_for_timeframe(tf: str) -> list[str]:
        lines: list[str] = []
        lines.append(f"## {tf} summary ✨")
        lines.append("| ticker | rows | start | end | last | min | max | mean_vol |")
        lines.append("|:---|---:|:---|:---|---:|---:|---:|---:|")
        for s in sorted(summaries, key=lambda x: x['base']):
            info = s['timeframes'].get(tf)
            ticker = s['symbol']
            if not info:
                lines.append(f"| {ticker} | — | — | — | — | — | — | — |")
                continue
            rows = fmt(info.get('rows'))
            start = info.get('start') or '—'
            end = info.get('end') or '—'
            last = fmt(info.get('last_close') or info.get('last'))
            minp = fmt(info.get('min_price'))
            maxp = fmt(info.get('max_price'))
            mv = fmt_vol(info.get('mean_volume'))
            lines.append(f"| {ticker} | {rows} | {start} | {end} | {last} | {minp} | {maxp} | {mv} |")
        return lines

    # append 1h table first, then 1d table
    body.extend(build_table_for_timeframe('1h'))
    body.append('')
    body.extend(build_table_for_timeframe('1d'))
    body.append('')

    footer = textwrap.dedent(
        """
        ---
        Notes:
        - This report reads `manifest_<timeframe>.yaml` when present, otherwise falls back to the canonical CSV.
        - If you want richer charts, run the summary scripts under `src/utils` to generate combined CSVs and plots.
        """
    )

    return header + '\n'.join(overview_lines) + '\n' + '\n'.join(body) + '\n' + footer


def main():
    if not DATA_ROOT.exists():
        print(f"No data directory found at {DATA_ROOT}. Nothing to summarize.")
        return 1

    summaries = []
    for symbol_dir in sorted([p for p in DATA_ROOT.iterdir() if p.is_dir()]):
        summaries.append(gather_symbol_summary(symbol_dir))

    md = format_onepager(summaries)
    with open(OUT_FILE, 'w', encoding='utf8') as fh:
        fh.write(md)

    print(f"Wrote one-pager to: {OUT_FILE}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
