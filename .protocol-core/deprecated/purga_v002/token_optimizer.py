#!/usr/bin/env python3
"""
token_optimizer.py v1.0 — NIVEL 5: Token-Saving Orchestrator
Coordinates compress_historial, smart_context_extractor, and cache_protocol_rules
to reduce context token usage. DB path via CERBERUS_DB_PATH env var.
"""

import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("token_optimizer")

_DEFAULT_DB = ".secrets/protocolo/protocol_state.db"


def _get_db_path() -> Path:
    return Path(os.getenv("CERBERUS_DB_PATH", _DEFAULT_DB))


def log_optimization(action: str, tokens_saved: int, method: str) -> bool:
    """Log optimization event to SQLite DB. Returns True on success."""
    db = _get_db_path()
    if not db.exists():
        _logger.debug("log_optimization: DB not found at %s, skipping log", db)
        return False
    try:
        conn = sqlite3.connect(str(db))
        try:
            conn.execute(
                "INSERT INTO token_optimizations (timestamp, action, tokens_saved, method)"
                " VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), action, tokens_saved, method),
            )
            conn.commit()
        finally:
            conn.close()
        return True
    except Exception as e:
        _logger.warning("log_optimization: failed to log %s: %s", action, e)
        return False


def run_compact(historial_path: Path, days: int = 30) -> dict | None:
    """Run compress_historial.py subprocess. Returns result dict or None on failure."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/compress_historial.py",
             "--historial", str(historial_path), "--days", str(days)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            _logger.info("run_compact: OK (days=%d)", days)
            log_optimization("COMPACT", days * 50, "compress_historial")
            return {"action": "COMPACT", "days": days}
        _logger.warning(
            "run_compact: failed rc=%d stderr=%s", result.returncode, result.stderr[:100]
        )
    except Exception as e:
        _logger.error("run_compact: exception: %s", e)
    return None


def run_cache_rebuild(rules_dir: Path) -> dict | None:
    """Run cache_protocol_rules.py subprocess. Returns result dict or None on failure."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/cache_protocol_rules.py",
             "--build", "--rules-dir", str(rules_dir)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            _logger.info("run_cache_rebuild: OK")
            log_optimization("REBUILD_CACHE", 500, "cache_protocol_rules")
            return {"action": "CACHE"}
        _logger.warning("run_cache_rebuild: failed rc=%d", result.returncode)
    except Exception as e:
        _logger.error("run_cache_rebuild: exception: %s", e)
    return None


def run_context_check(status_path: Path, task: str) -> dict | None:
    """Delegate to smart_context_extractor for extraction stats."""
    try:
        from scripts.smart_context_extractor import extract_relevant_context
        _, tokens_saved, report = extract_relevant_context(task, status_path)
        _logger.info(
            "run_context_check: saved=%.0f tokens (%.1f%%)",
            tokens_saved, report.get("savings_percent", 0),
        )
        log_optimization("SMART_EXTRACTION", int(tokens_saved), "smart_context_extractor")
        return {"action": "EXTRACTION", "tokens_saved": int(tokens_saved), "report": report}
    except Exception as e:
        _logger.error("run_context_check: exception: %s", e)
    return None


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Token optimizer — coordinates context reduction")
    parser.add_argument("--historial", type=Path, default=Path("HISTORIAL.md"))
    parser.add_argument("--rules-dir", type=Path, default=Path("REGLAS"))
    parser.add_argument("--status", type=Path, default=Path("STATUS.md"))
    parser.add_argument("--task", type=str, default="", help="Task description for context extraction")
    parser.add_argument("--days", type=int, default=30, help="Archive threshold in days")
    args = parser.parse_args()

    results: dict = {}

    compact = run_compact(args.historial, args.days)
    if compact:
        results["compact"] = compact

    cache = run_cache_rebuild(args.rules_dir)
    if cache:
        results["cache"] = cache

    if args.task and args.status.exists():
        extraction = run_context_check(args.status, args.task)
        if extraction:
            results["extraction"] = extraction

    _logger.info("main: optimizations applied: %d", len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
