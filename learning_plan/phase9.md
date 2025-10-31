# Phase 9 — Credit Risk & Credit Derivatives

Goal
- Understand credit risk modeling, default probability estimation, and credit derivatives pricing.

Description
- Study structural models (Merton), reduced form models, copula methods for portfolio credit risk, and credit derivatives (CDS, CDO).

Reading
- Duffie & Singleton, "Credit Risk"
- Schönbucher, "Credit Derivatives Pricing Models"
- O'Kane, "Modelling Single-name and Multi-name Credit Derivatives"

Weekly goals
- Week 57–58: Credit fundamentals, default probability, and credit spreads; create `credit_fundamentals.ipynb`.
- Week 59–60: Merton structural model and extensions (Black-Cox); `structural_models.ipynb`.
- Week 61–62: Reduced form models (Jarrow-Turnbull, intensity models); `reduced_form_models.ipynb`.
- Week 63–64: Credit derivatives (CDS pricing, CDO tranches, copulas); `credit_derivatives.ipynb`.

---

## Detailed Daily Breakdown

### Week 57: Credit Risk Fundamentals
- Day 1: Credit ratings, rating transitions, and default statistics
- Day 2: Recovery rates and loss given default (LGD) analysis
- Day 3: Credit spreads and their relationship to default probability
- Day 4: Bootstrapping default probabilities from bond prices
- Day 5: Historical default rate analysis by rating/sector
- Day 6: Build credit spread curves from market data
- Day 7: Commit `credit_fundamentals.ipynb`

### Week 58: Credit Metrics & Risk Measures
- Day 1: Expected loss (EL) and unexpected loss (UL) framework
- Day 2: Credit VaR and portfolio credit risk
- Day 3: Risk contributions and marginal risk
- Day 4: Concentration risk measurement
- Day 5: Credit exposure profiles over time
- Day 6: Credit risk adjusted performance metrics (RAROC)
- Day 7: Commit credit risk metrics notebook

### Week 59: Merton Structural Model
- Day 1: Derive Merton model (equity as call option on firm value)
- Day 2: Implement Merton model with Black-Scholes framework
- Day 3: Calibrate to equity and debt data
- Day 4: Compute implied default probabilities and credit spreads
- Day 5: Limitations of Merton model (short-term spreads, liquidity)
- Day 6: Sensitivity analysis and Greeks
- Day 7: Commit `merton_model.ipynb`

### Week 60: Black-Cox First Passage Model
- Day 1: Understand first passage time and safety covenants
- Day 2: Implement Black-Cox model with barrier feature
- Day 3: Compare to Merton model (earlier default possibility)
- Day 4: Calibrate to term structure of credit spreads
- Day 5: Analyze impact of barrier level on default probability
- Day 6: Extensions: KMV model and distance-to-default
- Day 7: Commit `structural_models.ipynb`

### Week 61: Reduced Form Models - Jarrow-Turnbull
- Day 1: Hazard rate / intensity process framework
- Day 2: Relationship between intensity and survival probability
- Day 3: Implement constant intensity model
- Day 4: Price defaultable bonds using risk-neutral pricing
- Day 5: Calibrate intensity from market credit spreads
- Day 6: Compare structural vs reduced form approaches
- Day 7: Commit initial `reduced_form_models.ipynb`

### Week 62: Advanced Intensity Models
- Day 1: Time-dependent intensity functions
- Day 2: CIR-style stochastic intensity (doubly stochastic)
- Day 3: Correlation between default intensity and interest rates
- Day 4: Jump-to-default models
- Day 5: Simulate default times and loss distributions
- Day 6: Model comparison and calibration stability
- Day 7: Finalize `reduced_form_models.ipynb`

### Week 63: Credit Default Swaps (CDS)
- Day 1: CDS contract mechanics (premium leg, protection leg)
- Day 2: CDS pricing with survival probabilities
- Day 3: Bootstrap default curve from CDS spreads
- Day 4: CDS index pricing (CDX, iTraxx)
- Day 5: CDS-bond basis and arbitrage opportunities
- Day 6: Counterparty risk in CDS (wrong-way risk)
- Day 7: Commit `cds_pricing.ipynb`

### Week 64: Portfolio Credit Risk & CDOs
- Day 1: Portfolio loss distribution basics
- Day 2: Gaussian copula model for joint defaults
- Day 3: Implement one-factor Gaussian copula
- Day 4: CDO tranche pricing with copula
- Day 5: Base correlation and implied correlation
- Day 6: Alternatives to Gaussian copula (t-copula, Archimedean)
- Day 7: Commit `credit_derivatives.ipynb` and final summary

---

## Optional Extensions (skip if time-constrained)

### Advanced Credit Modeling
- **Multi-factor copulas**: Beyond one-factor for better correlation structure
- **Bottom-up vs top-down models**: Loss process modeling
- **Contagion models**: Default correlation through counterparty chains
- **Regime-switching credit models**: Credit spreads depend on macro state

### Credit Exotics
- **First-to-default baskets**: Pricing and hedging
- **Nth-to-default baskets**: Extension with multiple defaults
- **Credit spread options**: Options on CDS spreads
- **Contingent CDS (CCDS)**: Protection contingent on another event

### Advanced CDO Topics
- **Synthetic CDOs**: Using CDS rather than cash bonds
- **Bespoke CDOs**: Custom reference portfolios
- **CDO squared**: CDO of CDO tranches
- **Large portfolio approximation**: Fast pricing for homogeneous pools

### Counterparty Credit Risk (CVA/DVA)
- **Credit valuation adjustment**: Mark-to-market of counterparty risk
- **Debt valuation adjustment**: Benefit from own default risk
- **Exposure simulation**: Monte Carlo for future exposure profiles
- **Collateral modeling**: CSA impact on CVA
- **Wrong-way risk**: Correlation between exposure and default

### Real-World Applications
- **Loan portfolio management**: Retail and corporate credit
- **Securitization**: MBS, ABS modeling
- **Economic capital**: Regulatory capital vs economic capital
- **Stress testing**: Adverse scenario impact on credit portfolios
- **Credit alpha strategies**: Long-short credit, capital structure arbitrage

### Machine Learning for Credit
- **Default prediction models**: Logistic regression, random forests, XGBoost
- **Feature engineering**: Ratios, trends, macro indicators
- **Interpretability**: SHAP values for credit decisions
- **Regulatory constraints**: Fair lending, explainability requirements
