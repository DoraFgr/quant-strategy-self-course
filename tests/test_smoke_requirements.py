"""Pytest for verifying requirements imports (fast smoke test).

This replaces the previous script-style smoke test and is suitable for CI.
"""
from __future__ import annotations
import importlib
from pathlib import Path
import re


REQ_FILE = Path(__file__).resolve().parents[1] / "requirements.txt"

# map packages to module names when they differ
SIMPLE_MAP = {
    "scikit-learn": "sklearn",
    "python-dotenv": "dotenv",
    "PyYAML": "yaml",
    "pillow": "PIL",
}


def read_pkg_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line = re.split(r"\s+#", line)[0].strip()
            name = re.split(r"[<=>!~\[]", line)[0].strip()
            if name:
                out.append(name)
    return out


def try_simple_import(pkg_name: str) -> bool:
    mapped = SIMPLE_MAP.get(pkg_name)
    tries = []
    if mapped:
        tries.append(mapped)
    tries.append(pkg_name)
    tries.append(pkg_name.replace('-', '_'))

    for mod in tries:
        try:
            importlib.import_module(mod)
            return True
        except Exception:
            continue
    return False


def test_requirements_imports():
    names = read_pkg_names(REQ_FILE)
    assert names, f"No packages found in {REQ_FILE}"

    failed = []
    for name in names:
        ok = try_simple_import(name)
        if not ok:
            failed.append(name)

    assert not failed, f"Failed to import: {failed}"
