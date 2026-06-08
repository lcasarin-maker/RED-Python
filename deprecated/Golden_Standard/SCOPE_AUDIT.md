# Scope Audit — What Should Be in GS vs Agent-Specific Files

**Date:** 2026-06-02 | **Issue:** Rules scattered across PROTOCOL_SYSTEM.md, GEMINI.md, CLAUDE.md, deprecated/

---

## FOUND: Universal Rules Currently NOT in GS

### Category 1: Dual-Session Awareness (GEMINI.md only)

**Location:** GEMINI.md lines 39-83
**Rule:** When multiple agents work on same repo, must document in HISTORIAL.md before destructive changes

**Assessment:** 🔴 **SHOULD BE IN GS** (applies to all agents)
- GEMINI.md line 46: "Dual-session risk: ALTO (v2.8.6 conflicted with Claude FASE 5)"
- GEMINI.md line 68: "Pre-destructive checklist"
- GEMINI.md line 117: "NO SILENT CHANGES — Gemini must document"

**Principle:** This is **LEVEL_2_Operation/M5** (Audit & Git) or **LEVEL_4_Guards/M2** (Mandatory Operatives)

**Action:** Create GS/Principles/LEVEL_2_Operation/M5_Audit_Git.md with:
- Single source of truth = HISTORIAL.md (not chat, not STATUS, not memory)
- Pre-destructive checklist (git status, git log, read HISTORIAL.md)
- Documentation obligation after each session
- Cross-agent awareness protocol

---

### Category 2: Pre-Destructive Checklist (AGENT.md + GEMINI.md)

**Location:** AGENT.md line 74; GEMINI.md lines 61-64
**Rule:** DOUBLE-KEY RULE: Any destructive operation requires isolated turn with human approval

**Assessment:** 🔴 **SHOULD BE IN GS** (applies to all agents)
- AGENT.md: "git reset --hard or destructive changes require human order"
- AGENT.md: "Destructive commands MUST be requested in isolated turn"
- GEMINI.md: "Never execute git destructive without explicit confirmation"

**Principle:** LEVEL_4_Guards/M2 (Mandatory Operatives) or M1 (Prohibitions)

**Action:** Add to GS/Principles/LEVEL_4_Guards/M1_Prohibitions.md:
```
## Destructive Operations Checklist

BEFORE any of these: git reset --hard, git rm, rm -rf, git rebase
1. Read HISTORIAL.md completely
2. Understand what other agents did
3. Ask human EXPLICITLY in isolated turn
4. Wait for approval
5. Document in HISTORIAL.md AFTER completion
```

---

### Category 3: Documentation Obligation (GEMINI.md only)

**Location:** GEMINI.md lines 89-130
**Rule:** Update STATUS.md + HISTORIAL.md + auto-commit after each session

**Assessment:** 🔴 **SHOULD BE IN GS** (applies to all agents)
- "When you finish your session, MUST update STATUS.md"
- "CAMPO 3: What you completed, CAMPO 6: Next steps"
- "Auto-commit if >3 files or >50 lines"
- "NEVER leave session without documenting"

**Principle:** LEVEL_2_Operation (M5) or LEVEL_5_TokenSaving (M1 Diagnostics)

**Action:** Create GS principle: "Session Closure Protocol"
```
END OF SESSION CHECKLIST:
- [ ] Updated HISTORIAL.md with today's work
- [ ] Updated STATUS.md CAMPO 3 (what done) + CAMPO 6 (next steps)
- [ ] Auto-committed if >3 files changed
- [ ] Left clear instructions for next agent
```

---

### Category 4: No Silent Changes (GEMINI.md)

**Location:** GEMINI.md lines 117-130
**Rule:** Leave no ambiguity; never leave incidents undocumented

**Assessment:** 🟡 **PARTIALLY IN GS** (mentioned in LEVEL_2, but needs explicit principle)
- LEVEL_2 says "Traceability, version control"
- But GEMINI.md is more explicit: "Don't terminate session without documentation"

**Principle:** LEVEL_1_Integrity (INTEGRIDAD TOTAL — code/decisions must be verifiable)

**Action:** Make explicit in LEVEL_1/M1: "All decisions, changes, and incidents must be traceable and documented. Undocumented work is unverifiable work."

---

### Category 5: System Mandates (S1-S9) Duplication

**Problem:** 
- PROTOCOL_SYSTEM.md has S1-S9 (appears universal)
- CLAUDE.md has S1-S9 (appears Claude-specific)
- Are they the same? Different? Overlapping?

**Status:** ⚠️ **NEEDS CLARIFICATION**

**Examples of S-mandates that appear in both:**
- S1 (Rigor): PROTOCOL_SYSTEM.md = 6D Angry Path; CLAUDE.md = "Ejecuto run_security_audit_12d.py"
- S5 (Anti-Slop): PROTOCOL_SYSTEM.md = "Zero warnings"; CLAUDE.md = same
- S7 (Anti-Shell): PROTOCOL_SYSTEM.md explicit; CLAUDE.md explicit
- S9 (Logging): Both mention structured logging

**Assessment:** 🔴 **CONFUSION** — Are S1-S9 universal (should be agent-agnostic in GS) or Claude-specific?

**Action:** Clarify governance:
- If S1-S9 are universal → Move to GS/Principles as formal system mandates
- If S1-S9 are tool-specific → Rename in CLAUDE.md to avoid confusion with potential GEMINI.md S1-S9

---

## MISSING FROM GS: Incident Prevention

**Found in GEMINI.md but NOT in GS:**
- Incident awareness (2026-05-17 revert incident)
- Why REGLA #0 exists
- Risk mitigation patterns

**Assessment:** 🔴 **Should be in GS** — This is learned from failure (LEVEL_1: CONTINUOUS IMPROVEMENT)

**Action:** Create:
- GS/Principles/LEVEL_1_Integrity/M1_Core_Principles.md with incident case studies
- Cross-link to GEMINI.md incident timeline as historical reference
- Principle: "Extract value from all failures and register as doctrine"

---

## SUMMARY TABLE

| Rule | Current Location | Should Be | Priority |
|------|------------------|-----------|----------|
| Dual-session awareness | GEMINI.md only | GS/Principles/LEVEL_2/M5 | 🔴 HIGH |
| Pre-destructive checklist | AGENT.md + GEMINI.md | GS/Principles/LEVEL_4/M1 | 🔴 HIGH |
| Documentation obligation | GEMINI.md only | GS/Principles/LEVEL_2/M5 | 🔴 HIGH |
| No silent changes | GEMINI.md only | GS/Principles/LEVEL_1/M1 | 🔴 HIGH |
| S1-S9 mandates | PROTOCOL_SYSTEM.md + CLAUDE.md | GS/Principles + clarify scope | 🟡 MEDIUM |
| Incident prevention | GEMINI.md (1 incident) | GS/Principles/LEVEL_1 | 🟡 MEDIUM |
| ChatGPT system prompt | deprecated/ | GS/Principles (universal rules only) | 🟡 MEDIUM |

---

## NEXT ACTIONS (Phase 2)

1. **Clarify S1-S9 governance:** Are they universal or Claude-specific?
2. **Migrate Dual-Session Rules:** GEMINI.md → GS/Principles/LEVEL_2/M5
3. **Migrate Pre-Destructive Protocol:** AGENT.md + GEMINI.md → GS/Principles/LEVEL_4
4. **Formalize Documentation Obligation:** Create explicit principle in GS
5. **Extract Incident Lessons:** GEMINI.md 2026-05-17 incident → GS/Principles/LEVEL_1 case study

---

## CRITICAL FINDING

**Problem:** Rules are **scattered** across:
- PROTOCOL_SYSTEM.md (universal?)
- AGENT.md (universal?)
- CLAUDE.md (Claude-specific)
- GEMINI.md (Gemini-specific + incident report)
- deprecated/ (legacy instructions)

**Solution:** GS should be the **single source of truth** for all universal rules. Agent-specific files (CLAUDE.md, GEMINI.md) should ONLY contain bindings (S1-S9 for Claude, equivalent for others), not rules.

