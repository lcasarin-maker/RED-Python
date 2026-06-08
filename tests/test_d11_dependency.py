#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests falsables de D11 Dependency (Sprint 28.5).

Deterministas: mockean PyPI (sin red real → sin flake) y la ausencia de Trivy.
Falsables porque dep YANKED debe ir FAIL, Trivy ausente debe ir UNAVAILABLE, y
offline/outdated deben ser WARN no-bloqueante (decisión usuario: offline informa)."""
import io
import json
import subprocess
import urllib.error

from dimensions import AuditContext, Status
from dimensions.d11_dependency import D11Dependency


class _FakeResp:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode()

    def __enter__(self):
        return io.BytesIO(self._b)

    def __exit__(self, *a):
        return False


def _req(tmp_path, line):
    (tmp_path / "requirements.txt").write_text(line + "\n")
    return AuditContext(tmp_path)


def test_yanked_dep_goes_red(tmp_path, monkeypatch):
    ctx = _req(tmp_path, "foo==1.0")
    payload = {"info": {"version": "1.0"}, "releases": {"1.0": [{"yanked": True}]}}
    monkeypatch.setattr(
        "dimensions.d11_dependency.urllib.request.urlopen",
        lambda *a, **k: _FakeResp(payload),
    )
    findings = D11Dependency()._pypi(ctx)
    assert any(f.status is Status.FAIL and "YANKED" in f.message for f in findings)


def test_outdated_is_warn_not_blocking(tmp_path, monkeypatch):
    ctx = _req(tmp_path, "foo==1.0")
    payload = {"info": {"version": "2.0"}, "releases": {"1.0": [{"yanked": False}]}}
    monkeypatch.setattr(
        "dimensions.d11_dependency.urllib.request.urlopen",
        lambda *a, **k: _FakeResp(payload),
    )
    findings = D11Dependency()._pypi(ctx)
    assert findings and all(not f.is_blocking() for f in findings)
    assert any(
        f.status is Status.WARN and "desactualizada" in f.message for f in findings
    )


def test_pypi_offline_is_warn_not_blocking(tmp_path, monkeypatch):
    ctx = _req(tmp_path, "foo==1.0")

    def _boom(*a, **k):
        raise urllib.error.URLError("sin red")

    monkeypatch.setattr("dimensions.d11_dependency.urllib.request.urlopen", _boom)
    findings = D11Dependency()._pypi(ctx)
    assert findings and all(
        f.status is Status.WARN and not f.is_blocking() for f in findings
    )


def test_trivy_absent_is_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr("dimensions.d11_dependency._find_trivy", lambda: "")
    findings = D11Dependency()._trivy(AuditContext(tmp_path))
    assert findings and all(
        f.status is Status.UNAVAILABLE and f.is_blocking() for f in findings
    )


def test_trivy_transient_error_is_warn_not_blocking(tmp_path, monkeypatch):
    """Trivy presente pero timeout transitorio (carga del hook) => WARN, NO bloquea
    — distinto de ausencia (UNAVAILABLE). Evita gate flaky en el pre-commit."""
    monkeypatch.setattr("dimensions.d11_dependency._find_trivy", lambda: "trivy")

    def _boom(*a, **k):
        raise subprocess.TimeoutExpired("trivy", 45)

    monkeypatch.setattr("dimensions.d11_dependency.subprocess.run", _boom)
    findings = D11Dependency()._trivy(AuditContext(tmp_path))
    assert findings and all(
        f.status is Status.WARN and not f.is_blocking() for f in findings
    )


def test_pypi_404_is_alucinated_dependency(tmp_path, monkeypatch):
    """Verifica que un error HTTP 404 en la consulta de PyPI se detecte como VC-129."""
    ctx = _req(tmp_path, "fake-package==1.0")

    def _boom(*a, **k):
        raise urllib.error.HTTPError("http://pypi.org", 404, "Not Found", {}, None)

    monkeypatch.setattr("dimensions.d11_dependency.urllib.request.urlopen", _boom)
    findings = D11Dependency()._pypi(ctx)
    assert len(findings) == 1
    f = findings[0]
    assert f.status is Status.FAIL
    assert f.is_blocking()
    assert "VC-129" in f.message
    assert "fake-package" in f.message
