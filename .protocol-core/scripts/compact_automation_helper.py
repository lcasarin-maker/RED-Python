#!/usr/bin/env python3
"""
compact_automation_helper.py v1.0 — Pre-COMPACT Task Orchestrator
Runs context compression steps before /compact: compress, cache, export, headspace.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("compact_automation_helper")


class CompactAutomationHelper:
    """Orchestrates pre-COMPACT tasks: compress, cache, export, headspace trigger."""

    def __init__(self, project_dir: Path | None = None):
        self.scripts_dir = (project_dir or Path(".")) / "scripts"

    def _run(self, cmd_args: list[str], label: str, timeout: int = 30) -> bool:
        """Run a subprocess command. Returns True on success."""
        try:
            result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                _logger.info("_run: %s OK", label)
                return True
            _logger.warning(
                "_run: %s failed (rc=%d): %s", label, result.returncode, result.stderr[:100]
            )
        except Exception as e:
            _logger.warning("_run: %s error: %s", label, e)
        return False

    def run_compress_historial(self, days: int = 30) -> bool:
        """Archive old HISTORIAL.md sessions."""
        return self._run(
            [sys.executable, str(self.scripts_dir / "compress_historial.py"), "--days", str(days)],
            "compress_historial",
        )

    def run_headspace_trigger(self) -> bool:
        """Check context usage via headspace_auto_trigger."""
        return self._run(
            [sys.executable, str(self.scripts_dir / "headspace_auto_trigger.py"), "--check"],
            "headspace_trigger",
        )

    def run_session_export(self) -> bool:
        """Export latest session retrospective."""
        return self._run(
            [sys.executable, str(self.scripts_dir / "auto_export_retrospective.py"), "--auto"],
            "session_export",
        )

    def run_cache_rebuild(self) -> bool:
        """Rebuild protocol rules cache."""
        return self._run(
            [sys.executable, str(self.scripts_dir / "cache_protocol_rules.py"), "--build"],
            "cache_rebuild",
        )

    def auto_compact_prepare(self) -> dict:
        """Run all pre-COMPACT tasks. Returns results dict."""
        _logger.info("auto_compact_prepare: starting pre-COMPACT sequence")
        results: dict = {
            "timestamp": datetime.now().isoformat(),
            "compress_historial": self.run_compress_historial(),
            "headspace_trigger": self.run_headspace_trigger(),
            "session_export": self.run_session_export(),
            "cache_rebuild": self.run_cache_rebuild(),
        }
        completed = sum(1 for k, v in results.items() if isinstance(v, bool) and v)
        _logger.info("auto_compact_prepare: %d/4 tasks completed", completed)
        return results


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Pre-COMPACT automation orchestrator")
    parser.add_argument("--prepare", action="store_true", help="Run all pre-COMPACT tasks")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    helper = CompactAutomationHelper()
    results = helper.auto_compact_prepare()

    if args.json:
        print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
