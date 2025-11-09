"""
Crypto Data Validation and Summary
Validates data quality, generates basic stats, and creates data loading utilities
Day 2 of Phase 0: Continue data pulls; ensure consistent date indices and schemas
"""

import pandas as pd
import numpy as np
import json
import os
import hashlib
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

##command

class CryptoDataValidator:
    """
    Validates crypto data quality and generates summary statistics
    Ensures consistent date indices and schemas across all data files
    """
    
    def __init__(self, data_dir: str = "data"):
        # Point to new crypto layout by default
        self.data_dir = Path(data_dir) / "crypto" / "USDT"
        self.hourly_manifest = None
        self.daily_manifest = None
        self.load_manifests()
    
    def load_manifests(self):
        """Load manifest files to understand available data"""
        manifest_files = list(self.data_dir.glob("crypto_manifest_*.json"))

        if manifest_files:
            for manifest_file in manifest_files:
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)

                if manifest.get('timeframe') == '1h':
                    self.hourly_manifest = manifest
                    print(f"Found hourly manifest: {manifest.get('total_symbols')} symbols, {manifest.get('total_rows')} rows")
                elif manifest.get('timeframe') == '1d':
                    self.daily_manifest = manifest
                    print(f"Found daily manifest: {manifest.get('total_symbols')} symbols, {manifest.get('total_rows')} rows")
        else:
            # No global JSON manifests found — build manifests by scanning per-symbol folders
            hourly = {'exchange': self.exchange_name, 'timeframe': '1h', 'symbols': {}, 'total_symbols': 0, 'total_rows': 0}
            daily = {'exchange': self.exchange_name, 'timeframe': '1d', 'symbols': {}, 'total_symbols': 0, 'total_rows': 0}

            for symbol_dir in sorted([p for p in self.data_dir.iterdir() if p.is_dir()], key=lambda p: p.name):
                base = symbol_dir.name
                # Hourly
                hf = symbol_dir / f"crypto_{base}_USDT_1h.csv"
                if hf.exists():
                    df = pd.read_csv(hf, index_col='datetime', parse_dates=True)
                    hourly['symbols'][f"{base}/USDT"] = {
                        'filename': hf.name,
                        'rows': len(df),
                        'start_date': df.index[0].isoformat(),
                        'end_date': df.index[-1].isoformat(),
                        'hash': hashlib.md5(hf.read_bytes()).hexdigest() if hasattr(hf, 'read_bytes') else None,
                        'subfolder': base
                    }
                    hourly['total_symbols'] += 1
                    hourly['total_rows'] += len(df)

                # Daily
                dfp = symbol_dir / f"crypto_{base}_USDT_1d.csv"
                if dfp.exists():
                    df2 = pd.read_csv(dfp, index_col='datetime', parse_dates=True)
                    daily['symbols'][f"{base}/USDT"] = {
                        'filename': dfp.name,
                        'rows': len(df2),
                        'start_date': df2.index[0].isoformat(),
                        'end_date': df2.index[-1].isoformat(),
                        'hash': hashlib.md5(dfp.read_bytes()).hexdigest() if hasattr(dfp, 'read_bytes') else None,
                        'subfolder': base
                    }
                    daily['total_symbols'] += 1
                    daily['total_rows'] += len(df2)

            if hourly['total_symbols'] > 0:
                self.hourly_manifest = hourly
                print(f"Built hourly manifest from files: {hourly['total_symbols']} symbols, {hourly['total_rows']} rows")
            if daily['total_symbols'] > 0:
                self.daily_manifest = daily
                print(f"Built daily manifest from files: {daily['total_symbols']} symbols, {daily['total_rows']} rows")
    
    def load_crypto_data(self, timeframe: str = '1h') -> Dict[str, pd.DataFrame]:
        """
        Load all crypto data for a given timeframe
        
        Args:
            timeframe: '1h' or '1d'
        
        Returns:
            Dictionary of symbol -> DataFrame
        """
        manifest = self.hourly_manifest if timeframe == '1h' else self.daily_manifest
        
        if not manifest:
            raise ValueError(f"No manifest found for timeframe {timeframe}")
        
        data_dict = {}

        print(f"\nLoading {timeframe} data...")

        for symbol, file_info in manifest['symbols'].items():
            filename = file_info['filename']
            filepath = self.data_dir / filename

            # If file isn't directly in the USDT folder, search subfolders (per-symbol dirs)
            if not filepath.exists():
                matches = list(self.data_dir.rglob(filename))
                if matches:
                    filepath = matches[0]
                else:
                    print(f"File not found: {filename}")
                    continue
            
            # Load data
            df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)
            
            # Verify hash if needed (optional)
            # self._verify_file_hash(filepath, file_info['hash'])
            
            data_dict[symbol] = df
            print(f"  Loaded {symbol}: {len(df)} rows from {df.index[0]} to {df.index[-1]}")
        
        return data_dict
    
    def validate_data_quality(self, data_dict: Dict[str, pd.DataFrame], timeframe: str) -> Dict:
        """
        Comprehensive data quality validation
        
        Returns:
            Dictionary with validation results
        """
        print(f"\nValidating {timeframe} data quality...")

        validation_results = {
            'timeframe': timeframe,
            'total_symbols': len(data_dict),
            'symbols': {},
            'schema_issues': [],
            'date_issues': [],
            'data_issues': []
        }
        
        expected_columns = ['open', 'high', 'low', 'close', 'volume', 'symbol']
        
        for symbol, df in data_dict.items():
            symbol_results = {
                'rows': len(df),
                'start_date': df.index[0],
                'end_date': df.index[-1],
                'null_count': df.isnull().sum().sum(),
                'duplicate_dates': df.index.duplicated().sum(),
                'schema_valid': True,
                'ohlc_valid': True,
                'volume_valid': True
            }
            
            # Check schema
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                validation_results['schema_issues'].append(f"{symbol}: Missing columns {missing_cols}")
                symbol_results['schema_valid'] = False
            
            # Check OHLC logic (High >= Open, Low <= Close, etc.)
            ohlc_issues = []
            if (df['high'] < df['open']).any():
                ohlc_issues.append("High < Open")
            if (df['high'] < df['close']).any():
                ohlc_issues.append("High < Close")
            if (df['low'] > df['open']).any():
                ohlc_issues.append("Low > Open")
            if (df['low'] > df['close']).any():
                ohlc_issues.append("Low > Close")
            
            if ohlc_issues:
                validation_results['data_issues'].extend([f"{symbol}: {issue}" for issue in ohlc_issues])
                symbol_results['ohlc_valid'] = False
            
            # Check for negative volumes
            if (df['volume'] < 0).any():
                validation_results['data_issues'].append(f"{symbol}: Negative volumes")
                symbol_results['volume_valid'] = False
            
            # Check date index consistency
            if not df.index.is_monotonic_increasing:
                validation_results['date_issues'].append(f"{symbol}: Non-monotonic dates")
            
            # Check for expected frequency
            if timeframe == '1h':
                expected_freq = pd.Timedelta(hours=1)
            elif timeframe == '1d':
                expected_freq = pd.Timedelta(days=1)
            
            time_diffs = df.index.to_series().diff().dropna()
            irregular_freq = (time_diffs != expected_freq).sum()
            if irregular_freq > 0:
                validation_results['date_issues'].append(f"{symbol}: {irregular_freq} irregular time intervals")
            
            validation_results['symbols'][symbol] = symbol_results
        
        return validation_results
    
    def generate_summary_stats(self, data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Generate summary statistics for all symbols"""
        print(f"\nGenerating summary statistics...")

        summary_data = []
        
        for symbol, df in data_dict.items():
            # Calculate returns
            df_copy = df.copy()
            df_copy['returns'] = df_copy['close'].pct_change()
            
            stats = {
                'symbol': symbol,
                'start_date': df.index[0],
                'end_date': df.index[-1],
                'observations': len(df),
                'avg_price': df['close'].mean(),
                'price_std': df['close'].std(),
                'avg_volume': df['volume'].mean(),
                'total_return': (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100,
                'volatility_annualized': df_copy['returns'].std() * np.sqrt(365 * 24) * 100,  # For hourly data
                'max_drawdown': self._calculate_max_drawdown(df['close']),
                'sharpe_ratio': self._calculate_sharpe_ratio(df_copy['returns']),
                'null_values': df.isnull().sum().sum()
            }
            
            summary_data.append(stats)
        
        summary_df = pd.DataFrame(summary_data)
        return summary_df
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min() * 100
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate annualized Sharpe ratio"""
        if returns.std() == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / (365 * 24)  # Hourly risk-free rate
        return (excess_returns.mean() / returns.std()) * np.sqrt(365 * 24)
    
    def save_validation_results(self, validation_results: Dict, summary_stats: pd.DataFrame, timeframe: str):
        """Save validation results and summary statistics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save validation results
        validation_file = self.data_dir / f"validation_report_{timeframe}_{timestamp}.json"
        with open(validation_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            results_copy = validation_results.copy()
            for symbol, symbol_data in results_copy['symbols'].items():
                symbol_data['start_date'] = symbol_data['start_date'].isoformat()
                symbol_data['end_date'] = symbol_data['end_date'].isoformat()
            # Ensure numeric numpy types are converted to native Python types
            for symbol, symbol_data in results_copy['symbols'].items():
                for k, v in list(symbol_data.items()):
                    # pandas / numpy numeric types
                    if hasattr(v, 'item') and (isinstance(v, (np.integer, np.floating)) or hasattr(v, 'dtype')):
                        try:
                            symbol_data[k] = v.item()
                        except Exception:
                            pass
            json.dump(results_copy, f, indent=2)
        
        # Save summary statistics
        summary_file = self.data_dir / f"summary_stats_{timeframe}_{timestamp}.csv"
        summary_stats.to_csv(summary_file, index=False)

        print(f"\nSaved validation results: {validation_file}")
        print(f"Saved summary statistics: {summary_file}")

        return validation_file, summary_file

    def generate_symbol_manifests(self, manifest: Dict, timeframe: str):
        """Generate per-symbol YAML manifests with field descriptions and min/max stats
        Each symbol will get a file: data/crypto/USDT/<SYMBOL>/manifest_<timeframe>.yaml
        """
        field_descriptions = {
            'open': 'Open price for the interval',
            'high': 'Highest trade price during the interval',
            'low': 'Lowest trade price during the interval',
            'close': 'Close price for the interval',
            'volume': 'Traded volume during the interval'
        }

        for symbol, info in manifest['symbols'].items():
            filename = info['filename']
            # resolve file path (allow per-symbol subfolders)
            filepath = self.data_dir / filename
            if not filepath.exists():
                matches = list(self.data_dir.rglob(filename))
                if matches:
                    filepath = matches[0]
                else:
                    print(f"Skipping manifest for {symbol}: file not found: {filename}")
                    continue

            df = pd.read_csv(filepath, index_col='datetime', parse_dates=True)

            # Basic metadata
            symbol_meta = {
                'symbol': symbol,
                'timeframe': timeframe,
                'rows': int(len(df)),
                'start_date': str(df.index[0]),
                'end_date': str(df.index[-1]),
                'total_return_pct': float((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100)
            }

            # Field stats
            fields = {}
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col not in df.columns:
                    continue
                col_series = df[col].dropna()
                fields[col] = {
                    'name': col,
                    'description': field_descriptions.get(col, ''),
                    'min': float(col_series.min()) if not col_series.empty else None,
                    'max': float(col_series.max()) if not col_series.empty else None,
                    'mean': float(col_series.mean()) if not col_series.empty else None,
                    'median': float(col_series.median()) if not col_series.empty else None,
                    'std': float(col_series.std()) if not col_series.empty else None,
                    'nulls': int(df[col].isnull().sum())
                }

            # Additional insights
            insights = {
                'price_range': {
                    'min_close': fields.get('close', {}).get('min'),
                    'max_close': fields.get('close', {}).get('max')
                },
                'avg_volume': fields.get('volume', {}).get('mean') if fields.get('volume') else None
            }

            # Build YAML content manually
            symbol_dir = filepath.parent
            manifest_path = symbol_dir / f"manifest_{timeframe}.yaml"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(f"symbol: {symbol}\n")
                f.write(f"timeframe: {timeframe}\n")
                f.write(f"rows: {symbol_meta['rows']}\n")
                f.write(f"start_date: '{symbol_meta['start_date']}'\n")
                f.write(f"end_date: '{symbol_meta['end_date']}'\n")
                f.write(f"total_return_pct: {symbol_meta['total_return_pct']}\n")
                f.write("fields:\n")
                for col, meta in fields.items():
                    f.write(f"  {col}:\n")
                    f.write(f"    name: {meta['name']}\n")
                    f.write(f"    description: '{meta['description']}'\n")
                    f.write(f"    min: {meta['min']}\n")
                    f.write(f"    max: {meta['max']}\n")
                    f.write(f"    mean: {meta['mean']}\n")
                    f.write(f"    median: {meta['median']}\n")
                    f.write(f"    std: {meta['std']}\n")
                    f.write(f"    nulls: {meta['nulls']}\n")
                f.write("insights:\n")
                f.write(f"  price_range:\n")
                f.write(f"    min_close: {insights['price_range']['min_close']}\n")
                f.write(f"    max_close: {insights['price_range']['max_close']}\n")
                f.write(f"  avg_volume: {insights['avg_volume']}\n")

            print(f"Wrote manifest for {symbol}: {manifest_path}")

##command

def main():
    """Main validation and summary function"""
    print("Crypto Data Validation & Summary")
    print("=" * 50)
    
    # Initialize validator
    validator = CryptoDataValidator()
    
    # Load and validate hourly data
    print("\nProcessing hourly data...")
    hourly_data = validator.load_crypto_data('1h')
    hourly_validation = validator.validate_data_quality(hourly_data, '1h')
    hourly_summary = validator.generate_summary_stats(hourly_data)
    
    # Load and validate daily data
    print("\nProcessing daily data...")
    daily_data = validator.load_crypto_data('1d')
    daily_validation = validator.validate_data_quality(daily_data, '1d')
    daily_summary = validator.generate_summary_stats(daily_data)
    
    # Print validation results
    print("\nVALIDATION RESULTS")
    print("-" * 30)
    
    for timeframe, validation in [('Hourly', hourly_validation), ('Daily', daily_validation)]:
        print(f"\n{timeframe} Data:")
        print(f"  Total symbols: {validation['total_symbols']}")
        print(f"  Schema issues: {len(validation['schema_issues'])}")
        print(f"  Date issues: {len(validation['date_issues'])}")
        print(f"  Data issues: {len(validation['data_issues'])}")

        if validation['schema_issues']:
            print("    Schema issues:", validation['schema_issues'])
        if validation['date_issues']:
            print("    Date issues:", validation['date_issues'])
        if validation['data_issues']:
            print("    Data issues:", validation['data_issues'])
    
    # Print summary statistics
    print("\nSUMMARY STATISTICS")
    print("-" * 30)
    
    print("\nHourly Data Summary:")
    print(hourly_summary[['symbol', 'observations', 'total_return', 'volatility_annualized', 'sharpe_ratio']].round(2))
    
    print("\nDaily Data Summary:")
    print(daily_summary[['symbol', 'observations', 'total_return', 'volatility_annualized', 'sharpe_ratio']].round(2))
    
    # Save results
    validator.save_validation_results(hourly_validation, hourly_summary, '1h')
    validator.save_validation_results(daily_validation, daily_summary, '1d')
    
    print("\nData validation complete!")
    
    # Generate per-symbol manifests (1h and 1d)
    if validator.hourly_manifest:
        validator.generate_symbol_manifests(validator.hourly_manifest, '1h')
    if validator.daily_manifest:
        validator.generate_symbol_manifests(validator.daily_manifest, '1d')

    return hourly_data, daily_data, hourly_summary, daily_summary

##command

if __name__ == "__main__":
    # Run validation
    hourly_data, daily_data, hourly_summary, daily_summary = main()
    
    # Display key insights
    print("\nKEY INSIGHTS")
    print("-" * 20)
    print(f"Data Coverage: {hourly_summary['observations'].iloc[0]:,} hours = {hourly_summary['observations'].iloc[0]/24:.0f} days")
    print(f"Best Performer: {hourly_summary.loc[hourly_summary['total_return'].idxmax(), 'symbol']} ({hourly_summary['total_return'].max():.1f}%)")
    print(f"Worst Performer: {hourly_summary.loc[hourly_summary['total_return'].idxmin(), 'symbol']} ({hourly_summary['total_return'].min():.1f}%)")
    print(f"Highest Volatility: {hourly_summary.loc[hourly_summary['volatility_annualized'].idxmax(), 'symbol']} ({hourly_summary['volatility_annualized'].max():.1f}%)")
    print(f"Best Sharpe Ratio: {hourly_summary.loc[hourly_summary['sharpe_ratio'].idxmax(), 'symbol']} ({hourly_summary['sharpe_ratio'].max():.2f})")