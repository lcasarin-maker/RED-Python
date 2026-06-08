#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests falsables de D3 Dead Code (Sprint 28.5).

Real-tooling: ejercen ruff+vulture sobre fixtures en disco. Falsables porque
el fixture sucio DEBE producir FAIL y el binario ausente DEBE producir
UNAVAILABLE (nunca []). Si la dimensión mintiera, estos tests irían rojos."""
from dimensions import AuditContext, Status
from dimensions.d3_dead_code import D3DeadCode


def _scripts(tmp_path):
    s = tmp_path / "scripts"
    s.mkdir()
    return s


def test_clean_scripts_has_no_blocking_findings(tmp_path):
    s = _scripts(tmp_path)
    (s / "ok.py").write_text("def used():\n    return 1\n\n\nprint(used())\n")
    findings = D3DeadCode().audit(AuditContext(tmp_path))
    assert [f for f in findings if f.is_blocking()] == []


def test_dead_code_fixture_goes_red(tmp_path):
    s = _scripts(tmp_path)
    # 'import os' sin usar => ruff F401; 'never_called' => vulture unused function
    (s / "bad.py").write_text("import os\n\n\ndef never_called():\n    return 42\n")
    findings = D3DeadCode().audit(AuditContext(tmp_path))
    assert any(f.status is Status.FAIL for f in findings), "fixture sucio debe ir ROJO"


def test_missing_tool_is_unavailable_not_silent_pass(tmp_path, monkeypatch):
    s = _scripts(tmp_path)
    (s / "x.py").write_text("x = 1\n")
    monkeypatch.setattr("dimensions.d3_dead_code.shutil.which", lambda name: None)
    findings = D3DeadCode().audit(AuditContext(tmp_path))
    assert findings, "binario ausente debe producir Finding, no []"
    assert all(f.status is Status.UNAVAILABLE and f.is_blocking() for f in findings)
