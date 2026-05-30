#!/usr/bin/env python3
"""
automation_scheduler.py v1.0 — Protocol Automation Scheduler
Simple interval-based scheduler for Cerberus maintenance scripts.
No external dependencies (replaces APScheduler-based deprecated version).
"""

import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("automation_scheduler")

# Default schedule: interval in seconds for each task
_DEFAULT_TASKS: list[dict] = [
    {"name": "cache_rebuild",   "script": "scripts/cache_protocol_rules.py --build", "interval_s": 3600},
    {"name": "headspace_check", "script": "scripts/headspace_auto_trigger.py --check", "interval_s": 900},
]


class AutomationScheduler:
    """Interval-based scheduler for maintenance scripts. No external deps."""

    def __init__(self, tasks: list[dict] | None = None):
        self.tasks: list[dict] = tasks if tasks is not None else list(_DEFAULT_TASKS)
        self._last_run: dict[str, float] = {}

    def _run_task(self, task: dict) -> bool:
        """Execute a single task via subprocess. Returns True on success."""
        parts = task["script"].split()
        cmd = [sys.executable] + parts
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                _logger.info("_run_task: %s OK", task["name"])
                return True
            _logger.warning(
                "_run_task: %s failed (rc=%d): %s",
                task["name"], result.returncode, result.stderr[:100],
            )
        except Exception as e:
            _logger.error("_run_task: %s error: %s", task["name"], e)
        return False

    def due_tasks(self) -> list[dict]:
        """Return tasks whose interval has elapsed since last run."""
        now = time.monotonic()
        due: list[dict] = []
        for task in self.tasks:
            last = self._last_run.get(task["name"], 0.0)
            if now - last >= task["interval_s"]:
                due.append(task)
        return due

    def tick(self) -> dict[str, bool]:
        """Run all due tasks once. Returns {task_name: success} for tasks that ran."""
        results: dict[str, bool] = {}
        for task in self.due_tasks():
            ok = self._run_task(task)
            self._last_run[task["name"]] = time.monotonic()
            results[task["name"]] = ok
        return results

    def run_once(self) -> dict[str, bool]:
        """Force-run all tasks once regardless of interval."""
        results: dict[str, bool] = {}
        for task in self.tasks:
            ok = self._run_task(task)
            self._last_run[task["name"]] = time.monotonic()
            results[task["name"]] = ok
        return results

    def start(self, poll_interval_s: int = 60) -> None:
        """Run scheduler loop. Blocks until KeyboardInterrupt."""
        _logger.info("start: AutomationScheduler running (%d tasks)", len(self.tasks))
        try:
            while True:
                results = self.tick()
                if results:
                    ran = sum(1 for ok in results.values() if ok)
                    ts = datetime.now().isoformat()
                    _logger.info("tick: %d/%d tasks succeeded at %s", ran, len(results), ts)
                time.sleep(poll_interval_s)
        except KeyboardInterrupt:
            _logger.info("start: scheduler stopped by user")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Cerberus automation scheduler")
    parser.add_argument("--start", action="store_true", help="Start scheduler loop")
    parser.add_argument("--run-once", action="store_true", help="Run all tasks once and exit")
    parser.add_argument("--poll", type=int, default=60, help="Poll interval in seconds")
    args = parser.parse_args()

    scheduler = AutomationScheduler()

    if args.run_once:
        results = scheduler.run_once()
        failed = [name for name, ok in results.items() if not ok]
        if failed:
            _logger.warning("run_once: failed tasks: %s", failed)
            return 1
        return 0

    if args.start:
        scheduler.start(poll_interval_s=args.poll)
        return 0

    _logger.info("Use --start or --run-once. Tasks: %d", len(scheduler.tasks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
