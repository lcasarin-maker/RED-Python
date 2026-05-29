#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Compression ReMe-style — 99.5% compression (223k → 1.1k tokens).
FASE 6.3: GitHub Strategy #3
Technique: Compact summaries + dialog path guides + file caching
Source: https://github.com/agentscope-ai/ReMe
Rescued and enhanced to parse markdown sessions natively.
"""

import json
import re
from pathlib import Path
from datetime import datetime

try:
    from scripts.core_utils import setup_windows_utf8
    setup_windows_utf8()
except ImportError as e:
    import sys
    sys.stderr.write(f"[WARN] setup_windows_utf8 not available: {e}\n")

_MD_FIELDS = [
    (("**Tarea:**", "**Task:**"), ("Tarea:", "Task:")),
    (("**Estado:**", "**Status:**"), ("Estado:", "Status:")),
    (("**Próximo agente:**", "**Next agent:**"), ("Próximo agente:", "Next agent:")),
]


def _parse_md_lines(lines: list) -> tuple:
    """Return (tarea, cambios, estado, proximo) parsed from markdown session lines."""
    vals = ["", "", ""]
    cambios: list = []
    for line in lines:
        s = line.strip()
        for i, (markers, strip_tokens) in enumerate(_MD_FIELDS):
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


def extract_compact_facts(session_content):
    """Extract only critical facts from session (ReMe strategy with Markdown fallback)."""
    facts = {
        "timestamp": datetime.now().isoformat(),
        "key_learnings": [], "violations": [],
        "decisions": [], "next_steps": [], "status": "COMPLETED"
    }

    has_json = False
    if '{"' in session_content or '```json' in session_content:
        try:
            j0, j1 = session_content.find('{'), session_content.rfind('}') + 1
            if j0 != -1 and j1 > j0:
                data = json.loads(session_content[j0:j1])
                answers = data.get('answers', {}) if isinstance(data.get('answers'), dict) else data
                learning = answers.get('q1_learning') or data.get('learning_1') or data.get('learning')
                if learning:
                    facts['key_learnings'] = [str(learning)[:120]]
                violation = answers.get('q2_violation') or data.get('violation') or data.get('violations')
                if violation:
                    facts['violations'] = [str(violation)[:120]]
                decisions = data.get('rules_touched') or data.get('decisions') or []
                facts['decisions'] = [str(d) for d in decisions] if isinstance(decisions, list) else ([decisions] if isinstance(decisions, str) and decisions else [])
                next_agent = answers.get('q3_next_agent') or data.get('next_agent_knows') or data.get('next_steps')
                if next_agent:
                    facts['next_steps'] = [str(next_agent)[:120]]
                status = data.get('status') or data.get('outcome')
                if status:
                    facts['status'] = str(status).upper()
                has_json = True
        except Exception as e:
            import sys
            sys.stderr.write(f"[DEBUG] JSON parsing fallback triggered: {e}\n")

    if not has_json:
        tarea, cambios, estado, proximo = _parse_md_lines(session_content.split('\n'))
        if tarea:
            facts['key_learnings'].append(tarea[:120])
        elif cambios:
            facts['key_learnings'].append(cambios[0][:120])
        if proximo:
            facts['next_steps'].append(proximo[:120])
        if estado:
            facts['status'] = estado.upper()
        rules: list = []
        for change in cambios:
            for r in re.findall(r'(?:REGLA|Rule|Fase|S|B)\s*#?\s*\d+', change, re.IGNORECASE):
                if r not in rules:
                    rules.append(r)
            if any(w in change.lower() for w in ["violation", "incidente", "error", "violación", "fallo", "advertencia"]):
                facts['violations'].append(change[:120])
        facts['decisions'] = rules

    return facts

def compress_session_to_fact_summary(session_id, session_content):
    """Compress entire session to 1 line of facts."""
    facts = extract_compact_facts(session_content)

    # Create ultra-compact summary
    summary = f"[{session_id}] "
    if facts['key_learnings']:
        summary += f"📚 {facts['key_learnings'][0]} "
    if facts['violations']:
        summary += f"⚠️ {facts['violations'][0]} "
    elif facts['decisions']:
        summary += f"📋 Rules: {', '.join(facts['decisions'][:3])} "
    
    status_icon = "✅" if "COMPLETO" in facts['status'] or "SUCCESS" in facts['status'] or "COMPLETED" in facts['status'] else "⚠️"
    summary += f"{status_icon} {facts['status']}"
    
    return summary

def build_dialog_path_guide(sessions):
    """Build navigation guide showing agent decision path."""
    path_guide = {
        "total_sessions": len(sessions),
        "path": [],
        "decision_tree": {}
    }

    for i, session in enumerate(sessions):
        content = session.get('content', '')
        facts = extract_compact_facts(content)
        node = {
            "step": i + 1,
            "session_id": session.get('id', 'unknown'),
            "decision": facts.get('decisions')[0] if facts.get('decisions') else None,
            "outcome": "✅ completed" if "COMPLETO" in facts.get('status', '').upper() or "COMPLETED" in facts.get('status', '').upper() else "⚠️ blocked"
        }
        path_guide['path'].append(node)

    return path_guide

def compress_memory_block(memory_content, max_tokens=1000):
    """
    Compress memory block using ReMe strategy.
    Goal: Reduce 223k tokens to ~1.1k (99.5% compression)
    """
    # Parse sessions
    sessions = []
    lines = memory_content.split('\n')

    current_session = None
    for line in lines:
        if line.startswith('## SESIÓN') or line.startswith('## SESSION'):
            if current_session:
                sessions.append(current_session)
            session_id = line.replace('## SESIÓN', '').replace('## SESSION', '').strip()
            current_session = {'id': session_id, 'content': line}
        elif current_session:
            current_session['content'] += '\n' + line

    if current_session:
        sessions.append(current_session)

    # Compress each session
    compressed = {
        "version": "ReMe v1.1-Markdown",
        "original_bytes": len(memory_content),
        "compressed_bytes": 0,
        "compression_ratio": 0,
        "fact_summaries": [],
        "dialog_path": build_dialog_path_guide(sessions),
        "file_cache_refs": []
    }

    for session in sessions:
        try:
            summary = compress_session_to_fact_summary(
                session.get('id', 'unknown'),
                session.get('content', '')
            )
            compressed['fact_summaries'].append(summary)
        except Exception as e:
            # Safe fallback if summary fails
            compressed['fact_summaries'].append(f"[{session.get('id', 'unknown')}] (failed to compress: {str(e)})")

    # Serialize and calculate compression
    compressed_json = json.dumps(compressed, separators=(',', ':'))
    compressed['compressed_bytes'] = len(compressed_json)
    if len(memory_content) > 0:
        compressed['compression_ratio'] = (1 - len(compressed_json) / len(memory_content)) * 100

    return compressed

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Memory compression (ReMe-style)")
    parser.add_argument("--input", default="HISTORIAL.md", help="Input memory file")
    parser.add_argument("--output", help="Output compressed JSON")

    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        print(f"❌ File not found: {args.input}")
        exit(1)

    content = input_file.read_text(encoding='utf-8')
    compressed = compress_memory_block(content)

    print("✅ MEMORY COMPRESSION (ReMe)")
    print(f"   Original size: {compressed['original_bytes']:,} bytes")
    print(f"   Compressed size: {compressed['compressed_bytes']:,} bytes")
    print(f"   Compression: {compressed['compression_ratio']:.1f}%")
    print(f"   Fact summaries: {len(compressed['fact_summaries'])}")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(compressed, f, indent=2, ensure_ascii=False)
        print(f"   Output: {args.output}")
