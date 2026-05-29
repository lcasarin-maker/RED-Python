#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_d10_tokenomics.py
Tests for P7.2 + P7.3: audit_10d.py D10 Tokenomics domain and D6 name-congruency sub-check.
Coverage: TK-023, TK-038, TK-039 (D10), and D6 name-congruency (_name_congruency_check).
"""

import sys
import inspect
import pytest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.audit_10d import DeepForensicAuditor


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
    (scripts_dir / "rigor_maestro.py").write_text(
        "# no compressor here\nprint('hello')\n", encoding="utf-8"
    )
    errors = auditor.audit_d10_tokenomics()
    tk023_errors = [e for e in errors if "TK-023" in e]
    assert tk023_errors, "Expected TK-023 error for orchestrator missing OutputCompressor"
    assert "rigor_maestro.py" in tk023_errors[0]


def test_tk023_output_compressor_present_passes(auditor, tmp_path):
    """TK-023: orchestrator that imports OutputCompressor should produce no TK-023 error."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "rigor_maestro.py").write_text(
        "from scripts.token_manager import OutputCompressor\n", encoding="utf-8"
    )
    errors = auditor.audit_d10_tokenomics()
    tk023_errors = [e for e in errors if "TK-023" in e and "rigor_maestro" in e]
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


# ── D6 Name-congruency sub-check ─────────────────────────────────────────────

def test_d6_name_congruency_matches_declared_domains():
    """D6 sub-check: audit_10d.py declares 10 and must have exactly 10 audit_dN_ methods."""
    auditor = DeepForensicAuditor(".")
    methods = [
        name for name, _ in inspect.getmembers(
            DeepForensicAuditor, predicate=inspect.isfunction
        )
        if __import__("re").match(r"audit_d\d+_", name)
    ]
    assert len(methods) == 10, (
        f"audit_10d.py declares 10 domains but found {len(methods)} audit_dN_ methods: {methods}"
    )
    # _name_congruency_check must return empty list (no mismatch) for this file
    errors = auditor._name_congruency_check()
    assert errors == [], f"Unexpected D6 congruency errors: {errors}"
