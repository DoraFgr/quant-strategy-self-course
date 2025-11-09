#!/usr/bin/env python3
"""Download Binance daily kline bundle ZIPs into a local bundle directory.

This script downloads files from Binance public dataset (data.binance.vision)
using the convention:

  https://data.binance.vision/data/spot/daily/klines/{symbol}/{interval}/{symbol}-{interval}-{YYYY-MM-DD}.zip

Defaults to the last 30 days and the repo's major pairs if no symbols provided.
Use --days-back to control range, or --start-date/--end-date for explicit ranges.

Run with --dry-run to only print planned URLs.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import sys
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter, Retry
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE_DIR = REPO_ROOT / 'bundles'


def get_major_pairs():
    # lightweight local fallback: common majors
    return ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']


def daterange(start_date: datetime, end_date: datetime):
    cur = start_date
    while cur <= end_date:
        yield cur
        cur += timedelta(days=1)


def download_file(url: str, dest: Path, session: requests.Session, dry_run: bool = False, force: bool = False) -> bool:
    if dry_run:
        print(f"DRY RUN: would download {url} -> {dest}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        print(f"Skipping existing file: {dest}")
        return True
    if dest.exists() and force:
        print(f"Overwriting existing file (force): {dest}")
        try:
            dest.unlink()
        except Exception:
            # if unlink fails, we'll attempt to overwrite when writing
            pass
    print(f"Downloading: {url}")
    try:
        r = session.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(dest, 'wb') as fh:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)
            return True
        else:
            print(f"Not found or error: {url} (status {r.status_code})")
            return False
    except Exception as e:
        print(f"Download failed: {url} -> {e}")
        return False


def main(argv=None):
    p = argparse.ArgumentParser(description='Download Binance daily kline bundles')
    p.add_argument('--bundle-dir', default=str(DEFAULT_BUNDLE_DIR), help='Local folder to store bundles')
    p.add_argument('--timeframe', default='1m', help='Kline interval folder (e.g. 1m,1h)')
    p.add_argument('--period', choices=['daily', 'monthly'], default='daily', help='Bundle period: daily (default) or monthly')
    p.add_argument('--symbols', nargs='*', help='Symbols in bundle naming (e.g. BTCUSDT ETHUSDT)')
    p.add_argument('--days-back', type=int, default=30, help='How many days back to download (default 30)')
    p.add_argument('--start-date', help='Start date YYYY-MM-DD (overrides days-back)')
    p.add_argument('--end-date', help='End date YYYY-MM-DD (overrides days-back)')
    p.add_argument('--dry-run', action='store_true', help='Only print planned downloads')
    p.add_argument('--force', action='store_true', help='Force re-download and overwrite existing files')
    p.add_argument('--pause', type=float, default=0.05, help='Pause between downloads (s)')
    args = p.parse_args(argv)

    bundle_dir = Path(args.bundle_dir)
    tf = args.timeframe

    if args.symbols:
        symbols = [s.upper() for s in args.symbols]
    else:
        symbols = get_major_pairs()

    if args.start_date and args.end_date:
        start = datetime.fromisoformat(args.start_date)
        end = datetime.fromisoformat(args.end_date)
    elif args.start_date:
        start = datetime.fromisoformat(args.start_date)
        end = datetime.utcnow()
    else:
        end = datetime.utcnow()
        start = end - timedelta(days=args.days_back)

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    # Select base URL according to desired bundle period
    if args.period == 'monthly':
        base_url = 'https://data.binance.vision/data/spot/monthly/klines'
    else:
        base_url = 'https://data.binance.vision/data/spot/daily/klines'

    planned = []
    for sym in symbols:
        if args.period == 'monthly':
            # iterate months between start and end (inclusive)
            cur = datetime(start.year, start.month, 1)
            last = datetime(end.year, end.month, 1)
            while cur <= last:
                date_str = cur.strftime('%Y-%m')
                filename = f"{sym}-{tf}-{date_str}.zip"
                url = f"{base_url}/{sym}/{tf}/{filename}"
                dest = bundle_dir / f"monthly_{tf}" / filename
                planned.append((url, dest))
                # advance one month
                if cur.month == 12:
                    cur = datetime(cur.year + 1, 1, 1)
                else:
                    cur = datetime(cur.year, cur.month + 1, 1)
        else:
            for dt in daterange(start.date(), end.date()):
                date_str = dt.strftime('%Y-%m-%d')
                filename = f"{sym}-{tf}-{date_str}.zip"
                url = f"{base_url}/{sym}/{tf}/{filename}"
                dest = bundle_dir / tf / filename
                planned.append((url, dest))

    # Dry-run prints planned items; otherwise attempt downloads.
    success = 0
    total = len(planned)
    for url, dest in planned:
        ok = download_file(url, dest, session, dry_run=args.dry_run, force=args.force)
        if ok:
            success += 1
        time.sleep(args.pause)

    print(f"Planned: {total}, succeeded (or would succeed in dry-run): {success}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
