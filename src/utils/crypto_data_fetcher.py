"""
Crypto Historical Data Fetcher
Fetches hourly and daily historical data from multiple exchanges
Focus on safety, rate limiting, and data consistency
"""

import ccxt
import pandas as pd
import numpy as np
import time
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import requests
from tqdm import tqdm
import math

##command

class CryptoDataFetcher:
    """
    Safe crypto data fetcher with rate limiting and error handling
    Supports multiple exchanges with focus on Binance as primary
    """
    
    def __init__(self, exchange_name: str = 'binance', rate_limit: float = 0.1):
        """
        Initialize fetcher
        
        Args:
            exchange_name: Exchange to use ('binance', 'kraken', 'coinbase', etc.)
            rate_limit: Minimum seconds between requests
        """
        self.exchange_name = exchange_name
        self.rate_limit = rate_limit
        self.exchange = None
        self.last_request_time = 0
        
        # Initialize exchange
        self._init_exchange()

        # Create data directory under data/crypto/USDT (one folder per quote and symbol)
        self.data_dir = Path("data") / "crypto" / "USDT"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _init_exchange(self):
        """Initialize exchange connection with safety settings"""
        try:
            if self.exchange_name.lower() == 'binance':
                self.exchange = ccxt.binance({
                    'rateLimit': int(self.rate_limit * 1000),  # ccxt expects milliseconds
                    'enableRateLimit': True,
                    'sandbox': False,  # Use real market data
                })
            elif self.exchange_name.lower() == 'kraken':
                self.exchange = ccxt.kraken({
                    'rateLimit': int(self.rate_limit * 1000),
                    'enableRateLimit': True,
                })
            elif self.exchange_name.lower() == 'coinbase':
                self.exchange = ccxt.coinbasepro({
                    'rateLimit': int(self.rate_limit * 1000),
                    'enableRateLimit': True,
                })
            else:
                raise ValueError(f"Exchange {self.exchange_name} not supported")
                
            # Test connection
            self.exchange.load_markets()
            print(f"Connected to {self.exchange_name}")
            print(f"Found {len(self.exchange.markets)} trading pairs")
            
        except Exception as e:
            print(f"Failed to initialize {self.exchange_name}: {e}")
            raise
    
    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_major_pairs(self) -> List[str]:
        """Get list of major cryptocurrency pairs"""
        major_cryptos = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'AVAX', 'MATIC', 'LINK']
        quote_currencies = ['USDT', 'USDC', 'USD']
        
        available_pairs = []
        
        for base in major_cryptos:
            for quote in quote_currencies:
                symbol = f"{base}/{quote}"
                if symbol in self.exchange.markets:
                    available_pairs.append(symbol)
                    break  # Take first available quote currency

        print(f"Found {len(available_pairs)} major pairs: {available_pairs}")
        return available_pairs
    
    def fetch_ohlcv_safe(self, symbol: str, timeframe: str = '1h', 
                        since: Optional[int] = None, limit: int = 1000) -> pd.DataFrame:
        """
        Safely fetch OHLCV data with error handling
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe ('1m', '5m', '1h', '1d')
            since: Timestamp to start from (milliseconds)
            limit: Number of candles to fetch (max 1000 for most exchanges)
        """
        self._respect_rate_limit()
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            
            if not ohlcv:
                print(f"No data returned for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            df.drop('timestamp', axis=1, inplace=True)
            
            # Add symbol for tracking
            df['symbol'] = symbol
            
            return df
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_historical_data(self, symbols: List[str], timeframe: str = '1h', 
                            days_back: int = 365, end_time_ms: Optional[int] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple symbols
        
        Args:
            symbols: List of trading pairs
            timeframe: Data frequency ('1h', '4h', '1d')
            days_back: How many days of history to fetch
        """
        print(f"\nFetching {timeframe} data for {len(symbols)} symbols...")
        print(f"Getting {days_back} days of history")
        
        # Calculate start time (UTC)
        now_utc = datetime.utcnow()
        start_time = int((now_utc - timedelta(days=days_back)).timestamp() * 1000)

        # By default, fetch up to end-of-yesterday (UTC) to avoid partial current-day bars
        if end_time_ms is None:
            start_of_today = datetime(now_utc.year, now_utc.month, now_utc.day)
            end_time_ms = int((start_of_today - timedelta(milliseconds=1)).timestamp() * 1000)
        
        data_dict = {}
        
        for symbol in tqdm(symbols, desc="Fetching data"):
            print(f"\nFetching {symbol}...")
            
            all_data = []
            current_since = start_time
            
            # Fetch data in chunks (most exchanges limit to 1000 candles per request)
            while True:
                df = self.fetch_ohlcv_safe(symbol, timeframe, current_since, 1000)

                if df.empty:
                    break

                all_data.append(df)

                # If the newest candle we received is beyond our requested end_time_ms,
                # trim and stop fetching further.
                last_ts = int(df.index[-1].timestamp() * 1000)
                if last_ts >= end_time_ms:
                    # Trim any rows beyond end_time_ms
                    df = df[df.index <= pd.to_datetime(end_time_ms, unit='ms')]
                    all_data[-1] = df
                    break

                # If the exchange returned fewer than limit candles, we've reached the available history
                if len(df) < 1000:
                    break

                # Update since timestamp for next chunk
                current_since = int(df.index[-1].timestamp() * 1000) + 1

                print(f"  Fetched {len(df)} candles ending {df.index[-1]}")
            
            if all_data:
                # Combine all chunks
                combined_df = pd.concat(all_data)
                combined_df = combined_df[~combined_df.index.duplicated(keep='last')]  # Remove duplicates
                combined_df.sort_index(inplace=True)
                
                data_dict[symbol] = combined_df
                print(f"  Total: {len(combined_df)} candles from {combined_df.index[0]} to {combined_df.index[-1]}")
            else:
                print(f"  No data retrieved for {symbol}")
        
        return data_dict

    def _read_manifest_end_date(self, symbol_dir: Path, timeframe: str) -> Optional[datetime]:
        """Read per-symbol YAML manifest and return the end_date as datetime if present."""
        manifest_path = symbol_dir / f"manifest_{timeframe}.yaml"
        if not manifest_path.exists():
            return None
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('end_date:'):
                        # line like: end_date: '2025-11-09 04:00:00'
                        parts = line.split(':', 1)[1].strip()
                        parts = parts.strip().strip("'")
                        # Try parsing ISO or space-separated
                        try:
                            return pd.to_datetime(parts)
                        except Exception:
                            try:
                                return datetime.fromisoformat(parts)
                            except Exception:
                                return None
        except Exception:
            return None

    def update_symbols_to_now(self, symbols: List[str], timeframe: str = '1h', days_back: int = 365, overlap: int = 1, include_now: bool = True) -> Dict[str, pd.DataFrame]:
        """Update per-symbol CSVs by fetching missing data up to now.

        Algorithm:
        - For each symbol, look for an existing canonical CSV under `data/crypto/USDT/<BASE>/`.
        - If found, use its last timestamp as the since point (minus an `overlap` number of intervals to be safe).
        - If no file exists, fetch `days_back` of history.
        - Fetch up to now if `include_now` is True, otherwise up to end-of-yesterday.
        - Append new rows to the canonical CSV and update per-symbol YAML manifest.
        """
        now_utc = datetime.utcnow()
        interval = None
        if timeframe.endswith('h'):
            # e.g., '1h' -> 3600 seconds
            n = int(timeframe.replace('h','')) if timeframe.replace('h','').isdigit() else 1
            interval = timedelta(hours=n)
        elif timeframe.endswith('d'):
            n = int(timeframe.replace('d','')) if timeframe.replace('d','').isdigit() else 1
            interval = timedelta(days=n)
        else:
            # fallback: assume hours
            interval = timedelta(hours=1)

        results = {}

        for symbol in symbols:
            base = symbol.split('/')[0]
            symbol_dir = self.data_dir / base
            symbol_dir.mkdir(parents=True, exist_ok=True)
            filename = f"crypto_{base}_USDT_{timeframe}.csv"
            filepath = symbol_dir / filename

            if filepath.exists():
                existing = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
                last_ts = existing.index[-1]
                since_dt = last_ts - overlap * interval
                since_ms = int(since_dt.timestamp() * 1000)
            else:
                # No existing file, start days_back
                since_dt = now_utc - timedelta(days=days_back)
                since_ms = int(since_dt.timestamp() * 1000)

            # Determine end_time_ms
            if include_now:
                end_time_ms = int(now_utc.timestamp() * 1000)
            else:
                start_of_today = datetime(now_utc.year, now_utc.month, now_utc.day)
                end_time_ms = int((start_of_today - timedelta(milliseconds=1)).timestamp() * 1000)

            # Fetch per-symbol with since and end_time_ms
            print(f"\nUpdating {symbol} from {pd.to_datetime(since_ms, unit='ms')} to {pd.to_datetime(end_time_ms, unit='ms')}")

            all_chunks = []
            current_since = since_ms
            while True:
                df = self.fetch_ohlcv_safe(symbol, timeframe, current_since, 1000)
                if df.empty:
                    break
                all_chunks.append(df)

                last_ts = int(df.index[-1].timestamp() * 1000)
                if last_ts >= end_time_ms:
                    # Trim
                    df = df[df.index <= pd.to_datetime(end_time_ms, unit='ms')]
                    all_chunks[-1] = df
                    break

                if len(df) < 1000:
                    break

                current_since = int(df.index[-1].timestamp() * 1000) + 1

            if all_chunks:
                combined_df = pd.concat(all_chunks)
                combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
                combined_df.sort_index(inplace=True)

                # Merge with existing if any
                if filepath.exists():
                    existing = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
                    merged = pd.concat([existing, combined_df])
                    merged = merged[~merged.index.duplicated(keep='last')]
                    merged.sort_index(inplace=True)
                    merged.to_csv(filepath)
                    final_df = merged
                else:
                    combined_df.to_csv(filepath)
                    final_df = combined_df

                print(f"  Updated {filepath} -> {len(final_df)} rows")
                results[symbol] = final_df
            else:
                print(f"  No new data for {symbol}")
                if filepath.exists():
                    results[symbol] = pd.read_csv(filepath, index_col='datetime', parse_dates=True)

            # After update, write per-symbol YAML manifest for timeframe
            # Reuse existing logic in save_data by building a small manifest dict
            try:
                # read final_df if not set
                if symbol in results:
                    final_df = results[symbol]
                else:
                    if filepath.exists():
                        final_df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
                    else:
                        continue

                # Build minimal manifest-like dict and call manifest writer block
                # Reuse same code as in save_data's manifest writer (fields, insights)
                field_descriptions = {
                    'open': 'Open price for the interval',
                    'high': 'Highest trade price during the interval',
                    'low': 'Lowest trade price during the interval',
                    'close': 'Close price for the interval',
                    'volume': 'Traded volume during the interval'
                }

                fields = {}
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col not in final_df.columns:
                        continue
                    s = final_df[col].dropna()
                    fields[col] = {
                        'name': col,
                        'description': field_descriptions.get(col, ''),
                        'min': float(s.min()) if not s.empty else None,
                        'max': float(s.max()) if not s.empty else None,
                        'mean': float(s.mean()) if not s.empty else None,
                        'median': float(s.median()) if not s.empty else None,
                        'std': float(s.std()) if not s.empty else None,
                        'nulls': int(final_df[col].isnull().sum())
                    }

                total_return_pct = None
                try:
                    if 'close' in final_df.columns and len(final_df['close']) >= 2:
                        total_return_pct = float((final_df['close'].iloc[-1] / final_df['close'].iloc[0] - 1) * 100)
                except Exception:
                    total_return_pct = None

                insights = {
                    'price_range': {
                        'min_close': fields.get('close', {}).get('min'),
                        'max_close': fields.get('close', {}).get('max')
                    },
                    'avg_volume': fields.get('volume', {}).get('mean') if fields.get('volume') else None
                }

                symbol_meta = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'rows': int(len(final_df)),
                    'start_date': str(final_df.index[0]),
                    'end_date': str(final_df.index[-1]),
                    'total_return_pct': total_return_pct
                }

                manifest_path = symbol_dir / f"manifest_{timeframe}.yaml"
                with open(manifest_path, 'w', encoding='utf-8') as mf:
                    mf.write(f"symbol: {symbol}\n")
                    mf.write(f"timeframe: {timeframe}\n")
                    mf.write(f"rows: {symbol_meta['rows']}\n")
                    mf.write(f"start_date: '{symbol_meta['start_date']}'\n")
                    mf.write(f"end_date: '{symbol_meta['end_date']}'\n")
                    mf.write(f"total_return_pct: {symbol_meta['total_return_pct']}\n")
                    mf.write("fields:\n")
                    for col, meta in fields.items():
                        mf.write(f"  {col}:\n")
                        mf.write(f"    name: {meta['name']}\n")
                        mf.write(f"    description: '{meta['description']}'\n")
                        mf.write(f"    min: {meta['min']}\n")
                        mf.write(f"    max: {meta['max']}\n")
                        mf.write(f"    mean: {meta['mean']}\n")
                        mf.write(f"    median: {meta['median']}\n")
                        mf.write(f"    std: {meta['std']}\n")
                        mf.write(f"    nulls: {meta['nulls']}\n")
                    mf.write("insights:\n")
                    mf.write("  price_range:\n")
                    mf.write(f"    min_close: {insights['price_range']['min_close']}\n")
                    mf.write(f"    max_close: {insights['price_range']['max_close']}\n")
                    mf.write(f"  avg_volume: {insights['avg_volume']}\n")

            except Exception as e:
                print(f"  Failed to write manifest for {symbol}: {e}")

        return results
    
    def save_data(self, data_dict: Dict[str, pd.DataFrame], timeframe: str):
        """Save data to CSV files with metadata"""
        # Use a stable filename per symbol/timeframe to avoid creating many timestamped files
        fetch_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        manifest = {
            'exchange': self.exchange_name,
            'timeframe': timeframe,
            'fetch_timestamp': fetch_timestamp,
            'symbols': {},
            'total_symbols': 0,
            'total_rows': 0
        }

        print(f"\nSaving data to {self.data_dir} ...")

        for symbol, df in data_dict.items():
            if df.empty:
                continue

            safe_symbol = symbol.replace('/', '_')
            filename = f"crypto_{safe_symbol}_{timeframe}.csv"  # stable filename
            base = symbol.split('/')[0]
            symbol_dir = self.data_dir / base
            symbol_dir.mkdir(parents=True, exist_ok=True)
            filepath = symbol_dir / filename

            # If a file already exists, read and append only missing rows
            if filepath.exists():
                existing = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
                # Only keep new rows beyond the last timestamp in existing file
                last_ts = existing.index[-1]
                new_rows = df[df.index > last_ts]
                if not new_rows.empty:
                    combined = pd.concat([existing, new_rows])
                    combined = combined[~combined.index.duplicated(keep='last')]
                    combined.sort_index(inplace=True)
                    combined.to_csv(filepath)
                    final_df = combined
                    action = f"appended {len(new_rows)} rows"
                else:
                    final_df = existing
                    action = "no new rows"
            else:
                # Write new file
                df.to_csv(filepath)
                final_df = df
                action = f"wrote {len(df)} rows"

            # Calculate file hash for integrity
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            manifest['symbols'][symbol] = {
                'filename': filename,
                'rows': len(final_df),
                'start_date': final_df.index[0].isoformat(),
                'end_date': final_df.index[-1].isoformat(),
                'hash': file_hash,
                'subfolder': base
            }

            manifest['total_symbols'] += 1
            manifest['total_rows'] += len(final_df)

            print(f"  {action} for {symbol} -> {filepath.name} ({len(final_df)} rows)")

            # --- Write per-symbol YAML manifest for this timeframe ---
            # Use same field descriptions as validator
            field_descriptions = {
                'open': 'Open price for the interval',
                'high': 'Highest trade price during the interval',
                'low': 'Lowest trade price during the interval',
                'close': 'Close price for the interval',
                'volume': 'Traded volume during the interval'
            }

            # Build fields stats
            fields = {}
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col not in final_df.columns:
                    continue
                s = final_df[col].dropna()
                fields[col] = {
                    'name': col,
                    'description': field_descriptions.get(col, ''),
                    'min': float(s.min()) if not s.empty else None,
                    'max': float(s.max()) if not s.empty else None,
                    'mean': float(s.mean()) if not s.empty else None,
                    'median': float(s.median()) if not s.empty else None,
                    'std': float(s.std()) if not s.empty else None,
                    'nulls': int(final_df[col].isnull().sum())
                }

            total_return_pct = None
            try:
                if 'close' in final_df.columns and len(final_df['close']) >= 2:
                    total_return_pct = float((final_df['close'].iloc[-1] / final_df['close'].iloc[0] - 1) * 100)
            except Exception:
                total_return_pct = None

            insights = {
                'price_range': {
                    'min_close': fields.get('close', {}).get('min'),
                    'max_close': fields.get('close', {}).get('max')
                },
                'avg_volume': fields.get('volume', {}).get('mean') if fields.get('volume') else None
            }

            symbol_meta = {
                'symbol': symbol,
                'timeframe': timeframe,
                'rows': int(len(final_df)),
                'start_date': str(final_df.index[0]),
                'end_date': str(final_df.index[-1]),
                'total_return_pct': total_return_pct
            }

            # Write YAML manifest manually to avoid adding a dependency
            manifest_path = symbol_dir / f"manifest_{timeframe}.yaml"
            try:
                with open(manifest_path, 'w', encoding='utf-8') as mf:
                    mf.write(f"symbol: {symbol}\n")
                    mf.write(f"timeframe: {timeframe}\n")
                    mf.write(f"rows: {symbol_meta['rows']}\n")
                    mf.write(f"start_date: '{symbol_meta['start_date']}'\n")
                    mf.write(f"end_date: '{symbol_meta['end_date']}'\n")
                    mf.write(f"total_return_pct: {symbol_meta['total_return_pct']}\n")
                    mf.write("fields:\n")
                    for col, meta in fields.items():
                        mf.write(f"  {col}:\n")
                        mf.write(f"    name: {meta['name']}\n")
                        mf.write(f"    description: '{meta['description']}'\n")
                        mf.write(f"    min: {meta['min']}\n")
                        mf.write(f"    max: {meta['max']}\n")
                        mf.write(f"    mean: {meta['mean']}\n")
                        mf.write(f"    median: {meta['median']}\n")
                        mf.write(f"    std: {meta['std']}\n")
                        mf.write(f"    nulls: {meta['nulls']}\n")
                    mf.write("insights:\n")
                    mf.write("  price_range:\n")
                    mf.write(f"    min_close: {insights['price_range']['min_close']}\n")
                    mf.write(f"    max_close: {insights['price_range']['max_close']}\n")
                    mf.write(f"  avg_volume: {insights['avg_volume']}\n")
                print(f"  Updated manifest for {symbol}: {manifest_path}")
            except Exception as e:
                print(f"  Failed to write manifest for {symbol}: {e}")

        # NOTE: We do not write a JSON manifest here because per-symbol YAML manifests
        # are the canonical source of metadata for each symbol (validator writes them).
        # Returning the manifest dict so callers can inspect or persist if desired.
        print(f"\nSaved data for {manifest['total_symbols']} symbols, {manifest['total_rows']} rows")

        return manifest

##command

def main():
    """Main execution function"""
    print("Crypto Historical Data Fetcher")
    print("=" * 50)
    
    # Initialize fetcher
    fetcher = CryptoDataFetcher(exchange_name='binance', rate_limit=0.1)
    
    # Get major trading pairs
    symbols = fetcher.get_major_pairs()
    
    # Fetch 1-year of hourly data
    print("\nPhase 1: Fetching hourly data (1 year)")
    hourly_data = fetcher.fetch_historical_data(
        symbols=symbols[:5],  # Start with 5 symbols to test
        timeframe='1h',
        days_back=365
    )
    
    # Save hourly data
    hourly_manifest = fetcher.save_data(hourly_data, '1h')
    
    # Also fetch daily data for longer history
    print("\nPhase 2: Fetching daily data (2 years)")
    daily_data = fetcher.fetch_historical_data(
        symbols=symbols[:5],
        timeframe='1d',
        days_back=730
    )
    
    # Save daily data
    daily_manifest = fetcher.save_data(daily_data, '1d')
    
    print("\nData fetch complete!")
    print(f"Hourly data: {hourly_manifest['total_symbols']} symbols, {hourly_manifest['total_rows']} rows")
    print(f"Daily data: {daily_manifest['total_symbols']} symbols, {daily_manifest['total_rows']} rows")
    
    return hourly_data, daily_data

##command

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Run main function
    hourly_data, daily_data = main()