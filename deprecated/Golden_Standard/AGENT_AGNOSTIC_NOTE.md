# Agent-Agnostic vs Agent-Specific Binding

**Date:** 2026-06-02 | **Clarification:** What lives in GS vs what lives in CLAUDE.md

---

## RULE: GS is Universal; CLAUDE.md is Claude-Only

### Golden Standard (Agent-Agnostic)
**Contains:** Principles, Patterns, Vices that apply to ANY agent (Claude, Gemini, ChatGPT, etc.)

✅ **Example:** VC-118 (Zombie Compatibility Theater) lives in GS
- Reason: Replace = Delete + Create is a universal code pattern
- Applies to: All agents that touch code replacement

✅ **Example:** LEVEL_1 (Integrity) lives in GS
- Reason: INTEGRIDAD TOTAL is agent-agnostic
- Applies to: All agents

### CLAUDE.md (Claude-Specific Binding)
**Contains:** Mandatos (S1-S9, S17, B1-B11) that are specific to Claude's tooling and constraints

❌ **Example:** S6 (Large File Safety) is Claude-specific
- Reason: Edit <50 lines, Write >200 lines — Claude-specific tool constraints
- Does NOT apply to: Gemini, ChatGPT

❌ **Example:** S19 (Anti-Zombie-Compat) as a CLAUDE-SPECIFIC PROMISE
- Reason: It's in CLAUDE.md's "PROMESA EXPLICITA" section, not the official S1-S9, S17 mandate table
- Does NOT apply to: Other agents (though they should follow VC-118)

---

## The Mistake Found

**Error:** VC-118 was sourced from CLAUDE.md's S19 reference, making it seem agent-specific.

**Correction:** VC-118 is UNIVERSAL (lives in GS/Patterns). S19 is Claude's explicit commitment to enforce it.

---

## Distinction

| Item | Location | Authority | Scope |
|------|----------|-----------|-------|
| **VC-118** | GS/Patterns/Coding_Vices/VIII | Universal principle | All agents |
| **LEVEL_4/M1** | GS/Principles/LEVEL_4_Guards | Universal principle | All agents |
| **S19 promise** | CLAUDE.md line 145 | Claude binding only | Claude only |

---

## Implication for Mandates

**Rule:** If a mandate should apply to all agents, it MUST be in GS as a Principle or Vice, NOT in CLAUDE.md.

If it's agent-specific (like S6 Edit constraints), it stays in CLAUDE.md.

**Current Status:**
- ✅ VC-118 is correctly in GS (universal)
- ✅ LEVEL_4 is correctly in GS (universal)
- ⚠️ S19 is correctly in CLAUDE.md (Claude-specific promise to enforce universal rule)

---

## Next Actions

1. **Remove any reference to "S19" as a universal mandate** — It's Claude's promise, not a system mandate
2. **Keep VC-118 in GS as authoritative** — It's the universal principle
3. **Ensure all agent-agnostic rules live in GS** — Check NORMALIZATION_MANDATE.md for compliance
4. **Document this distinction in Cerberus/README.md** — Clarify GS vs CLAUDE.md scope for future agents

