# Quant Strategy Self-Course

A structured 48-week learning journey in quantitative trading strategies, alpha research, and simulations.

## Project Structure

```
├── data/                   # raw & cleaned datasets
├── src/                    # main Python scripts (.py) with ##command cells
│   ├── alpha_strategies/
│   ├── simulations/
│   └── utils/              # helper functions, data loading, plotting
├── notebooks/              # exploratory notebooks, experiments
│   ├── book_notes/
│   ├── alpha_prototypes/
│   └── simulations/
├── results/                # charts, backtest outputs
├── learning_plan/          # 48-week roadmap + micro-checklists
├── docs/                   # methodology writeups, lessons learned
└── README.md
```

## Getting Started

[Add your setup instructions here]

## Learning Plan

See `learning_plan/` for the 48-week roadmap and weekly checklists.

## Data policy & quick run instructions

This repository ignores large CSV datasets that live under `data/` to avoid accidental commits. Manifest files (per-symbol YAML manifests and the global JSON manifests) are kept in source control so metadata and provenance are preserved.

- CSV files under `data/` are ignored by default. If you need to keep a small sample CSV, add an explicit negation in `.gitignore`.
- Manifests that are retained:
	- `data/**/manifest_*.yaml` (per-symbol manifests)
	- `data/**/crypto_manifest_*.json` and `data/**/manifest_*.json` (global manifests)

Running the small, safe fetch test (no edit to repo required)

Use the repository venv python executable to run a short 7-day hourly fetch for two symbols. Replace the path below with your venv python if different.

```bash
C:/Users/df/repo/quant-strategy-self-course/venv/Scripts/python.exe \
	c:/Users/df/repo/quant-strategy-self-course/scripts/test_fetcher_run.py
```

Run the full validator and summary tools (reads manifests under `data/crypto/USDT` and writes summary/validation reports):

```bash
C:/Users/df/repo/quant-strategy-self-course/venv/Scripts/python.exe \
	c:/Users/df/repo/quant-strategy-self-course/src/utils/crypto_data_validator.py

C:/Users/df/repo/quant-strategy-self-course/venv/Scripts/python.exe \
	c:/Users/df/repo/quant-strategy-self-course/src/utils/crypto_data_summary.py
```

How to keep specific CSVs

If you want to track a particular CSV (for example `data/crypto/USDT/combined/sample.csv`), add an explicit negation to `.gitignore` like:

```text
!/data/crypto/USDT/combined/sample.csv
```

Notes

- For large historical pulls, consider running the fetcher on a machine with a stable connection and respecting exchange rate limits. The fetcher uses `ccxt` with `enableRateLimit=True`.
- If you'd like, I can add a small README section with recommended disk layout and an example `git-lfs` pointer for large datasets.

## Data tooling (what we added)

This repo now contains small, well-scoped utilities to fetch, validate, summarize and surface your crypto datasets.

- Storage layout
	- Canonical per-symbol CSVs: `data/crypto/USDT/<BASE>/crypto_<BASE>_USDT_<timeframe>.csv` (stable filenames; fetcher appends new rows and deduplicates)
	- Per-symbol manifests: `data/crypto/USDT/<BASE>/manifest_1h.yaml` and `manifest_1d.yaml` (metadata, row counts, min/max, etc.)
	- Combined outputs and the one-pager: `results/data_onepager.md` and other summary CSVs under `results/` or `data/crypto/USDT/combined/`

- Important scripts (usage examples)
	- Update most-recent data for one or more symbols (defaults to top major pairs):

		```bash
		python scripts/update_symbol_latest.py BTC ETH --timeframe 1d
		# or
		python scripts/update_symbol_latest.py        # updates top major pairs, default timeframe=1d
		```

		Behavior notes: by default the updater fetches up to end-of-yesterday (UTC) to avoid partial current-day bars; pass `--include-today` to include now. Use `--overlap N` to re-fetch N overlapping bars for safety.

	- Generate the one-page summary (human-readable markdown with emoticons):

		```bash
		python scripts/generate_data_onepager.py
		```

		Output: `results/data_onepager.md` (contains two aggregated tables: 1h and 1d, one row per ticker).

	- Run tests (unit/local only; there are no integration/network tests in CI):

		```bash
		python scripts/run_all_tests.py
		```

- Key implementation files
	- `src/utils/crypto_data_fetcher.py` — chunked ccxt-based historical fetcher, stable CSV writes, YAML manifest updates, incremental updater `update_symbols_to_now()`.
	- `src/utils/crypto_data_validator.py` — schema & quality checks, manifest generation.
	- `src/utils/crypto_data_summary.py` — combined CSVs and summaries.
	- `scripts/generate_data_onepager.py` — builds `results/data_onepager.md` (includes emoticons as requested).

- Testing & policy
	- There are no integration tests in `tests/` or CI; unit/local tests are lightweight and run quickly.
	- The project uses a venv and `requirements.txt` — create/activate your venv and `pip install -r requirements.txt` before running fetchers.

If you'd like, I can (1) add quick examples showing how to change the universe of symbols, (2) add a `--dry-run` flag to the updater, or (3) add CI jobs that run only the lint/tests (no network). Tell me which and I'll add it.

## Backfill 1m using Binance public bundles (how-to)

If you need full historical 1-minute OHLCV backfills, Binance provides pre-built monthly/daily "bundle" ZIP files with 1m klines. The repo includes small utilities to download those bundles and import them into the repo partition layout (year/month CSVs + per-month manifests).

1) Download bundles (dry-run first)

Run a dry-run to see which bundle files would be downloaded. Replace `ETHUSDT` with the symbol you want.

```bash
python scripts/download_binance_bundles.py --period monthly --symbols ETHUSDT --start-date 2022-11-01 --end-date 2025-10-31 --timeframe 1m --dry-run
```

2) Download monthly historical bundles

When ready, run the real download (we include a small pause by default to be polite to the host):

```bash
python scripts/download_binance_bundles.py --period monthly --symbols ETHUSDT --start-date 2022-11-01 --end-date 2025-10-31 --timeframe 1m --pause 0.7
```

3) Download recent daily bundles (current partial month)

For the current (partial) month it's safer to use daily bundles:

```bash
python scripts/download_binance_bundles.py --period daily --symbols ETHUSDT --start-date 2025-11-01 --end-date 2025-11-08 --timeframe 1m --pause 0.7
```

4) Import bundles into repo partitions

Once the ZIPs are downloaded under `bundles/`, import them to the repo partition layout and create per-month manifests:

```bash
python scripts/import_binance_bundles.py --bundle-dir bundles --timeframe 1m --symbols ETHUSDT --force
```

Notes
- Use `--dry-run` on both downloader and importer to preview actions before making changes.
- The importer detects timestamps in micro/milli/seconds and coerces invalid rows; manifests are written to `data/crypto/USDT/<BASE>/1m/<YYYY>/<MM>/manifest_1m_<YYYY-MM>.yaml`.
- If you want Parquet output instead of CSV, say so and I can add it (recommended for large datasets).


