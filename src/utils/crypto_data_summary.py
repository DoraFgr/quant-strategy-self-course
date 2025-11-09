"""
Simple Crypto Data Summary
Creates a basic summary of the fetched crypto data for Day 2 validation
"""

import pandas as pd
import numpy as np
import json
import hashlib
from pathlib import Path
from datetime import datetime

##command

def load_crypto_data_summary():
    """Load and summarize crypto data"""
    # point to new crypto storage layout
    data_dir = Path("data") / "crypto" / "USDT"
    
    # Try to load JSON manifests; if none exist, build a manifest by scanning per-symbol folders
    manifest_files = list(data_dir.glob("crypto_manifest_*.json"))

    print("Crypto Data Summary")
    print("=" * 40)

    manifests = []
    if manifest_files:
        for manifest_file in manifest_files:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            manifests.append(manifest)
    else:
        # Build manifests for 1h and 1d if stable CSV files exist under symbol folders
        for timeframe in ['1h', '1d']:
            symbols = {}
            total_rows = 0
            for symbol_dir in sorted([p for p in data_dir.iterdir() if p.is_dir()], key=lambda p: p.name):
                base = symbol_dir.name
                filename = f"crypto_{base}_USDT_{timeframe}.csv"
                filepath = symbol_dir / filename
                if filepath.exists():
                    df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
                    with open(filepath, 'rb') as fh:
                        file_hash = hashlib.md5(fh.read()).hexdigest()
                    symbols[f"{base}/USDT"] = {
                        'filename': filename,
                        'rows': len(df),
                        'start_date': df.index[0].isoformat(),
                        'end_date': df.index[-1].isoformat(),
                        'hash': file_hash,
                        'subfolder': base
                    }
                    total_rows += len(df)

            if symbols:
                manifest = {
                    'exchange': 'binance',
                    'timeframe': timeframe,
                    'fetch_timestamp': datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
                    'symbols': symbols,
                    'total_symbols': len(symbols),
                    'total_rows': total_rows
                }
                manifests.append(manifest)

        for manifest in manifests:
            print(f"\n{manifest['timeframe'].upper()} Data ({manifest.get('exchange','unknown')})")
            print(f"   Fetched: {manifest.get('fetch_timestamp','n/a')}")
            print(f"   Symbols: {manifest.get('total_symbols', len(manifest.get('symbols', {}))) }")
            print(f"   Total rows: {manifest.get('total_rows', 0):,}")

            # Load one sample file to check data quality
            sample_symbol = list(manifest['symbols'].keys())[0]
            sample_file = manifest['symbols'][sample_symbol]['filename']
            # Resolve sample path by searching per-symbol subfolders
            matches = list(data_dir.rglob(sample_file))
            if matches:
                sample_path = matches[0]
            else:
                raise FileNotFoundError(f"Sample file not found: {sample_file} under {data_dir}")

        df = pd.read_csv(sample_path, index_col='datetime', parse_dates=True)

        print(f"\n   Sample ({sample_symbol}):")
        print(f"   - Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   - Rows: {len(df):,}")
        print(f"   - Columns: {list(df.columns)}")
        print(f"   - Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        print(f"   - Avg daily volume: {df['volume'].mean():,.0f}")
        print(f"   - Missing values: {df.isnull().sum().sum()}")

        # Basic statistics
        returns = df['close'].pct_change().dropna()
        total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100

        print(f"   - Total return: {total_return:.1f}%")
        print(f"   - Daily volatility: {returns.std() * 100:.2f}%")

        # Data integrity checks
        integrity_issues = []

        if df.index.duplicated().any():
            integrity_issues.append("Duplicate timestamps")

        if (df['high'] < df['low']).any():
            integrity_issues.append("High < Low")

        if (df['high'] < df['open']).any() or (df['high'] < df['close']).any():
            integrity_issues.append("High < Open/Close")

        if (df['low'] > df['open']).any() or (df['low'] > df['close']).any():
            integrity_issues.append("Low > Open/Close")

        if (df['volume'] < 0).any():
            integrity_issues.append("Negative volume")

        if integrity_issues:
            print(f"   Issues: {', '.join(integrity_issues)}")
        else:
            print(f"   Data integrity: PASS")

##command

def create_combined_dataset():
    """Create a combined dataset for easier analysis"""
    data_dir = Path("data") / "crypto" / "USDT"

    print(f"\nCreating combined datasets...")

    # Helper that resolves file paths (handles per-symbol subfolders)
    def _resolve_filepath(filename: str) -> Path:
        candidate = data_dir / filename
        if candidate.exists():
            return candidate
        matches = list(data_dir.rglob(filename))
        if matches:
            return matches[0]
        raise FileNotFoundError(f"File not found: {filename} under {data_dir}")

    # Load hourly manifest (fallback to scanning per-symbol dirs)
    hourly_manifest_files = list(data_dir.glob("crypto_manifest_1h_*.json"))
    if hourly_manifest_files:
        with open(hourly_manifest_files[0], 'r') as f:
            hourly_manifest = json.load(f)
    else:
        # Build hourly manifest by scanning per-symbol folders for stable CSVs
        symbols = {}
        for symbol_dir in sorted([p for p in data_dir.iterdir() if p.is_dir()], key=lambda p: p.name):
            base = symbol_dir.name
            filename = f"crypto_{base}_USDT_1h.csv"
            matches = list(data_dir.rglob(filename))
            if not matches:
                continue
            filepath = matches[0]
            df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
            symbols[f"{base}/USDT"] = {'filename': filepath.name}
        hourly_manifest = {'symbols': symbols}

    # Combine hourly data
    all_hourly_data = []
    for symbol, file_info in hourly_manifest['symbols'].items():
        try:
            filepath = _resolve_filepath(file_info['filename'])
        except FileNotFoundError:
            print(f"Missing file for {symbol}: {file_info['filename']}")
            continue
        df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
        df['symbol'] = symbol
        all_hourly_data.append(df)

    if all_hourly_data:
        combined_hourly = pd.concat(all_hourly_data)
        combined_dir = data_dir / "combined"
        combined_dir.mkdir(parents=True, exist_ok=True)
        combined_hourly_file = combined_dir / "crypto_combined_1h.csv"
        combined_hourly.to_csv(combined_hourly_file)
        print(f"   Combined hourly: {len(combined_hourly):,} rows -> {combined_hourly_file}")

    # Load daily manifest (fallback to scanning per-symbol dirs)
    daily_manifest_files = list(data_dir.glob("crypto_manifest_1d_*.json"))
    if daily_manifest_files:
        with open(daily_manifest_files[0], 'r') as f:
            daily_manifest = json.load(f)
    else:
        symbols = {}
        for symbol_dir in sorted([p for p in data_dir.iterdir() if p.is_dir()], key=lambda p: p.name):
            base = symbol_dir.name
            filename = f"crypto_{base}_USDT_1d.csv"
            matches = list(data_dir.rglob(filename))
            if not matches:
                continue
            filepath = matches[0]
            symbols[f"{base}/USDT"] = {'filename': filepath.name}
        daily_manifest = {'symbols': symbols}

    # Combine daily data
    all_daily_data = []
    for symbol, file_info in daily_manifest['symbols'].items():
        try:
            filepath = _resolve_filepath(file_info['filename'])
        except FileNotFoundError:
            print(f"Missing file for {symbol}: {file_info['filename']}")
            continue
        df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
        df['symbol'] = symbol
        all_daily_data.append(df)

    if all_daily_data:
        combined_daily = pd.concat(all_daily_data)
        combined_dir = data_dir / "combined"
        combined_dir.mkdir(parents=True, exist_ok=True)
        combined_daily_file = combined_dir / "crypto_combined_1d.csv"
        combined_daily.to_csv(combined_daily_file)
        print(f"   Combined daily: {len(combined_daily):,} rows -> {combined_daily_file}")

##command

if __name__ == "__main__":
    # Load and summarize data
    load_crypto_data_summary()
    
    # Create combined datasets
    create_combined_dataset()
    
    print(f"\nData validation complete! All files are ready for analysis.")
    print(f"\nFiles in /data:")
    
    data_dir = Path("data")
    for file in sorted(data_dir.rglob("crypto_*")):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"   {file.name} ({size_mb:.1f} MB)")