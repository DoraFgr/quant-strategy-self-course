# AI Agent Instructions for Quant Strategy Self-Course

## Project Overview

This is a **48-week structured learning journey** in quantitative trading, combining rigorous statistical foundations with practical alpha research and simulations. The project emphasizes:
- **Public accountability**: Weekly GitHub commits and documented progress
- **Reproducibility**: Data versioning, checksums, and explicit random seeds
- **Learning-by-doing**: Notebooks for exploration, Python scripts with `##command` cells for production code

## Architecture & Code Organization

### Directory Structure
```
├── data/              # Raw & cleaned datasets (time-series, market data)
├── src/               # Production Python scripts (.py) with ##command cells
│   ├── alpha_strategies/  # Signal generation, portfolio construction
│   ├── simulations/       # Monte Carlo, GBM, option pricing
│   └── utils/             # Data loading, plotting helpers, diagnostics
├── notebooks/         # Exploratory Jupyter notebooks (experiments, prototypes)
│   ├── book_notes/        # Reading summaries (Rice, Shreve, Sen & Srivastava)
│   ├── alpha_prototypes/  # Alpha signal R&D, backtests
│   └── simulations/       # Stochastic process experiments, pricing tests
├── results/           # Charts, backtest outputs, performance metrics
├── learning_plan/     # Phase files (phase0.md through phase10.md), weekly checklists
└── docs/              # Methodology writeups, lessons learned
```

### Phase-Based Learning Model
The project follows **11 phases** (see `learning_plan/plan.md`):
- **Phase 0**: Setup (env, data workflows)
- **Phase 1-2**: Statistical foundations, financial data basics
- **Phase 3, 5**: Alpha experiments (momentum, multi-factor)
- **Phase 4**: Stochastic processes & Monte Carlo
- **Phase 6-7**: Portfolio construction, internal visibility
- **Phase 8-10**: Fixed income, credit risk, numerical methods

Each phase file (`learning_plan/phase*.md`) contains:
- Weekly goals and daily breakdowns
- Optional extensions (ML, alternative data, advanced theory)
- Reading assignments from textbooks

## Code Style & Conventions

### EditorConfig Rules
- **Python**: 4-space indentation, UTF-8, LF line endings
- **Markdown**: Preserve trailing spaces (2 spaces for line breaks)
- **General**: Insert final newline, trim trailing whitespace

### Python Script Patterns
- Use `##command` cells for VS Code interactive execution (similar to Jupyter cells)
- Structure: imports → config/params → helper functions → main logic
- Always set `random.seed()` / `np.random.seed()` for reproducibility
- Document data versions with checksums or hashes

### Notebook Conventions
- Clear section headers (Markdown cells): Intro, Data Loading, Analysis, Results, Conclusions
- Run cells sequentially; avoid hidden state issues
- Export key figures to `results/` with descriptive filenames
- Include assumptions and caveats in narrative

### Naming Conventions
- Notebooks: descriptive names like `alpha_momentum_v1.ipynb`, `GBM_simulation.ipynb`
- Scripts: `data_loader.py`, `backtest_utils.py`, `signal_generators.py`
- Results: `momentum_equity_curve_2024Q1.png`, `sharpe_rolling.csv`

## Key Workflows

### Data Handling
1. **Pull data** (yfinance, ccxt, FRED) → save to `data/` with date suffix
2. **Log data versions**: Create manifest with checksums (`data/manifest.txt`)
3. **Clean & validate**: Check nulls, duplicates, index consistency
4. **Commit strategy**: TBD - exploring options between bundled data (self-contained) vs gitignore (large backtests)
   - Small reference datasets: Commit directly
   - Large historical data: Consider `.gitignore` + reproduction scripts
   - Document data sources and fetch commands for reproducibility

### Alpha Development Cycle
1. **Define signal** in `alpha_prototypes/` notebook (lookback, normalization, universe)
2. **Sanity checks**: Signal stability, turnover, no look-ahead bias
3. **Backtest**: Long top decile, short bottom decile; compute Sharpe, max drawdown
4. **Walk-forward validation**: Rolling windows, out-of-sample evaluation
5. **Document**: Assumptions, transaction costs, reproducibility steps
6. **Migrate to `src/alpha_strategies/`** when production-ready

### Simulation Workflow
1. **Implement models** in `notebooks/simulations/` (GBM, Heston, jump-diffusion)
2. **Verify distributions**: Compare simulated vs theoretical moments
3. **Discretization tests**: Euler-Maruyama vs exact solution, step-size sensitivity
4. **Option pricing**: MC vs Black-Scholes, confidence intervals, variance reduction
5. **Commit results** with figures showing convergence, error metrics

### Weekly Commit Ritual
- **Monday**: Review phase checklist, set daily goals
- **Daily**: 1-2 hours coding/learning, update notebooks
- **Friday**: Commit progress, update phase file checkboxes
- **Sunday**: Write weekly summary (GitHub Issues or discussion), adjust next week

## Dependencies & Environment

### Python Version & Package Manager
- **Python 3.11** required
- **venv** (or `uv` for faster installation) for virtual environments
- Solo learning project - optimize for rapid experimentation over production hardening

### Core Libraries (Phase 0)
- **Data**: `pandas`, `yfinance`, `ccxt` (crypto), `requests`
- **Numerics**: `numpy`, `scipy`, `statsmodels`
- **ML**: `scikit-learn`, `xgboost`, `lightgbm` (later phases)
- **Plotting**: `matplotlib`, `seaborn`, `plotly`
- **Finance**: `QuantLib` (Phase 8+), `pymc` (Bayesian extensions)

### Environment Setup
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Or using uv (faster alternative)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip freeze > requirements.txt  # After adding packages
```

### Optional Extensions
- **Crypto data**: CCXT for exchanges, Dune Analytics for on-chain
- **Sentiment**: FinBERT for NLP, Twitter API for social signals
- **Database**: SQLite/PostgreSQL for time-series storage
- **Acceleration**: `numba`, `cupy` for GPU, `cython` for hot loops

## Testing & Validation Patterns

### Minimal Testing Strategy
- **Focus**: Research and learning, not production hardening
- **Pytest for utilities**: Test data loaders, fetch pipelines, reusable helper functions in `src/utils/`
- **Skip over-testing**: Notebooks and exploratory code don't need exhaustive test coverage
- **Validation over tests**: Prefer statistical validation, sanity checks, and visual inspection

### Statistical Tests
- **CLT verification**: Simulate 1000+ paths, check convergence (Week 3-4)
- **Regression diagnostics**: Residual plots, VIF for multicollinearity (Phase 1)
- **Bootstrap CI**: Compare coverage vs nominal level

### Backtest Validation
- **Out-of-sample split**: Never optimize on full dataset
- **Rolling Sharpe**: Assess stability over time
- **Permutation tests**: Shuffle returns to test significance
- **Transaction cost sensitivity**: Vary cost assumptions, check robustness

### Simulation Validation
- **Analytical benchmarks**: GBM moments, Black-Scholes prices
- **Convergence plots**: MC error vs number of paths (log-log scale)
- **Discretization error**: Step size vs pricing error

## Common Pitfalls to Avoid

1. **Look-ahead bias**: Ensure signals use only past data; check date indices carefully
2. **Data snooping**: Don't re-optimize on test set; use walk-forward or cross-validation
3. **Overfitting**: Prefer simpler models; document out-of-sample performance
4. **Ignoring costs**: Always include realistic transaction costs and slippage
5. **Non-reproducibility**: Set seeds, freeze library versions, log data checksums
6. **Hidden state in notebooks**: Restart kernel and run all cells before committing

## Reading & Theory Integration

When implementing concepts from textbooks:
- **Rice (Stats)**: Applied notebooks in `notebooks/book_notes/`, focus on simulations
- **Sen & Srivastava (Regression)**: Diagnostic functions in `src/utils/regression_diagnostics.py`
- **Shreve I (Stochastic Calc)**: Simulation experiments validate theoretical properties
- Reference specific chapters/sections in notebook Markdown cells for traceability

## AI Agent Best Practices for This Repo

1. **Check phase context**: Read relevant `learning_plan/phase*.md` before suggesting implementations
2. **Prioritize reproducibility**: Always include seeds, versions, data hashes
3. **Notebook-first for R&D**: Use notebooks for exploration, migrate to `.py` for reusable code
4. **Commit granularly**: Daily commits with descriptive messages tied to phase/week
5. **Extend thoughtfully**: Suggest optional extensions from phase files (ML, alternative data) when user shows interest
6. **Document assumptions**: Every backtest/simulation should state lookback periods, rebalancing frequency, cost assumptions
7. **Respect learning pace**: Don't jump ahead to advanced topics (Phase 8-10) if user is in early phases
8. **Optimize for learning**: Favor clear, educational code over over-engineered solutions; this is a solo learning journey, not a production system

## Public Accountability & Visibility

- **Weekly predictions**: Generate and post forecasts with dataset hashes (Phase 3+)
- **GitHub Issues**: Track alpha hypotheses, open questions, next steps
- **Results publication**: Polish figures in `results/`, create summary dashboards
- **Internal leverage**: Translate work for stakeholders (Phase 7)
