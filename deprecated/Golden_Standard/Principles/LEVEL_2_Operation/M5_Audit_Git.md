# M5: Audit & Git — Multi-Agent Coordination

**Source:** Integrated from GEMINI.md (incident-driven) + AGENT.md (core protocol)
**Status:** ACTIVE (Phase 2) | **Date:** 2026-06-02 | **Authority:** B10, S2

---

## Single Source of Truth: HISTORIAL.md

**Rule:** HISTORIAL.md is the ONLY authoritative record of what all agents have done.

- Not STATUS.md (too volatile)
- Not chat (ephemeral)
- Not .agent_state.json (technical handoff only)
- **ONLY: HISTORIAL.md**

Every agent must:
1. **READ** HISTORIAL.md COMPLETELY at session start (not just last 3 entries)
2. **UNDERSTAND** what other agents changed
3. **DOCUMENT** their work in HISTORIAL.md before closing session
4. **NEVER assume** it's safe to revert another agent's work

---

## Pre-Destructive Checklist (DOUBLE-KEY RULE)

**Before ANY destructive operation** (`git reset --hard`, `git rm`, `rm -rf`, `git rebase`):

1. ✅ Read HISTORIAL.md COMPLETELY
2. ✅ Run `git status` + `git log --oneline -10`
3. ✅ Identify what other agents did
4. ✅ Ask human EXPLICITLY in isolated turn: "Can I [DESTRUCTIVE_OP]?"
5. ✅ WAIT for explicit approval
6. ✅ Document in HISTORIAL.md AFTER execution

**PROHIBITIONS:**
- ❌ NEVER execute destructive ops in grouped commands with other work
- ❌ NEVER assume it's safe based on "my territory"
- ❌ NEVER skip human confirmation, even if confident

**Why:** Multi-agent work on same repo = HIGH conflict risk (GEMINI.md 2026-05-17 incident)

---

## Session Closure Protocol (Mandatory)

When terminating a session, MUST execute this checklist:

1. **Update HISTORIAL.md:**
   ```markdown
   ## SESIÓN [FECHA] — [AGENT_NAME]
   
   **Tarea:** [What you completed]
   **Cambios:** [Files modified, commits made]
   **Estado:** ✅ COMPLETO / ⚠️ EN PROGRESO / ❌ BLOQUEADO
   **Próximo agente:** [Who should continue, what to do next]
   ```

2. **Update STATUS.md:**
   - CAMPO 3: What you completed exactly
   - CAMPO 6: Next step for next agent (CLEAR instructions)
   - CAMPO 7: Technical details if any

3. **Auto-commit if >3 files changed:**
   ```bash
   git add [specific files]
   git commit -m "Brief description"
   ```

4. **Never leave ambiguity:** Next agent must read HISTORIAL.md and know exactly what you did and what's next.

---

## Dual-Agent Conflict Pattern

If you find changes from another agent on files you're about to modify:

```
"He visto que [AGENT] hizo [CAMBIOS] en [FECHA].
¿Puedo proceder con [MI_TAREA]?
¿Hay conflictos potenciales?"

→ WAIT for explicit approval before touching those files
```

---

## Related Principles

- **LEVEL_1/M1:** INTEGRIDAD TOTAL (code/decisions must be verifiable)
- **LEVEL_4/M2:** Mandatory Operatives (ask before destructive ops)
- **TK-008:** Memory Segregation (checkpoint state properly)

---

## Incident Case Study

**2026-05-17 — Gemini Revert Incident**
- Gemini executed `git reset --hard` without documenting in HISTORIAL.md
- Lost Claude's changes (README.md, CONTRIBUTING.md, .secrets/)
- Lesson: REGLA #0 exists because of this. Dual-session awareness is CRITICAL.
- Fix: Pre-destructive checklist + mandatory HISTORIAL.md documentation

**Prevention:** This protocol prevents repeat incidents.

---

## Next Steps

- [ ] All agents follow Session Closure Protocol
- [ ] HISTORIAL.md read completely at session start
- [ ] Pre-destructive checklist executed before any `git` destructive op

