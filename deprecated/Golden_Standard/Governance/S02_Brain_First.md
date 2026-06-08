# S2: Brain-First — SPEC.md Authority

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_2/M1 (Fundamentals)
**Severity:** 🔴 CRITICAL

---

## Definition

**SPEC.md is the only "Brain"** — the single source of truth for architecture, assumptions, and state.

Prohibited: Mutating code without updating SPEC.md first. No divergence between memory (what agent thinks) and truth (what SPEC says).

---

## Why

Agents hallucinate. An agent edits code based on outdated assumptions. SPEC.md is the checkpoint that prevents context drift.

---

## How to Apply

**Before any code change:**
1. Read SPEC.md (lines 1-50 minimum)
2. Verify your assumptions match SPEC.md
3. If they don't, STOP
4. Update SPEC.md FIRST with corrected assumptions
5. THEN code

**Pattern:**
```
Bad: Edit code, then assume changes are reflected in everyone's mental model
Good: Update SPEC.md, then code, then assume SPEC.md is source of truth
```

---

## Whitelist Strict

Any file not in SPEC.md whitelist = Zombie. Blocks commit.

---

## Exceptions

None. SPEC.md is non-negotiable.

---

## Related

- **LEVEL_2/M1:** Startup ritual (read SPEC first)
- **S17:** Version Sync (SPEC.md must match reality)
