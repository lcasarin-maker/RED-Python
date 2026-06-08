#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_core_self_audit.py
Sprint 6 — exclusión mínima y real.

El auditor se auto-exime de la D-suite en `_get_audit_files()` (línea ~442) para 4
archivos core, porque contiene los PATRONES de detección como literales de string y
escanearse a sí mismo daría falsos positivos en D6/D7. Esa exención es legítima PERO
demasiado amplia: también ocultaba violaciones reales de D5 (except silenciosos) en el
propio auditor.

Este test re-arma la cobertura D5 para los archivos exentos: usa el MISMO `TryBlockVisitor`
del auditor y exige cero handlers silenciosos (pass/continue/...). Así la exención queda
acotada a lo que necesita (dimensiones de string-pattern) y no puede esconder un except mudo.
"""

import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.run_security_audit_12d import TryBlockVisitor

# Archivos exentos de la D-suite (run_security_audit_12d._get_audit_files) + el motor de
# reglas (protocol_engine/, fuera del scan de scripts/tests/src). Todos deben ser D5-puros.
_CORE_FILES = [
    "scripts/run_security_audit_12d.py",
    "scripts/core_utils.py",
    "scripts/verify_chaos_robustness.py",
    "protocol_engine/rule_collector.py",
]


def _silent_handlers(rel_path: str) -> list:
    src = (_ROOT / rel_path).read_text(encoding="utf-8", errors="ignore")
    visitor = TryBlockVisitor(rel_path)
    visitor.visit(ast.parse(src, filename=rel_path))
    return visitor.errors


def test_exempted_core_files_have_no_silent_except():
    """Los archivos exentos de la D-suite NO pueden contener except silenciosos.
    Si este test falla, hay un bloque pass/continue mudo que la exención estaba ocultando.
    """
    offenders = {f: errs for f in _CORE_FILES if (errs := _silent_handlers(f))}
    assert (
        not offenders
    ), "D5 silencioso oculto por la auto-exención de la D-suite:\n" + "\n".join(
        f"  {f}: {e}" for f, errs in offenders.items() for e in errs
    )


def test_tryblockvisitor_discriminates_silent_vs_handled():
    """Discriminación (si no, el test de arriba sería teatro): el visitor MARCA un except mudo
    y NO marca uno con cuerpo real. Cubre el path positivo y el negativo del símbolo importado.
    """
    silent = "try:\n    x = 1\nexcept Exception:\n    pass\n"
    v1 = TryBlockVisitor("silent.py")
    v1.visit(ast.parse(silent))
    assert v1.errors, "TryBlockVisitor no detectó un except silencioso evidente"

    handled = "import logging\ntry:\n    x = 1\nexcept Exception as e:\n    logging.debug(e)\n"
    v2 = TryBlockVisitor("handled.py")
    v2.visit(ast.parse(handled))
    assert (
        v2.errors == []
    ), f"TryBlockVisitor marcó un except con cuerpo real: {v2.errors}"
