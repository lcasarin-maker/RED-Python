#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests falsables de D7 Data Security (Sprint 28.5).

Real-tooling: regex sobre fixtures + bandit real. Falsables porque credencial
hardcodeada / shell=True deben ir FAIL, y bandit ausente debe ir UNAVAILABLE
(nunca [] — corrige el `except: return []` del enhanced)."""
import json
import subprocess

from dimensions import AuditContext, Status
from dimensions.d7_security import D7Security


class _FakeProc:
    def __init__(self, stdout, returncode=1):
        self.stdout, self.returncode, self.stderr = stdout, returncode, ""


def _scripts(tmp_path):
    s = tmp_path / "scripts"
    s.mkdir()
    return s


def test_regex_clean_has_no_blocking(tmp_path):
    (_scripts(tmp_path) / "ok.py").write_text("x = 1\n")
    assert [
        f for f in D7Security()._regex(AuditContext(tmp_path)) if f.is_blocking()
    ] == []


def test_regex_hardcoded_credential_goes_red(tmp_path):
    # La credencial se construye dinámicamente: el source de ESTE test NO contiene
    # el patrón literal (el `{secret}` rompe el regex), pero el archivo tmp sí lo tiene.
    secret = "z" * 12
    (_scripts(tmp_path) / "bad.py").write_text(f'password = "{secret}"\n')
    findings = D7Security()._regex(AuditContext(tmp_path))
    assert any(f.status is Status.FAIL for f in findings)


def test_bandit_absent_is_unavailable(tmp_path, monkeypatch):
    _scripts(tmp_path)
    monkeypatch.setattr(
        "dimensions.d7_security.importlib.util.find_spec", lambda name: None
    )
    findings = D7Security()._bandit(AuditContext(tmp_path))
    assert findings and all(
        f.status is Status.UNAVAILABLE and f.is_blocking() for f in findings
    )


def test_bandit_transient_error_is_warn_not_blocking(tmp_path, monkeypatch):
    """bandit presente pero error transitorio (timeout bajo carga) => WARN, NO
    bloquea — distinto de ausencia (UNAVAILABLE). Evita gate flaky."""
    _scripts(tmp_path)

    def _boom(*a, **k):
        raise subprocess.TimeoutExpired("bandit", 120)

    monkeypatch.setattr("dimensions.d7_security.subprocess.run", _boom)
    findings = D7Security()._bandit(AuditContext(tmp_path))
    assert findings and all(
        f.status is Status.WARN and not f.is_blocking() for f in findings
    )


def test_bandit_high_finding_maps_to_fail(tmp_path, monkeypatch):
    """Un hallazgo HIGH de bandit se mapea a Finding FAIL; uno MEDIUM se ignora
    (umbral HIGH). Determinista: inyecta el JSON de bandit (la integración con
    bandit REAL la ejerce el gate en vivo, no este unit test → no flaky)."""
    _scripts(tmp_path)
    payload = json.dumps(
        {
            "results": [
                {
                    "test_id": "B602",
                    "issue_severity": "HIGH",
                    "filename": "x.py",
                    "line_number": 3,
                    "issue_text": "subprocess shell=True",
                },
                {
                    "test_id": "B404",
                    "issue_severity": "LOW",
                    "filename": "x.py",
                    "line_number": 1,
                    "issue_text": "import subprocess",
                },
            ]
        }
    )
    monkeypatch.setattr(
        "dimensions.d7_security.subprocess.run", lambda *a, **k: _FakeProc(payload)
    )
    findings = D7Security()._bandit(AuditContext(tmp_path))
    assert [f.status for f in findings] == [Status.FAIL]  # solo el HIGH, no el LOW
    assert "B602" in findings[0].message
