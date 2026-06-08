# M1: Prohibitions — Hard Stops (No Exceptions)

**Source:** Integrated from PROTOCOL_SYSTEM.md + AGENT.md (S3, S14) + GEMINI.md (incident prevention)
**Status:** ACTIVE (Phase 2) | **Date:** 2026-06-02 | **Authority:** S3, S14, B3

---

## Absolute Prohibitions (No Context Changes This)

### 1. Destructive Operations Without Approval (DOUBLE-KEY RULE)

**PROHIBITED:**
- `git reset --hard` (unless isolated turn with human approval)
- `git rm` (unless isolated turn with human approval)
- `rm -rf` (unless isolated turn with human approval)
- `git rebase` (unless isolated turn with human approval)

**REQUIRED BEFORE EXECUTION:**
1. Read HISTORIAL.md COMPLETELY
2. Ask human EXPLICITLY: "Can I execute [OPERATION]?"
3. Wait for approval (cannot assume)
4. Confirm in isolated turn only
5. Document result in HISTORIAL.md

**Why:** Multi-agent coordination (see LEVEL_2/M5). One destructive op can wipe another agent's work.

**Incident Example:** 2026-05-17 Gemini reverted Claude's changes because it didn't check HISTORIAL.md first.

---

### 2. Silent Changes (No Untraced Work)

**PROHIBITED:**
- ❌ Modifying >3 files without auto-commit
- ❌ Leaving session without updating HISTORIAL.md
- ❌ Leaving session without updating STATUS.md CAMPO 6 (next steps)
- ❌ Making changes without documenting their purpose

**REQUIRED:**
- ✅ Update HISTORIAL.md with session summary BEFORE closing
- ✅ Update STATUS.md CAMPO 3 (what done) + CAMPO 6 (what's next)
- ✅ Auto-commit if >3 files changed
- ✅ Leave clear instructions for next agent

**Why:** INTEGRIDAD TOTAL requires all work to be traceable and documented. Undocumented work = unverifiable work.

---

### 3. Pure Replacement Only (VC-118)

**PROHIBITED:**
- `from OLD import X` (in replacement file)
- `(new.exists() or old.exists())` (fallback logic)
- Dual test sentinels (testing both old and new)
- Comments: "# deprecated", "# backward compat", "# for now"

**REQUIRED:**
- `git rm OLD && git add NEW` (same commit)
- Copy code from OLD to NEW if needed (don't import)
- Tests point ONLY to NEW
- No alternative code paths

**Why:** Code is not "good" unless verifiable. Mixed paths make verification impossible.

**Authority:** VC-118 (Zombie Compatibility Theater), INTEGRIDAD TOTAL (LEVEL_1/M1)

---

### 4. No Hardcoded Secrets

**PROHIBITED:**
- Passwords in code
- API keys in .env files tracked in VCS
- Database credentials anywhere in repo
- Tokens in configuration files

**REQUIRED:**
- All secrets in `.secrets/` (outside VCS)
- Only `.example` files in repo
- Use environment variables or vault systems

---

### 5. No Silent Failures

**PROHIBITED:**
- Error handling without logging
- Try/catch blocks without 4 required elements:
  1. **LOG** — logger.error with context
  2. **USER** — Human-readable message (not "Error 500")
  3. **STATE** — Rollback or consistency guarantee
  4. **ACTION** — Retry? Fail? Degrade?

**REQUIRED:**
- Every error MUST have these 4 elements
- Errors must be observable and traceable

---

## When Prohibitions Are Violated

**Consequence:** Hard block. Code does not proceed past validation. No exceptions, no context changes this.

- Pre-commit hook blocks commit
- `run_security_audit_12d.py` gates deployment
- No approval waiver exists

---

## Next Steps

- [ ] All agents follow DOUBLE-KEY RULE before destructive ops
- [ ] All agents document work in HISTORIAL.md before session close
- [ ] All agents use VC-118 pure replacement strategy

