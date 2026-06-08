# Testing Vices (VT) — Complete Catalog

**Source:** `deprecated/BIBLIOTECA_VICIOS_TESTING_EVALUACION.md` (integrated + deduplicated)
**Status:** ACTIVE | **Total:** 115 entries | **Categories:** 3

---

## Structure

| Category | Range | Count | Focus | File |
|----------|-------|-------|-------|------|
| **I: Logic & Oracles** | VT-001..022 | 22 | Assertion sterility (hardcoded, stubs, tautologies) | `I_Logic_Oracles.md` |
| **II: Simulation & Isolation** | VT-023..034 | 12 | False mocks & incomplete fakes | `II_Simulation.md` |
| **III: Flow & Discovery** | VT-035..115 | 81 | Test evasion, coverage theater, framework debt | `III_Flow_Discovery.md` |

---

## Cross-Domain Links

These VTs correlate to Coding Vices (VC) and Tokenomics (TK):

- **Mock Complacency** (VT-023, 024, 033) → See VC-118 (Zombie Compat)
- **False Oracles** (VT-004, 014, 083) → See VC-015, VC-037 (Epistemology)
- **Observability Failures** (VT-074, 087) → See VC-085, TK-026
- **Coverage Theater** (VT-020, 022, 112) → See VC-052 (Context Rot)
- **Stack Incompleteness** (VT-107, 109) → See VC-106 (Setup Phantom)

---

## Reading Path

**Foundation:**
1. `I_Logic_Oracles.md` — What makes assertions fail

**Defensive:**
2. `II_Simulation.md` — Why mocks deceive
3. `III_Flow_Discovery.md` — Coverage evasion patterns (Largest, read with intention)

---

## Format

Each VT entry:

```
| VT-NNN | Name | Symptom | Root Cause | Principle |
```

---

## Deduplication

See DEDUP_LOG.yaml:
- VT-023 (Mock Complacency) is authority for simulation theater
- VT-074 (Observability) links to VC-085, TK-026
- VT-001..022 (Oracles) are authoritative; VC entries reference back

---

## Appendices

None (see Coding_Vices/APPENDICES.md for 4-phase machine and escalation matrix).
