#!/usr/bin/env python3
"""preflight_compliance.py — Codebase inventory for agent startup (Barrier 1).

Generates .protocol/codebase_map.json with all existing classes, functions,
and test names. Prints a summary so the agent sees what already exists before
proposing new implementations. NO plan validation — pure visibility tool.

Usage:
    python scripts/preflight_compliance.py          # generate + print summary
    python scripts/preflight_compliance.py --json   # output raw JSON only
"""
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Bootstrap: allow running as `python scripts/preflight_compliance.py`
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8  # noqa: E402

_logger = __import__("logging").getLogger(__name__)
REPO_ROOT = Path(__file__).parent.parent
MAP_PATH = REPO_ROOT / ".protocol" / "codebase_map.json"
# Only scan directories where agents write code — avoids scanning backups/deprecated/etc.
_SCAN_DIRS = ("scripts", "tests")
_SKIP_DIRS = frozenset({"deprecated", "__pycache__", ".git", ".protocol"})


def _parse_file(py_file: Path) -> dict:
    """Extract classes, functions, and test names from a single .py file."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return {}
    classes, functions, tests = [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
            if node.name.startswith("test_"):
                tests.append(node.name)
    return {"classes": classes, "functions": functions, "tests": tests}


def build_map(root: Path = REPO_ROOT) -> dict:
    """Scan scripts/ and tests/ .py files and return structured inventory dict."""
    inventory: dict = {}
    scan_targets = [root / d for d in _SCAN_DIRS if (root / d).is_dir()]
    for scan_root in scan_targets:
        for py_file in scan_root.rglob("*.py"):
            if any(part in _SKIP_DIRS for part in py_file.parts):
                continue
            rel = py_file.relative_to(root).as_posix()
            data = _parse_file(py_file)
            if data:
                inventory[rel] = data
    return inventory


def save_map(inventory: dict) -> None:
    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAP_PATH.write_text(json.dumps({
        "generated": datetime.now(timezone.utc).isoformat(),
        "files": inventory,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def print_summary(inventory: dict) -> None:
    total_classes = sum(len(v.get("classes", [])) for v in inventory.values())
    total_fns = sum(len(v.get("functions", [])) for v in inventory.values())
    total_tests = sum(len(v.get("tests", [])) for v in inventory.values())
    print(f"\n[PREFLIGHT] Codebase inventory — {len(inventory)} files")
    print(f"  Classes  : {total_classes}")
    print(f"  Functions: {total_fns}")
    print(f"  Tests    : {total_tests}")
    print(f"  Map      : {MAP_PATH}")
    print("[PREFLIGHT] Lee .protocol/codebase_map.json antes de proponer nuevas implementaciones.\n")


def main() -> int:
    setup_windows_utf8()
    inventory = build_map()
    save_map(inventory)
    if "--json" in sys.argv:
        print(json.dumps(inventory, indent=2, ensure_ascii=False))
    else:
        print_summary(inventory)
    return 0


if __name__ == "__main__":
    sys.exit(main())
