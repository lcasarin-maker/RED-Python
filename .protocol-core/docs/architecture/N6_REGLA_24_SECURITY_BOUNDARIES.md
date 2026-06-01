# REGLA #24 — Security Boundaries & Code Execution Sandboxing
**Estado:** ✅ CONFIRMED v3.0 | **Adoptado de:** AutoGen sandbox execution model

---

## Problema (Por qué existe)

AutoGen permite agents ejecutar código arbitrario. Sin boundaries:
- **Untrusted agents** pueden modificar archivos críticos
- **Code injection** via tool parameters
- **Lateral movement** entre proyectos (D:\GoogleDrive\AI\*)
- **Data exfiltration** sin auditoría

Protocolo v3.0 define security tiers para agents.

---

## Regla

**Todos los agents (Claude, Gemini, Custom) deben operar dentro de security boundaries definidas.**

### Tier 1: TRUSTED (Default — Claude Code)
- ✅ Read/write any file in project directory
- ✅ Execute Bash/PowerShell (with auditing)
- ✅ Access MCP tools (Google Drive, GitHub, etc)
- ✅ Can modify REGLAS / CLAUDE.md / AGENT.md
- **Validación:** Agente es Anthropic Claude (identity verified)

### Tier 2: SEMI-TRUSTED (Gemini, Custom API Agents)
- ✅ Read files in project directory
- ❌ Write only to designated `.agent-sandbox/{agent_name}/` folder
- ❌ Cannot execute Bash/PowerShell (read-only scripts)
- ✅ Can call external APIs (Gemini, OpenAI, etc)
- ✅ Can append to HISTORIAL.md (not modify existing)
- **Validación:** API key verified, request signed, rate limits enforced

### Tier 3: UNTRUSTED (User-submitted code, external tools)
- ✅ Read from project directory (no secrets)
- ❌ Write nowhere without explicit approval
- ❌ No code execution (analyze-only mode)
- ❌ No external API calls
- ✅ Can generate reports (stdout only)
- **Validación:** Sandboxed environment (Docker), no network access

---

## Implementation

### 1. Agent Identity Declaration (In HISTORIAL.md)
```json
{
  "session_id": "uuid",
  "agent": {
    "name": "Claude",
    "identity_verified": true,
    "security_tier": "TRUSTED",
    "api_key_hash": "sha256(...)",
    "request_signed": false
  }
}
```

### 2. Filesystem Boundaries
```
Protocolo Agentes/
├── .git/
├── AGENT.md  [Tier 1 only: modify]
├── CLAUDE.md [Tier 1 only: modify]
├── HISTORIAL.md [Tier 2+: append only]
├── STATUS.md [Tier 1 only: overwrite]
├── REGLAS/   [Tier 1 only: create/modify]
├── .agent-sandbox/
│   ├── gemini/          [Tier 2: write here]
│   │   └── session_*.md
│   └── custom_agent/    [Tier 2: write here]
│       └── output/
└── scripts/ [Tier 1 only: create]
```

### 3. Pre-commit Hook Validation
```bash
# .git/hooks/pre-commit
for changed_file in $(git diff --cached --name-only):
    TIER=$(get_agent_security_tier)
    if can_write(TIER, changed_file):
        OK
    else:
        ABORT commit
        Log: CRITICAL violation
        Exit code: 1
```

### 4. Code Execution Sandbox
```bash
# For Tier 2/3 agents requesting code execution:
if agent_tier < TRUSTED:
    create_docker_container(
        image="python:3.11-slim",
        volumes={"./project": "/code:ro"},  # Read-only
        network="none",  # No internet
        memory="512m",
        timeout="30s"
    )
    execute_code_in_sandbox()
    cleanup()
else:
    execute_directly()  # Tier 1
```

---

## Threat Model

| Threat | Mitigation | REGLA |
|--------|-----------|-------|
| **Untrusted agent writes STATUS.md** | Tier check pre-commit | REGLA #24 |
| **External API steals secrets** | No secrets in project files | REGLA #17 |
| **Tier 2 agent exfiltrates data** | .agent-sandbox isolation | REGLA #24 |
| **Code injection via tool parameters** | Input validation (REGLA #15) | REGLA #15 |
| **Agent modifies REGLA #0-27** | Tier 1 only | REGLA #24 |

---

## Examples

### Example 1: Claude (Tier 1) modifying REGLA
```
Claude: Voy a crear REGLA #28
↓ git diff: REGLAS/N7_REGLA_28.md (new file)
↓ pre-commit hook: agent_tier=TRUSTED, file=REGLAS/*.md, allow=YES
↓ Commit OK
```

### Example 2: Gemini (Tier 2) trying to modify STATUS.md
```
Gemini API: "Voy a actualizar STATUS.md"
↓ git add status_changes
↓ pre-commit hook: agent_tier=SEMI-TRUSTED, file=STATUS.md, allow=NO
↓ ABORT, log CRITICAL violation
↓ Gemini redirected to .agent-sandbox/gemini/status_update.md
```

### Example 3: Untrusted code execution request
```
User: "Ejecuta este script de web scraping"
↓ Script uploaded: D:/GoogleDrive/AI/.agent-sandbox/user_script.py
↓ Security tier = UNTRUSTED
↓ Docker container created (read-only, no network)
↓ Script executes in sandbox
↓ Output returned to user (no side effects)
↓ Container deleted
```

---

## Enforcement

| Tier | Mecanismo | Cómo validar |
|------|-----------|------------|
| **Prose** | Esta REGLA documenta boundaries | Readable, shareable |
| **Hooks** | .git/hooks/pre-commit valida tier | `python validate_security_tier.py` |
| **Tests** | tests/test_regla_24_security.py | pytest (baseline archived; future expansion tracked separately) |

---

## Integration with Other REGLAs

- **REGLA #18 (Hooks)** — Pre-commit uses REGLA #24 logic
- **REGLA #17 (Secrets)** — No API keys in project (Tier 2/3 can't access)
- **REGLA #21 (Retrospective)** — Log security events
- **REGLA #28 (Routing)** — Tier influences which agents can coordinate

---

## Superioridad vs AutoGen

| Aspecto | AutoGen | Protocolo v3.0 |
|--------|---------|--------------|
| Agent authentication | None (implicit) | **3-tier identity verification** |
| File access control | Trust everyone | **Tier-based ACL** |
| Code execution | Local (unsafe) | **Sandboxed (Docker)** |
| Secrets protection | None | **Enforced no-secrets policy** |
| Audit trail | Manual logs | **Automatic HISTORIAL.md logging** |

---

**Versión:** 1.0 | **Adoptado:** 2026-05-17 | **Fuente:** AutoGen sandbox case study
