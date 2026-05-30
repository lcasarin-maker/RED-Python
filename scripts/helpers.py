#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helper utilities for refactored Cerberus scripts.
This module consolidates small private helper functions that were previously
nested deep inside individual scripts. Keeping them in a single file reduces
nesting depth and improves reuse.
"""

import json
import re
from pathlib import Path
from typing import List, Optional, Dict

# ---------------------------------------------------------------------------
# Memory Compression (ReMe) helpers
# ---------------------------------------------------------------------------

_MARKDOWN_FIELDS = [
    (("**Tarea:**", "**Task:**"), ("Tarea:", "Task:")),
    (("**Estado:**", "**Status:**"), ("Estado:", "Status:")),
    (("**Próximo agente:**", "**Next agent:**"), ("Próximo agente:", "Next agent:")),
]


def _parse_markdown_lines(lines: List[str]) -> tuple:
    """Parse session markdown lines into (tarea, cambios, estado, proximo)."""
    vals = ["", "", ""]
    cambios: List[str] = []
    for line in lines:
        s = line.strip()
        for i, (markers, strip_tokens) in enumerate(_MARKDOWN_FIELDS):
            if any(m in s for m in markers):
                val = s.split("**")[-1]
                for tok in strip_tokens:
                    val = val.replace(tok, "")
                vals[i] = val.strip()
                break
        else:
            if s.startswith("- "):
                cambios.append(s[2:])
    return vals[0], cambios, vals[1], vals[2]


def extract_compact_facts(session_content: str) -> dict:
    """Extract a compact fact dictionary from a session's markdown or JSON."""
    facts: dict = {
        "timestamp": None, "key_learnings": [], "violations": [],
        "decisions": [], "next_steps": [], "status": "COMPLETED",
    }

    has_json = False
    if "{\"" in session_content or "```json" in session_content:
        try:
            j0, j1 = session_content.find('{'), session_content.rfind('}') + 1
            if j0 != -1 and j1 > j0:
                data = json.loads(session_content[j0:j1])
                answers = data.get('answers', {}) if isinstance(data.get('answers'), dict) else data
                learning = answers.get('q1_learning') or data.get('learning_1') or data.get('learning')
                if learning:
                    facts['key_learnings'].append(str(learning)[:120])
                violation = answers.get('q2_violation') or data.get('violation') or data.get('violations')
                if violation:
                    facts['violations'].append(str(violation)[:120])
                decisions = data.get('rules_touched') or data.get('decisions') or []
                facts['decisions'] = [str(d) for d in decisions] if isinstance(decisions, list) else ([decisions] if isinstance(decisions, str) and decisions else [])
                next_agent = answers.get('q3_next_agent') or data.get('next_agent_knows') or data.get('next_steps')
                if next_agent:
                    facts['next_steps'].append(str(next_agent)[:120])
                status = data.get('status') or data.get('outcome')
                if status:
                    facts['status'] = str(status).upper()
                has_json = True
        except Exception as e:
            import logging
            logging.debug(f"JSON parsing error in session data: {e}")

    if not has_json:
        tarea, cambios, estado, proximo = _parse_markdown_lines(session_content.split('\n'))
        if tarea:
            facts['key_learnings'].append(tarea[:120])
        elif cambios:
            facts['key_learnings'].append(cambios[0][:120])
        if proximo:
            facts['next_steps'].append(proximo[:120])
        if estado:
            facts['status'] = estado.upper()
        for change in cambios:
            found = re.findall(r'(?:REGLA|Rule|Fase|S|B)\s*#?\s*\d+', change, re.IGNORECASE)
            for r in found:
                if r not in facts['decisions']:
                    facts['decisions'].append(r)
            if any(w in change.lower() for w in ["violation", "incidente", "error", "violación", "fallo", "advertencia"]):
                facts['violations'].append(change[:120])
    return facts


def compress_session_to_fact_summary(session_id: str, session_content: str) -> str:
    """Create a one‑line ultra‑compact fact summary for a session."""
    facts = extract_compact_facts(session_content)
    parts = [f"[{session_id}] "]
    if facts['key_learnings']:
        parts.append(f"📚 {facts['key_learnings'][0]} ")
    if facts['violations']:
        parts.append(f"⚠️ {facts['violations'][0]} ")
    elif facts['decisions']:
        parts.append(f"📋 Rules: {', '.join(facts['decisions'][:3])} ")
    status_icon = "✅" if any(tok in facts['status'] for tok in ("COMPLETO", "SUCCESS", "COMPLETED")) else "⚠️"
    parts.append(f"{status_icon} {facts['status']}")
    return "".join(parts)


def build_dialog_path_guide(sessions: List[dict]) -> dict:
    """Construct a navigation guide that outlines the decision path across sessions."""
    guide: dict = {
        "total_sessions": len(sessions),
        "path": [],
        "decision_tree": {},
    }
    for i, session in enumerate(sessions):
        content = session.get('content', '')
        facts = extract_compact_facts(content)
        node = {
            "step": i + 1,
            "session_id": session.get('id', 'unknown'),
            "decision": facts.get('decisions')[0] if facts.get('decisions') else None,
            "outcome": "✅ completed" if "COMPLETO" in facts.get('status', '').upper() or "COMPLETED" in facts.get('status', '').upper() else "⚠️ blocked",
        }
        guide['path'].append(node)
    return guide


def compress_memory_block(memory_content: str, max_tokens: int = 1000) -> dict:
    """Compress a raw memory log into a compact JSON structure.

    The implementation mirrors the original script but now lives as a reusable
    helper.
    """
    # Parse sessions
    sessions: List[dict] = []
    current_session: Optional[dict] = None
    for line in memory_content.split('\n'):
        if line.startswith('## SESIÓN') or line.startswith('## SESSION'):
            if current_session:
                sessions.append(current_session)
            session_id = line.replace('## SESIÓN', '').replace('## SESSION', '').strip()
            current_session = {'id': session_id, 'content': line}
        elif current_session:
            current_session['content'] += '\n' + line
    if current_session:
        sessions.append(current_session)

    compressed: dict = {
        "version": "ReMe v1.1-Markdown",
        "original_bytes": len(memory_content),
        "compressed_bytes": 0,
        "compression_ratio": 0,
        "fact_summaries": [],
        "dialog_path": build_dialog_path_guide(sessions),
        "file_cache_refs": [],
    }

    for session in sessions:
        try:
            summary = compress_session_to_fact_summary(session.get('id', 'unknown'), session.get('content', ''))
            compressed['fact_summaries'].append(summary)
        except Exception as e:
            compressed['fact_summaries'].append(f"[{session.get('id', 'unknown')}] (failed to compress: {e})")

    compressed_json = json.dumps(compressed, separators=(',', ':'))
    compressed['compressed_bytes'] = len(compressed_json)
    if len(memory_content) > 0:
        compressed['compression_ratio'] = (1 - len(compressed_json) / len(memory_content)) * 100
    return compressed

def _write_results(compacted: list, output_path: Path) -> None:
    """Write compacted token data to ``output_path`` as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(compacted, indent=2, ensure_ascii=False), encoding='utf-8')

# End of helpers module
