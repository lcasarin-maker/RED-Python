# VT-III: Flow & Discovery (VT-035..115)

**Source:** `deprecated/BIBLIOTECA_VICIOS_TESTING_EVALUACION.md` (Categories III-VI)
**Status:** ACTIVE | **Entries:** 81 | **Date:** 2026-06-02
**Focus:** Test evasion, coverage theater, framework debt, governance

---

## Sub-Categories

### **III-A: Test Evasion & Coverage (VT-035..074)**
Xfail, skip, impossible branches, order dependencies, temporal failures, absorbed exceptions.

**Key Vices:** VT-035 (xfail permanent), VT-036 (skip permanent), VT-040 (exception absorbed), VT-045 (happy path only), VT-051 (CI informational), VT-057 (skip forever), VT-074 (observability untested)

**Prevention:** No xfail/skip in healthy verdict; all tests active + independent; CI blocks on critical failures; logs discriminate breakage.

### **III-B: Environment & Portability (VT-076..080)**
System-dependent, timeout deception, machine-local, sandbox fiction, physical path coupling.

**Key Vices:** VT-076 (system dependency), VT-078 (local-only), VT-080 (hardcoded paths)

**Prevention:** Matrix of environments; parameterized resources; absolute → relative paths.

### **III-C: Validation Integrity (VT-081..104)**
Author tests own code, review without tests, hardcoded expected, approval fiction, golden file complacency.

**Key Vices:** VT-081 (author bias), VT-083 (expected from implementation), VT-084 (approval hardcoded), VT-085 (obsolete golden), VT-093 (docstrings as quality), VT-104 (warnings not scored)

**Prevention:** Independent review + tests; expected from specification; approval evidence-based; warnings count as fail.

### **III-D: Governance & Nomenclature (VT-105..115)**
Missing hooks, unchecked exclusions, incomplete stack, naming drift, test discovery gaps, mutation insensitivity.

**Key Vices:** VT-105 (no hook test), VT-108 (name-implementation drift), VT-113 (no mutation validation), VT-115 (discovery incomplete)

**Prevention:** Hook verification in startup; name == behavior; mutation testing mandatory; discoverable all tests.

---

## Critical Cluster

**VT-070..075 (Validation Preconditions)**
- Setup validation absent
- Handoff non-resumable
- Rollback undocumented
- Compatibility not sampled
- Observability not tested
- Discovery incomplete

**Principle:** Every exit point must prove reanudability; every change must sample historical consumers; every failure must produce diagnostic logs.

---

## Related

- **S23:** Test Purity (no theater)
- **LEVEL_3:** Validation (testing gates)
- **VC-118:** Zombie Compat (wrappers hide real breaks)

