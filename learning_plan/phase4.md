# Phase 4 — Stochastic Processes & Applied Simulation

Goal
- Understand price dynamics via discrete and continuous stochastic models and run simulation experiments.

Description
- Implement binomial models, geometric Brownian motion (GBM), and Monte Carlo experiments including option pricing comparisons with analytical formulas.

Reading
- Shreve I, Chapters 1–3 (binomial model, GBM intro)
- Steele, GBM & Ito chapters

Weekly goals
- Week 15–16: Implement GBM simulators (many paths), analyze distributional properties, create `GBM_simulation.ipynb`.
- Week 17–18: Monte Carlo option pricing and comparison with Black–Scholes; document error/CI behavior in `option_pricing_MC.ipynb`.

---

## Detailed Daily Breakdown

### Week 15
- Day 1: Implement basic GBM simulator; set seeds and parameters.
- Day 2: Generate multiple paths; compute pathwise stats.
- Day 3: Compare simulated mean/variance vs theoretical.
- Day 4: Visualize distributions and time-slices.
- Day 5: Add discretization step-size sensitivity.
- Day 6: Start `GBM_simulation.ipynb` narrative and figures.
- Day 7: Commit initial results and code.

### Week 16
- Day 1: Add alternative schemes (e.g., exact solution vs Euler-Maruyama).
- Day 2: Quantify discretization error; plot convergence.
- Day 3: Include correlation between assets (optional multi-asset GBM).
- Day 4: Summarize simulation takeaways and practical notes.
- Day 5: Polish figures and tables.
- Day 6: Finalize `GBM_simulation.ipynb`.
- Day 7: Commit/tag version.

### Week 17
- Day 1: Implement European call/put payoff simulation.
- Day 2: Add discounting; compute MC price and confidence interval.
- Day 3: Compare MC price with Black–Scholes for matching params.
- Day 4: Study variance reduction (antithetic, control variates) optional.
- Day 5: Record runtime vs accuracy trade-offs.
- Day 6: Draft `option_pricing_MC.ipynb` sections.
- Day 7: Commit intermediate results.

### Week 18
- Day 1: Expand tests across strikes/maturities/vols.
- Day 2: Summarize pricing error patterns and CI coverage.
- Day 3: Add sensitivity plots (Greeks via bump-and-revalue, optional).
- Day 4: Write conclusions and lessons learned.
- Day 5: Final figure polish and code cleanup.
- Day 6: Finalize `option_pricing_MC.ipynb`.
- Day 7: Commit/tag version and open follow-ups.

---

## Optional Extensions (skip if time-constrained)

### Rigorous Stochastic Calculus
- **Ito's Lemma deep dive**: Rigorous derivation and multi-dimensional extensions
  - Applications to option pricing and hedging
  - Change of numeraire technique
- **Martingale theory**: Filtrations, stopping times, optional sampling theorem
  - Risk-neutral pricing as martingale
  - Girsanov theorem for measure changes
- **Fokker-Planck equation**: Forward equation for probability density evolution
  - Derive from SDE, solve simple cases analytically
- **Kolmogorov equations**: Backward equation for pricing
  - Connection to Black-Scholes PDE
  - Feynman-Kac formula
- **Advanced SDEs**: Multi-dimensional systems, correlated Brownian motions
  - Existence and uniqueness theorems
  - Strong vs weak solutions

### Advanced Stochastic Models
- **Jump-diffusion (Merton model)**: Add Poisson jumps to GBM
  - Calibrate jump intensity and size distribution
  - Analyze impact on option prices vs Black-Scholes
  - Implement compensated jumps for martingale property
- **Regime-switching models**: Hidden Markov models for volatility regimes
  - 2-state model (low vol / high vol)
  - Estimate transition probabilities from data
  - Simulate paths with regime switches
- **Stochastic volatility (Heston)**: Volatility as a separate stochastic process
  - CIR process for variance
  - Correlation between price and volatility innovations
  - Monte Carlo pricing with full truncation schemes
- **Levy processes**: Beyond Brownian motion (VG, NIG processes)

### Variance Reduction Techniques
- **Antithetic variates**: Use $-Z$ along with $Z$ for dependent samples
- **Control variates**: Use Black-Scholes as control for exotic options
- **Importance sampling**: Shift distribution toward valuable regions
- **Quasi-random sequences**: Sobol/Halton sequences vs pseudo-random
- **Stratified sampling**: Partition sample space for uniform coverage

### Exotic Options & Path-Dependent Payoffs
- **Asian options**: Average price options (arithmetic/geometric)
- **Barrier options**: Knock-in/knock-out with continuous monitoring
- **Lookback options**: Depend on max/min price over path
- **American options**: Least-squares Monte Carlo (Longstaff-Schwartz)
- **Multi-asset options**: Basket, rainbow, spread options

### Greeks & Hedging
- **Delta hedging simulation**: Dynamic hedging with discrete rebalancing
  - Analyze hedging error vs rebalancing frequency
  - Transaction cost impact on P&L
- **Greeks via finite differences**: Bump-and-revalue for all Greeks
- **Pathwise derivatives**: Differentiate MC paths for more efficient Greeks
- **Likelihood ratio method**: Score function approach for sensitivity analysis

### Calibration & Model Selection
- **Parameter calibration**: Fit models to market option prices
  - Minimize squared error between model and market implied vols
  - Use scipy.optimize or global optimization (differential evolution)
- **Model comparison**: AIC/BIC for competing stochastic models
- **Implied parameters over time**: Track calibrated params and regime changes

### Risk & Scenario Analysis
- **VaR & CVaR**: Compute risk metrics from simulated P&L distributions
- **Stress testing**: Shock scenarios (vol spike, gap down, correlation breaks)
- **Wrong-way risk**: Correlation between exposure and counterparty credit
- **Model risk**: Quantify pricing error from model misspecification

### Computational Optimization
- **GPU acceleration**: Implement MC with `cupy` or `numba.cuda`
- **Parallel processing**: Multi-core with `joblib` or `multiprocessing`
- **Cython/Numba**: JIT compilation for hot loops
- **Benchmarking**: Profile code and optimize critical paths
