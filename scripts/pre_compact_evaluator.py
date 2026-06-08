#!/usr/bin/env python3
"""
pre_compact_evaluator.py — Evaluación pre-compact (PreCompact hook).
Genera un snapshot de estado antes de compactar: contexto, tests, git, deuda.
Siempre exit 0 (no bloquea /compact), pero deja evidencia en stderr.
"""
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _run_short(cmd: list[str], timeout: int = 10) -> str:
    """Ejecuta comando y retorna stdout truncado, '' si falla."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(_ROOT))
        return (r.stdout + r.stderr)[:400].strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def main() -> int:
    lines = ["[PRE-COMPACT EVAL] ── Snapshot antes de compactar ──"]

    # Git: rama + archivos modificados
    branch = _run_short(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    dirty = _run_short(["git", "status", "--short"])
    lines.append(f"  Git rama: {branch} | Modificados: {len(dirty.splitlines())} archivo(s)")
    if dirty:
        for entry in dirty.splitlines()[:5]:
            lines.append(f"    {entry}")
        if len(dirty.splitlines()) > 5:
            lines.append(f"    ... (+{len(dirty.splitlines()) - 5} más)")

    # Sentinel compact
    sentinel = _ROOT / ".compact_needed"
    if sentinel.exists():
        lines.append(f"  .compact_needed: PRESENTE → {sentinel.read_text().strip()}")
    else:
        lines.append("  .compact_needed: ausente (compact voluntario)")

    # Tests: conteo rápido de fallos si pytest disponible
    pytest_out = _run_short(
        [sys.executable, "-m", "pytest", "--tb=no", "-q", "--co", "-q"],
        timeout=15,
    )
    test_lines = [ln for ln in pytest_out.splitlines() if "failed" in ln or "passed" in ln or "error" in ln]
    lines.append(f"  Tests: {' | '.join(test_lines) if test_lines else 'no disponible'}")

    # Deuda D1: zombies conocidos
    for zombie in ["scripts/sandwich_model_detector.py", "scripts/sync_v05.py"]:
        if (_ROOT / zombie).exists():
            lines.append(f"  ⚠ Zombie pendiente: {zombie}")

    lines.append("[PRE-COMPACT EVAL] ── Fin snapshot ──")
    print("\n".join(lines), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
