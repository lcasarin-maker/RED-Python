#!/usr/bin/env python3
"""
Deprecated compatibility wrapper for legacy promotion.

All promotion must go through protocol_cli.py so permissions, backup, audit,
and evidence logging remain under one control plane.
"""

from __future__ import annotations

import argparse
import subprocess
import sys


DEPRECATED_SAFE_WRAPPER = True


def main() -> int:
    parser = argparse.ArgumentParser(description="Deprecated promote wrapper")
    parser.add_argument("project", help="Registry project name")
    parser.add_argument("file", help="Relative protocol file")
    parser.add_argument("--apply", action="store_true", help="Apply promotion; default is dry-run")
    args = parser.parse_args()

    command = [
        sys.executable,
        "scripts/protocol_cli.py",
        "promote",
        "--project",
        args.project,
        "--file",
        args.file,
    ]
    if args.apply:
        command.append("--apply")

    print("[DEPRECATED] Delegating promotion to protocol_cli.py")
    result = subprocess.run(command)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
