#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_p1_dead_code.py
P1.1/VC-118: el gate de dead-code (ruff pyflakes F) bloquea imports/vars muertas.
Soft-gate: si ruff no está instalado, audit_dead_code no penaliza (se omite el test).
"""

import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.run_security_audit_12d import DeepForensicAuditor

_no_ruff = shutil.which("ruff") is None


@pytest.mark.skipif(_no_ruff, reason="ruff no instalado (soft-gate VT-112)")
def test_dead_import_is_flagged(tmp_path):
    """Un import muerto en scripts/ debe ser bloqueado por el gate (VC-118)."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "victim.py").write_text("import os\nprint('hi')\n", encoding="utf-8")
    errors = DeepForensicAuditor(str(tmp_path)).audit_dead_code()
    assert any("victim.py" in e and "F401" in e for e in errors), f"Expected dead-import flag, got: {errors}"


@pytest.mark.skipif(_no_ruff, reason="ruff no instalado (soft-gate VT-112)")
def test_clean_script_passes(tmp_path):
    """Un script sin residuo no debe producir errores de dead-code."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "clean.py").write_text("import os\nprint(os.getcwd())\n", encoding="utf-8")
    errors = DeepForensicAuditor(str(tmp_path)).audit_dead_code()
    assert errors == [], f"Clean script must not be flagged, got: {errors}"


def test_dead_code_softgate_without_scripts_dir(tmp_path):
    """Sin scripts/ (p.ej. satélite) el gate no penaliza."""
    assert DeepForensicAuditor(str(tmp_path)).audit_dead_code() == []
