# Phase 2 — Financial Data Foundations

Goal
- Become comfortable acquiring, cleaning, and summarizing financial time series and run basic factor regressions.

Description
- Work with equities/crypto, compute returns, volatility, and implement CAPM / Fama-French regressions with clear notebooks and reproducible code.

Reading
- Ilmanen, "Expected Returns", Chapters 1–3

Weekly goals
- Week 7: Pull 50–100 stock/asset histories, compute returns and basic stats, create `returns_volatility.ipynb`.
- Week 8: Implement CAPM regressions per asset and document alpha/beta findings in `CAPM_analysis.ipynb`.
- Week 9–10: Implement Fama-French 3-factor regressions, save results in `FF3_factor_model.ipynb`.

---

## Detailed Daily Breakdown

### Week 7
- Day 1: Define universe and date range; draft data pull script.
- Day 2: Fetch raw data; store as partitioned CSV/Parquet in `/data`.
- Day 3: Compute daily and monthly returns; align calendars/time zones.
- Day 4: Calculate basic stats (mean, std, Sharpe per asset) and sanity-check outliers.
- Day 5: Start `returns_volatility.ipynb`; add plots and tables.
- Day 6: Add data quality checks and logging.
- Day 7: Commit/push notebook and data manifest.

### Week 8
- Day 1: Prepare risk-free rate and market proxy series.
- Day 2: Build CAPM regression loop using `statsmodels.OLS`.
- Day 3: Persist results (alpha, beta, R²) to a tidy table.
- Day 4: Visualize distribution of alphas/betas across assets.
- Day 5: Document methodology and assumptions in the notebook.
- Day 6: Code cleanup and function extraction.
- Day 7: Commit `CAPM_analysis.ipynb` and results.

### Week 9
- Day 1: Acquire/construct Fama-French 3 factors aligned to your universe.
- Day 2: Join factors to asset returns; verify alignment and missing data.
- Day 3: Run FF3 regressions and collect loadings and t-stats.
- Day 4: Validate results; compare to CAPM outcomes.
- Day 5: Create plots for factor loadings and alpha distributions.
- Day 6: Draft text for `FF3_factor_model.ipynb`.
- Day 7: Commit intermediate results.

### Week 10
- Day 1: Robustness checks (subperiods, winsorization, outlier handling).
- Day 2: Re-run regressions on robustness subsets.
- Day 3: Summarize model fit metrics and insights.
- Day 4: Finalize figures and tables.
- Day 5: Write conclusions and limitations.
- Day 6: Final code polish; ensure reproducibility.
- Day 7: Commit final `FF3_factor_model.ipynb` and tag version.

---

## Optional Extensions (skip if time-constrained)

### Crypto & Alternative Assets
- **Crypto factor models**: Replicate Fama-French for crypto universe
  - Size: market cap quintiles
  - Momentum: trailing returns
  - Volatility: realized vol or beta to BTC
- **On-chain factors**: Transaction volume, active addresses, exchange flows
- **DeFi metrics**: TVL changes, protocol revenues, token emissions
- **Cross-asset factors**: Crypto beta to equities, gold, USD

### Alternative Data Integration
- **Sentiment signals**: Twitter/Reddit sentiment scores via NLP
  - Use pre-trained models (FinBERT, StockTwits embeddings)
  - Aggregate sentiment to daily/weekly frequency
- **Order book data**: Microstructure features (bid-ask spread, depth, imbalance)
- **Options data**: Implied volatility, skew, put/call ratios
- **Macro data**: Fed funds rate, yield curve, credit spreads from FRED API

### Advanced Data Processing
- **Robust statistics**: Winsorization, trimmed means for outlier handling
- **Data quality scoring**: Create metadata tracking coverage, staleness, anomalies
- **Corporate actions handling**: Splits, dividends, mergers adjustments
- **Survivorship bias**: Add delisted stocks to avoid upward bias
- **Point-in-time data**: Ensure no look-ahead bias in fundamentals

### Advanced Factor Models
- **Fama-French 5-factor**: Add profitability (RMW) and investment (CMA) factors
- **Custom factors**: Construct your own (e.g., earnings quality, accruals)
- **Dynamic factor models**: Time-varying betas, rolling regressions
- **Instrumented regressions**: Address endogeneity in factor loadings

### Performance Attribution
- **Brinson attribution**: Decompose returns into allocation vs selection
- **Risk decomposition**: Variance attribution to systematic vs idiosyncratic risk
- **Factor timing**: Analyze when factors work vs fail (regime analysis)
