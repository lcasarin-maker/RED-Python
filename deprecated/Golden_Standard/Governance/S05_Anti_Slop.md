# S5: Anti-Slop — Zero Warnings, Quality Mandate

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_1/M1 (INTEGRIDAD TOTAL)
**Severity:** 🔴 CRITICAL

---

## Definition

**Every warning IS an error.** Zero tolerance. Code with warnings is debt.

Dead code or redundant logic moves to `deprecated/` after validation, not left in place.

---

## Why

Warnings are lies. They say "something is wrong here but it's fine." It's not fine.

---

## How to Apply

1. **Run linter/compiler:** Capture ALL warnings
2. **Fix every warning:** No exceptions
3. **Dead code?** Move to `deprecated/`, don't comment it out
4. **Redundant logic?** Delete or refactor, don't leave it

---

## Enforcement

- **PreCommit:** Blocks if warnings present
- **Audit:** `run_security_audit_12d.py` counts warnings as failures

---

## Related

- **S1:** Rigor (warnings block validation)
- **S8:** Debt Tax (max 50 lines to prevent debt accumulation)
