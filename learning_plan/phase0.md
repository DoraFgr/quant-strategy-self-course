# Phase 0 — Setup

Goal
- Establish repo, tooling, and a reproducible environment so work can be executed and shared.

Description
- Create repository structure, set up virtual environment, install core Python libraries, and pull initial sample data.

Weekly goals
- Week 1: Initialize repository, create folders (`/data`, `/notebooks`, `/results`, `/docs`), install Python and libraries, create first example notebook.
- Week 2: Pull historical sample data, write basic data loader and cleaning notebook, commit initial artifacts to GitHub.

---

## Detailed Daily Breakdown

### Week 1
- Day 1: Create repo structure (`/data`, `/notebooks`, `/results`, `/docs`) and a README skeleton.
- Day 2: Install Python, create venv, install packages (pandas, numpy, matplotlib, statsmodels, scikit-learn, yfinance, ccxt).
- Day 3: Smoke-test environment; run a quick import test and freeze requirements.
- Day 4: Create `hello_world.ipynb` that fetches a small dataset and plots a simple chart.
- Day 5: Draft first alpha hypothesis in GitHub Issues; outline assumptions and metrics.
- Day 6: Optional public accountability: create/post a pinned update with project goal and repo link.
- Day 7: Review setup; list next week's data tasks.

### Week 2
- Day 1: Identify tickers/universe; script historical data pull; save to `/data`.
- Day 2: Continue data pulls; ensure consistent date indices and schemas.
- Day 3: Add basic validations (nulls, duplicates), write checksum/log of data versions.
- Day 4: Create `data_loader_cleaning.ipynb` with summary stats and quick EDA.
- Day 5: Commit/push all changes (data manifests, notebook, logs) to GitHub.
- Day 6: Visualize price series and returns; export plots to `/results`.
- Day 7: Write a short weekly summary and open issues for next week.

---

## Optional Extensions (skip if time-constrained)

### Alternative Data Sources
- **Crypto data**: Add cryptocurrency data via CCXT, Binance API, or Dune Analytics
- **On-chain metrics**: Integrate Glassnode, CryptoQuant, or blockchain explorers
- **Alternative data**: Twitter sentiment, Reddit mentions, Google Trends
- **Options data**: Add CBOE data, implied volatility surfaces from CBOE or OptionMetrics
- **Fixed income data**: Treasury yields, corporate bond data from FRED or Bloomberg

### Advanced Data Tools
- **Database for time-series**: Consider PostgreSQL or SQLite for structured storage
- **Data versioning**: Track data versions with checksums and metadata logs
- **Configuration files**: Use YAML/JSON for parameters and data sources
