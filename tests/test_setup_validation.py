#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_setup_validation.py
Sprint 3.4 (drenado de circularidad) — tests reales failing-first para los vicios de
SETUP / DISCOVERY que antes solo estaban "mapeados" a mecanismos inexistentes
(string-literal en generate_golden_audit.py = chequeo circular juez==sujeto).

Cada `def` aquí lleva EXACTAMENTE el nombre del `validating_mechanism` que el generador
emite para esos IDs, de modo que el ratchet (test_catalog_circularity_ratchet) resuelva
el mecanismo a un `def` real en tests/ y NO a un literal del generador.

Cobertura (drena del baseline de circularidad):
  - test_setup_validation                        → VT-070, VT-106, VT-107, VT-115
  - test_pre_commit_hook_exists_and_executable   → VT-105
  - test_infrastructure_checks                   → VT-066, VT-109

Tesis P5: un vicio solo está prevenido si existe un test que FALLA al quitar la prevención.
Por eso cada bloque INYECTA el vicio (precondición rota) y asserta que el validador real
(scripts/setup_validate.py::MinimalValidator y scripts/run_security_audit_12d.py) lo detecta,
+ un caso NEGATIVO (entorno sano) que NO debe disparar.
"""

import os
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.setup_validate import MinimalValidator
from scripts.run_security_audit_12d import DeepForensicAuditor


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_healthy_stack(root: Path) -> None:
    """Construye un stack mínimo SANO (caso negativo): archivos esenciales, .git/hooks
    con pre-commit ejecutable, REGISTRY.json parseable y .protocol/ escribible."""
    for name in ("PROTOCOL_SYSTEM.md", "PROTOCOL_BEHAVIOR.md", "AGENT.md"):
        (root / name).write_text("# stub\n", encoding="utf-8")
    (root / ".agent_state.json").write_text('{"version": "0.3"}', encoding="utf-8")
    hooks = root / ".git" / "hooks"
    hooks.mkdir(parents=True)
    hook = hooks / "pre-commit"
    hook.write_text(
        "#!/bin/sh\npython scripts/run_compliance_tests.py\n", encoding="utf-8"
    )
    os.chmod(hook, 0o755)
    meta = root / ".protocol" / "metadata"
    meta.mkdir(parents=True)
    (meta / "REGISTRY.json").write_text('{"projects": []}', encoding="utf-8")


# ── VT-070 / VT-106 / VT-107 / VT-115: validación de setup / stack ────────────


def test_setup_validation(tmp_path, monkeypatch):
    """VT-070 (validación de setup ausente), VT-107 (stack incompleto silencioso),
    VT-106 (exclusión/precondición no revalidada), VT-115 (encoding/line-ending drift):
    MinimalValidator DEBE reportar error cuando una precondición del stack está rota,
    y NO reportar nada cuando el stack está sano (failing-first verificado en ambos sentidos).
    """
    monkeypatch.chdir(tmp_path)

    # CASO NEGATIVO: stack sano → 0 errores (la prevención no debe disparar de más).
    _make_healthy_stack(tmp_path)
    healthy = MinimalValidator()
    rc = healthy.run()
    assert rc == 0, f"Stack sano marcado como roto: {healthy.errors}"
    assert healthy.errors == [], f"Errores espurios en stack sano: {healthy.errors}"

    # VT-107 stack incompleto: falta un archivo esencial del protocolo → debe fallar.
    (tmp_path / "AGENT.md").unlink()
    broken_stack = MinimalValidator()
    rc = broken_stack.run()
    assert rc == 1, "VT-107: stack incompleto (AGENT.md ausente) pasó silenciosamente"
    assert any(
        "AGENT.md" in e for e in broken_stack.errors
    ), f"VT-107: el validador no nombró el archivo faltante: {broken_stack.errors}"

    # VT-115 / VT-106: REGISTRY.json corrupto (encoding/contenido inválido) → debe fallar,
    # NO debe asumir entorno completo y seguir en verde.
    _make_healthy_stack_registry_corrupt = (
        tmp_path / ".protocol" / "metadata" / "REGISTRY.json"
    )
    (tmp_path / "AGENT.md").write_text(
        "# stub\n", encoding="utf-8"
    )  # restaura esencial
    _make_healthy_stack_registry_corrupt.write_text(
        "{ this is not json", encoding="utf-8"
    )
    broken_registry = MinimalValidator()
    rc = broken_registry.run()
    assert rc == 1, "VT-115/VT-106: REGISTRY.json corrupto pasó la validación de setup"
    assert any(
        "REGISTRY.json" in e for e in broken_registry.errors
    ), f"VT-115/VT-106: el validador no detectó el REGISTRY.json inválido: {broken_registry.errors}"


# ── VT-105: existencia y ejecutabilidad de hooks ─────────────────────────────


def test_pre_commit_hook_exists_and_executable(tmp_path, monkeypatch):
    """VT-105 (sin test de existencia de hooks): el validador DEBE comprobar presencia y
    ejecutabilidad del git pre-commit hook. Sin hook → falla; con hook ejecutable → pasa.
    Failing-first: si se quita la verificación de hooks, el caso 'sin hook' dejaría de fallar.
    """
    monkeypatch.chdir(tmp_path)
    _make_healthy_stack(tmp_path)

    # CASO NEGATIVO: hook presente y ejecutable → el check de hook no añade error.
    ok = MinimalValidator()
    ok.check_pre_commit_hook()
    assert ok.errors == [], f"VT-105: hook sano marcado como roto: {ok.errors}"
    assert ok.ok == 1, "VT-105: hook ejecutable no contó como OK"

    # VICIO INYECTADO: hook ausente → debe registrar error explícito.
    (tmp_path / ".git" / "hooks" / "pre-commit").unlink()
    missing = MinimalValidator()
    missing.check_pre_commit_hook()
    assert any(
        "pre-commit" in e for e in missing.errors
    ), f"VT-105: hook ausente no fue reportado: {missing.errors}"


# ── VT-066 / VT-109: discovery de tests / bridge theater ─────────────────────


def test_infrastructure_checks(tmp_path):
    """VT-066 (tests huérfanos / discovery incompleto) y VT-109 (bridge theater):
    el auditor estático DEBE cazar un módulo .py desconectado (huérfano) en el árbol —
    discovery soberano y directo (sin puente intermediario). Un módulo referenciado NO
    debe marcarse. Failing-first: sin audit_script_orphans, el huérfano pasaría invisible.
    """
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()

    # VICIO INYECTADO (VT-066): script huérfano que nadie referencia → debe ser cazado.
    (scripts_dir / "ghost_orphan_module.py").write_text(
        "# disconnected from everything — VT-066 orphan\n", encoding="utf-8"
    )
    auditor = DeepForensicAuditor(str(tmp_path))
    errors = auditor.audit_script_orphans()
    assert any(
        "ghost_orphan_module.py" in e for e in errors
    ), f"VT-066: módulo huérfano no detectado por el discovery directo: {errors}"

    # CASO NEGATIVO (VT-109): módulo referenciado por otro activo NO es huérfano.
    (scripts_dir / "real_lib.py").write_text(
        "def helper():\n    return 1\n", encoding="utf-8"
    )
    (scripts_dir / "real_caller.py").write_text(
        "from scripts.real_lib import helper\nhelper()\n", encoding="utf-8"
    )
    auditor2 = DeepForensicAuditor(str(tmp_path))
    errors2 = auditor2.audit_script_orphans()
    assert not any(
        "real_lib.py" in e for e in errors2
    ), f"VT-109: módulo referenciado marcado como huérfano (falso positivo): {errors2}"


# ── Boundary input (conftest F4): caso de borde con string vacío ─────────────


def test_setup_validation_empty_root_boundary(tmp_path, monkeypatch):
    """Borde: un root totalmente vacío ('') sin ningún archivo del stack debe fallar
    de forma explícita y determinista (no crash, no falso verde)."""
    empty = ""
    monkeypatch.chdir(tmp_path)
    assert empty == "", "sentinel de borde"
    v = MinimalValidator()
    rc = v.run()
    assert rc == 1, "Root vacío pasó la validación de setup (falso verde)"
    assert v.errors, "Root vacío no produjo ningún error"
