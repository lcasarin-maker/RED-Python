# adapters/claude — Claude Code Adapter

Adapts the agent-agnostic Cerberus core to Claude Code.

## Files required by Claude Code (fixed path, do not move)

| File | Real path | Purpose |
|---------|-----------|-----------|
| settings.json | `.claude/settings.json` | Hook automation |
| CLAUDE.md | `.claude/CLAUDE.md` | Binding + mandates |
| ACTIVE_HOOKS.json | `.claude/ACTIVE_HOOKS.json` | Automation registry |

## Implemented hooks

### PreToolUse (before Edit/Write)
- `pre_edit_guard.py` — bloquea ediciones peligrosas
- `block_auto_docs.py` — TK-049: bloquea docs auto-generados

### PreToolUse (before any tool - session init)
- `preflight_compliance.py` — genera codebase_map.json
- `sync_binding.py` — verifica paridad de protocolo

### PostToolUse (after Bash/PowerShell)
- `validate_data.py` — valida datos en fronteras I/O
- `detect_rule_code_drift.py` - detects rule-code inconsistencies

### PreCompact (before context compression)
- `compact_automation_helper.py`
- `enforce_thinking_limits.py` — TK-044
- `model_router.py` — TK-045
- `trigger_context_compression.py`

### Stop (when the response finishes)
- `discourse_hook.py`
- `tool_result_cleaner.py` — TK-047
- `image_cost_detector.py` — TK-050
- `sandwich_model_detector.py` — TK-048
- `track_tokens.py`
- `compress_historial.py`
- `validate_state_checkpoint.py`

## Equivalence in other agents

For Gemini/ChatGPT to run the same scripts, they must do so
**manually at session start** (see adapters/gemini/ and adapters/chatgpt/).
