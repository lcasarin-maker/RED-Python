# 🔐 PERMISSIONS.md — Agent Authorization Matrix
**CoderCerberus v0.02 | Permissions Framework v1.0**

---

## 📋 Agent Permission Matrix

| Operation | Claude | Gemini | ChatGPT | Codex | Notes |
|-----------|--------|--------|---------|-------|-------|
| **protocol_cli.py check** | ✅ FULL | ✅ FULL | ✅ FULL | ✅ FULL | Validation only; read-only |
| **protocol_cli.py sync** | ✅ FULL | ⚠️ DRY-RUN ONLY | ❌ NO | ✅ FULL | Dangerous; sync after review |
| **protocol_cli.py sync --dry-run** | ✅ FULL | ✅ FULL | ✅ FULL | ✅ FULL | Safe preview; recommended |
| **protocol_cli.py install** | ✅ FULL | ❌ NO | ❌ NO | ✅ FULL | Setup; full agents only |
| **protocol_cli.py promote** | ⚠️ PROPOSAL | ❌ NO | ❌ NO | ⚠️ PROPOSAL | Requires human review |
| **protocol_cli.py doctor** | ✅ READ-ONLY | ✅ READ-ONLY | ✅ READ-ONLY | ✅ READ-ONLY | Diagnostics only |
| **protocol_cli.py doctor --fix** | ✅ FULL | ❌ NO | ❌ NO | ✅ FULL | Auto-repair; restricted |
| **protocol_cli.py evidence** | ✅ FULL | ✅ FULL | ✅ FULL | ✅ FULL | Audit trail; read-only |
| **protocol_cli.py rollback-plan** | ✅ FULL | ✅ FULL | ✅ FULL | ✅ FULL | Planning only; non-destructive |
| **git commit** | ✅ FULL | ❌ NO | ❌ NO | ✅ FULL | Code changes; restricted |
| **git push** | ✅ FULL | ❌ NO | ❌ NO | ✅ FULL | Remote changes; restricted |
| **git reset --hard** | ❌ NO | ❌ NO | ❌ NO | ❌ NO | FORBIDDEN; destructive |
| **git push --force** | ❌ NO | ❌ NO | ❌ NO | ❌ NO | FORBIDDEN; destructive |
| **Python generic** | ❌ NO | ❌ NO | ❌ NO | ❌ NO | FORBIDDEN; execute protocol_cli.py instead |
| **Bash/PowerShell write** | ❌ NO | ❌ NO | ❌ NO | ❌ NO | FORBIDDEN; use Edit/Write tools |

---

## 🎯 Agent Tiers

### TIER 1: Full Authority (Claude, Codex)
**Capabilities:**
- ✅ All protocol_cli.py commands including sync, install, doctor --fix, promote
- ✅ Git commit/push (via protocol_cli.py enforcement)
- ✅ Code modifications via Edit/Write
- ✅ Executing tests and audits

**Restrictions:**
- ❌ git reset --hard (no destructive operations)
- ❌ git push --force (no force overwrite)
- ❌ Generic Python execution (only protocol_cli.py)
- ❌ Shell write operations (only Edit/Write tools)

**Use Case:** Primary development agents; full governance authority

---

### TIER 2: Governance-Only (Gemini)
**Capabilities:**
- ✅ protocol_cli.py check (validation)
- ✅ protocol_cli.py sync --dry-run (preview)
- ✅ protocol_cli.py evidence (audit trail)
- ✅ protocol_cli.py rollback-plan (planning)
- ✅ protocol_cli.py doctor (read-only)

**Restrictions:**
- ⚠️ protocol_cli.py sync (requires human approval; dry-run only)
- ❌ Git operations (commit/push)
- ❌ Code modifications (read-only analysis)
- ❌ Execution of doctorFix or dangerous commands

**Use Case:** Governance monitoring; suggestions only; no direct execution

---

### TIER 3: Advisory-Only (ChatGPT)
**Capabilities:**
- ✅ protocol_cli.py check (read-only validation)
- ✅ protocol_cli.py sync --dry-run (read-only preview)
- ✅ protocol_cli.py evidence (read-only audit)
- ✅ protocol_cli.py rollback-plan (planning only)

**Restrictions:**
- ❌ Any write operation (commit, push, modify)
- ❌ Git operations
- ❌ Code modifications
- ❌ Execution of any protocol command beyond read-only

**Use Case:** External analysis; reporting; no execution authority

---

## 🚫 Global Restrictions (ALL AGENTS)

```
FORBIDDEN (No Agent Exemption):
├─ git reset --hard
├─ git push --force
├─ git clean -fdx
├─ git revert --hard
├─ rm -rf / or similar destructive shell
├─ Python eval() on untrusted code
├─ Adding scripts outside whitelist
├─ Modifying git hooks without protocol_cli.py
├─ Shell write (sed, echo, Add-Content, powershell -Command)
└─ Execution of scripts not in SPEC.md whitelist
```

---

## 🔑 Permission Validation Logic

**protocol_cli.py enforces:**
```python
def validate_agent_permission(agent: str, command: str) -> bool:
    """Check if agent is allowed to execute command."""
    permissions = {
        "Claude": ["check", "sync", "install", "promote", "doctor", "evidence", "rollback-plan"],
        "Gemini": ["check", "sync --dry-run", "evidence", "rollback-plan", "doctor"],
        "ChatGPT": ["check", "sync --dry-run", "evidence", "rollback-plan"],
        "Codex": ["check", "sync", "install", "promote", "doctor", "evidence", "rollback-plan"],
    }
    
    if agent not in permissions:
        return False
    
    if command not in permissions[agent]:
        if command.startswith("sync") and agent == "Gemini":
            # Gemini allowed only --dry-run variant
            return "--dry-run" in command
        return False
    
    return True
```

**Entry point validation:**
```bash
$ protocol_cli.py sync
# Agent validation → (Claude: OK | Gemini: DENIED | ChatGPT: DENIED)
# If denied: "❌ Gemini is not authorized for 'sync'. Use 'sync --dry-run' or ask Claude."
```

---

## 📊 Permission Inheritance

- **Base permissions:** Defined per tier (TIER 1/2/3)
- **Command restrictions:** Specific commands may require additional context
  - Example: `sync` requires prior `check` to pass
  - Example: `promote` requires evidence of testing
- **Escalation path:** ChatGPT → Gemini (suggestion) → Claude (execution)

---

## 🔔 Audit Trail

All permission checks logged in evidence:
```json
{
  "timestamp": "2026-05-21T06:15:00Z",
  "operation": "permission_check",
  "agent_name": "Gemini",
  "command": "sync",
  "permission_granted": false,
  "reason": "TIER 2 agent limited to --dry-run variant",
  "suggestion": "Use: protocol_cli.py sync --dry-run"
}
```

---

## 🎯 Future Enhancements

- **Context-aware permissions:** Relax restrictions if within designated "maintenance window"
- **Temporary escalation:** Claude can grant temporary full permissions to Gemini for specific tasks
- **Role-based access:** Beyond agent type; e.g., "integration_tester", "security_auditor"
- **Time-based restrictions:** Enforce quiet hours; no dangerous ops after 18:00 UTC

---

**Version:** 1.0 | **Effective:** 2026-05-21 | **Review:** Quarterly or on protocol update
