#!/usr/bin/env python3
"""Central CLI to run repository scripts from one place.

This prevents having many ad-hoc top-level scripts. It invokes the existing
script files under `scripts/` using the repository Python interpreter so
behaviour is identical to running them directly.

Usage examples:
  python scripts/cli.py fetch-1m --symbols BTC --limit 120
  python scripts/cli.py import-bundles --bundle-dir ./bundles --timeframe 1m --dry-run
  python scripts/cli.py generate-onepager
  python scripts/cli.py update-latest BTC --timeframe 1d
  python scripts/cli.py run-tests
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / 'scripts'


def run_script(script_name: str, extra_args: list[str] | None = None) -> int:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return 2
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd += extra_args
    print(f"Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd)
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(prog='repo-cli', description='Central script runner for repo utilities')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('generate-onepager', help='Generate results/data_onepager.md')

    f1 = sub.add_parser('fetch-1m', help='Fetch 1m OHLCV')
    f1.add_argument('symbols', nargs='*', help='Symbols to fetch (e.g. BTC)')
    f1.add_argument('--limit', type=int, help='Limit candles per symbol')
    f1.add_argument('--days-back', type=int, default=1)

    ib = sub.add_parser('import-bundles', help='Import local Binance bundles')
    ib.add_argument('--bundle-dir', required=True)
    ib.add_argument('--timeframe', default='1m')
    ib.add_argument('--symbols', nargs='*')
    ib.add_argument('--dry-run', action='store_true')

    upd = sub.add_parser('update-latest', help='Update canonical CSVs to most recent')
    upd.add_argument('symbols', nargs='*')
    upd.add_argument('--timeframe', default='1d')
    upd.add_argument('--include-today', action='store_true')
    upd.add_argument('--overlap', type=int, default=1)

    sub.add_parser('run-tests', help='Run all repo tests (wrapper around scripts/run_all_tests.py)')

    ns, extras = p.parse_known_args(argv)

    if ns.cmd is None:
        p.print_help()
        return 2

    if ns.cmd == 'generate-onepager':
        return run_script('generate_data_onepager.py', extras)

    if ns.cmd == 'fetch-1m':
        args = []
        if ns.symbols:
            args += ns.symbols
        if ns.limit:
            args += ['--limit', str(ns.limit)]
        if ns.days_back:
            args += ['--days-back', str(ns.days_back)]
        args += extras
        return run_script('fetch_1m_ohlcv.py', args)

    if ns.cmd == 'import-bundles':
        args = ['--bundle-dir', ns.bundle_dir, '--timeframe', ns.timeframe]
        if ns.symbols:
            args += ['--symbols'] + list(ns.symbols)
        if ns.dry_run:
            args.append('--dry-run')
        args += extras
        return run_script('import_binance_bundles.py', args)

    if ns.cmd == 'update-latest':
        args = []
        if ns.symbols:
            args += ns.symbols
        args += ['--timeframe', ns.timeframe, '--overlap', str(ns.overlap)]
        if ns.include_today:
            args.append('--include-today')
        args += extras
        return run_script('update_symbol_latest.py', args)

    if ns.cmd == 'run-tests':
        return run_script('run_all_tests.py', extras)

    print('Unknown command')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
