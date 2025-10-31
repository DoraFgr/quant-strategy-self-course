# Phase 1 — Statistical Refresher

Goal
- Rebuild applied statistics and regression foundations needed for quantitative analysis.

Description
- Focused refresh on probability, sampling, hypothesis testing, and regression diagnostics with small, reproducible notebooks.

Reading
- Rice, "Mathematical Statistics and Data Analysis", Chapters 1–4
- Sen & Srivastava, "Regression Analysis", Chapters 1–3

Weekly goals
- Week 3–4: Read targeted chapters, simulate distributions, verify CLT, and produce `statistical_refresher.ipynb`.
- Week 5–6: Implement simple and multiple regression on synthetic and small real datasets; analyze residuals and inference; deliver `regression_synthetic.ipynb`.

---

## Detailed Daily Breakdown

### Week 3
- Day 1: Implement random number generation (normal/uniform) utils.
- Day 2: Simulate 100 random walks; compute sample mean/variance.
- Day 3: Scale up to 1000 paths; visualize distributions and convergence.
- Day 4: Compare empirical vs theoretical stats; write notes on law of large numbers.
- Day 5: Design a small hypothesis test example; document results.
- Day 6: Clean notebook, add functions and docstrings.
- Day 7: Commit/push with a weekly summary of insights.

### Week 4
- Day 1: Implement sampling and confidence intervals.
- Day 2: Verify CLT via sums/averages of iid variables; plot histograms.
- Day 3: Add bootstrapping example; compare CI coverage.
- Day 4: Organize notebook sections (intro, sims, results).
- Day 5: Draft conclusions for `statistical_refresher.ipynb`.
- Day 6: Peer-review pass (self): refactor code cells and naming.
- Day 7: Commit final Week 3–4 notebook and tag version.

### Week 5
- Day 1: Generate synthetic linear data; fit simple OLS.
- Day 2: Compute R², t-stats, p-values; interpret coefficients.
- Day 3: Plot residuals; check homoscedasticity and normality.
- Day 4: Introduce mild multicollinearity; observe effects on inference.
- Day 5: Document findings and create helper functions for diagnostics.
- Day 6: Clean up figures and ensure reproducibility (random seeds, versions).
- Day 7: Commit notebook progress and notes.

### Week 6
- Day 1: Build multiple regression with interaction terms.
- Day 2: Add regularization comparison (ridge/lasso) on synthetic data.
- Day 3: K-fold CV for model selection; log results.
- Day 4: Residual analysis and influence measures.
- Day 5: Summarize Week 5–6 in `regression_synthetic.ipynb`.
- Day 6: Final refactor and figure polish.
- Day 7: Commit/push; open issues for real-data extensions.

---

## Optional Extensions (skip if time-constrained)

### Advanced Statistical Methods
- **Bayesian regression**: Implement conjugate priors and MCMC sampling with `PyMC` or `Stan`
  - Compare Bayesian vs frequentist inference on same dataset
  - Credible intervals vs confidence intervals interpretation
- **Quantile regression**: Analyze tail behavior and asymmetric relationships
  - Use `statsmodels.QuantReg` for median and extreme quantiles
  - Applications: Value-at-Risk, tail risk modeling
- **Time series analysis deep dive**:
  - ARIMA/GARCH modeling for returns and volatility
  - VAR models for multi-asset relationships
  - State-space models and Kalman filtering

### Machine Learning Perspective
- **Elastic Net**: Combine L1/L2 regularization with `sklearn`
- **Cross-validation strategies**: Time-series CV, purged/embargoed CV (de Prado)
- **Feature engineering**: Polynomial features, basis expansions, splines
- **Causal inference basics**: IV regression, difference-in-differences

### Mathematical Depth
- **Matrix calculus refresher**: Gradients for ML/optimization
- **Concentration inequalities**: Hoeffding, Bernstein for backtesting significance
- **Information theory**: Entropy, mutual information for feature selection
