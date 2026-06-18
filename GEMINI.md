# Coder Cerberus V0.1 - GEMINI EXTENSION
**v2.9.0 | Gemini-specific | Extends AGENT.md**

> **IMPORTANT:** Read [AGENT.md](AGENT.md) first. This file only adds Gemini-specific instructions and historical incident context.

---

## Incident awareness: 2026-05-17 revert incident

**What happened:**
- Gemini ran `git reset --hard` in Coder Cerberus V0.1.
- It lost Claude changes (Phase 5: polished `README.md`, `CONTRIBUTING.md`, `.secrets/`).
- It did not document the action in `HISTORIAL.md`.
- Rule #13 violation: more than 3 modified files without auto-commit.

**Lesson learned:**
- Rule #0 exists for Gemini and all agents.
- Dual-session awareness through `HISTORIAL.md` is critical.
- The pre-destructive checklist in `AGENT.md` must always run.
- `AGENT_SAFETY.md` critical prohibition #3 prevents this.

**For you:** Read `AGENT_SAFETY.md` lines 1-50 on every session. This incident must not repeat.

---

## Gemini vs AGENT.md

| Aspect | AGENT.md (all) | GEMINI.md (Gemini only) |
|--------|----------------|-------------------------|
| Auto-initialization | Manual (every session) | Manual (Gemini does not auto-initialize) |
| Memory context | Via `HISTORIAL.md` | `HISTORIAL.md` only (no `.google/memory/`) |
| Available models | N/A | Google Gemini (single model) |
| Context window | N/A | Gemini context window limits |
| COMPACT strategy | Via `STATUS.md` | Critical: read field 6, "Next session" |
| Dual-session risk | Standard | High (v2.8.6 conflicted with Claude Phase 5) |

---

## Extra checklist for Gemini after the incident

In addition to the checklist in AGENT.md, do this:

1. **Read `HISTORIAL.md` completely** (not just the last 3 entries).
   - Understand what Claude did.
   - Understand what you did.
   - Detect overlaps and conflicts.

2. **Check git status before any change:**
   ```bash
   git status
   git log --oneline -10
   ```
   - Are there undocumented commits?
   - Is my last work recorded?

3. **Understand `AGENT_SAFETY.md` critical prohibition #3:**
   - Dual-session awareness.
   - Why you cannot assume your past changes are "your territory".
   - `HISTORIAL.md` is the single source of truth.

4. **Before any destructive git command:**
   - Run the pre-destructive checklist in `AGENT.md`.
   - Ask Luis explicitly.
   - Do not execute without confirmation.

---

## Avoid conflicts

**If you find recent changes from other agents:**

```bash
# 1. Read HISTORIAL.md
# 2. Understand what happened
# 3. Ask:

"I saw that Claude made [CHANGES] on [DATE].
May I proceed with my task [YOUR_TASK]?
Are there any potential conflicts?"

# 4. Wait for explicit confirmation from Luis
# 5. Proceed only then
```

Never assume it is safe to revert another agent's changes.

---

## Required documentation

When you finish your session, you must:

1. **Update `STATUS.md`:**
   - Field 3: What you completed exactly.
   - Field 6: Next step (for Claude or the next agent).
   - Field 7: Technical details.

2. **Create or update `HISTORIAL.md`:**
   ```markdown
   ## SESSION [DATE] - GEMINI

   **Task:** [What you did]
   **Changes:** [Modified files]
   **Documentation:** [Where]
   **Status:** ✅ COMPLETE / ⚠️ IN PROGRESS / ❌ BLOCKED
   **Next agent:** [Who should continue]
   ```

3. **Auto-commit if >3 files or >50 lines:**
   ```bash
   git add [specific files]
   git commit -m "Brief description"
   ```

---

## Critical rule: no silent changes

Gemini must document before finishing:

```bash
❌ BAD: End the session without updating `HISTORIAL.md`
❌ BAD: Change 5 files without auto-commit
❌ BAD: Assume "another agent will see my changes"

✅ GOOD: Document in `HISTORIAL.md`
✅ GOOD: Auto-commit if >3 files
✅ GOOD: Leave clear instructions in `STATUS.md` field 6
```

---

## Incident timeline

```
2026-05-17 18:32 — Gemini runs COMANDO_SYNC.py
                   (symlinks in 4 projects)

2026-05-17 19:17 — Gemini finishes without documenting
                   VIOLATION: Rule #13, AGENT_SAFETY #3

2026-05-17 22:00 — Claude detects inconsistency
                   (`STATUS.md` says "symlinks pending" but they exist)
                   Documented in `HISTORIAL.md` session 2026-05-17 part 3

2026-05-18+     — AGENT_SAFETY.md and RULE #20 implemented
                   Prevent future incidents
```

---

## You are ready when...

- [ ] You understand why Rule #0 exists (because of the revert incident).
- [ ] You read `HISTORIAL.md` completely, not just the last 3 entries.
- [ ] You always run the pre-destructive checklist.
- [ ] You ask Luis before any destructive git command.
- [ ] You document changes in `HISTORIAL.md` and auto-commit.
- [ ] You update `STATUS.md` field 6 for the next agent.
- [ ] You never assume it is safe to revert others' changes.

---

## Gemini golden rule

**After every session:**
- ✅ `STATUS.md` updated
- ✅ `HISTORIAL.md` documented
- ✅ Changes committed if >3 files
- ✅ Luis can read `HISTORIAL.md` and know exactly what happened
- ✅ The next agent has clear instructions in field 6

Do not leave ambiguity. Do not leave incidents undocumented.

---

**Core:** AGENT.md (all agents)
**Extension:** GEMINI.md (Gemini only, with incident awareness)
**Global context:** AGENT_SAFETY.md (prohibitions that protect everyone)

Learn from the incident. Follow the protocol. Document everything.
