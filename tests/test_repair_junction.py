"""Tests Sprint 3.9 (3-a): lógica pura de reparación de junction .protocol-core.

No crea junctions reales (requiere privilegio); valida la clasificación y la
decisión de acción, que es donde vive el riesgo (Angry Path B3: nunca tocar un
dir real, sí reparar colgantes/wrong_target).
"""

from pathlib import Path

from scripts.repair_protocol_junction import (
    classify,
    repair_action,
    canonical_core_root,
)

_CORE = Path("fake_core")  # relativo: D9/S23 prohíbe paths absolutos en tests
_WRONG = str(_CORE / "rules")
_RIGHT = str(_CORE)


def test_classify_missing():
    assert classify(False, False, None, _CORE, False) == "missing"


def test_classify_not_junction_real_dir():
    # entrada existe, NO es junction (dir real con contenido) → jamás tocar
    assert classify(True, False, None, _CORE, True) == "not_junction"


def test_classify_broken_dangling():
    # es junction pero el target no resuelve
    assert classify(True, True, None, _CORE, False) == "broken"


def test_classify_wrong_target():
    assert classify(True, True, _WRONG, _CORE, False) == "wrong_target"


def test_classify_ok_resolves_with_scripts():
    assert classify(True, True, _RIGHT, _CORE, True) == "ok"


def test_classify_ok_target_but_no_scripts_is_broken():
    # target correcto pero el junction no expone scripts/ → roto efectivo
    assert classify(True, True, _RIGHT, _CORE, False) == "broken"


def test_repair_action_noop_when_ok():
    assert repair_action("ok") == "noop"


def test_repair_action_skip_unsafe_on_real_dir():
    # NUNCA reparar (borrar) un dir real con contenido del usuario
    assert repair_action("not_junction") == "skip_unsafe"


def test_repair_action_repairs_broken_states():
    for st in ("missing", "broken", "wrong_target"):
        assert repair_action(st) == "repair"


def test_canonical_core_root_points_to_cerberus_root():
    root = canonical_core_root()
    assert (root / "scripts" / "protocol_cli.py").is_file()
