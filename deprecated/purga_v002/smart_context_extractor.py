#!/usr/bin/env python3
"""
smart_context_extractor.py v1.0 — NIVEL 5: Context Management
Extracts only relevant sections from STATUS.md (-40% to -60% tokens).
Auto-decides whether COMPACT is needed based on context usage.
"""

import json
import logging
import re
from pathlib import Path

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("smart_context_extractor")

TOKEN_BUDGET = 150_000


def extract_keywords(task_description: str) -> set[str]:
    """Extract key technical terms from task description."""
    keywords: set[str] = set()
    tech_terms = [
        "heartbeat", "merge", "token", "cache", "compact", "dashboard",
        "encoding", "validation", "git", "hook", "test", "script", "db",
        "api", "daemon", "alert", "monitor", "remediate", "historial",
    ]
    for term in tech_terms:
        if term in task_description.lower():
            keywords.add(term)
    # File/component names
    keywords.update(re.findall(r'(\w+\.py|\w+\.md|\w+\.json)', task_description))
    return keywords


def parse_status_md(content: str) -> dict[str, str]:
    """Parse STATUS.md into CAMPO sections keyed by CAMPO number."""
    campos: dict[str, str] = {}
    current_campo: str | None = None
    current_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("## CAMPO"):
            if current_campo:
                campos[current_campo] = "\n".join(current_lines).strip()
            match = re.search(r'CAMPO (\d+)', line)
            current_campo = match.group(1) if match else None
            current_lines = [line]
        elif current_campo:
            current_lines.append(line)

    if current_campo:
        campos[current_campo] = "\n".join(current_lines).strip()
    return campos


def score_campo_relevance(campo_num: str, campo_content: str, keywords: set[str]) -> float:
    """Score how relevant a CAMPO is to the task (0.0 to 1.0)."""
    score = 0.0
    if campo_num == "1":
        score += 0.3
    if campo_num == "3":
        score += 0.2
    if campo_num == "4" and any(kw in {"error", "bug", "block", "issue"} for kw in keywords):
        score += 0.3
    if campo_num == "6":
        score += 0.4
    content_lower = campo_content.lower()
    keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
    score += (keyword_matches / (len(keywords) + 1)) * 0.5
    return min(score, 1.0)


def extract_relevant_context(
    task_description: str, status_md_path: Path
) -> tuple[str, float, dict]:
    """Extract only relevant sections from STATUS.md.

    Returns:
        (extracted_context, tokens_saved, extraction_report)
    """
    try:
        status_content = status_md_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        _logger.error("extract_relevant_context: cannot read %s: %s", status_md_path, e)
        return "", 0.0, {"keywords_found": [], "campos_extracted": [], "scores": {},
                         "original_tokens": 0, "extracted_tokens": 0, "savings_percent": 0}
    campos = parse_status_md(status_content)
    keywords = extract_keywords(task_description)

    scored: list[tuple[str, str, float]] = [
        (num, content, score_campo_relevance(num, content, keywords))
        for num, content in campos.items()
    ]
    scored.sort(key=lambda x: x[2], reverse=True)
    relevant = [s for s in scored if s[2] > 0.1][:4]

    extracted_context = "\n\n".join(content for _, content, _ in relevant)

    original_tokens = len(status_content.split()) * 1.3
    extracted_tokens = len(extracted_context.split()) * 1.3
    tokens_saved = original_tokens - extracted_tokens

    report = {
        "task": task_description[:50],
        "keywords_found": sorted(keywords),
        "campos_extracted": [num for num, _, _ in relevant],
        "scores": {num: round(sc, 2) for num, _, sc in relevant},
        "original_tokens": int(original_tokens),
        "extracted_tokens": int(extracted_tokens),
        "savings_percent": round((tokens_saved / original_tokens) * 100, 1) if original_tokens else 0,
    }
    return extracted_context, tokens_saved, report


def auto_compact_decision(
    historial_path: Path, status_md_path: Path
) -> tuple[bool, str | None, dict | None]:
    """Decide automatically if COMPACT is needed.

    Returns:
        (should_compact, reason, recommendation)
    """
    historial_content = historial_path.read_text(encoding="utf-8", errors="ignore")
    status_content = status_md_path.read_text(encoding="utf-8", errors="ignore")

    msg_count = historial_content.count("\n\n")
    historial_tokens = len(historial_content.encode("utf-8")) / 4
    status_tokens = len(status_content.encode("utf-8")) / 4
    total_tokens = historial_tokens + status_tokens
    context_pct = (total_tokens / TOKEN_BUDGET) * 100

    should_compact = False
    reason: str | None = None

    if msg_count > 45:
        should_compact = True
        reason = f"Messages > 45 (current: {msg_count})"
    elif context_pct > 70:
        should_compact = True
        reason = f"Context usage > 70% (current: {context_pct:.1f}%)"

    recommendation = None
    if should_compact:
        recommendation = {
            "action": "AUTO_COMPACT",
            "steps": [
                "Run: python scripts/compress_historial.py --days 30",
                "Run: python scripts/cache_protocol_rules.py --build",
                "Write new STATUS.md (7 campos)",
                "Generate COMPACT summary",
            ],
            "expected_savings_tokens": int(historial_tokens * 0.6),
            "estimated_new_context": int(total_tokens * 0.4),
        }

    _logger.info(
        "auto_compact_decision: compact=%s reason=%s context_pct=%.1f%%",
        should_compact, reason, context_pct,
    )
    return should_compact, reason, recommendation


def main() -> int:
    """CLI entry point: check compact decision for HISTORIAL.md + STATUS.md."""
    import argparse
    parser = argparse.ArgumentParser(description="Smart context extractor — compact decision")
    parser.add_argument("--historial", type=Path, default=Path("HISTORIAL.md"))
    parser.add_argument("--status", type=Path, default=Path("STATUS.md"))
    args = parser.parse_args()
    try:
        should, reason, rec = auto_compact_decision(args.historial, args.status)
    except Exception as e:
        _logger.error("main: auto_compact_decision failed: %s", e)
        return 1
    if should:
        _logger.info("COMPACT recommended: %s", reason)
        if rec:
            for step in rec.get("steps", []):
                _logger.info("  → %s", step)
        return 0
    _logger.info("No compact needed.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
