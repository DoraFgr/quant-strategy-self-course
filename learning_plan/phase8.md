# Phase 8 — Fixed Income & Interest Rate Models

Goal
- Master interest rate modeling, yield curve construction, and bond pricing.

Description
- Study short rate models, HJM framework, LIBOR market models, and implement yield curve bootstrapping and calibration to market data.

Reading
- Brigo & Mercurio, "Interest Rate Models: Theory and Practice"
- Hull, "Options, Futures, and Other Derivatives", Interest Rate chapters
- James & Webber, "Interest Rate Modelling"

Weekly goals
- Week 49–50: Yield curve construction, bootstrapping, and bond pricing basics; create `yield_curve_basics.ipynb`.
- Week 51–52: Implement Vasicek and CIR short rate models with simulation and calibration; `short_rate_models.ipynb`.
- Week 53–54: Hull-White model and numerical methods for bond option pricing; `hull_white_model.ipynb`.
- Week 55–56: HJM framework and LIBOR market models; `hjm_libor_models.ipynb`.

---

## Detailed Daily Breakdown

### Week 49: Yield Curve Foundations
- Day 1: Understand zero-coupon bonds, spot rates, forward rates relationships
- Day 2: Implement bootstrapping from coupon bond prices
- Day 3: Build yield curve from FRED or Bloomberg data
- Day 4: Interpolation methods (linear, cubic spline, Nelson-Siegel)
- Day 5: Price vanilla bonds using constructed curve
- Day 6: Duration, convexity, and key rate duration calculations
- Day 7: Commit `yield_curve_basics.ipynb`

### Week 50: Bond Risk Metrics
- Day 1: DV01 and PV01 calculations
- Day 2: Portfolio-level risk metrics
- Day 3: Principal component analysis of yield curve moves
- Day 4: Historical analysis of yield curve shifts (parallel, twist, butterfly)
- Day 5: Hedging bond portfolios with swaps/futures
- Day 6: Document methodology and create visualizations
- Day 7: Commit bond risk analysis

### Week 51: Vasicek Model
- Day 1: Derive Vasicek SDE and its analytical solution
- Day 2: Implement Monte Carlo simulation of short rate paths
- Day 3: Derive zero-coupon bond pricing formula (analytical)
- Day 4: Calibrate parameters to market data (MLE or matching moments)
- Day 5: Analyze model properties (mean reversion, negative rates issue)
- Day 6: Price bond options using Vasicek
- Day 7: Commit `vasicek_model.ipynb`

### Week 52: CIR Model
- Day 1: Derive CIR SDE and non-central chi-squared distribution
- Day 2: Implement simulation (handle square-root, avoid negative rates)
- Day 3: Analytical bond pricing formula derivation
- Day 4: Calibrate CIR to historical data
- Day 5: Compare Vasicek vs CIR (pros/cons, fit quality)
- Day 6: Sensitivity analysis of parameters
- Day 7: Commit `cir_model.ipynb`

### Week 53: Hull-White Model
- Day 1: Understand time-dependent parameters (fit to initial curve)
- Day 2: Calibrate Hull-White to match market yield curve exactly
- Day 3: Simulate short rate paths with time-varying drift
- Day 4: Trinomial tree implementation for Hull-White
- Day 5: Price European and Bermudan swaptions
- Day 6: Greeks and hedging with Hull-White
- Day 7: Commit `hull_white_model.ipynb`

### Week 54: Numerical PDE Methods
- Day 1: Derive PDE for bond options from short rate models
- Day 2: Implement finite difference schemes (explicit, implicit, Crank-Nicolson)
- Day 3: Handle boundary conditions for bond derivatives
- Day 4: Compare PDE vs Monte Carlo vs analytical solutions
- Day 5: American-style exercise using PDE methods
- Day 6: Optimize numerical stability and convergence
- Day 7: Commit numerical methods notebook

### Week 55: HJM Framework
- Day 1: Study Heath-Jarrow-Morton forward rate evolution
- Day 2: No-arbitrage drift condition derivation
- Day 3: Implement simple HJM with single-factor Gaussian driving process
- Day 4: Simulate entire forward curve evolution
- Day 5: Price derivatives in HJM framework via Monte Carlo
- Day 6: Understand relationship to short rate models
- Day 7: Commit `hjm_framework.ipynb`

### Week 56: LIBOR Market Models
- Day 1: Understand LIBOR vs OIS discounting post-crisis
- Day 2: BGM/Brace-Gatarek-Musiela model formulation
- Day 3: Lognormal forward LIBOR dynamics
- Day 4: Calibrate to cap/floor volatilities (caplet pricing)
- Day 5: Swaption pricing in LMM framework
- Day 6: Terminal vs spot measure considerations
- Day 7: Commit `libor_market_model.ipynb` and final summary

---

## Optional Extensions (skip if time-constrained)

### Advanced Interest Rate Models
- **Two-factor models**: G2++ model (Gaussian two-factor)
- **Quadratic Gaussian models**: For negative rates environment
- **SABR model**: Stochastic alpha-beta-rho for swaption volatility smile
- **Affine term structure models**: General affine framework

### Credit-Adjusted Discounting
- **OIS vs LIBOR**: Multi-curve framework post-2008
- **CSA discounting**: Collateral agreements impact on pricing
- **xVA calculations**: CVA, DVA, FVA basics

### Exotic Interest Rate Derivatives
- **Range accruals**: Interest based on rate staying in range
- **CMS (Constant Maturity Swap)**: Convexity adjustments
- **Spread options**: Options on rate spreads
- **Target redemption notes (TARNs)**

### Calibration & Model Selection
- **Global calibration**: Fit to entire surface of caps and swaptions
- **Local vs global volatility**: Parallels to equity volatility modeling
- **Model risk**: Compare pricing across different rate models
- **Parameter stability**: Track calibrated parameters over time
