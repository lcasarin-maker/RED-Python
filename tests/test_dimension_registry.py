#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests del ledger de dimensiones (Sprint 28.5 Paso 1).

Falsable por diseño: cuando una dimensión enhanced se cablee, el ancla de
'verdad inerte' DEBE fallar y forzar su actualización + regeneración del JSON.
"""
import json

import pytest

from scripts.generate_dimension_registry import build_registry, REGISTRY_PATH


def _committed() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_registry_committed_is_fresh():
    """Regenera en memoria y compara (ignora git_sha volátil). Stale => RED."""
    fresh = build_registry()
    committed = _committed()
    assert committed["dimensions"] == fresh["dimensions"], (
        "dimension_registry.json desactualizado: "
        "corre `python scripts/generate_dimension_registry.py`"
    )
    assert committed["dimension_count"] == fresh["dimension_count"]


def test_all_dimensions_fully_wired():
    """Cierre de Sprint 28.5: las 14 dimensiones están fully-wired (gate vía REGISTRY
    o hook vía discourse_hook.py). Ya no hay verdes-huérfanos. Falsable: si una dim
    pierde su cableado (o binario), fully_wired baja y este test cae."""
    reg = _committed()
    assert reg["fully_wired_count"] == reg["dimension_count"] == 14
    assert all(dim["fully_wired"] for dim in reg["dimensions"].values())


def test_discourse_dims_route_to_hook_channel():
    """H3: D13/D14 auditan al agente => canal hook, no gate forense."""
    dims = _committed()["dimensions"]
    assert dims["d13"]["channel"] == "hook"
    assert dims["d14"]["channel"] == "hook"


def test_fully_wired_requires_wiring_and_binary():
    """Path negativo (D8): build_registry NUNCA marca fully_wired=True si la
    implementación prevista no está cableada o le falta el binario. Y un id
    inexistente no aparece en el ledger."""
    reg = build_registry()
    for dim in reg["dimensions"].values():
        intended = dim["implementations"][-1]  # enhanced si existe; si no, inline
        if dim["fully_wired"]:
            assert intended["wired"] and intended["binary_available"]
        if not (intended["wired"] and intended["binary_available"]):
            assert dim["fully_wired"] is False
    with pytest.raises(KeyError):
        _ = reg["dimensions"]["d99"]


def test_migrated_dims_are_consolidated():
    """H1 resuelto: d3/d7/d11 ya NO tienen dual-impl (inline+enhanced) — el teatro
    se borró y la lógica vive en dimensions/. Falsable: si reapareciera un script
    enhanced dN_*, has_dual_impl volvería True y este test caería."""
    dims = _committed()["dimensions"]
    for dim in ("d3", "d7", "d11"):
        assert dims[dim]["has_dual_impl"] is False
        assert any(i["kind"] == "package" for i in dims[dim]["implementations"])
    assert dims["d11"]["has_dual_impl"] is False  # d11 consolidada en dimensions/
