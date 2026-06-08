# S14: Zero-Trust — DOUBLE-KEY RULE

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_4/M1 (Prohibitions) + LEVEL_2/M5 (Audit_Git)
**Severity:** 🔴 CRITICAL

---

## Definition

**Destructive operations require isolated human approval.**

Any `git reset --hard`, `git revert`, `rm -rf`, or equivalent MUST be requested in a separate turn with explicit human confirmation.

---

## Why

One destructive op in a grouped command can wipe another agent's work. Multi-agent coordination requires atomic decision + action.

---

## Rules

1. **Destructive ops cannot be grouped** with other work
2. **Must ask in isolated turn:** "Can I execute [OP]?"
3. **Must wait for approval** before executing
4. **Must document result** in HISTORIAL.md immediately after

---

## Exceptions

None. This is the REGLA #0 from the 2026-05-17 incident.

---

## Related

- **S21:** Git Veto + Dual-Session (pre-destructive checklist)
- **LEVEL_2/M5:** Dual-Session Awareness (when to ask)
- **LEVEL_4/M1:** Prohibitions (what's blocked)
