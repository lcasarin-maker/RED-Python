#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_sprint3_security.py
Sprint 3.2 — tests reales failing-first para los 3 vicios de seguridad más severos.
Antes solo estaban "mapeados" a tests inexistentes (chequeo circular de strings).
- VC-115: ejecución dinámica de reglas externas (eval/RCE) → rules_engine debe RECHAZAR
          checks no registrados (no eval).
- VC-116: pip install automático ante ImportError → auto_repair NO debe instalar.
- VC-117: escritura no-atómica de estado crítico → debe existir y usarse escritura atómica.
"""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ── VC-115: RCE por eval de reglas externas ──────────────────────────────────
def test_rule_security_rejects_arbitrary_check(tmp_path, monkeypatch):
    """VC-115: una regla externa con un `check` arbitrario (payload) NO debe ejecutarse;
    el motor debe rechazarla por no estar en SAFE_CHECKS (sin eval/exec)."""
    from protocol_engine import rules_engine
    evil = tmp_path / "evil.yaml"
    evil.write_text(
        "- id: EVIL\n"
        "  check: \"__import__('os').system('echo pwned')\"\n"
        "  description: intento de RCE\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(rules_engine, "RULES_DIR", tmp_path)
    with pytest.raises(ValueError) as exc:
        rules_engine._load_rules()
    msg = str(exc.value).lower()
    assert "unknown check" in msg or "forbidden" in msg, (
        f"El motor debe rechazar el check arbitrario, got: {exc.value}"
    )


# ── VC-116: pip install automático prohibido ─────────────────────────────────
def test_auto_repair_does_not_pip_install(monkeypatch):
    """VC-116: ante un ImportError, auto_repair debe REPORTAR (return False) y NUNCA
    invocar `pip install` (riesgo de supply-chain)."""
    import auto_repair
    pip_calls = []

    def _spy(cmd, *a, **k):
        flat = " ".join(map(str, cmd)) if isinstance(cmd, (list, tuple)) else str(cmd)
        if "pip" in flat:
            pip_calls.append(flat)
        return 0

    for fn in ("run", "check_call", "call", "Popen"):
        monkeypatch.setattr(auto_repair.subprocess, fn, _spy, raising=False)

    result = auto_repair.handle_import_error({"message": "No module named 'evilpkg'"})
    assert result is False, "auto_repair NO debe auto-instalar; debe escalar al humano"
    assert pip_calls == [], f"pip install automático detectado (prohibido): {pip_calls}"


# ── VC-117: escritura atómica de estado crítico ──────────────────────────────
def test_critical_state_write_is_atomic(tmp_path):
    """VC-117: debe existir un helper de escritura atómica (temp + os.replace) para que
    un crash a mitad de escritura no corrompa el estado crítico (JSON). Failing-first:
    hoy no existe → este test falla hasta implementarlo."""
    from scripts.core_utils import write_json_atomic
    target = tmp_path / "state.json"
    write_json_atomic(target, {"k": "v", "n": 1})
    assert json.loads(target.read_text(encoding="utf-8")) == {"k": "v", "n": 1}
    # No debe dejar temporales sueltos en el directorio.
    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "state.json"]
    assert leftovers == [], f"escritura atómica dejó temporales: {leftovers}"


# ── Sprint 3.3 (acotado): no-circularidad de los mecanismos de seguridad ──────
def test_security_mechanisms_are_noncircular():
    """Sprint 3.3: el validating_mechanism de VC-115/116/117 debe resolver a un `def` de
    test REAL en tests/ — NO solo aparecer como string literal en generate_golden_audit.py
    (chequeo circular judge=sujeto). Garantiza que los 3 vicios de seguridad más severos
    están cubiertos de verdad, no en teatro."""
    db = json.loads(
        (_ROOT / ".protocol" / "metadata" / "golden_standard_audit.json").read_text(encoding="utf-8")
    )
    test_text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in (_ROOT / "tests").glob("**/*.py")
    )
    for vid in ("VC-115", "VC-116", "VC-117"):
        assert vid in db, f"{vid} ausente del JSON de cobertura"
        mech = db[vid]["validating_mechanism"]
        assert f"def {mech}" in test_text, (
            f"{vid}: el mecanismo '{mech}' no existe como def de test real en tests/ "
            f"(circular/teatro)."
        )
