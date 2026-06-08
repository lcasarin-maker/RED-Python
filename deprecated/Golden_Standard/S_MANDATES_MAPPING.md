# S1-S23 System Mandates — Mapping to GS/Principles

**Discovery:** PROTOCOL_SYSTEM.md contains S1-S23 (universal), not just S1-S9.
CLAUDE.md implements subset S1-S9, S17 (Claude-specific binding).

**This document:** Maps all S1-S23 to GS/Principles for universal accessibility.

---

## LEVEL 1: INTEGRITY (S1, S5, S9, S22, S23)

| S-Mandate | Title | Maps To | Status |
|-----------|-------|---------|--------|
| **S1** | 6D Angry Path (Rigor) | LEVEL_1/M1 Core Principles | ✅ INTEGRATED |
| **S5** | Anti-Slop (Quality) | LEVEL_1/M1 Core Principles | ✅ INTEGRATED |
| **S9** | Structured Logging (Observability) | LEVEL_1/M4 Errors_Secrets | 🔲 PENDING |
| **S22** | Code Purity (No Stubs) | LEVEL_1/M1 Core Principles | 🔲 PENDING |
| **S23** | Test Purity (No Theater) | LEVEL_1/M3 Angry_Path | 🔲 PENDING |

---

## LEVEL 2: OPERATION (S2, S10, S17, S21)

| S-Mandate | Title | Maps To | Status |
|-----------|-------|---------|--------|
| **S2** | Brain-First (SPEC.md) | LEVEL_2/M1 Fundamentals | 🔲 PENDING |
| **S10** | Code Lifecycle (deprecated/) | LEVEL_2/M5 Audit_Git | 🔲 PENDING |
| **S17** | Version Sync (Anti-Drift) | LEVEL_2/M5 Audit_Git | 🔲 PENDING |
| **S21** | Git Veto + Dual-Session | LEVEL_2/M5 Audit_Git | ✅ INTEGRATED |

---

## LEVEL 3: VALIDATION (Missing in S-mandates)

No direct S-mandate mapping. Covered by S1 (Angry Path) + test requirements.

| S-Mandate | Title | Maps To | Status |
|-----------|-------|---------|--------|
| *S1 subset* | Angry Path Testing | LEVEL_3/M2 Angry_Path_Testing | 🔲 PENDING |
| *S23 subset* | Test Purity | LEVEL_3/M1 Regression_Suite | 🔲 PENDING |

---

## LEVEL 4: GUARDS (S3, S4, S6, S7, S8, S14, S20, S21)

| S-Mandate | Title | Maps To | Status |
|-----------|-------|---------|--------|
| **S3** | Bio-Containment (Security) | LEVEL_4/M1 Prohibitions | ✅ INTEGRATED |
| **S4** | Modularity (Schemas) | LEVEL_4/M2 Mandatory_Operatives | 🔲 PENDING |
| **S6** | Large File Safety | LEVEL_4/M1 Prohibitions | 🔲 PENDING |
| **S7** | Anti-Shell (Edit Guards) | LEVEL_4/M1 Prohibitions | 🔲 PENDING |
| **S8** | Debt Tax (50-line limit) | LEVEL_4/M1 Prohibitions | 🔲 PENDING |
| **S14** | Zero-Trust (Double-Key Rule) | LEVEL_4/M1 Prohibitions | ✅ INTEGRATED |
| **S20** | Structured Error Logs | LEVEL_4/M1 Prohibitions | 🔲 PENDING |
| **S21** | Git Veto + Dual-Session | LEVEL_4/M1 Prohibitions | ✅ INTEGRATED |

---

## LEVEL 5: TOKEN SAVING (S18, S13)

| S-Mandate | Title | Maps To | Status |
|-----------|-------|---------|--------|
| **S13** | Prompt Caching | LEVEL_5/M1 Diagnostics | 🔲 PENDING |
| **S18** | Token Optimization (3 Leaks) | LEVEL_5/M2 Leaks_Solutions | 🔲 PENDING |

---

## Summary: S1-S23 Consolidation

**Total S-mandates:** 23
**Already integrated into GS:** 5 (S1, S3, S5, S14, S21)
**Need migration:** 18

**Migration Priority:**
1. **CRITICAL:** S2, S4, S6, S7, S8, S9 (operational + guards)
2. **HIGH:** S10, S17, S20, S22, S23 (operations + quality)
3. **MEDIUM:** S13, S18 (token optimization)

---

## Decision: How to Handle S1-S23 in GS?

**Option A: Integrate all S1-S23 as Principles (Recommended)**
- Pros: GS becomes single source of truth for ALL universal rules
- Cons: Makes GS heavier, blur between "principles" and "system mandates"
- Path: Add new sections in LEVEL_4 (Guards) for S1-S23 cross-reference

**Option B: Keep PROTOCOL_SYSTEM.md as authority, GS references it**
- Pros: Clear separation (PROTOCOL_SYSTEM = enforcement, GS = principles)
- Cons: Dual source of truth persists
- Path: GS links to PROTOCOL_SYSTEM.md line numbers

**Option C: Create GS/Governance/SYSTEM_MANDATES.md for S1-S23**
- Pros: Dedicated section, all mandates in one place
- Cons: Adds another file layer
- Path: GS/Governance/ mirrors PROTOCOL_SYSTEM.md structure

**RECOMMENDATION: Option C** (dedicated GS/Governance section)
- Keeps GS unified (all rules in one repo)
- Separate concerns (Principles ≠ Mandates)
- Easier for agents to reference

---

## Implementation Plan (Phase 2B)

1. ✅ Migrate S1, S3, S5, S14, S21 → done (in M1, M5)
2. Create GS/Governance/SYSTEM_MANDATES.md
3. Populate S2-S23 (in Governance section)
4. Update LEVEL_* modules to cross-link to Governance
5. Deprecate PROTOCOL_SYSTEM.md with redirect to GS/Governance

**Estimated effort:** 2-3 hours

---

## Critical Decisions Embedded Here

1. **S1-S23 are universal** (not agent-specific)
   - PROTOCOL_SYSTEM.md = authoritative source
   - CLAUDE.md = Claude binding (subset)

2. **Dual-Session Awareness is S21** (universal mandate)
   - Not Gemini-specific (though GEMINI.md documented it first)
   - Applies to ALL agents

3. **GS should centralize everything**
   - Single source of truth for all rules
   - Agents reference GS, not scattered files

