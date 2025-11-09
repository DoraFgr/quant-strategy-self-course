#!/usr/bin/env python3
"""Run the repository's pytest suite.

By default this script excludes tests marked with 'integration' to avoid network calls.
Pass any extra pytest args after `--`.

Examples:
  python scripts/run_all_tests.py            # run tests, excluding integration
  python scripts/run_all_tests.py -- -k smoke
  python scripts/run_all_tests.py -- -m "integration"  # run only integration tests
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]

    # Split user args at '--' so we can pass extras to pytest
    if '--' in argv:
        split_at = argv.index('--')
        extra = argv[split_at + 1 :]
    else:
        extra = []

    # Default pytest invocation: run unit tests from repo root (no integration tests present)
    cmd = [sys.executable, '-m', 'pytest', '-q'] + extra

    print(f"Running tests from {REPO_ROOT} with: {' '.join(cmd)}")

    proc = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return proc.returncode


if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
