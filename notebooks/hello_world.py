# hello_world.py
# Purpose: fetch small sample dataset (crypto, indices, forex) and plot a simple chart.

#%%
# Imports and configuration
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Tickers: top 5 crypto (USD pairs via yfinance), 1-2 indices, and forex pairs
TICKERS = {
    'crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD'],
    'indices': ['^GSPC', '^IXIC'],  # S&P 500 and NASDAQ
    'forex': ['EURUSD=X', 'GBPUSD=X']
}

START = '2024-01-01'
END = datetime.today().strftime('%Y-%m-%d')

# %%
# Simple fetch function using yfinance. Returns a DataFrame or a dict of DataFrames depending on input.
def fetch_tickers(ticker_list, start=START, end=END, interval='1d'):
    """Fetch historical adjusted close prices for a list of tickers using yfinance.

    Returns a DataFrame of adjusted closes (columns=tickers) when possible.
    """
    if not ticker_list:
        return pd.DataFrame()

    # yfinance can download multiple tickers at once; use auto_adjust to get adjusted prices
    raw = yf.download(ticker_list, start=start, end=end, interval=interval, group_by='ticker', auto_adjust=True, threads=True)

    # If single ticker, ensure consistent DataFrame
    if isinstance(raw.columns, pd.MultiIndex):
        # We'll extract the 'Close' column (already adjusted due to auto_adjust)
        adj_close = pd.concat([raw[t]['Close'].rename(t) for t in ticker_list], axis=1)
    else:
        # raw is a single ticker DataFrame
        adj_close = raw['Close'].to_frame()
        adj_close.columns = ticker_list

    return adj_close

# (Next step: run a small fetch and inspect shape; we'll add that after you confirm tickers/time range.)

# %%
# Example usage: fetch a small sample (BTC-USD and ^GSPC), save to data/ and show head/shape
import os
os.makedirs('data', exist_ok=True)

sample = fetch_tickers(['BTC-USD', '^GSPC'])
sample_path = 'data/hello_world_sample_combined_from_notebook.csv'
sample.to_csv(sample_path)
print('Saved:', sample_path)
print('Shape:', sample.shape)
print(sample.head())

# %%
# Plotting cell: simple adjusted-close time series and save figure + returns CSV
os.makedirs('results', exist_ok=True)
fig, ax = plt.subplots(figsize=(10, 5))
sample.plot(ax=ax)
ax.set_title('Adjusted Close — BTC and S&P (sample)')
ax.set_xlabel('Date')
ax.set_ylabel('Price (USD)')
ax.legend(sample.columns)
plt.tight_layout()
fig_path = 'results/hello_world_prices.png'
plt.savefig(fig_path)
plt.show()

# compute daily returns and save
returns = sample.pct_change().dropna()
returns_path = 'results/hello_world_returns.csv'
returns.to_csv(returns_path)
print('Saved returns:', returns_path)
print('Figure saved:', fig_path)
