"""Docstring for conftest."""
import json
import os
import subprocess
import sys
import ast
import logging
from datetime import datetime, timezone
from pathlib import Path

# Ensure the project root is in sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)


def pytest_sessionfinish(session, exitstatus):
    """Imprime reporte automático de calidad de tests al final de cada sesión.
    No bloquea — informa sobre F4 (boundary coverage) y G4 (tests demasiado amplios).
    El usuario no necesita hacer nada — el análisis es automático.
    """
    tests_dir = Path(__file__).parent
    BOUNDARY_VALS = frozenset({None, 0, -1})
    files_no_boundary, wide_tests = [], []

    for f in tests_dir.glob("test_*.py"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if "scripts." not in content:
                continue
            tree = ast.parse(content, filename=f.name)
            funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
            if len(funcs) >= 3:
                has_boundary = any(
                    (isinstance(n, ast.Constant) and (n.value in BOUNDARY_VALS or n.value == ""))
                    or (isinstance(n, ast.List) and not n.elts)
                    for n in ast.walk(tree)
                )
                if not has_boundary:
                    files_no_boundary.append(f.name)
            import_names = {
                alias.asname or alias.name
                for nd in ast.walk(tree)
                if isinstance(nd, ast.ImportFrom) and nd.module and nd.module.startswith("scripts.")
                for alias in nd.names
            }
            for fn in funcs:
                called = {
                    getattr(c.func, "id", None) or getattr(c.func, "attr", None)
                    for c in ast.walk(fn) if isinstance(c, ast.Call)
                } & import_names
                if len(called) >= 5:
                    wide_tests.append(f"{f.name}:{fn.name}()")
        except SyntaxError as e:
            logging.debug("conftest: skip unparseable %s: %s", f.name, e)

    lines = ["\n--- REPORTE AUTO CALIDAD DE TESTS ---"]
    if files_no_boundary:
        lines.append(f"[F4] Sin inputs de borde (None/0/''): {', '.join(files_no_boundary)}")
    else:
        lines.append("[F4] OK — inputs de borde presentes en todos los archivos relevantes")
    if wide_tests:
        lines.append(f"[G4] Tests demasiado amplios (5+ funciones): {', '.join(wide_tests)}")
    else:
        lines.append("[G4] OK — sin tests que abarquen 5+ funciones a la vez")
    # Barrier 2: [I] conditional — only fire when AI modified both code AND tests
    _changed: list = []
    try:
        _diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=str(tests_dir.parent),
        )
        _changed = [f for f in _diff.stdout.splitlines() if f.endswith(".py")]
    except Exception as _git_exc:
        logging.debug("theater_risk: git unavailable: %s", _git_exc)
    _theater_risk = any(not f.startswith("tests/") for f in _changed) and any(
        f.startswith("tests/") for f in _changed
    )
    if _theater_risk:
        lines.append("[I]  AVISO: IA escribio codigo Y tests — verifica que al menos 1 test falla sin el feature.")
        _ev_dir = tests_dir.parent / ".protocol" / "evidence"
        _ev_dir.mkdir(parents=True, exist_ok=True)
        _ev_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "test_quality_theater_risk",
            "outcome": "blocked",
            "details": {
                "files": _changed,
                "verified": False,
                "risk_translation": (
                    "Codigo y tests cambiaron juntos; se previene aprobar un verde "
                    "complaciente sin prueba de falsabilidad independiente."
                ),
                "rollback_guarantee": "No se modifica codigo productivo desde este hook.",
            },
        }
        _ev_path = _ev_dir / f"theater_risk_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        try:
            _ev_path.write_text(json.dumps(_ev_payload, indent=2))
        except Exception as _write_exc:
            logging.debug("theater_risk evidence write failed: %s", _write_exc)
    lines.append("--------------------------------------")

    print("\n".join(lines))
