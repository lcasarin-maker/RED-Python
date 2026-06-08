# PI-009: Deuda Cero Antes de Avanzar

**Source:** Cerberus Sprint 5 | **Project:** Core Protocol | **Date:** 2026-05-20

---

## Learning

All warnings, findings, and tech debt that are not blocking must be treated as operational errors until they are fixed or explicitly blocked.

The system accumulates "non-blocking noise" (recommendations, TODOs, lint) that eventually becomes systemic debt.

### Observation

In Gate APPROVED, the system was printing non-blocking recommendations for every domain, even when there were no FAILs. This:
- Diluted signal (noise reduction needed)
- Created false sense of progress (warnings ≠ action)
- Allowed drift (small issues compounded)

### Resolution

Modified gate APPROVED to suppress [RECOMENDACIONES POR DOMINIO] output when there are no FAIL signals. Now recommendations only appear when a domain has actual failures, guiding the fix.

**Implementation:**
- Refactored `_print_recommendations()` (C901 compliance)
- Failing-first test validates both branches
- No-warning baseline maintained

---

## Status

- **Current:** IMPLEMENTED
- **Scope:** Operational (gate behavior)
- **Falsifiable:** Yes (test: gate output when FAIL=0 vs FAIL>0)

---

## Promotion Path

→ Candidate for **VC-009: Deuda Pendiente Tolerance**
→ Maps to **GS/Principles/LEVEL_1: Integridad (ZERO-WARNING)**
