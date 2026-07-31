#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural audit for red_python (SP-006).

Checks that the canonical Golden Standard CORE structure is present.
Dependency-free on purpose: it must run in a bare checkout.

Exit 0 = the structure holds. Exit 1 = at least one violation.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = ('README.md', 'SPEC.md', 'HANDOFF.md', 'DECISIONS.md', '.agents/AGENTS.md', 'tasks/README.md', 'audit/AUDIT_TRAIL.md', 'audit/README.md', 'scripts/audit.py',)
REQUIRED_DIRECTORIES = ('tasks/backlog', 'tasks/active', 'tasks/blocked', 'tasks/review', 'tasks/done', 'audit/sessions', 'tests', 'docs',)


def find_violations(root: Path) -> list[str]:
    """Return one English finding per missing profile item."""
    findings = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            findings.append(f"Missing file: {rel}")
    for rel in REQUIRED_DIRECTORIES:
        if not (root / rel).is_dir():
            findings.append(f"Missing directory: {rel}/")
    if (root / ".protocol-core").exists():
        findings.append("Vendored core present: .protocol-core/")
    return findings


def main() -> int:
    """Report every structural violation and exit 1 when any exists."""
    findings = find_violations(ROOT)
    if not findings:
        print("[audit] Canonical structure OK.")
        return 0
    print(f"[audit] {len(findings)} violation(s):", file=sys.stderr)
    for finding in findings:
        print(f"  - {finding}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
