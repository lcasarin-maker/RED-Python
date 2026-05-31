#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_p22_protocol_hash.py
P2.2: el gate auto-refresca protocol_hash SOLO cuando el commit incluye un archivo de
protocolo (drift legítimo). Un commit sin archivos de protocolo no lo toca.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import scripts.protocol_cli as pcli
import scripts.sync_binding as sb


def _patch(monkeypatch, staged_output):
    """Stub git staged-files output and capture update_checksums() calls."""
    calls = {"n": 0}
    monkeypatch.setattr(pcli, "run_command", lambda *a, **k: (0, staged_output, ""))
    monkeypatch.setattr(sb.ProtocolSyncManager, "update_checksums", lambda self: calls.__setitem__("n", calls["n"] + 1))
    monkeypatch.setattr(sb.ProtocolSyncManager, "__init__", lambda self, root_dir=None: None)
    return calls


def test_refresh_when_protocol_file_staged(monkeypatch):
    """SPEC.md en el commit → protocol_hash refrescado."""
    calls = _patch(monkeypatch, "SPEC.md\nscripts/foo.py\n")
    pcli.ProtocolClient()._auto_refresh_protocol_hash()
    assert calls["n"] == 1, "Debe refrescar el hash cuando un archivo de protocolo está staged"


def test_no_refresh_when_no_protocol_file(monkeypatch):
    """Commit sin archivos de protocolo → no se toca el hash."""
    calls = _patch(monkeypatch, "scripts/foo.py\ntests/bar.py\n")
    pcli.ProtocolClient()._auto_refresh_protocol_hash()
    assert calls["n"] == 0, "No debe refrescar el hash si el commit no toca protocolo"


def test_refresh_is_best_effort(monkeypatch):
    """Un fallo al refrescar nunca rompe el commit (best-effort)."""
    monkeypatch.setattr(pcli, "run_command", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    # No debe propagar la excepción: completa y retorna None.
    result = pcli.ProtocolClient()._auto_refresh_protocol_hash()
    assert result is None, "best-effort: traga la excepción y retorna None sin romper el commit"
