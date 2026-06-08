#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
satellite_validation_debt.py v1.0 — Satellite Validation Debt Registry
Records false positives and functional risks in satellite audits.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()

VALIDATION_DEBT_DB = _ROOT / ".protocol" / "validation_debt.json"


def _ensure_debt_db_exists():
    """Initialize validation debt database if missing."""
    if VALIDATION_DEBT_DB.exists():
        return

    debt_db = {
        "version": "1.0",
        "debts": [],
        "summary": {
            "total_debts": 0,
            "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "by_type": {}
        }
    }

    VALIDATION_DEBT_DB.parent.mkdir(parents=True, exist_ok=True)
    with VALIDATION_DEBT_DB.open("w", encoding="utf-8") as f:
        json.dump(debt_db, f, indent=2, ensure_ascii=False)


def register_validation_debt(
    satellite: str,
    debt_type: str,
    severity: str,
    description: str,
    evidence: list[str],
    remediation: Optional[str] = None,
    falsely_approved_phase: Optional[str] = None
):
    """Register a validation debt: a risk that was missed or falsely approved.

    Used by: audit_d13_validation_debt.py (registers failures),
             postmortem_validation_analysis.py (via get_all_debts),
             bootstrap scripts (historical debt seeding).

    Args:
        satellite: Project name (e.g., "Control_Procesal")
        debt_type: Type of failure ("functional", "structural", "performance", "security")
        severity: "critical", "high", "medium", "low"
        description: What went wrong
        evidence: List of proof files/logs
        remediation: How it was fixed or can be fixed
        falsely_approved_phase: Which audit phase falsely approved this
    """
    _ensure_debt_db_exists()

    try:
        with VALIDATION_DEBT_DB.open("r", encoding="utf-8") as f:
            db = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Validation debt database is corrupted: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"ERROR: Cannot read validation debt database: {e}")
        sys.exit(1)

    debt_record = {
        "id": f"{satellite}_{int(datetime.utcnow().timestamp())}",
        "satellite": satellite,
        "type": debt_type,
        "severity": severity,
        "description": description,
        "evidence": evidence,
        "remediation": remediation,
        "falsely_approved_phase": falsely_approved_phase,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "RECORDED"
    }

    db["debts"].append(debt_record)
    db["summary"]["total_debts"] = len(db["debts"])

    # Update severity count
    db["summary"]["by_severity"][severity] = db["summary"]["by_severity"].get(severity, 0) + 1

    # Update type count
    db["summary"]["by_type"][debt_type] = db["summary"]["by_type"].get(debt_type, 0) + 1

    try:
        with VALIDATION_DEBT_DB.open("w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"ERROR: Cannot write to validation debt database: {e}")
        sys.exit(1)

    return debt_record["id"]


def get_all_debts() -> dict:
    """Get all validation debts."""
    _ensure_debt_db_exists()

    with VALIDATION_DEBT_DB.open("r", encoding="utf-8") as f:
        return json.load(f)


def print_debt_report():
    """Print validation debt report."""
    db = get_all_debts()

    print("\n" + "=" * 80)
    print("📋 SATELLITE VALIDATION DEBT REPORT")
    print("=" * 80)

    summary = db["summary"]
    print("\n📊 Summary:")
    print(f"   Total Debts: {summary['total_debts']}")
    print(f"   By Severity: {summary['by_severity']}")
    print(f"   By Type: {summary['by_type']}")

    if db["debts"]:
        print("\n🔴 Debts (by satellite):")
        by_satellite = {}
        for debt in db["debts"]:
            sat = debt["satellite"]
            if sat not in by_satellite:
                by_satellite[sat] = []
            by_satellite[sat].append(debt)

        for sat, debts in sorted(by_satellite.items()):
            print(f"\n   {sat}: {len(debts)} debt(s)")
            for debt in debts:
                print(f"      [{debt['severity'].upper()}] {debt['type']}: {debt['description']}")
                if debt.get("falsely_approved_phase"):
                    print(f"         ⚠️  Falsely approved in: {debt['falsely_approved_phase']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_debt_report()
