#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_d12_release_adoption.py
P3: D12 valida ADOPCIÓN DE RELEASE por versión (VERSION.txt), no byte-a-byte.
- Satélite en la versión del core -> sin drift (las micro-ediciones del core no flagean).
- Satélite en versión distinta -> drift (frontera de release, propagación deliberada).
- Satélite sin VERSION.txt -> no adoptó el protocolo.
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.audit_10d import DeepForensicAuditor


def _make_core(tmp_path, core_version="0.3"):
    """Build a tmp 'core' with VERSION.txt + an empty satellite registry."""
    (tmp_path / "VERSION.txt").write_text(core_version, encoding="utf-8")
    reg_dir = tmp_path / ".protocol" / "metadata"
    reg_dir.mkdir(parents=True)
    return reg_dir / "REGISTRY.json"


def _add_satellite(tmp_path, registry_file, name, version):
    """Create a satellite dir with .protocol-core/VERSION.txt and register it.
    version=None means the satellite has no VERSION.txt (never adopted)."""
    sat = tmp_path / name
    (sat / ".protocol-core").mkdir(parents=True)
    if version is not None:
        (sat / ".protocol-core" / "VERSION.txt").write_text(version, encoding="utf-8")
    reg = json.loads(registry_file.read_text(encoding="utf-8")) if registry_file.exists() else {"projects": []}
    reg["projects"].append({
        "name": name, "path": str(sat), "role": "SATELLITE",
        "status": "active", "adoption_verified": True,
    })
    registry_file.write_text(json.dumps(reg), encoding="utf-8")


def test_satellite_on_release_version_passes(tmp_path):
    """A satellite on the core's protocol version must not be flagged (decoupling)."""
    reg = _make_core(tmp_path, "0.3")
    _add_satellite(tmp_path, reg, "sat_current", "0.3")
    errors = DeepForensicAuditor(str(tmp_path)).validate_satellite_drift()
    assert errors == [], f"Satellite on release version must pass, got: {errors}"


def test_satellite_on_old_version_is_flagged(tmp_path):
    """A satellite on an older protocol version must be flagged (release boundary)."""
    reg = _make_core(tmp_path, "0.3")
    _add_satellite(tmp_path, reg, "sat_old", "0.2")
    errors = DeepForensicAuditor(str(tmp_path)).validate_satellite_drift()
    assert any("sat_old" in e and "0.2" in e for e in errors), f"Expected drift for old version, got: {errors}"


def test_satellite_without_version_file_is_flagged(tmp_path):
    """A satellite that never adopted the protocol (no VERSION.txt) must be flagged."""
    reg = _make_core(tmp_path, "0.3")
    _add_satellite(tmp_path, reg, "sat_none", None)
    errors = DeepForensicAuditor(str(tmp_path)).validate_satellite_drift()
    assert any("sat_none" in e and "VERSION.txt" in e for e in errors), f"Expected adoption error, got: {errors}"
