# Hooks — CoderCerberus V0.5

Automation of TK rules for token optimization.

## Estructura

```
hooks/
├── pre_write.sh              ← TK-049: Bloquear auto-docs
├── post_tool_result.sh       ← TK-047: Limpiar resultados gigantes
├── pre_model_selection.sh    ← TK-044: Thinking limits
│                            ← TK-045: Router de modelos
├── pre_screenshot.sh         ← TK-050: Detect unnecessary images
└── README.md                 ← Este archivo
```

## Active Hooks (Phase 1)

### pre_write.sh — TK-049
**When:** Before file Write/Create operations
**What it does:** Blocks automatic .md/.json/.yaml generation without an explicit request
**Exceptions:** SPEC.md, PLAN.md, HISTORIAL.md, .agent_state.json, VERSION.txt
**Output:** Error + suggestion to describe the change in chat

### post_tool_result.sh — TK-047
**When:** After running a tool (grep, find, git, ls, cat)
**What it does:** Truncates results over 5K tokens
**Strategies:**
- grep: max 20 lines
- find: max 10 items
- git log: max 3 commits
- git diff: max 50 lines
- ls: max 50 items
- cat: max 100 lines
**Output:** Cleaned result + saved token log

### pre_model_selection.sh — TK-044, TK-045
**When:** Before model selection
**What it does:**
- TK-044: Limita reasoning tokens en tareas simples
- TK-045: Recomienda modelo (Haiku/Sonnet/Opus)
**Logic:**
- Haiku: <10K tokens, simple tasks (80% allocation)
- Sonnet: <50K tokens, moderate tasks (15% allocation)
- Opus: strategic, critical tasks (5% allocation)
**Output:** Thinking settings + model recommendation

### pre_screenshot.sh — TK-050
**When:** Before taking a screenshot
**What it does:** Detects unnecessary images and suggests alternatives
**Cost:** 1000 base tokens + 2 tokens/KB
**Allowed use cases:** UI layouts, design mockups, devtools
**Discouraged:** terminal errors, JSON, small files
**Output:** Cost warning (does not block)

---

## Integration

### Requirements
- Python 3.7+
- `jq` (para parsing JSON en bash)
- Scripts en `D:\AI\Cerberus\scripts/`
- Configs en `D:\AI\Cerberus\rules/`

### Activation
1. Copy hooks to `.git/hooks/` or the system pre/post hook location
2. Make them executable: `chmod +x hooks/*.sh`
3. Register them in Claude Code settings or pre-commit hooks

### Ejemplo: pre-commit hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
source hooks/pre_write.sh "$1" "$2"
source hooks/post_tool_result.sh "$3" "$4"
```

---

## Logs

Todos los hooks registran en `HISTORIAL.md`:

```
[TK-049] 2026-06-01 10:30:45 — File blocked: SPEC_NEW.md, reason: auto-generated
[TK-047] 2026-06-01 10:31:12 — Tool result cleaned: grep → 2500→500 tokens (saved 2000)
[TK-044] 2026-06-01 10:32:00 — Thinking disabled: Opus + simple task
[TK-045] 2026-06-01 10:32:15 — Model escalation suggested: Haiku → Sonnet
[TK-050] 2026-06-01 10:33:00 — Screenshot discouraged: terminal_error context (would cost 1200 tokens)
```

---

## Impact

**Phase 1 (5 hooks):** -35% tokens/session

| TK | Impacto |
|---|---|
| TK-044 (Thinking) | -20% |
| TK-045 (Router) | -15% |
| TK-047 (Cleaner) | -25% |
| TK-049 (No auto-docs) | -8% |
| TK-050 (Images) | -12% |

---

## Configuration

### rules/thinking_limits.json
```json
{
  "thinking_level": "low",
  "max_tokens": 8000,
  "rules": {
    "opus_simple_task": false,
    "opus_strategy_task": true
  }
}
```

### rules/model_routing_matrix.yaml
```yaml
routing_matrix:
  haiku:
    allocation: 80%
    budget: 10000
    keywords: [list, grep, format, small, simple]
  sonnet:
    allocation: 15%
    budget: 50000
    keywords: [implement, debug, refactor, moderate]
  opus:
    allocation: 5%
    budget: 200000
    keywords: [architecture, critical, strategic, design]
```

### rules/image_policy.yaml
```yaml
image_policy:
  default_mode: "discourage"
  rejection_rules:
    - context: terminal_error
      action: suggest_text
  approval_rules:
    - context: ui_layout
      action: allow
```

---

## Next Phases

**Phase 2 (next sprint):**
- TK-048: Sandwich model detector (2-phase execution)
- Refine thresholds based on real data
- Roll out to all 16 satellites

**Phase 3 (Manual):**
- TK-046: Sub-agents (strategic decision, not automatable)

---

**Last updated:** 2026-06-01 | **Status:** Phase 1 COMPLETE
