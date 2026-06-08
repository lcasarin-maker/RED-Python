#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests falsables del Stop hook de discurso (Sprint 28.5).

Ejercen el parser del transcript JSONL (la lógica nueva): extrae la prosa del
último mensaje assistant, ignora los pure-tool_use (sin prosa) y tolera transcript
ausente/parcial sin crashear el turno."""
import json

import scripts.discourse_hook as dh
from scripts.discourse_hook import last_assistant_text


def _write_jsonl(path, records):
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def _assistant(blocks):
    return {"type": "assistant", "message": {"role": "assistant", "content": blocks}}


def test_extracts_last_assistant_prose(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_jsonl(
        t,
        [
            {"type": "user", "message": {"role": "user", "content": "hola"}},
            _assistant([{"type": "text", "text": "primera respuesta"}]),
            _assistant(
                [{"type": "tool_use", "name": "Bash", "input": {}}]
            ),  # sin prosa
            _assistant([{"type": "text", "text": "respuesta final clara"}]),
        ],
    )
    assert last_assistant_text(str(t)) == "respuesta final clara"


def test_pure_tool_use_turn_yields_empty(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_jsonl(t, [_assistant([{"type": "tool_use", "name": "Read", "input": {}}])])
    assert last_assistant_text(str(t)) == ""


def test_missing_transcript_returns_empty_not_crash(tmp_path):
    assert last_assistant_text(str(tmp_path / "no_existe.jsonl")) == ""


def test_partial_jsonl_line_is_skipped(tmp_path):
    t = tmp_path / "transcript.jsonl"
    t.write_text(
        '{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"buena"}]}}\n'
        "{roto no es json\n",
        encoding="utf-8",
    )
    assert last_assistant_text(str(t)) == "buena"


def _isolate_sentinel(monkeypatch, tmp_path):
    """Apunta el sentinel a un tmp y neutraliza la prep (efectos colaterales)."""
    sentinel = tmp_path / ".compact_needed"
    monkeypatch.setattr(dh, "_SENTINEL", sentinel)
    monkeypatch.setattr(dh, "_auto_prepare_compact", lambda *_: None)
    return sentinel


def test_many_msgs_low_tokens_does_not_block(monkeypatch, tmp_path):
    """TK-031 Deuda #4 (2º eje): 62 msgs / 13K tokens NO escribe sentinel.
    El conteo de mensajes es informativo, nunca bloqueante."""
    sentinel = _isolate_sentinel(monkeypatch, tmp_path)
    dh._check_and_flag_compact({"assistant_messages": 62, "output_tokens": 13_000})
    assert not sentinel.exists()


def test_high_tokens_blocks(monkeypatch, tmp_path):
    """El bloqueo cuelga SOLO de tokens: ≥80K escribe sentinel."""
    sentinel = _isolate_sentinel(monkeypatch, tmp_path)
    dh._check_and_flag_compact({"assistant_messages": 5, "output_tokens": 80_000})
    assert sentinel.exists()
    body = sentinel.read_text(encoding="utf-8")
    assert "tokens out" in body


def test_high_tokens_and_msgs_reason_is_token_driven(monkeypatch, tmp_path):
    """Con ambos ejes altos, el sentinel se escribe y marca msgs como informativo."""
    sentinel = _isolate_sentinel(monkeypatch, tmp_path)
    dh._check_and_flag_compact({"assistant_messages": 99, "output_tokens": 90_000})
    body = sentinel.read_text(encoding="utf-8")
    assert "tokens out" in body and "informativo" in body
