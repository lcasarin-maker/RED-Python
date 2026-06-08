# S1: 6D Angry Path — Rigor Validation

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_1/M1 (INTEGRIDAD TOTAL)
**Severity:** 🔴 CRITICAL

---

## Definition

**No task closes without 100% score on `scripts/run_security_audit_12d.py`** (10-domain forensic gatekeeper).

Angry Path: If code runs but lacks robust `try/except` or type validation, the task is a security failure.

---

## Why

Code that appears to work but lacks defensive handling is unverifiable code. An agent claiming success without proof is committing fraud on the evidence trail.

**Reference:** LEVEL_1/M1 (INTEGRIDAD TOTAL) — "Code is not good unless verifiable"

---

## How to Apply

1. **Before declaring code complete**, run:
   ```bash
   python scripts/run_security_audit_12d.py
   ```

2. **Require 100% score** — do not settle for 80%, 90%, or "close enough"

3. **Angry Path test:** For each code block, ask:
   - What if input is `NULL`?
   - What if DB fails?
   - What if file doesn't exist?
   - What if permission denied?
   - What if type mismatch?
   → Each scenario must have a handler

4. **Logging mandatory:** Every error case must log before returning

---

## Enforcement

- **Blocker:** `run_security_audit_12d.py` gates commit
- **PreCommit:** Blocks if score < 100%
- **Agent responsibility:** Must run audit before claiming complete

---

## Exceptions

None. 100% is non-negotiable. If audit fails, fix and re-run.

---

## Related

- **S3:** Bio-Containment (where validation happens)
- **S5:** Anti-Slop (zero warnings = zero debt)
- **S20:** Structured Error Logs (what audit checks)
- **LEVEL_1/M3:** Angry Path (adversarial testing)

