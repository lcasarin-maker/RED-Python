#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_protocol_adoption.py — CoderCerberus P5.1
Audits each active project in REGISTRY.json for REAL protocol adoption.

Checks per project (H/A/T):
  H — .git/hooks/pre-commit exists and is executable
  A — scripts/audit_10d.py present (auditor installed)
  T — tests/ directory has at least one test_*.py or automation_test_*.py

Updates REGISTRY.json: adoption_verified (bool) + adoption_details per project.

Usage:
  python scripts/verify_protocol_adoption.py          # report + update registry
  python scripts/verify_protocol_adoption.py --check  # report only, no write, exit 1 if any fail
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = _ROOT / ".protocol" / "metadata" / "REGISTRY.json"


def _has_test_files(tests_dir: Path) -> bool:
    """Return True if tests_dir contains at least one test_*.py or automation_test_*.py."""
    if not tests_dir.is_dir():
        return False
    return any(
        f.name.startswith("test_") or f.name.startswith("automation_test_")
        for f in tests_dir.glob("*.py")
    )


def _check_project(project: dict) -> dict:
    """Run 3 adoption checks for one project. Returns dict with bool fields."""
    path = Path(project["path"])
    if not path.exists():
        return {"hook": False, "auditor": False, "tests": False, "path_missing": True}
    try:
        hook = path / ".git" / "hooks" / "pre-commit"
        hook_ok = hook.exists() and os.access(hook, os.X_OK)
        # Check standard path OR subtree prefix path for the protocol core auditor
        auditor_ok = False
        if (path / "scripts" / "audit_10d.py").exists():
            auditor_ok = True
        elif (path / ".protocol-core" / "scripts" / "audit_10d.py").exists():
            auditor_ok = True
        tests_ok = _has_test_files(path / "tests")
        return {"hook": hook_ok, "auditor": auditor_ok, "tests": tests_ok, "path_missing": False}
    except OSError as e:
        import logging
        logging.debug("_check_project failed for %s: %s", project.get("name"), e)
        return {"hook": False, "auditor": False, "tests": False, "path_missing": False}


def _is_adopted(r: dict) -> bool:
    """True only when all 3 adoption checks pass and the project path exists."""
    if r.get("path_missing", False):
        return False
    return all([r["hook"], r["auditor"], r["tests"]])


def run(write: bool = True) -> int:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    now = datetime.now(tz=timezone.utc).isoformat()
    rows = []
    adopted = 0

    active = [p for p in data["projects"] if p.get("status") not in ("archived", "inactive")]

    for proj in active:
        r = _check_project(proj)
        ok = _is_adopted(r)
        if ok:
            adopted += 1
        rows.append((proj["name"], r, ok))
        proj["adoption_verified"] = ok
        proj["adoption_verified_date"] = now
        proj["adoption_details"] = {
            "hook_installed": r["hook"],
            "auditor_present": r["auditor"],
            "tests_present": r["tests"],
            "path_exists": not r.get("path_missing", False),
        }

    if write:
        data["last_updated"] = now
        REGISTRY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Report ────────────────────────────────────────────────
    total = len(active)
    pct = (adopted / total * 100) if total else 0
    print(f"\n{'='*62}")
    print(f"  PROTOCOL ADOPTION AUDIT — {now[:10]}")
    print(f"  Legend: H=hook  A=auditor  T=tests  x=pass  -=missing")
    print(f"{'='*62}")
    for name, r, ok in rows:
        missing = r.get("path_missing", False)
        tag = "PATH MISSING" if missing else ("OK  " if ok else "FAIL")
        h = "H" if r["hook"] else "-"
        a = "A" if r["auditor"] else "-"
        t = "T" if r["tests"] else "-"
        print(f"  [{tag}] [{h}{a}{t}]  {name}")
    print(f"{'='*62}")
    print(f"  Adoption: {adopted}/{total} active projects ({pct:.0f}%)")
    outcome = "ALL ADOPTED" if adopted == total else f"{total - adopted} NOT ADOPTED"
    print(f"  Status:   {outcome}")
    print(f"{'='*62}\n")

    return 0 if adopted == total else 1


if __name__ == "__main__":
    check_only = "--check" in sys.argv
    strict = "--strict" in sys.argv
    rc = run(write=not check_only)
    sys.exit(rc if strict else 0)
