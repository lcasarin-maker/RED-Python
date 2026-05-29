#!/usr/bin/env python3
"""
Deprecated compatibility wrapper for the removed auto-commit workflow.

Automatic commits hid failures and bypassed evidence review. This wrapper is
kept only so old hooks or project scripts fail closed with a clear migration
path.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEPRECATED_SAFE_WRAPPER = True


def changed_summary() -> tuple[int, str]:
    result = subprocess.run(
        ["git", "diff", "--shortstat"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        cwd=Path.cwd(),
    )
    summary = result.stdout.strip() or "no unstaged diff"
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        cwd=Path.cwd(),
    )
    changed = len([line for line in status.stdout.splitlines() if line.strip()])
    return changed, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Deprecated auto-commit wrapper")
    parser.add_argument("--dry-run", action="store_true", help="Print status and exit 0")
    args = parser.parse_args()

    changed, summary = changed_summary()
    print("[DEPRECATED] Automatic commits are disabled by protocol policy.")
    print(f"[STATUS] changed_paths={changed}; diff={summary}")
    print("[NEXT] Run protocol_cli.py check, then create an explicit human-reviewed commit.")
    return 0 if args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())
