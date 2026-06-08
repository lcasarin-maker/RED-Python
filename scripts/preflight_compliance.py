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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Bootstrap: allow running as `python scripts/preflight_compliance.py`
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from importlib import import_module

setup_windows_utf8 = import_module("scripts.core_utils").setup_windows_utf8
compute_blast = import_module("scripts.blast_radius").compute_blast
load_internal_graph = import_module("scripts.blast_radius").load_internal_graph

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
    MAP_PATH.write_text(
        json.dumps(
            {
                "generated": datetime.now(timezone.utc).isoformat(),
                "files": inventory,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def print_summary(inventory: dict) -> None:
    total_classes = sum(len(v.get("classes", [])) for v in inventory.values())
    total_fns = sum(len(v.get("functions", [])) for v in inventory.values())
    total_tests = sum(len(v.get("tests", [])) for v in inventory.values())
    print(f"\n[PREFLIGHT] Codebase inventory — {len(inventory)} files")
    print(f"  Classes  : {total_classes}")
    print(f"  Functions: {total_fns}")
    print(f"  Tests    : {total_tests}")
    print(f"  Map      : {MAP_PATH}")
    print(
        "[PREFLIGHT] Lee .protocol/codebase_map.json antes de proponer nuevas implementaciones.\n"
    )


def _staged_python_files(root: Path = REPO_ROOT) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    return [
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip().endswith(".py")
        and line.strip().replace("\\", "/").startswith(("scripts/", "protocol_engine/"))
    ]


def print_blast_warnings(staged_files: list[str]) -> None:
    if not staged_files:
        return
    try:
        internal_graph = load_internal_graph(REPO_ROOT)
    except Exception as exc:
        print(f"[WARN] blast: no se pudo cargar internal_graph.json ({exc})")
        return
    for rel in staged_files:
        result = compute_blast(internal_graph, rel)
        direct = ", ".join(result["direct"]) if result["direct"] else "(none)"
        print(
            f"[WARN] blast: {rel} severity={result['severity']} "
            f"direct_consumers={direct}"
        )


def check_remediation_queue(root: Path = REPO_ROOT) -> None:
    queue_path = root / ".protocol" / "remediation_queue.json"
    if not queue_path.exists():
        return
    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            queue = json.load(f)
        pending = [item for item in queue if item.get("status") == "pending"]
        if not pending:
            return
        print("\n" + "!" * 80)
        print("🚨 BARRERA DE ENTRADA: COLA DE REMEDIACIÓN ACTIVA 🚨")
        print("!" * 80)
        print(f"Hay {len(pending)} fallos pendientes en la cola que requieren resolución LLM:")
        for idx, item in enumerate(pending, 1):
            print(f"  {idx}. [{item.get('project_name')}] Check: {item.get('check_name')}")
            print(f"     Síntoma: {item.get('symptom')}")
            print(f"     Path: {item.get('file_path')}")
            print(f"     Fecha: {item.get('timestamp')}")
        print("\n[MANDATO COMPORTAMIENTO]: DEBES resolver estos fallos lógicos prioritariamente")
        print("antes de realizar cualquier otro desarrollo en esta sesión.")
        print("!" * 80 + "\n")
    except Exception as e:
        print(f"[WARN] No se pudo leer la cola de remediación: {e}")


def main() -> int:
    setup_windows_utf8()
    inventory = build_map()
    save_map(inventory)
    print_blast_warnings(_staged_python_files())
    check_remediation_queue()
    if "--json" in sys.argv:
        print(json.dumps(inventory, indent=2, ensure_ascii=False))
    else:
        print_summary(inventory)
    return 0


if __name__ == "__main__":
    sys.exit(main())

