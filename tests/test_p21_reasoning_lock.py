#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_p21_reasoning_lock.py
P2.1: el reasoning_lock no debe alimentarse de corridas informativas/de gate.
- update_lock_state sigue siendo el ÚNICO mutador del contador (mecanismo intacto).
- run_compliance_tests.__main__ solo llama update_lock_state con --track-lock (default OFF),
  por lo que self_improvement_loop (post-commit), el gate y los reintentos de commit
  no incrementan consecutive_failures.
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts import run_compliance_tests


def _state(tmp_path, **kw):
    """Create a tmp .agent_state.json (+ STATUS.md) and point run_compliance_tests._ROOT at it."""
    (tmp_path / "STATUS.md").write_text(
        "# STATUS.md — Project status\n", encoding="utf-8"
    )
    (tmp_path / ".agent_state.json").write_text(json.dumps(kw), encoding="utf-8")
    return tmp_path / ".agent_state.json"


def _read(state_file):
    return json.loads(state_file.read_text(encoding="utf-8"))


def test_update_lock_state_increments_and_locks_on_failure(tmp_path, monkeypatch):
    """Mecanismo intacto: 2 fallos + 1 fallo => 3 => reasoning_lock activo."""
    monkeypatch.setattr(run_compliance_tests, "_ROOT", tmp_path)
    sf = _state(tmp_path, consecutive_failures=2, reasoning_lock=False)
    run_compliance_tests.update_lock_state(success=False)
    data = _read(sf)
    assert data["consecutive_failures"] == 3
    assert data["reasoning_lock"] is True


def test_update_lock_state_resets_on_success(tmp_path, monkeypatch):
    """Mecanismo intacto: un éxito limpia el contador y libera el lock."""
    monkeypatch.setattr(run_compliance_tests, "_ROOT", tmp_path)
    sf = _state(tmp_path, consecutive_failures=2, reasoning_lock=True)
    run_compliance_tests.update_lock_state(success=True)
    data = _read(sf)
    assert data["consecutive_failures"] == 0
    assert data["reasoning_lock"] is False


def test_main_default_does_not_track_lock():
    """P2.1: run_compliance_tests.__main__ por defecto NO llama update_lock_state — solo con
    --track-lock. Bloquea la regresión que dejaba que el post-commit deadlockee."""
    source = (_ROOT / "scripts" / "run_compliance_tests.py").read_text(encoding="utf-8")
    assert (
        "if args.track_lock:" in source
    ), "update_lock_state debe estar detrás de --track-lock"
    # update_lock_state aparece exactamente 1 vez en __main__, condicionada por el flag
    main_block = source.split('if __name__ == "__main__":')[1]
    assert (
        "if args.track_lock:\n        update_lock_state" in main_block
    ), "la llamada en __main__ debe estar condicionada por args.track_lock"
