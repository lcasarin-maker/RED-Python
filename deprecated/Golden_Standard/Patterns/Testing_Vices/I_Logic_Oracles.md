# VT-I: Logic & Oracles (VT-001..022)

**Source:** `deprecated/BIBLIOTECA_VICIOS_TESTING_EVALUACION.md` (Category I)
**Status:** ACTIVE | **Entries:** 22 | **Date:** 2026-06-02
**Focus:** Assertion sterility, hardcoded values, stubs, false oracles

---

## Catalog

| ID | Name | Symptom | Root Cause | Prevention |
|---|---|---|---|---|
| **VT-001** | Hardcoded Return | Returns expected value unconditionally | Optimization against single test input | Test general properties, not exact values |
| **VT-002** | Permanent Stub | Fake body passes | Missing implementation | Block active stubs in gatekeeper |
| **VT-003** | Response by Exact Input | Only passes exact test data | Memorization | Vary inputs |
| **VT-004** | Copy Expected | Code knows what test expects | Contaminated oracle | Separate test from solution |
| **VT-005** | Trivial Assert | Always true | Tautology | Demand demonstrable failure |
| **VT-006** | Test Without Assert | Runs without verifying | Missing oracle | Assertion mandatory |
| **VT-007** | Presence Not Correction | File exists but untested | Weak proxy | Validate effect |
| **VT-008** | Message Not Result | Search for "success" text | Indirect signal | Validate final state |
| **VT-009** | Tautology | Verify universal law | Useless predicate | Test must discriminate |
| **VT-010** | Implementation Test | Internal change, test passes | Wrong coupling | Test behavior, not internals |
| **VT-011** | Incorrect Expected | Test and code both wrong | False oracle | Verify specification independently |
| **VT-012** | Coverage Without Asserts | Execute but don't verify | Empty metric | Asserts required for credit |
| **VT-013** | Coverage by Percentage | Gamified metric | Wrong incentive | Assert quality, not count |
| **VT-014** | Circular Test | Auditor approves itself | Non-independent validator | External oracle |
| **VT-015** | Test Too Broad | Doesn't isolate failure | Low granularity | Focal tests |
| **VT-016** | Theatrical Text Assert | Text exists | Presence via action | Invoke mandate |
| **VT-017** | Hardcoded Evidence | Outcome always success | Predetermined result | Outcome from verification |
| **VT-018** | Fragile String Match | Message change breaks test | Brittle contract | Structured states |
| **VT-019** | Error Hash Valid | Unreadable appears as data | Encoded error as value | Explicit failure |
| **VT-020** | 100% as Target | Tests hunted | Inverted incentive | 100% only as consequence |
| **VT-021** | Regression Without Sentinel | Old bug reappears | Failure memory absent | Each bug leaves discriminant test |
| **VT-022** | Tautology & Theatrical Success | Useless asserts that always pass | Coverage gaming | Require boundary + adversarial assertions |

---

## Prevention Path

1. **Assume oracle is broken** → Validate independently
2. **Test must fail** → Demonstrable when logic breaks
3. **Separate test from solution** → No cross-contamination
4. **External oracle** → Truth outside tested code
5. **Boundary + adversary** → Edge cases + attack tests

---

## Related

- **S23:** Test Purity (no theater)
- **LEVEL_3/M1:** Regression Suite (test quality)
- **VC-004, VC-037:** False oracles in code generation

