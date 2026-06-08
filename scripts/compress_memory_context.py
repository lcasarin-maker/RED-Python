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
import sys
from pathlib import Path

# Bootstrap sys.path for portability
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from scripts.core_utils import setup_windows_utf8

    setup_windows_utf8()
except ImportError as e:
    sys.stderr.write(f"[WARN] setup_windows_utf8 not available: {e}\n")

from scripts.helpers import extract_compact_facts


def compress_session_to_fact_summary(session_id, session_content):
    """Compress entire session to 1 line of facts."""
    facts = extract_compact_facts(session_content)

    # Create ultra-compact summary
    summary = f"[{session_id}] "
    if facts["key_learnings"]:
        summary += f"📚 {facts['key_learnings'][0]} "
    if facts["violations"]:
        summary += f"⚠️ {facts['violations'][0]} "
    elif facts["decisions"]:
        summary += f"📋 Rules: {', '.join(facts['decisions'][:3])} "

    status_icon = (
        "✅"
        if "COMPLETO" in facts["status"]
        or "SUCCESS" in facts["status"]
        or "COMPLETED" in facts["status"]
        else "⚠️"
    )
    summary += f"{status_icon} {facts['status']}"

    return summary


def build_dialog_path_guide(sessions):
    """Build navigation guide showing agent decision path."""
    path_guide = {"total_sessions": len(sessions), "path": [], "decision_tree": {}}

    for i, session in enumerate(sessions):
        content = session.get("content", "")
        facts = extract_compact_facts(content)
        node = {
            "step": i + 1,
            "session_id": session.get("id", "unknown"),
            "decision": facts.get("decisions")[0] if facts.get("decisions") else None,
            "outcome": (
                "✅ completed"
                if "COMPLETO" in facts.get("status", "").upper()
                or "COMPLETED" in facts.get("status", "").upper()
                else "⚠️ blocked"
            ),
        }
        path_guide["path"].append(node)

    return path_guide


def compress_memory_block(memory_content):
    """
    Compress memory block using ReMe strategy.
    Goal: Reduce 223k tokens to ~1.1k (99.5% compression)
    """
    # Parse sessions
    sessions = []
    lines = memory_content.split("\n")

    current_session = None
    for line in lines:
        if line.startswith("## SESIÓN") or line.startswith("## SESSION"):
            if current_session:
                sessions.append(current_session)
            session_id = line.replace("## SESIÓN", "").replace("## SESSION", "").strip()
            current_session = {"id": session_id, "content": line}
        elif current_session:
            current_session["content"] += "\n" + line

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
        "file_cache_refs": [],
    }

    for session in sessions:
        try:
            summary = compress_session_to_fact_summary(
                session.get("id", "unknown"), session.get("content", "")
            )
            compressed["fact_summaries"].append(summary)
        except Exception as e:
            # Safe fallback if summary fails
            compressed["fact_summaries"].append(
                f"[{session.get('id', 'unknown')}] (failed to compress: {str(e)})"
            )

    # Serialize and calculate compression
    compressed_json = json.dumps(compressed, separators=(",", ":"))
    compressed["compressed_bytes"] = len(compressed_json)
    if len(memory_content) > 0:
        compressed["compression_ratio"] = (
            1 - len(compressed_json) / len(memory_content)
        ) * 100

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

    content = input_file.read_text(encoding="utf-8")
    compressed = compress_memory_block(content)

    print("✅ MEMORY COMPRESSION (ReMe)")
    print(f"   Original size: {compressed['original_bytes']:,} bytes")
    print(f"   Compressed size: {compressed['compressed_bytes']:,} bytes")
    print(f"   Compression: {compressed['compression_ratio']:.1f}%")
    print(f"   Fact summaries: {len(compressed['fact_summaries'])}")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(compressed, f, indent=2, ensure_ascii=False)
        print(f"   Output: {args.output}")
