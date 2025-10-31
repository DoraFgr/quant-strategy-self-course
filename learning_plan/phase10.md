# Phase 10 — Numerical Methods for Derivatives Pricing

Goal
- Master numerical techniques for solving PDEs and pricing derivatives when analytical solutions don't exist.

Description
- Implement finite difference methods, tree-based methods, and advanced Monte Carlo techniques for pricing equity, FX, and interest rate derivatives.

Reading
- Wilmott, "Paul Wilmott on Quantitative Finance", Numerical Methods chapters
- Glasserman, "Monte Carlo Methods in Financial Engineering"
- Duffy, "Finite Difference Methods in Financial Engineering"

Weekly goals
- Week 65–66: Finite difference methods for Black-Scholes PDE and extensions; create `finite_difference_methods.ipynb`.
- Week 67–68: Tree methods (binomial, trinomial) for American options; `tree_methods.ipynb`.
- Week 69–70: Advanced Monte Carlo (variance reduction, quasi-random, path-dependent); `advanced_monte_carlo.ipynb`.
- Week 71–72: Multi-dimensional problems and correlation handling; `multidimensional_pricing.ipynb`.

---

## Detailed Daily Breakdown

### Week 65: Finite Difference Basics
- Day 1: Derive Black-Scholes PDE from no-arbitrage arguments
- Day 2: Transform to heat equation form
- Day 3: Implement explicit finite difference scheme
- Day 4: Analyze stability (CFL condition), convergence
- Day 5: Implement implicit scheme (solve tridiagonal system)
- Day 6: Crank-Nicolson method (best of both)
- Day 7: Commit `finite_difference_intro.ipynb`

### Week 66: FD for American Options & Extensions
- Day 1: Free boundary problem for American options
- Day 2: Implement early exercise check in implicit scheme
- Day 3: Projected SOR method for American options
- Day 4: Barrier options with FD (modify boundary conditions)
- Day 5: Greeks via finite differences (bump and solve)
- Day 6: Compare FD vs analytical solutions (accuracy, speed)
- Day 7: Commit `finite_difference_methods.ipynb`

### Week 67: Binomial Tree Model
- Day 1: Derive Cox-Ross-Rubinstein binomial tree
- Day 2: Implement for European call/put options
- Day 3: American option pricing with backward induction
- Day 4: Convergence to Black-Scholes as steps increase
- Day 5: Dividend-paying stocks and adjustments
- Day 6: Path-dependent options (Asian, lookback) with tree
- Day 7: Commit `binomial_trees.ipynb`

### Week 68: Trinomial Trees & Interest Rate Applications
- Day 1: Trinomial tree construction and parameter choice
- Day 2: Implement for equity options
- Day 3: Apply trinomial tree to Hull-White interest rate model
- Day 4: Build recombining tree for short rate
- Day 5: Price bond options and swaptions with trinomial tree
- Day 6: Compare trinomial vs binomial (convergence, smoothness)
- Day 7: Commit `tree_methods.ipynb`

### Week 69: Advanced Monte Carlo - Variance Reduction
- Day 1: Review basic Monte Carlo from Phase 4
- Day 2: Antithetic variates implementation and efficiency gain
- Day 3: Control variates (use Black-Scholes as control)
- Day 4: Importance sampling for rare events (deep OTM)
- Day 5: Stratified sampling technique
- Day 6: Compare variance reduction techniques (efficiency ratio)
- Day 7: Commit variance reduction analysis

### Week 70: Quasi-Random & Path-Dependent
- Day 1: Sobol sequences vs pseudo-random
- Day 2: Implement Sobol for high-dimensional problems
- Day 3: Asian option pricing (discrete vs continuous monitoring)
- Day 4: Lookback options (min/max tracking)
- Day 5: Barrier options with continuous monitoring (Brownian bridge)
- Day 6: Efficiency comparison across methods
- Day 7: Commit `advanced_monte_carlo.ipynb`

### Week 71: Multi-Asset Options
- Day 1: Correlated random variables (Cholesky decomposition)
- Day 2: Simulate correlated asset prices
- Day 3: Basket option pricing (weighted average of assets)
- Day 4: Best-of/worst-of options
- Day 5: Rainbow options and exchange options
- Day 6: Correlation sensitivity and Greeks
- Day 7: Commit multi-asset pricing notebook

### Week 72: High-Dimensional Problems & Advanced Topics
- Day 1: Curse of dimensionality in MC and PDE
- Day 2: Sparse grids for high-dimensional PDEs
- Day 3: Least-squares Monte Carlo (Longstaff-Schwartz) for American options
- Day 4: Path-dependent American options (early exercise)
- Day 5: Multi-asset American options
- Day 6: Compare all methods on complex derivative
- Day 7: Commit `multidimensional_pricing.ipynb` and summary

---

## Optional Extensions (skip if time-constrained)

### Advanced PDE Techniques
- **Adaptive mesh refinement**: Focus grid where needed (near strike, barriers)
- **Higher-order schemes**: Fourth-order compact schemes
- **Operator splitting**: ADI (Alternating Direction Implicit) for 2D PDEs
- **Convergence acceleration**: Richardson extrapolation, Romberg integration

### Advanced Tree Methods
- **Implied trees**: Build tree consistent with observed option prices
- **Non-recombining trees**: For path-dependent features
- **Adaptive trees**: Refine where needed (early exercise region)

### Monte Carlo Advanced
- **Multilevel Monte Carlo**: Reduce variance across discretization levels
- **Polynomial chaos**: Spectral methods for uncertainty quantification
- **Adjoint methods**: Efficient Greeks via automatic differentiation
- **GPU acceleration**: CUDA/OpenCL for massive parallelization

### Fourier Methods
- **FFT for option pricing**: Carr-Madan formula
- **Characteristic function approach**: Price European options via Fourier transform
- **COS method**: Fast pricing with Fourier-cosine expansion
- **Applications**: Heston model, jump-diffusion models

### Practical Considerations
- **Interpolation techniques**: Cubic splines, Bessel interpolation
- **Extrapolation**: Handling domain boundaries
- **Error estimation**: Theoretical vs empirical convergence rates
- **Benchmarking**: Compare speed and accuracy across methods
- **Choosing the right method**: Decision tree for method selection
