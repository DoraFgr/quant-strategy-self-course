# Phase 5 — Alpha Experiment 2

Goal
- Build a second, refined alpha (multi-factor), validate with walk-forward/backtest, and analyze factor interactions.

Description
- Extend single-signal experiments to multi-factor constructions (momentum + volatility adjustments), use PCA if helpful, and quantify improvements or degradation.

Weekly goals
- Week 19–20: Implement multi-factor alpha and run cross-sectional tests; create `alpha_multifactor_v2.ipynb`.
- Week 21–22: Run PCA or factor extraction, analyze variance explained and factor stability.
- Week 23–24: Walk-forward/backtest and finalize documentation of assumptions and metrics.

---

## Detailed Daily Breakdown

### Week 19
- Day 1: Define multi-factor framework (momentum + volatility + value/growth)
- Day 2: Implement second factor (e.g., volatility-adjusted returns)
- Day 3: Normalize and combine signals (equal-weight, optimal weights)
- Day 4: Test cross-sectional rank correlations between factors
- Day 5: Build long-short portfolio based on combined signal
- Day 6: Compute preliminary performance metrics
- Day 7: Commit `alpha_multifactor_v2.ipynb` draft

### Week 20
- Day 1: Add third factor (value, carry, or quality metric)
- Day 2: Implement factor orthogonalization techniques
- Day 3: Test factor combinations with different weighting schemes
- Day 4: Analyze factor contributions to total alpha
- Day 5: Run turnover and transaction cost analysis
- Day 6: Create factor exposure plots and correlation heatmaps
- Day 7: Commit updated notebook with multi-factor results

### Week 21
- Day 1: Implement PCA on factor matrix
- Day 2: Analyze eigenvalues and variance explained by components
- Day 3: Interpret principal components (factor loadings)
- Day 4: Test using PC1/PC2 as combined signals
- Day 5: Compare PCA-based vs manual combination approaches
- Day 6: Document PCA methodology and interpretation
- Day 7: Commit PCA analysis section

### Week 22
- Day 1: Implement rolling PCA to check factor stability over time
- Day 2: Analyze how factor loadings change across regimes
- Day 3: Test alternative dimensionality reduction (ICA, NMF)
- Day 4: Factor timing: predict which factors will work next period
- Day 5: Summarize factor extraction findings
- Day 6: Clean code and refactor for reusability
- Day 7: Commit complete factor analysis

### Week 23
- Day 1: Set up walk-forward framework (expanding/rolling window)
- Day 2: Implement out-of-sample backtesting with proper time alignment
- Day 3: Run walk-forward tests on multi-factor alpha
- Day 4: Compute rolling Sharpe, IC (information coefficient), turnover
- Day 5: Analyze performance degradation and stability
- Day 6: Create walk-forward performance visualization
- Day 7: Commit walk-forward results

### Week 24
- Day 1: Final robustness checks (subperiods, universes)
- Day 2: Compare to Phase 3 single-factor alpha
- Day 3: Document all assumptions, data versions, parameters
- Day 4: Write methodology and conclusions section
- Day 5: Final figure polish and narrative cleanup
- Day 6: Prepare public summary and results
- Day 7: Commit final `alpha_multifactor_v2.ipynb` and tag version

---

## Optional Extensions (skip if time-constrained)

### Advanced Factor Engineering
- **Interaction terms**: Momentum × volatility, value × momentum
- **Non-linear transformations**: Log, sqrt, rank transforms
- **Time-series features**: Moving averages, exponential smoothing
- **Cross-sectional features**: Quintile/decile ranks, z-scores within sectors
- **Macro conditioning**: Adjust factor exposures based on VIX, yield curve

### Machine Learning Factor Models
- **Autoencoder-based factors**: Deep learning for non-linear factor extraction
  - Train autoencoder on factor matrix
  - Use latent representation as combined signal
- **Sparse PCA**: L1-penalized PCA for interpretable factors
- **Dynamic factor models**: State-space models with time-varying loadings
- **Hierarchical clustering**: Group assets by factor exposures
- **Factor zoo analysis**: Test 100+ published factors, find robust subset

### Advanced Combination Methods
- **Optimal factor weighting**: Mean-variance optimization of factor portfolio
  - Maximize Sharpe subject to turnover/leverage constraints
  - Use shrinkage estimators for covariance matrix
- **Bayesian model averaging**: Weight factors by posterior model probabilities
- **Ensemble stacking**: Use ML meta-model to combine factor predictions
- **Adaptive weighting**: Adjust weights based on recent factor performance
- **Kelly-optimal allocation**: Maximize log returns across factors

### Risk Model Development
- **Factor risk model**: Decompose portfolio variance into factor and specific risk
  - Estimate factor covariance matrix
  - Compute risk attribution by factor
- **Risk parity**: Weight factors by equal risk contribution
- **Conditional risk models**: Regime-dependent covariances
- **Tail risk**: Estimate factor exposures in extreme events

### Factor Timing & Regime Analysis
- **Factor momentum**: Overweight recently strong factors
- **Regime detection**: HMM or threshold models for market states
  - High/low vol regimes, bull/bear markets
  - Switch factor weights based on detected regime
- **Macro timing**: Use economic indicators to predict factor returns
- **Crowding indicators**: Detect when factors become too popular

### Alternative Factor Construction
- **Text-based factors**: NLP on earnings calls, news, SEC filings
  - Sentiment, uncertainty, forward-guidance scores
  - LLM embeddings as factor features
- **Network factors**: Graph metrics from correlation networks
- **Order flow factors**: Microstructure-based alpha
- **Options-implied factors**: IV skew, term structure, volatility risk premium

### Performance Attribution & Analysis
- **Brinson-style attribution**: Factor allocation vs selection
- **Returns decomposition**: Factor returns + specific returns + interaction
- **Factor IC analysis**: Information coefficient time-series and decay
  - IC by sector, size, liquidity bucket
  - Optimal horizon for each factor
- **Factor concentration**: How many factors drive most returns?


