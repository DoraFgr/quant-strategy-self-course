#!/usr/bin/env python3
"""Update the canonical CSV for one or more symbols to the most recent safe date.

Usage examples:
  python scripts/update_symbol_latest.py BTC --timeframe 1d
  python scripts/update_symbol_latest.py BTC ETH --timeframe 1h --overlap 2

By default this will update up to end-of-yesterday (UTC) to avoid partial "today" bars.
Set --include-today to fetch up to now (may include partial bars).
"""
from pathlib import Path
import argparse
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.utils.crypto_data_fetcher import CryptoDataFetcher


def normalize_symbol(s: str) -> str:
    s = s.upper()
    if '/' not in s:
        s = f"{s}/USDT"
    return s


def main(argv=None):
    p = argparse.ArgumentParser(description="Update canonical CSV(s) for given symbol(s) to most recent date")
    p.add_argument('symbols', nargs='*', help='Symbol(s) to update, e.g. BTC or BTC/USDT (if omitted, defaults to top major pairs)')
    p.add_argument('--timeframe', '-t', default='1d', help='OHLC timeframe (e.g. 1h, 1d)')
    p.add_argument('--overlap', '-o', type=int, default=1, help='Number of overlapping bars to re-fetch to be safe')
    p.add_argument('--include-today', action='store_true', help='Include current partially-complete bar (fetch up to now)')
    p.add_argument('--exchange', default='binance', help='Exchange name for CCXT (default: binance)')
    args = p.parse_args(argv)

    # If no symbols passed, use the fetcher's major pairs (top 5 by default)
    if len(args.symbols) == 0:
        temp_fetcher = CryptoDataFetcher(exchange_name=args.exchange)
        symbols = temp_fetcher.get_major_pairs()[:5]
    else:
        symbols = [normalize_symbol(s) for s in args.symbols]

    fetcher = CryptoDataFetcher(exchange_name=args.exchange)

    print(f"Updating symbols: {symbols} timeframe={args.timeframe} overlap={args.overlap} include_today={args.include_today}")

    # Use the fetcher's incremental updater if available
    if hasattr(fetcher, 'update_symbols_to_now'):
        # days_back is None to rely on manifests/csv to determine where to resume
        results = fetcher.update_symbols_to_now(symbols=symbols, timeframe=args.timeframe, days_back=None, overlap=args.overlap, include_now=args.include_today)
        for sym, info in (results or {}).items():
            print(f"{sym}: {info}")
    else:
        # Fallback: fetch a small window (7 days) and save
        print("update_symbols_to_now not available on fetcher, falling back to short historical fetch")
        data = fetcher.fetch_historical_data(symbols=symbols, timeframe=args.timeframe, days_back=7)
        manifest = fetcher.save_data(data, args.timeframe)
        print("Saved manifest keys:", list(manifest.keys()))


if __name__ == '__main__':
    main()
