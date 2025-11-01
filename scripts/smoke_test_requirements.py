"""
Very small and friendly smoke-test for requirements.

What it does:
- Reads `requirements.txt` and finds each package name (ignores comments and versions).
- For each package it tries a simple import. If the import works we print PASS; otherwise we print FAIL.
- Exit code is 0 if all packages imported, 1 if any import failed.
"""

from __future__ import annotations
import importlib
import sys
from pathlib import Path
import re


REQ_FILE = Path(__file__).resolve().parents[1] / "requirements.txt"

# Small map for packages that are imported under a different module name
SIMPLE_MAP = {
    "scikit-learn": "sklearn",
    "python-dotenv": "dotenv",
    "PyYAML": "yaml",
    "pillow": "PIL",
}


def read_pkg_names(path: Path) -> list[str]:
    """Return a list of raw package names (no versions, no comments).

    Examples of lines it can handle:
      pandas>=2.0.0
      # a comment
      scikit-learn==1.3.0
    """
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # drop inline comments
            line = re.split(r"\s+#", line)[0].strip()
            # split on common version/operator characters
            name = re.split(r"[<=>!~\[]", line)[0].strip()
            if name:
                out.append(name)
    return out


def try_simple_import(pkg_name: str) -> tuple[bool, str]:
    """Try a couple of simple module names for a package and return (ok, error).

    We try, in order:
    - a mapped module name from SIMPLE_MAP
    - the package name itself (e.g. "pandas")
    - the package name with '-' replaced by '_' (e.g. "python-dotenv" -> "python_dotenv")
    """
    tries = []
    mapped = SIMPLE_MAP.get(pkg_name)
    if mapped:
        tries.append(mapped)
    tries.append(pkg_name)
    tries.append(pkg_name.replace("-", "_"))

    last_err = ""
    for mod in tries:
        try:
            importlib.import_module(mod)
            return True, ""
        except Exception as e:
            last_err = str(e)
    return False, last_err


def main() -> int:
    names = read_pkg_names(REQ_FILE)
    if not names:
        print(f"No packages found in {REQ_FILE} (file missing or empty).")
        return 0

    failures = []
    print(f"Testing imports for {len(names)} entries from {REQ_FILE}\n")
    for name in names:
        ok, err = try_simple_import(name)
        if ok:
            print(f"PASS {name}")
        else:
            print(f"FAIL {name} -> {err.splitlines()[0] if err else 'import error'}")
            failures.append((name, err))

    print("\nSummary:")
    print(f"  Passed: {len(names) - len(failures)}")
    print(f"  Failed: {len(failures)}")

    return 1 if failures else 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
