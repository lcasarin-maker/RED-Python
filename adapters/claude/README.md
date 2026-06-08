# adapters/claude — Claude Code Adapter

Adapta el núcleo agent-agnostic de Cerberus a Claude Code.

## Archivos requeridos por Claude Code (path fijo, no mover)

| Archivo | Path real | Propósito |
|---------|-----------|-----------|
| settings.json | `.claude/settings.json` | Hook automation |
| CLAUDE.md | `.claude/CLAUDE.md` | Binding + mandatos |
| ACTIVE_HOOKS.json | `.claude/ACTIVE_HOOKS.json` | Registro de automatización |

## Hooks implementados

### PreToolUse (antes de Edit/Write)
- `pre_edit_guard.py` — bloquea ediciones peligrosas
- `block_auto_docs.py` — TK-049: bloquea docs auto-generados

### PreToolUse (antes de cualquier tool — session init)
- `preflight_compliance.py` — genera codebase_map.json
- `sync_binding.py` — verifica paridad de protocolo

### PostToolUse (después de Bash/PowerShell)
- `validate_data.py` — valida datos en fronteras I/O
- `detect_rule_code_drift.py` — detecta inconsistencias regla-código

### PreCompact (antes de comprimir contexto)
- `compact_automation_helper.py`
- `enforce_thinking_limits.py` — TK-044
- `model_router.py` — TK-045
- `trigger_context_compression.py`

### Stop (al finalizar respuesta)
- `discourse_hook.py`
- `tool_result_cleaner.py` — TK-047
- `image_cost_detector.py` — TK-050
- `sandwich_model_detector.py` — TK-048
- `track_tokens.py`
- `compress_historial.py`
- `validate_state_checkpoint.py`

## Equivalencia en otros agentes

Para que Gemini/ChatGPT ejecuten los mismos scripts, deben hacerlo
**manualmente al inicio de sesión** (ver adapters/gemini/ y adapters/chatgpt/).
