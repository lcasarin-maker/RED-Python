# S21: Git Veto & Dual-Session Awareness

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_2/M5 (Audit_Git) + LEVEL_4/M1 (Prohibitions)
**Severity:** 🔴 CRITICAL

---

## Definition

Destructive `git` operations require **explicit human approval** (S14).

**Dual-Session Awareness:** Before editing shared files, verify state and recent commits via `git status` + `git log`. If other agents changed files, analyze impact before committing.

---

## Why

Multiple agents on same repo = conflict risk. One agent's change can break another's work. HISTORIAL.md is single source of truth.

---

## Pre-Destructive Checklist

1. **Read HISTORIAL.md COMPLETELY** (not just last 3 entries)
2. **Run `git status` + `git log --oneline -10`**
3. **Identify what other agents did**
4. **Ask human:** "Can I execute [OPERATION]?"
5. **Wait for approval**
6. **Document in HISTORIAL.md immediately after**

---

## Dual-Session Pattern

If you find changes from another agent:
```
"He visto que [AGENT] hizo [CAMBIOS] en [FECHA].
¿Puedo proceder con [MI_TAREA]?
¿Hay conflictos potenciales?"

→ WAIT for explicit approval
```

---

## Incident Case Study

**2026-05-17 Gemini incident:**
- Gemini executed `git reset --hard` without checking HISTORIAL.md
- Lost Claude's changes (README.md, CONTRIBUTING.md)
- Lesson: This rule exists because of that failure

---

## Exceptions

None. REGLA #0 is absolute.

---

## Related

- **S14:** Zero-Trust (double-key rule)
- **LEVEL_2/M5:** Session Closure (document before closing)
- **LEVEL_4/M1:** Prohibitions (what's blocked)
