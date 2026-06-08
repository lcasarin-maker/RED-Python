#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hook commit-msg (VC-140, norma de continuidad agnóstica): bloquea el commit si
hay cambios sustantivos staged pero HANDOFF.md no se actualizó o no cumple el esquema.

Agnóstico: corre con cualquier `git commit` (Codex/Gemini/Claude). Escape explícito:
token [skip-handoff] en el mensaje o env CERBERUS_SKIP_HANDOFF=1."""
import logging
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_HANDOFF = "HANDOFF.md"
_REQUIRED = ("## ESTADO", "## SIGUIENTE", "## VERIFICAR")
# Archivos que NO cuentan como cambio sustantivo (no exigen relevo por sí solos).
_TRIVIAL = {_HANDOFF, "HISTORIAL.md", "STATUS.md"}

logger = logging.getLogger("check_handoff_freshness")


def _staged_files() -> list[str]:
    """Rutas staged (git diff --cached). [] si git falla."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=str(_ROOT), check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        logger.warning("git diff --cached falló: %s", exc)
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def check_handoff_freshness(staged: list[str], handoff_text: str, msg: str) -> tuple[bool, str]:
    """PURA. (ok, motivo). Bloquea si hay cambio sustantivo y el handoff no está staged
    o le faltan secciones; pasa con escape explícito o sin cambios sustantivos."""
    # El token de escape SOLO cuenta en la línea de asunto (donde van los flags
    # intencionales). Si aparece en el cuerpo —p.ej. documentando la feature— NO escapa,
    # para no auto-desactivar el enforcement por mencionarlo en prosa.
    subject = msg.splitlines()[0] if msg.strip() else ""
    if "[skip-handoff]" in subject or os.environ.get("CERBERUS_SKIP_HANDOFF") == "1":
        return True, "escape explícito ([skip-handoff]/env)"
    substantive = [f for f in staged if Path(f).name not in _TRIVIAL]
    if not substantive:
        return True, "sin cambios sustantivos"
    if not any(Path(f).name == _HANDOFF for f in staged):
        return False, f"{_HANDOFF} no actualizado en este commit ({len(substantive)} archivos sustantivos)"
    missing = [s for s in _REQUIRED if s not in handoff_text]
    if missing:
        return False, f"{_HANDOFF} sin secciones obligatorias: {', '.join(missing)}"
    return True, "handoff fresco"


def main() -> int:
    if len(sys.argv) <= 1 or sys.argv[1] in ("-h", "--help"):
        # Fuera del hook commit-msg (sin archivo de mensaje, o --help): modo informativo,
        # nunca bloquea. El enforcement solo aplica con el archivo de mensaje del hook.
        print(
            "ℹ️ [HANDOFF VC-140] uso: check_handoff_freshness.py <archivo-mensaje-commit>; "
            "sin archivo = modo informativo (no bloquea).",
            file=sys.stderr,
        )
        return 0
    try:
        msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("mensaje de commit ilegible %s: %s", sys.argv[1], exc)
        msg = ""
    hp = _ROOT / _HANDOFF
    text = hp.read_text(encoding="utf-8") if hp.exists() else ""
    ok, reason = check_handoff_freshness(_staged_files(), text, msg)
    if ok:
        print(f"✅ [HANDOFF VC-140] {reason}", file=sys.stderr)
        return 0
    print(
        f"❌ [HANDOFF VC-140] BLOQUEADO — {reason}.\n"
        f"   Actualiza {_HANDOFF} (ESTADO/SIGUIENTE/VERIFICAR) y haz `git add {_HANDOFF}`,\n"
        f"   o usa [skip-handoff] en el mensaje para fixes triviales.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
