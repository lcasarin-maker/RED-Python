#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_d10_tokenomics.py
Tests for P7.2 + P7.3: run_security_audit_12d.py D10 Tokenomics domain and D6 name-congruency sub-check.
Coverage: TK-023, TK-038, TK-039 (D10), and D6 name-congruency (_name_congruency_check).
"""

import sys
import inspect
import pytest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.run_security_audit_12d import DeepForensicAuditor


# ── Fixture ───────────────────────────────────────────────────────────────────


@pytest.fixture()
def auditor(tmp_path):
    """Return a 10D auditor pointed at an isolated tmp directory."""
    return DeepForensicAuditor(str(tmp_path))


# ── TK-023: OutputCompressor in orchestrators ─────────────────────────────────


def test_tk023_missing_output_compressor_raises(auditor, tmp_path):
    """TK-023: orchestrator that lacks OutputCompressor should produce D10 error."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run_compliance_tests.py").write_text(
        "# no compressor here\nprint('hello')\n", encoding="utf-8"
    )
    errors = auditor.audit_d10_tokenomics()
    tk023_errors = [e for e in errors if "TK-023" in e]
    assert (
        tk023_errors
    ), "Expected TK-023 error for orchestrator missing OutputCompressor"
    assert "run_compliance_tests.py" in tk023_errors[0]


def test_tk023_output_compressor_present_passes(auditor, tmp_path):
    """TK-023: orchestrator that imports OutputCompressor should produce no TK-023 error."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run_compliance_tests.py").write_text(
        "from scripts.manage_tokens import OutputCompressor\n", encoding="utf-8"
    )
    errors = auditor.audit_d10_tokenomics()
    tk023_errors = [e for e in errors if "TK-023" in e and "run_compliance_tests" in e]
    assert not tk023_errors, f"Unexpected TK-023 errors: {tk023_errors}"


# ── TK-038: Manifest size gates ───────────────────────────────────────────────


def test_tk038_manifest_exceeds_limit_raises(auditor, tmp_path):
    """TK-038: AGENT.md with >150 lines should produce D10 error."""
    over_limit = "\n".join(f"line {i}" for i in range(200))
    (tmp_path / "AGENT.md").write_text(over_limit, encoding="utf-8")
    errors = auditor.audit_d10_tokenomics()
    tk038_errors = [e for e in errors if "TK-038" in e and "AGENT.md" in e]
    assert tk038_errors, "Expected TK-038 error for AGENT.md exceeding 150 lines"


def test_tk038_manifest_within_limit_passes(auditor, tmp_path):
    """TK-038: AGENT.md with <=150 lines should produce no TK-038 error."""
    within_limit = "\n".join(f"line {i}" for i in range(100))
    (tmp_path / "AGENT.md").write_text(within_limit, encoding="utf-8")
    errors = auditor.audit_d10_tokenomics()
    tk038_errors = [e for e in errors if "TK-038" in e and "AGENT.md" in e]
    assert not tk038_errors, f"Unexpected TK-038 errors: {tk038_errors}"


# ── TK-039: Spectral script references ───────────────────────────────────────


def test_tk039_spectral_reference_raises(auditor, tmp_path):
    """TK-039: TOKEN_BUDGET.md referencing a non-existent script should produce D10 error."""
    (tmp_path / "TOKEN_BUDGET.md").write_text(
        "Run: python scripts/ghost_script.py --compact\n", encoding="utf-8"
    )
    (tmp_path / "scripts").mkdir()
    errors = auditor.audit_d10_tokenomics()
    tk039_errors = [e for e in errors if "TK-039" in e]
    assert tk039_errors, "Expected TK-039 error for spectral script reference"
    assert "ghost_script.py" in tk039_errors[0]


def test_tk039_existing_reference_passes(auditor, tmp_path):
    """TK-039: TOKEN_BUDGET.md referencing an existing script should produce no TK-039 error."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "real_script.py").write_text("# real\n", encoding="utf-8")
    (tmp_path / "TOKEN_BUDGET.md").write_text(
        "Run: python scripts/real_script.py --compact\n", encoding="utf-8"
    )
    errors = auditor.audit_d10_tokenomics()
    tk039_errors = [e for e in errors if "TK-039" in e]
    assert not tk039_errors, f"Unexpected TK-039 errors: {tk039_errors}"


# ── TK-039/TK-043: Spectral (orphan) scripts — gobernanza de salida ──────────


def test_orphan_script_raises(auditor, tmp_path):
    """TK-039/TK-043: a scripts/*.py referenced by nothing active must be flagged."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "lonely_orphan.py").write_text(
        "# nobody calls me\n", encoding="utf-8"
    )
    errors = auditor.audit_script_orphans()
    assert any(
        "lonely_orphan.py" in e for e in errors
    ), f"Expected orphan error for lonely_orphan.py, got: {errors}"


def test_referenced_script_passes(auditor, tmp_path):
    """TK-039/TK-043: a script whose name appears in another active script is not orphan."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "used_lib.py").write_text(
        "def helper():\n    return 1\n", encoding="utf-8"
    )
    (scripts_dir / "caller.py").write_text(
        "from scripts.used_lib import helper\nhelper()\n", encoding="utf-8"
    )
    errors = auditor.audit_script_orphans()
    assert not any(
        "used_lib.py" in e for e in errors
    ), f"used_lib.py is referenced by caller.py and must not be flagged: {errors}"


def test_orphan_in_subdir_is_flagged(auditor, tmp_path):
    """P6: un módulo huérfano en un SUBDIR (no solo scripts/ top-level) debe ser cazado."""
    sub = tmp_path / "scripts" / "automation"
    sub.mkdir(parents=True)
    (sub / "lost_module.py").write_text(
        "# disconnected from everything\n", encoding="utf-8"
    )
    errors = auditor.audit_script_orphans()
    assert any(
        "lost_module.py" in e for e in errors
    ), f"Subdir orphan must be flagged (P6 generalization): {errors}"


# ── D6 Name-congruency sub-check ─────────────────────────────────────────────


def test_d6_name_congruency_matches_declared_domains():
    """D6 sub-check: el gate declara 12 dominios y debe enforcer 12 IDs distintos,
    contando inline (audit_dN_) + paquete dimensions/ (canal gate). Sprint 28.5:
    d3/d11 migraron al paquete; se cuentan IDs únicos, no métodos."""
    import re as _re

    auditor = DeepForensicAuditor(".")
    ids = {
        int(_re.match(r"audit_d(\d+)_", name).group(1))
        for name, _ in inspect.getmembers(
            DeepForensicAuditor, predicate=inspect.isfunction
        )
        if _re.match(r"audit_d\d+_", name)
    }
    from dimensions import REGISTRY

    ids |= {int(d.id[1:]) for d in REGISTRY if d.channel == "gate"}
    assert (
        len(ids) == 12
    ), f"el gate declara 12 dominios pero enforce {len(ids)} IDs distintos: {sorted(ids)}"
    # _name_congruency_check no debe reportar mismatch
    errors = auditor._name_congruency_check()
    assert errors == [], f"Unexpected D6 congruency errors: {errors}"
