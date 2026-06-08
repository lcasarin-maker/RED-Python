#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_d13_validation_debt.py — Domain 13: Validation Debt Check
Ensures satellites have no unrecorded validation debts and require functional proof.
Part of the 12D audit validator; extends to D13 validation debt domain.
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.satellite_validation_debt import get_all_debts, register_validation_debt


class ValidationDebtChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_satellite_registry(self, registry_path: str) -> bool:
        """
        D13-1: Check REGISTRY.json for any satellites with APPROVED status
        but unreported validation debts.
        """
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to read REGISTRY: {e}")
            return False

        projects = registry.get("projects", [])
        all_debts = get_all_debts()
        debt_satellites = {d["satellite"] for d in all_debts["debts"]}

        for proj in projects:
            name = proj.get("name")
            audit_status = proj.get("audit_status", "")
            has_recorded_debt = name in debt_satellites
            has_registry_debt = "validation_debt" in proj

            # Check 1: If APPROVED, must have documented debt or clean bill of health
            if "APPROVED" in audit_status and not has_recorded_debt and not has_registry_debt:
                self.warnings.append(
                    f"[D13-1] {name}: Marked APPROVED but no validation debt recorded. "
                    f"Recommend functional validation before advancing."
                )

            # Check 2: If debt in registry but not in validation_debt.json, flag inconsistency
            if has_registry_debt and not has_recorded_debt:
                self.warnings.append(
                    f"[D13-2] {name}: Recorded in REGISTRY.validation_debt but not in validation_debt.json. "
                    f"Inconsistency detected."
                )

            # Check 3: Critical debts should block APPROVED status UNLESS remediated
            if has_recorded_debt:
                sat_debts = [d for d in all_debts["debts"] if d["satellite"] == name]
                critical_debts = [d for d in sat_debts if d["severity"] == "critical"]
                is_remediated = proj.get("validation_debt", {}).get("remediated", False)

                if critical_debts and "APPROVED" in audit_status and not is_remediated:
                    self.errors.append(
                        f"[D13-3] {name}: Has CRITICAL validation debts but marked APPROVED. "
                        f"Blocking approval until remediated."
                    )
                elif critical_debts and is_remediated:
                    self.warnings.append(
                        f"[D13-3] {name}: Has remediated critical debt (recorded {proj.get('validation_debt', {}).get('remediation_date')}). "
                        f"Status: APPROVED_WITH_REMEDIATION"
                    )

        return len(self.errors) == 0

    def _debt_already_recorded(self, satellite_name: str, debt_type: str) -> bool:
        """Idempotency guard: True if an open debt of this type already exists."""
        existing = [
            d for d in get_all_debts()["debts"]
            if d["satellite"] == satellite_name and d["type"] == debt_type
        ]
        return len(existing) > 0

    def check_functional_test_requirements(self, satellite_name: str, satellite_path: str) -> bool:
        """
        D13-4: Require evidence of functional testing before approval.
        When a satellite lacks functional test evidence, record the debt formally
        (item #2: each failing satellite must register its debt, not stay silent).
        """
        path = Path(satellite_path)

        # Check for tests/
        tests_dir = path / "tests"
        has_tests = tests_dir.exists() and any(tests_dir.glob("test_*.py"))

        # Check for evidence/ directory (screenshots, logs, etc.)
        evidence_dir = path / "evidence"
        has_evidence = evidence_dir.exists() and list(evidence_dir.glob("*"))

        # Check for specific functional test markers
        has_e2e_tests = any(path.glob("**/test_*e2e*.py")) or any(path.glob("**/test_*ui*.py"))

        if not has_tests:
            self.warnings.append(
                f"[D13-4] {satellite_name}: No tests/ directory found. "
                f"Functional testing evidence required before approval."
            )
            # Item #2: a satellite that fails validation must record its debt.
            if not self._debt_already_recorded(satellite_name, "functional"):
                register_validation_debt(
                    satellite=satellite_name,
                    debt_type="functional",
                    severity="high",
                    description="No functional test evidence found (tests/ absent). "
                    "Approval would be ceremonial, not empirical.",
                    evidence=[f"{satellite_path} (no tests/ directory)"],
                    remediation="Add functional test suite before declaring APPROVED.",
                )
                self.warnings.append(
                    f"[D13-4] {satellite_name}: Validation debt auto-recorded (functional gap)."
                )
        elif not has_e2e_tests:
            self.warnings.append(
                f"[D13-4] {satellite_name}: Has unit tests but no end-to-end/UI tests. "
                f"Recommend E2E coverage before functional approval."
            )

        return has_tests or has_evidence

    def print_report(self):
        """Print D13 validation debt check report."""
        print("\n" + "=" * 80)
        print("🔍 D13: VALIDATION DEBT CHECK")
        print("=" * 80)

        if self.errors:
            print(f"\n🔴 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validation debt checks passed")

        print("\n" + "=" * 80)

        return len(self.errors) == 0


def main():
    checker = ValidationDebtChecker()

    registry_path = _ROOT / ".protocol" / "metadata" / "REGISTRY.json"
    checker.check_satellite_registry(str(registry_path))

    # Example: Check Control_Procesal
    checker.check_functional_test_requirements(
        "Control_Procesal",
        "D:\\AI\\Control_Procesal"
    )

    passed = checker.print_report()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
