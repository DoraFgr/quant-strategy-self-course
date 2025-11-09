#!/usr/bin/env python3
"""Fetch 1-minute OHLCV for given symbols using our CryptoDataFetcher.

This uses the existing fetcher to fetch 1m candles and save canonical CSVs
under `data/crypto/USDT/<BASE>/crypto_<BASE>_USDT_1m.csv`.

Default behavior: if no symbols provided, fetch top major pairs (first 5).
"""
from pathlib import Path
import sys
import argparse

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.utils.crypto_data_fetcher import CryptoDataFetcher


def normalize_symbol(s: str) -> str:
    s = s.upper()
    if '/' not in s:
        s = f"{s}/USDT"
    return s


def main(argv=None):
    p = argparse.ArgumentParser(description='Fetch 1m OHLCV for symbols')
    p.add_argument('symbols', nargs='*', help='Symbols to fetch (e.g. BTC or BTC/USDT)')
    p.add_argument('--days-back', type=int, default=1, help='How many days back to fetch')
    p.add_argument('--limit', type=int, default=None, help='Optional: limit number of candles to fetch per symbol (overrides days_back when set)')
    p.add_argument('--exchange', default='binance', help='Exchange name for ccxt')
    args = p.parse_args(argv)

    fetcher = CryptoDataFetcher(exchange_name=args.exchange)

    if not args.symbols:
        symbols = fetcher.get_major_pairs()[:5]
    else:
        symbols = [normalize_symbol(s) for s in args.symbols]

    print(f"Fetching 1m OHLCV for: {symbols} (days_back={args.days_back} limit={args.limit})")

    if args.limit:
        # If a limit is provided, fetch only up to that many candles per symbol.
        data = {}
        for s in symbols:
            df = fetcher.fetch_ohlcv_safe(s, '1m', since=None, limit=args.limit)
            data[s] = df
    else:
        data = fetcher.fetch_historical_data(symbols=symbols, timeframe='1m', days_back=args.days_back)
    manifest = fetcher.save_data(data, '1m')

    # report saved files (manifest maps symbol->info)
    for sym, info in (manifest or {}).items():
        print(sym, info)


if __name__ == '__main__':
    main()
