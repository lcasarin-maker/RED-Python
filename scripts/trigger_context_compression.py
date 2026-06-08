#!/usr/bin/env python3
"""
trigger_context_compression.py v1.0 — FASE 8: Context Compression Trigger
Auto-activates context compression when usage exceeds threshold.
Self-contained: estimates context usage from HISTORIAL.md/STATUS.md against
TOKEN_BUDGET and decides whether compaction is due (see check()).
"""

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8, TOKEN_BUDGET

setup_windows_utf8()

import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
_logger = logging.getLogger("headspace_auto_trigger")

CONTEXT_THRESHOLD_PCT = 75.0


class HeadspaceAutoTrigger:
    """Detects and triggers context compression automatically."""

    def __init__(
        self, historial_path: Path | None = None, status_path: Path | None = None
    ):
        self.historial_path = historial_path or Path("HISTORIAL.md")
        self.status_path = status_path or Path("STATUS.md")

    def estimate_context_usage(self) -> int:
        """Estimate current context token usage from key files."""
        total = 0
        for path in [
            self.historial_path,
            self.status_path,
            Path("AGENT.md"),
            Path("CLAUDE.md"),
        ]:
            if path.exists():
                try:
                    total += len(path.read_bytes()) // 4
                except OSError as e:
                    _logger.warning(
                        "estimate_context_usage: cannot read %s: %s", path, e
                    )
        return total

    def check(self) -> dict:
        """Check context usage and return a status report."""
        current_tokens = self.estimate_context_usage()
        context_pct = (current_tokens / TOKEN_BUDGET) * 100
        should_compress = context_pct >= CONTEXT_THRESHOLD_PCT
        report = {
            "context_tokens": current_tokens,
            "context_percentage": round(context_pct, 1),
            "threshold": CONTEXT_THRESHOLD_PCT,
            "should_compress": should_compress,
        }
        _logger.info(
            "check: tokens=%d pct=%.1f%% compress=%s",
            current_tokens,
            context_pct,
            should_compress,
        )
        return report

    def trigger_compression(self) -> list[str]:
        """Execute compression sub-scripts. Returns list of completed action labels."""
        actions: list[str] = []
        steps = [
            (
                [sys.executable, "scripts/compress_historial.py", "--days", "30"],
                "Archived old sessions",
            ),
            (
                [sys.executable, "scripts/cache_protocol_rules.py", "--build"],
                "Cached protocol rules",
            ),
        ]
        for cmd_args, label in steps:
            try:
                result = subprocess.run(
                    cmd_args, capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    actions.append(label)
                    _logger.info("trigger_compression: %s OK", label)
                else:
                    _logger.warning(
                        "trigger_compression: %s failed (rc=%d)",
                        label,
                        result.returncode,
                    )
            except Exception as e:
                _logger.warning("trigger_compression: %s error: %s", label, e)
        actions.append("Context >75% — recommend /compact before next session")
        return actions

    def get_report(self) -> dict:
        """Return full report; include triggered actions if threshold exceeded."""
        report = self.check()
        if report["should_compress"]:
            report["actions"] = self.trigger_compression()
        return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Headspace context compression trigger"
    )
    parser.add_argument("--check", action="store_true", help="Check context usage")
    parser.add_argument(
        "--trigger", action="store_true", help="Trigger compression if needed"
    )
    parser.add_argument("--report", action="store_true", help="Print detailed report")
    args = parser.parse_args()

    trigger = HeadspaceAutoTrigger()

    if args.report:
        report = trigger.get_report()
        _logger.info(
            "Context: %d tokens (%.1f%%) threshold=%.0f%%",
            report["context_tokens"],
            report["context_percentage"],
            report["threshold"],
        )
        for action in report.get("actions", []):
            _logger.info("  -> %s", action)
        return 0

    report = trigger.check()
    _logger.info(
        "Context %.1f%% — %s",
        report["context_percentage"],
        "EXCEEDS threshold" if report["should_compress"] else "OK",
    )
    if report["should_compress"] and args.trigger:
        for action in trigger.trigger_compression():
            _logger.info("  -> %s", action)

    return 0


if __name__ == "__main__":
    sys.exit(main())
