#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop hook (canal hook runtime, Sprint 28.5): el primer enforcement que auditа
la PROSA de respuesta del agente, no el repo. Lee {transcript_path,
stop_hook_active} de stdin, extrae el texto del último mensaje assistant del
transcript JSONL, y corre D14 Discourse Rigor sobre él.

WARN-only (decisión usuario): imprime hallazgos a stderr y SIEMPRE exit 0 — nunca
bloquea el turno (un BLOCK forzaría al agente a continuar; sin corpus de
calibración eso es ruido). Hace a D14 enforcar de verdad en vez de verde-huérfano."""
import json
import logging
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dimensions.d13_observable import D13Observable  # noqa: E402
from dimensions.d14_discourse_rigor import D14DiscourseRigor  # noqa: E402

logger = logging.getLogger("discourse_hook")


def _assistant_text_blocks(obj: dict) -> list:
    """Texto de los bloques 'text' de un msg assistant; [] si no es assistant o no
    tiene prosa (p.ej. un turno pure-tool_use)."""
    if obj.get("type") != "assistant":
        return []
    content = obj.get("message", {}).get("content")
    if not isinstance(content, list):
        return []
    return [
        b.get("text", "")
        for b in content
        if isinstance(b, dict) and b.get("type") == "text"
    ]


def _parse_jsonl_line(line: str):
    """Parsea una línea del transcript; None si vacía o no-JSON (registrado, no
    silencioso)."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        logger.debug("línea de transcript no-JSON, saltada")
        return None


def last_assistant_text(transcript_path: str) -> str:
    """Prosa del último mensaje assistant con bloques de texto. Devuelve '' si no
    hay transcript legible."""
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as exc:
        logger.warning("transcript ilegible %s: %s", transcript_path, exc)
        return ""
    text_parts = []
    for line in lines:
        obj = _parse_jsonl_line(line)
        if obj is None:
            continue
        parts = _assistant_text_blocks(obj)
        if parts:
            text_parts = parts  # conserva el último turno con prosa
    return "\n".join(text_parts)


_SENTINEL = _ROOT / ".compact_needed"
_MSG_THRESHOLD = 40       # mensajes assistant — ~40 turnos = contexto alto
_TOKEN_THRESHOLD = 80_000  # output tokens acumulados en la sesión


_PRE_THRESHOLD = 28  # aviso temprano: auto-prep sin bloqueo


def _auto_prepare_compact(reason_parts: list[str]) -> None:
    """Ejecuta compact_automation_helper inline — no subprocess, no bloqueo."""
    try:
        from scripts.compact_automation_helper import CompactAutomationHelper
        helper = CompactAutomationHelper(_ROOT)
        # Solo compress + headspace; no clear sentinel (aún no corrió /compact)
        ok_hist = helper.run_compress_historial()
        ok_head = helper.run_headspace_trigger()
        print(
            f"[TK-031] Auto-prep compact: historial={'OK' if ok_hist else 'FAIL'}, "
            f"headspace={'OK' if ok_head else 'FAIL'}",
            file=sys.stderr,
        )
    except Exception as exc:
        logger.warning("_auto_prepare_compact falló: %s", exc)


def _check_and_flag_compact(obs: dict) -> None:
    """Si el contexto real supera umbral, escribe .compact_needed para bloquear
    herramientas hasta que el usuario corra /compact (TK-031 enforcement real).
    Al superar PRE_THRESHOLD ejecuta preparación anticipada sin bloquear."""
    has_sentinel = _SENTINEL.exists()
    msgs = obs.get("assistant_messages", 0)
    tokens = obs.get("output_tokens", 0)
    over_pre = msgs >= _PRE_THRESHOLD
    over_msgs = msgs >= _MSG_THRESHOLD
    over_tokens = tokens >= _TOKEN_THRESHOLD

    # TK-031 (Deuda #4, 2º eje): el BLOQUEO depende SOLO de tokens. El conteo de
    # msgs no es proxy de contexto — un turno con muchas herramientas acumula ≥40
    # mensajes assistant con tokens bajos (p.ej. 62 msgs / 13K tokens). El eje-msgs
    # queda como aviso informativo, nunca bloqueante.
    if over_tokens:
        reason = [f"{tokens:,} tokens out (umbral {_TOKEN_THRESHOLD:,})"]
        if over_msgs:
            reason.append(f"{msgs} msgs (informativo, no bloquea)")
        # Preparación anticipada antes de escribir sentinel
        _auto_prepare_compact(reason)
        _SENTINEL.write_text(
            f"compact_needed: {', '.join(reason)}\n", encoding="utf-8"
        )
        print(
            f"\n🚨 [TK-031] COMPACT REQUERIDO — contexto alto: {', '.join(reason)}\n"
            f"   Preparación anticipada ejecutada. Corre /compact para liberar.\n"
            f"   El bloqueo se libera automáticamente al iniciar /compact.",
            file=sys.stderr,
        )
    elif (over_pre or over_msgs) and not has_sentinel:
        # Zona de aviso (msgs altos o pre-umbral): prepara SIN bloquear.
        nota = (
            f"{msgs} msgs (≥ umbral informativo {_MSG_THRESHOLD})"
            if over_msgs
            else f"{msgs} msgs (pre-aviso {_PRE_THRESHOLD})"
        )
        print(
            f"[TK-031] PRE-AVISO: {nota} — solo informativo; el bloqueo depende de "
            f"tokens (umbral {_TOKEN_THRESHOLD:,}). Prep anticipada.",
            file=sys.stderr,
        )
        _auto_prepare_compact([f"{msgs} msgs pre-aviso"])
    elif _SENTINEL.exists():
        # Contexto bajó (nueva sesión) — limpiar sentinel viejo
        _SENTINEL.unlink(missing_ok=True)


def main() -> int:
    import argparse

    argparse.ArgumentParser(
        description="Stop hook de CoderCerberus: audita prosa (D14) y detecta "
        "contexto alto para forzar /compact (TK-031)."
    ).parse_args()
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if payload.get("stop_hook_active"):
        return 0  # no recursar
    transcript = payload.get("transcript_path")
    if not transcript:
        return 0
    # D13 observabilidad: corre siempre (incluso en turnos pure-tool_use).
    obs = D13Observable().observe_session(transcript)
    print(
        f"[D13 obs] {obs['assistant_messages']} msgs assistant, "
        f"{obs['output_tokens']} tokens out",
        file=sys.stderr,
    )
    # TK-031: detectar contexto alto con datos reales y forzar compact si aplica.
    _check_and_flag_compact(obs)
    # D14 discurso: solo si el turno tiene prosa.
    text = last_assistant_text(transcript)
    if not text.strip():
        return 0
    findings = D14DiscourseRigor().audit_response(text)
    logger.info("discourse_hook: %d hallazgos sobre %d chars", len(findings), len(text))
    for f in findings:
        print(f"[D14 {f.status.value}] {f.message}", file=sys.stderr)
    return 0  # WARN-only: D14 nunca bloquea


if __name__ == "__main__":
    sys.exit(main())
