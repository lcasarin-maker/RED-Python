#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postmortem_validation_analysis.py v1.0 — Validation Debt Post-Mortem Analysis
Analyzes patterns in validation debts to identify systemic failures.
Generates recommendations for improving validation rules.
"""

from datetime import datetime
from pathlib import Path
from collections import defaultdict
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8
from scripts.satellite_validation_debt import get_all_debts

setup_windows_utf8()


def _analyze_severity_pattern(debts: list, analysis: dict):
    """Extract severity-based patterns."""
    severity_counts = defaultdict(int)
    for debt in debts:
        severity_counts[debt["severity"]] += 1

    critical_count = severity_counts.get("critical", 0)
    if critical_count > 0:
        analysis["patterns"].append({
            "name": "CRITICAL_DEBT_ACCUMULATION",
            "description": f"{critical_count} critical-severity validation debts found",
            "impact": "HIGH"
        })
        analysis["recommendations"].append({
            "priority": "IMMEDIATE",
            "action": "Review and remediate all critical debts before advancing satellites",
            "rationale": "Critical validation gaps indicate systematic audit failures"
        })


def _analyze_false_positive_pattern(debts: list, analysis: dict):
    """Extract false positive audit patterns."""
    false_positive_count = len([d for d in debts if d.get("falsely_approved_phase")])
    if false_positive_count > 0:
        analysis["patterns"].append({
            "name": "FALSE_POSITIVE_AUDIT_DECLARATIONS",
            "description": f"{false_positive_count} false positives",
            "impact": "HIGH"
        })
        analysis["recommendations"].append({
            "priority": "IMMEDIATE",
            "action": "Require empirical proof before declaring APPROVED",
            "rationale": "Validation is ceremonial (files) not empirical (functionality)"
        })


def _analyze_type_patterns(debts: list, analysis: dict):
    """Extract type-based patterns."""
    type_counts = defaultdict(int)
    for debt in debts:
        type_counts[debt["type"]] += 1

    for debt_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 1:
            analysis["patterns"].append({
                "name": f"REPEATED_{debt_type.upper()}_FAILURES",
                "description": f"{count} {debt_type} validation debts",
                "impact": "MEDIUM" if count == 2 else "HIGH"
            })


def _build_satellite_risk_map(debts: list, analysis: dict):
    """Build per-satellite risk map."""
    satellite_debts = defaultdict(list)
    for debt in debts:
        satellite_debts[debt["satellite"]].append(debt)

    for satellite, sat_debts in satellite_debts.items():
        critical_count = len([d for d in sat_debts if d["severity"] == "critical"])
        high_count = len([d for d in sat_debts if d["severity"] == "high"])
        risk_level = "CRITICAL" if critical_count > 0 else ("HIGH" if high_count > 0 else "MEDIUM")

        analysis["satellite_risk_map"][satellite] = {
            "total_debts": len(sat_debts),
            "risk_level": risk_level,
            "critical": critical_count,
            "high": high_count
        }


def _analyze_functional_patterns(debts: list, analysis: dict):
    """Extract functional vs structural patterns."""
    functional_debts = len([d for d in debts if d["type"] == "functional"])
    if functional_debts > len(debts) * 0.5:
        analysis["patterns"].append({
            "name": "PREDOMINANT_FUNCTIONAL_FAILURES",
            "description": f"{functional_debts}/{len(debts)} debts are functional",
            "impact": "HIGH"
        })
        analysis["recommendations"].append({
            "priority": "HIGH",
            "action": "Implement mandatory functional test suite for each satellite",
            "rationale": "Structural validation alone is insufficient"
        })


def analyze_validation_debts() -> dict:
    """Analyze all validation debts for patterns."""
    db = get_all_debts()
    debts = db["debts"]

    if not debts:
        return {
            "finding": "No validation debts recorded yet",
            "patterns": [],
            "recommendations": []
        }

    analysis = {
        "total_debts": len(debts),
        "timestamp": datetime.utcnow().isoformat(),
        "patterns": [],
        "recommendations": [],
        "satellite_risk_map": {}
    }

    _analyze_severity_pattern(debts, analysis)
    _analyze_false_positive_pattern(debts, analysis)
    _analyze_type_patterns(debts, analysis)
    _build_satellite_risk_map(debts, analysis)
    _analyze_functional_patterns(debts, analysis)

    if analysis["patterns"]:
        analysis["recommendations"].append({
            "priority": "SYSTEMIC",
            "action": "Implement 3-tier validation: Structure + Functional + Empirical",
            "rationale": "Current single-tier validation allows false positives"
        })

    return analysis


def print_postmortem_report():
    """Print post-mortem analysis report."""
    try:
        analysis = analyze_validation_debts()
    except Exception as e:
        print(f"ERROR: Failed to analyze validation debts: {e}")
        sys.exit(1)

    print("\n" + "=" * 90)
    print("📊 VALIDATION DEBT POST-MORTEM ANALYSIS")
    print("=" * 90)

    if analysis.get("finding"):
        print(f"\n✓ {analysis['finding']}")
        return

    print("\n📈 Statistics:")
    print(f"   Total Debts: {analysis['total_debts']}")
    print(f"   Satellites at Risk: {len(analysis['satellite_risk_map'])}")

    if analysis["satellite_risk_map"]:
        print("\n🗺️  Satellite Risk Map:")
        for satellite, risk_info in sorted(analysis["satellite_risk_map"].items()):
            print(f"   {satellite}: {risk_info['risk_level']} ({risk_info['total_debts']} debts, "
                  f"{risk_info['critical']} critical, {risk_info['high']} high)")

    if analysis["patterns"]:
        print(f"\n🔍 Patterns Identified ({len(analysis['patterns'])}):")
        for pattern in analysis["patterns"]:
            print(f"\n   {pattern['name']}")
            print(f"      Description: {pattern['description']}")
            print(f"      Impact: {pattern['impact']}")

    if analysis["recommendations"]:
        print(f"\n💡 Recommendations ({len(analysis['recommendations'])}):")
        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"\n   {i}. [{rec['priority']}] {rec['action']}")
            print(f"      Rationale: {rec['rationale']}")

    print("\n" + "=" * 90)

    return analysis


if __name__ == "__main__":
    print_postmortem_report()
