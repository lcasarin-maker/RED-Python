#!/usr/bin/env python3
"""
compress_historial.py v1.0 — FASE 5: Token-Saving Strategies
Aggregates HISTORIAL.md sessions older than N days into an archive,
reducing active file size for faster agent context loading.
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("compress_historial")


def parse_sessions(content: str) -> list[dict]:
    """Extract sessions from HISTORIAL.md."""
    sessions: list[dict] = []
    # Header form in the real HISTORIAL.md is "## SESIÓN <date> <title>" (no
    # brackets). Capture the rest of the header line as the session id; the
    # lazy body runs until the next session header or EOF.
    pattern = r"## SESI[O\xd3]N ([^\n]+).*?(?=## SESI[O\xd3]N|\Z)"
    for match in re.finditer(pattern, content, re.DOTALL):
        session_id = match.group(1).strip()
        block = match.group(0)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", block)
        sessions.append(
            {
                "id": session_id,
                "date": date_match.group(1) if date_match else None,
                "content": block,
                "size": len(block),
            }
        )
    return sessions


def extract_critical_info(session_content: str) -> dict | None:
    """Extract essential info from session JSON retrospective block."""
    try:
        json_match = re.search(r'\{[^}]*"learning[^}]*\}', session_content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return {
                "learning": data.get("learning_1", ""),
                "violation": data.get("violation", ""),
                "next_agent_knows": data.get("next_agent_knows", ""),
                "rules_touched": data.get("rules_touched", []),
            }
    except Exception as e:
        _logger.debug("extract_critical_info: could not parse JSON block: %s", e)
    return None


def create_summary(session: dict) -> str:
    """Create one-line summary of a session."""
    critical = extract_critical_info(session["content"])
    if critical:
        learning = critical.get("learning", "")[:40]
        rules = ",".join(map(str, critical.get("rules_touched", [])))
        return f"- **[{session['date']}]** Rules {rules}: {learning}"
    first_line = session["content"].split("\n")[0]
    return f"- **[{session['date']}]** {first_line[:60]}"


def compress_historial(
    historial_path: Path,
    archive_dir: Path,
    days_threshold: int = 30,
) -> bool:
    """Archive sessions older than days_threshold and rewrite HISTORIAL.md.

    Args:
        historial_path: Path to HISTORIAL.md.
        archive_dir: Directory where archive files are written.
        days_threshold: Sessions older than this many days are archived.

    Returns:
        True on success, False if HISTORIAL.md not found.
    """
    if not historial_path.exists():
        _logger.error("compress_historial: %s not found", historial_path)
        return False

    content = historial_path.read_text(encoding="utf-8")
    sessions = parse_sessions(content)

    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    keep_sessions: list[dict] = []
    archive_sessions: list[dict] = []

    for session in sessions:
        if session["date"]:
            try:
                session_date = datetime.strptime(session["date"], "%Y-%m-%d")
                if session_date < cutoff_date:
                    archive_sessions.append(session)
                    continue
            except ValueError as e:
                _logger.warning(
                    "compress_historial: bad date in session %s: %s", session["id"], e
                )
        keep_sessions.append(session)

    if not archive_sessions:
        _logger.info(
            "compress_historial: no sessions to archive (threshold: %s days)",
            days_threshold,
        )
        return True

    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_date = (
        archive_sessions[0]["date"][:7] if archive_sessions[0]["date"] else "unknown"
    )
    archive_file = archive_dir / f"HISTORIAL_ARCHIVE_{archive_date}.md"

    archive_content = (
        f"# HISTORIAL ARCHIVE — {archive_date}\n\n## Summary (Compressed)\n\n"
    )
    archive_content += "Critical insights from archived sessions:\n\n"
    for session in archive_sessions:
        archive_content += create_summary(session) + "\n"
    archive_content += "\n---\n\n## Full Sessions (Original)\n\n"
    for session in archive_sessions:
        archive_content += session["content"] + "\n\n"

    archive_file.write_text(archive_content, encoding="utf-8")

    new_content = "# HISTORIAL\n\n"
    new_content += f"**Archived sessions before {cutoff_date.date()}:** See archive dir.\n\n---\n\n"
    for session in keep_sessions:
        new_content += session["content"] + "\n\n"

    historial_path.write_text(new_content, encoding="utf-8")

    original_size = sum(s["size"] for s in sessions)
    compressed_size = sum(s["size"] for s in keep_sessions)
    savings = original_size - compressed_size
    _logger.info(
        "compress_historial: archived=%s kept=%s saved=%.1fKB (%.1f%%)",
        len(archive_sessions),
        len(keep_sessions),
        savings / 1024,
        (savings / original_size * 100) if original_size else 0,
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compress HISTORIAL.md by archiving old sessions"
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Archive sessions older than N days"
    )
    parser.add_argument("--historial", type=Path, default=None)
    parser.add_argument("--archive-dir", type=Path, default=None)
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run with root-relative defaults (used by stop hook / PreCompact)",
    )
    args = parser.parse_args()

    # --auto (or absent paths): resolve relative to project root, not CWD.
    # This makes the stop-hook invocation safe regardless of CWD.
    historial = args.historial or _ROOT / "HISTORIAL.md"
    archive_dir = args.archive_dir or _ROOT / ".git" / "historial_archive"

    ok = compress_historial(historial, archive_dir, args.days)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
