# Validation Debt System — CoderCerberus v0.5+

**Effective since:** 2026-06-05
**Purpose:** Remove audit false positives through formal debt tracking.

## Components

1. `satellite_validation_debt.py` - Formal debt registry
2. `validate_satellite_functional.py` - Validates endpoints, not just files
3. `postmortem_validation_analysis.py` - Systemic pattern analysis
4. `audit_d13_validation_debt.py` - Requires documented and remediated debt

## Control_Procesal - Use Case

**Problem:** The auditor marked APPROVED in Phase 1, but validation was ceremonial (files only).
**Result:** The server did not respond and the UI hung (discovered in Phase 2/3).
**Solution:** Async bootstrap + 26 functional tests (remediated in Phase 3).

**Recorded debt:** `validation_debt.json` with ID, severity=CRITICAL, remediation_date=2026-06-05

## D13 Rules (Improved Auditor)

- **D13-1:** No recorded debt = WARNING (recommend validation)
- **D13-2:** Registry ↔ validation_debt mismatch = WARNING
- **D13-3:** CRITICAL debt not remediated = ERROR (blocks approval)
- **D13-4:** No functional tests = WARNING

## Key Files

- `.protocol/validation_debt.json` - Debt store
- `REGISTRY.json[Control_Procesal].validation_debt` - Per-satellite metadata
- `scripts/satellite_validation_debt.py` - Registry API
- `scripts/postmortem_validation_analysis.py` - Automated analysis

**Status:** ACTIVE | **V0.5+**
