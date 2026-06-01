# 🚨 ESCALATION_PROTOCOL — Cross-Phase Behavior & Interruption Rules
**CoderCerberus V0.02 | Effective: 2026-05-21**

Defines when to interrupt execution, how to escalate findings, and recovery procedures across STARTUP/PLANNING/EXECUTION/VALIDATION phases.

---

## 📌 ESCALATION vs. CONTINUATION

### Rule 1: Real Bugs ALWAYS Interrupt
A **real bug** is one that:
- ❌ Blocks the current task (prevents completion)
- ❌ Is in critical path (not optional, not nice-to-have)
- ❌ Has verified root cause (not hypothetical)
- ❌ Requires PLANNING-phase rethink to fix safely

**Action:** Return to PLANNING, update PLAN.md, execute B3/B9 Angry Path
**Log:** HISTORIAL.md + Escalation Entry with root cause + reversal steps

### Rule 2: Secondary Findings NEVER Interrupt (B8 Compliance)
A **secondary finding** is one that:
- ✅ Would be nice-to-fix (optimization, refactor, cleanup)
- ✅ Is NOT in critical path (task completes without it)
- ✅ Has no verified root cause (observation only)
- ✅ Requires no PLANNING rethink

**Action:** Document in HISTORIAL.md as "Hallazgo Secundario" + continue EXECUTION
**Log:** HISTORIAL.md Hallazgo entry with: finding, why secondary, suggested owner/phase
**Approval Required:** Before executing secondary finding, must get user approval (B8)

### Rule 3: Ambiguity Blocks (B9 Threshold)
If a task requires >2 unverified assumptions, STOP:
- "¿La entrada es UTF-8?" ← Assumption
- "¿El puerto está libre?" ← Assumption
- "¿El usuario quiso decir X?" ← Assumption

**Action:** Declare BLOCKED, list assumptions, request clarification
**Log:** HISTORIAL.md Bloqueado entry with assumptions required + awaiting user input

---

## 🔄 PHASE-SPECIFIC ESCALATION RULES

### STARTUP Phase (B2, S17, S2, B1)
**Escalation Trigger:** Version mismatch, encoding corruption, missing core files
- **If triggered:** Halt bootstrap, document encoding/version state, request user intervention
- **Recovery:** Re-read problematic files with UTF-8 encoding, update versions via sync_binding.py
- **Severity:** CRITICAL — no continuation until resolved
- **Log:** HISTORIAL.md Startup Failure with diagnostics

### PLANNING Phase (B3, B9, B10, B4, B11)
**Escalation Trigger:** Angry Path reveals actual design flaw (not just theoretical)
- **If triggered:** User reviews B3 failure modes, decides: proceed or redesign
- **Action:** Document decision in PLAN.md, user approval, continue
- **B11 Trigger:** Dependency validation fails (package doesn't exist, incompatible)
- **Action:** Halt PLANNING, research alternatives, propose revised dependencies
- **Recovery:** Update PLAN.md with approved dependencies, request user confirmation
- **Severity:** HIGH — no code written until plan approved
- **Log:** HISTORIAL.md Planning Escalation with decision/rationale

### EXECUTION Phase (S1-S9, B5, B8, B7)
**Escalation Trigger:** Code modification introduces blocking error or silent failure
- **If triggered:** 
  1. Revert last edit
  2. Run audit_6d_expanded.py to identify failed domain
  3. Determine: is this a real bug (Rule 1) or dev artifact?
  4. If real bug: return to PLANNING, update PLAN.md
  5. If dev artifact: fix in-place, log in HISTORIAL.md, continue

**B8 Trigger (Anti-Deriva):** Finds secondary optimization while implementing
- **If triggered:** Document in HISTORIAL.md Hallazgo entry, user approval for scope change
- **Action:** User decides: continue execution OR approve scope expansion
- **Note:** Scope expansion requires NEW PLAN.md step; not part of original task
- **Severity:** MEDIUM — continue execution, don't auto-expand

**B5 Trigger (Ethical):** Pressure to cut corners (sacrifice precision for speed)
- **If triggered:** Refuse. Document in HISTORIAL.md why corners cannot be cut
- **Action:** Maintain rigor. User can manually abort task if time-critical
- **Severity:** CRITICAL — ethics non-negotiable

**B7 Trigger (Anti-Triunfalismo):** Temptation to declare success without empirical proof
- **If triggered:** Halt claim. Demand terminal logs, user confirmation, or screenshot
- **Action:** Continue validation. Collect evidence before declaring done
- **Severity:** HIGH — success claims without evidence are forbidden

---

## 🔧 AUDIT FAILURE TRIAGE & REMEDIATION PROTOCOL

When `audit_6d_expanded.py` fails (D1-D6), **NEVER fix all failures at once**. Categorize → Remediate by priority → Validate → Repeat.

### Step 1: Triage Failures (Categorization)

Run audit, collect ALL failures, categorize by SEVERITY + DOMAIN:

| Severity | Definition | Example | Action |
|----------|-----------|---------|--------|
| **CRITICAL** | Blocks task entirely; prevents continuation | D1 Whitelist violation; D2 code won't run | Fix immediately, re-audit before next |
| **HIGH** | Blocks specific domain; affects functionality | D4 Secret detected; D5 JSON corrupt | Fix after CRITICAL, re-audit before next |
| **MEDIUM** | Quality issue; task completes but degraded | D3 Documentation missing; D6 cleanup needed | Fix after HIGH, optional batching |
| **LOW** | Nice-to-have; no impact on task completion | D3 Minor doc improvement | Batch, mark as secondary finding |

### Step 2: Create Remediation Plan (B10 Checkpointing)

**Template:**
```markdown
## [2026-05-21] AUDIT FAILURE TRIAGE

**Total Failures:** 8 (D1: 2, D2: 1, D3: 3, D4: 1, D5: 1)

**Remediation Order:**
1. [CRITICAL] D2: Fix code syntax error (blocks all)
2. [CRITICAL] D1: Remove zombie file X (whitelist violation)
3. [HIGH] D4: Remove hardcoded API key from line 42
4. [HIGH] D5: Fix JSON in .protocol/evidence/audit.json
5. [MEDIUM] D3: Add docstring to main function
6. [LOW] D3: Minor doc improvement (secondary finding)

**Estimated time per fix:** 5, 5, 3, 3, 5 min
**Total:** 21 min + validation passes (5 min each = 15 min)
**Grand Total:** ~36 min, ~6 re-audit cycles
```

### Step 3: Remediate by Severity (B8 Anti-Deriva)

**Rule:** Fix ONE category, then re-audit BEFORE moving to next.

```
FOR each category (CRITICAL → HIGH → MEDIUM → LOW):
  1. Identify failures in this category
  2. Fix each failure (max 50 lines per edit, S6)
  3. Log fix in HISTORIAL.md with line numbers
  4. Re-run audit_6d_expanded.py
  5. Verify ONLY this category passes
  6. Document status in triage plan
  7. If new failures appeared: escalate (don't fix scope-creep)
  8. Move to next category
```

**CRITICAL Validation Example:**
```bash
# Before fix
$ python audit_6d_expanded.py
D1 FAIL: zombie file [foo.txt]
D2 FAIL: syntax error in bar.py line 42
...

# After fixing D2 syntax error
$ python audit_6d_expanded.py
D1 FAIL: zombie file [foo.txt]
D2 PASS ✅
D3 FAIL: missing docstring
...

# After fixing D1 zombie file
$ python audit_6d_expanded.py
D1 PASS ✅
D2 PASS ✅
D3 FAIL: missing docstring
...
```

### Step 4: Intermediate Validation (B1 Doctrine Failure)

After EACH category fix, verify:
- ✅ That domain is now PASS (not introduced new failures)
- ✅ No scope creep (no changes to OTHER domains)
- ✅ Edits were <50 lines (S6 compliance)
- ✅ Logging added if code modified (S9)

**REJECT fixes that:**
- ❌ "Fix everything" in one commit (scope creep → B8 violation)
- ❌ Touch multiple categories without re-audit (skipped validation)
- ❌ Introduce new failures in different domain (regression)

### Step 5: Log Remediation Progress (B4 Decision Logging)

```markdown
## [2026-05-21 15:30] AUDIT FAILURE REMEDIATION

**Initial Status:** 8 failures (D1:2, D2:1, D3:3, D4:1, D5:1)
**Current Status:** 6 failures remaining (D2:0, D1:1, D3:3, D4:1, D5:1)

**Completed (CRITICAL):**
- ✅ D2 syntax error (line 42, bar.py): Fixed, re-audited, PASS
- Status: CRITICAL category complete

**In Progress (HIGH):**
- D1 zombie file: Remove [foo.txt]
- Will re-audit after

**Remaining (MEDIUM + LOW):**
- D3: 3 docstring issues (batch after HIGH)
- D4: API key hardcoded (fix after D1)
- D5: JSON corrupt (lowest priority)
```

### Example: 8-Failure Audit Remediation

**Initial Audit Output:**
```
D1 FAIL: Zombie files (2): foo.txt, bar.json
D2 FAIL: Syntax error in scoring.py line 42
D3 FAIL: Missing docstrings (3): func_A, func_B, func_C
D4 FAIL: Secret detected: hardcoded API key line 88
D5 FAIL: JSON corrupt in .protocol/evidence/audit.json
```

**Triage:**
- CRITICAL (2): D2 syntax (blocks run), D1 zombie (whitelist violation)
- HIGH (2): D4 secret (security), D5 JSON (state integrity)
- MEDIUM (3): D3 docstrings (quality)

**Remediation Turn 1: Fix D2 Syntax**
```
1. Edit scoring.py line 42: Fix syntax error (2 lines edited)
2. Commit: "Fix D2 syntax error in scoring.py:42"
3. Re-audit: D2 now PASS, others unchanged
4. Document in triage log: "D2 CRITICAL complete"
```

**Remediation Turn 2: Fix D1 Zombie**
```
1. Delete foo.txt (untracked, remove)
2. Delete bar.json (check before removing!)
3. Commit: "Remove D1 zombie files"
4. Re-audit: D1 now PASS, D2 still PASS, others unchanged
5. Document: "D1 CRITICAL complete"
```

**Remediation Turn 3: Fix D4 Secret**
```
1. Edit config.py line 88: Replace hardcoded key with os.getenv("API_KEY")
2. Add logging: logger.info("Using API key from environment")
3. Commit: "Remove hardcoded API key, use environment variable"
4. Re-audit: D4 now PASS, D1/D2 still PASS, others unchanged
5. Document: "D4 HIGH complete"
```

**Remediation Turn 4: Fix D5 JSON**
```
1. Read .protocol/evidence/audit.json (diagnose corruption)
2. Regenerate valid JSON (if possible) or delete corrupted entry
3. Verify JSON format: python -m json.tool .protocol/evidence/audit.json
4. Commit: "Fix corrupted JSON in .protocol/evidence/audit.json"
5. Re-audit: D5 now PASS, all CRITICAL/HIGH categories PASS
6. Document: "D5 HIGH complete"
```

**Remediation Turn 5: Batch D3 Docstrings**
```
1. Add docstring to func_A (3 lines)
2. Add docstring to func_B (3 lines)
3. Add docstring to func_C (2 lines) — total 8 lines <50
4. Commit: "Add missing docstrings (D3)"
5. Re-audit: D3 now PASS, ALL domains PASS
6. Document: "D3 MEDIUM complete — FULL AUDIT PASS"
```

**Final Status:**
```
✅ D1: PASS (Whitelist)
✅ D2: PASS (Functionality)
✅ D3: PASS (Clarity)
✅ D4: PASS (Security & I/O)
✅ D5: PASS (State Integrity)
✅ D6: PASS (Workspace Cleanup)

🎯 AUDIT: 6/6 DOMAINS PASSED
```

### B8 Anti-Deriva Enforcement

**FORBIDDEN:**
```
Turn 1: Fix D2, D1, AND D3 all at once (scope creep → no re-audit between)
Turn 1: Fix D4 secret AND refactor entire security module (scope expansion)
Turn 1: "I see 8 failures, let me fix 6 today and leave 2 for later" (random batch)
```

**REQUIRED:**
```
Turn 1: Fix ONLY D2 CRITICAL, re-audit, document, commit
Turn 2: Fix ONLY D1 CRITICAL, re-audit, document, commit
Turn 3: Fix ONLY D4 HIGH, re-audit, document, commit
...
```

---

### VALIDATION Phase (B6, B3-complement, B7-complement)
**Escalation Trigger:** Tests fail; evidence missing; human validation not collected
- **If triggered:** 
  1. If test fails: identify failure, return to EXECUTION, fix code
  2. If evidence missing: collect proof (logs, screenshots, test output)
  3. If human validation missing: request user confirmation of behavior
- **Recovery:** Re-run tests, collect evidence, get user approval
- **Severity:** BLOCKER — cannot exit phase without all validations passing
- **Log:** HISTORIAL.md Validation Failure with root cause + remediation

---

## 📝 ESCALATION LOGGING (HISTORIAL.md Format)

Every escalation creates a timestamped entry in HISTORIAL.md with structure:

```markdown
## [2026-05-21 14:32] ESCALATION: [Type]

**Fase:** PLANNING | EXECUTION | VALIDATION
**Trigger:** [Rule 1 / Rule 2 / Rule 3 / Phase-Specific]
**Severity:** CRITICAL | HIGH | MEDIUM | LOW

**Description:**
[What happened, where, why]

**Root Cause:**
[Technical reason if real bug; observation only if secondary]

**Action Taken:**
[What was done: returned to PLANNING, documented in secondary, etc.]

**User Decision:**
[Proceed | Redesign | Approved Scope Change | etc.]

**Reversal Steps:**
[If needed to rollback this escalation]
```

Example:
```markdown
## [2026-05-21 15:15] ESCALATION: Real Bug in D2 Domain

**Fase:** EXECUTION
**Trigger:** Rule 1 (Real bug blocks task)
**Severity:** HIGH

**Description:**
audit_6d_expanded.py D2 validation failed: SPEC.md required section missing.
Task cannot proceed without completing SPEC.

**Root Cause:**
The DATA SKELETON & UI LAYOUT section in SPEC.md now requires an explicit canonical schema definition to validate compliance.

**Action Taken:**
Returned to PLANNING, updated PLAN.md to include SPEC completion as Step 1.

**User Decision:**
Approved. User provided schema definition.

**Reversal Steps:**
If needed: revert PLAN.md to v1, skip SPEC completion step.
```

---

## 🛡️ INTERRUPT CONDITIONS (When to Stop Immediately)

Stop and escalate if ANY of these occur:

| Condition | Type | Trigger | Action |
|-----------|------|---------|--------|
| **Version mismatch** | B2 | .version ≠ v0.02 | STARTUP failure |
| **Encoding corruption** | S3 | Mojibake in file | Halt, diagnose UTF-8 |
| **Whitelist violation** | D1 | Zombie file created | Audit, understand, whitelist or remove |
| **Real bug blocks task** | Rule 1 | Code won't run | Return to PLANNING |
| **Dependency missing** | B11 | npm/pip fails | Return to PLANNING, research |
| **Test fails** | D2 | Unit/integration test red | Fix in-place or escalate |
| **Evidence missing** | B7 | No proof of behavior | Collect before declaring done |
| **Ambiguity >2 assumptions** | B9 | Unverified guesses | BLOCKED, request clarification |
| **Scope pressure** | B5 | User pushes for shortcuts | Refuse, maintain rigor |

---

## 🔁 ESCALATION DECISION TREE

```
Is this finding blocking the current task?
├─ YES → Is the root cause real/verified?
│  ├─ YES → REAL BUG (Rule 1)
│  │        Return to PLANNING
│  │        Update PLAN.md with root cause
│  │        Run Angry Path (B3/B9)
│  │        Log in HISTORIAL.md
│  │
│  └─ NO → AMBIGUITY (Rule 3)
│           Declare BLOCKED
│           List unverified assumptions
│           Request user clarification
│           Log in HISTORIAL.md
│
└─ NO → Is it optimization/refactor/cleanup?
   ├─ YES → SECONDARY FINDING (Rule 2)
   │        Document in HISTORIAL.md Hallazgo
   │        Continue EXECUTION
   │        Wait for user approval before execution
   │
   └─ NO → Ignore, continue task
```

---

## 🔐 ENFORCEMENT

**Pre-Commit Hook (run_compliance_tests.py):**
- Validates no escalation entries in HISTORIAL.md lack closure status
- Requires all BLOCKED entries to be resolved before commit
- Allows secondary findings (will be executed in future phases)

**Evidence Logger (log_evidence.py):**
- Logs every escalation with operation=escalation
- Tracks resolution time and outcome
- Prevents duplicate escalations on same issue

**Protocol CLI (protocol_cli.py):**
- Command: `protocol_cli.py escalation-status` — shows open escalations
- Command: `protocol_cli.py escalation-resolve [id]` — close resolved escalation

---

**Efectivo desde:** 2026-05-21 | **Versión:** 5.7.0 | **Próxima revisión:** sync_binding.py
