"""Sprint 5 — WARN→BLOCK (PI-009).

Verifica que las recomendaciones del gate sean condicionales:
- Gate APPROVED → sin ruido de recomendaciones (el gate actúa como fuente de verdad)
- Gate REJECTED (error activo) → recomendaciones visibles para guiar el fix

Failing-first: introducir un zombie activo → recomendaciones aparecen.
Gate limpio → recomendaciones silenciadas.
"""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AUDITOR = ROOT / "scripts" / "run_security_audit_12d.py"
MARKER = "[RECOMENDACIONES POR DOMINIO]"


def _run_gate(cwd=None) -> str:
    env = {"PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(ROOT)}
    import os

    env = {**os.environ, **env}
    result = subprocess.run(
        [sys.executable, str(AUDITOR), str(cwd or ROOT)],
        cwd=ROOT,
        capture_output=True,
        env=env,
        timeout=120,
    )
    return result.stdout.decode("utf-8", errors="ignore") + result.stderr.decode(
        "utf-8", errors="ignore"
    )


def test_approved_gate_shows_no_recommendations():
    """Gate APPROVED → sección [RECOMENDACIONES] NO debe aparecer (Sprint 5 WARN→BLOCK)."""
    output = _run_gate(ROOT)
    assert (
        "APPROVED" in output
    ), "El gate debe estar APPROVED antes de verificar recomendaciones"
    assert MARKER not in output, (
        f"Gate APPROVED no debe emitir '{MARKER}' — las recomendaciones son ruido no bloqueante "
        "cuando todo pasa. Sprint 5: WARN→BLOCK o silencio."
    )


def test_rejected_gate_shows_recommendations(tmp_path):
    """Gate REJECTED (zombie activo) → sección [RECOMENDACIONES] SÍ aparece para guiar el fix."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    # zombie: script en scripts/ no wired a ningún hook/doc/CLI → D1 Zombi + D10 TK-039
    (scripts / "zombie_warn_block.py").write_text(
        'print("unregistered")\n', encoding="utf-8"
    )
    output = _run_gate(tmp_path)
    assert "REJECTED" in output, "Un zombie debe rechazar el gate (D1 Zombi)"
    assert MARKER in output, (
        f"Gate REJECTED debe mostrar '{MARKER}' para guiar el fix. "
        "Sprint 5: recomendaciones activas solo cuando hay error bloqueante."
    )
