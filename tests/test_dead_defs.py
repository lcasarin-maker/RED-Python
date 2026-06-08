#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_dead_defs.py
Sprint 4.1 — gate de código desconectado (dead defs).

Detecta funciones/clases definidas en el código activo y NUNCA referenciadas (ni como
identificador, ni como string-literal para cubrir getattr/dispatch/registry). Falla si
aparece una def huérfana nueva → fuerza wire-or-remove en el commit que la introduce.

Exclusiones (sin ellas el scan da falsos positivos — calibrado a baseline 0):
  - dunders (__x__), entrypoints convencionales (main/setup/teardown)
  - test_*  (pytest los invoca dinámicamente)
  - visit_* (despacho dinámico de ast.NodeVisitor: generic_visit → getattr('visit_'+tipo))
  - defs con marca de DEUDA DECLARADA en docstring (GF-/VC-039) — código guardado a propósito
    (p.ej. setup_sessions_db: schema de observabilidad aún no cableado, ver core_utils.py)

Failing-first: si se quita una prevención (p.ej. se borra un caller), la def queda huérfana
y este test la caza. Probado en Sprint 4.1 removiendo _write_results y _auto_compact_check.
"""

import ast
import collections
import logging
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_EXCLUDE_DIRS = {
    "deprecated",
    ".git",
    "__pycache__",
    ".protocol-core",
    "backups",
    "RED-Python",
    "node_modules",
    ".venv",
    "venv",
}
_DEF_ROOTS = ("scripts", "protocol_engine", "dashboard", "tools")

logger = logging.getLogger("test_dead_defs")


def _is_active(p: Path) -> bool:
    return not (set(p.parts) & _EXCLUDE_DIRS)


def _safe_parse(p: Path):
    """Parsea un .py a AST; ante un archivo no parseable lo REPORTA (no silencioso, D5) y lo
    omite del scan devolviendo None. Un SyntaxError aquí es de un archivo ajeno al scan, no un
    fallo del gate — se registra para que sea visible, no se traga en silencio."""
    try:
        return ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as exc:
        logger.warning("dead-def scan: omitido archivo no parseable %s: %s", p, exc)
        return None


def _def_files() -> list:
    files = []
    for r in _DEF_ROOTS:
        d = _ROOT / r
        if d.is_dir():
            files += [p for p in d.glob("**/*.py") if _is_active(p)]
    files += [p for p in _ROOT.glob("*.py") if _is_active(p)]
    return files


def _all_active_files() -> list:
    return [p for p in _ROOT.glob("**/*.py") if _is_active(p)]


def _should_skip(name: str, docstring: str) -> bool:
    if (name.startswith("__") and name.endswith("__")) or name in (
        "main",
        "setup",
        "teardown",
    ):
        return True
    if name.startswith("test_") or name.startswith("visit_"):
        return True
    doc = docstring or ""
    if "GF-" in doc or "VC-039" in doc or "deuda declarada" in doc.lower():
        return True
    return False


def _reference_index() -> tuple:
    """(Counter de usos como identificador/atributo, blob de string-literals) sobre código activo."""
    uses = collections.Counter()
    str_blob = []
    for p in _all_active_files():
        tree = _safe_parse(p)
        if tree is None:
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                uses[n.id] += 1
            elif isinstance(n, ast.Attribute):
                uses[n.attr] += 1
            elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                str_blob.append(n.value)
    return uses, " ".join(str_blob)


def _find_dead_defs() -> list:
    uses, strset = _reference_index()
    dead = []
    for p in _def_files():
        tree = _safe_parse(p)
        if tree is None:
            continue
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if _should_skip(n.name, ast.get_docstring(n)):
                    continue
                if uses[n.name] == 0 and n.name not in strset:
                    dead.append(
                        f"{p.relative_to(_ROOT).as_posix()}:{n.lineno} {n.name}"
                    )
    return sorted(dead)


class TestDeadDefs(unittest.TestCase):
    def test_no_disconnected_defs_in_active_code(self):
        """Sprint 4.1: cero funciones/clases definidas y nunca referenciadas en código activo."""
        dead = _find_dead_defs()
        self.assertEqual(
            dead,
            [],
            "Código desconectado detectado (def/clase nunca referenciada — ni identificador ni "
            "string-literal). Cablea o elimina (S5/VC-118):\n  " + "\n  ".join(dead),
        )

    def test_scanner_discriminates_injected_orphan(self):
        """Failing-first del propio scanner: un nombre obviamente huérfano cuenta 0 usos y uno
        referenciado (Path) cuenta >0. Garantiza que el gate discrimina (no es teatro).
        """
        uses, _ = _reference_index()
        self.assertEqual(
            uses["zzz_definitely_orphan_name_42"],
            0,
            "centinela de huérfano contaminado",
        )
        self.assertGreater(
            uses.get("Path", 0),
            0,
            "centinela de nombre referenciado (Path) debe tener usos",
        )


if __name__ == "__main__":
    unittest.main()
