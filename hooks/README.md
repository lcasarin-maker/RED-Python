# Hooks — CoderCerberus V0.5

Automatización de TK-rules para optimización de tokens.

## Estructura

```
hooks/
├── pre_write.sh              ← TK-049: Bloquear auto-docs
├── post_tool_result.sh       ← TK-047: Limpiar resultados gigantes
├── pre_model_selection.sh    ← TK-044: Límites thinking
│                            ← TK-045: Router de modelos
├── pre_screenshot.sh         ← TK-050: Detectar imágenes innecesarias
└── README.md                 ← Este archivo
```

## Hooks Activos (Fase 1)

### pre_write.sh — TK-049
**Cuándo:** Antes de Write/Create de archivos
**Qué hace:** Bloquea generación automática .md/.json/.yaml sin solicitud explícita
**Excepciones:** SPEC.md, PLAN.md, HISTORIAL.md, .agent_state.json, VERSION.txt
**Salida:** Error + sugerencia para describir en chat

### post_tool_result.sh — TK-047
**Cuándo:** Después de ejecutar herramienta (grep, find, git, ls, cat)
**Qué hace:** Trunca resultados > 5K tokens
**Estrategias:**
- grep: máximo 20 líneas
- find: máximo 10 items
- git log: máximo 3 commits
- git diff: máximo 50 líneas
- ls: máximo 50 items
- cat: máximo 100 líneas
**Salida:** Resultado limpiado + log de tokens ahorrados

### pre_model_selection.sh — TK-044, TK-045
**Cuándo:** Antes de seleccionar modelo
**Qué hace:**
- TK-044: Limita reasoning tokens en tareas simples
- TK-045: Recomienda modelo (Haiku/Sonnet/Opus)
**Lógica:**
- Haiku: <10K tokens, tareas simples (80% asignación)
- Sonnet: <50K tokens, tareas moderadas (15% asignación)
- Opus: estratégicas, críticas (5% asignación)
**Salida:** Settings de thinking + recomendación de modelo

### pre_screenshot.sh — TK-050
**Cuándo:** Antes de tomar screenshot
**Qué hace:** Detecta imágenes innecesarias y sugiere alternativas
**Costo:** 1000 tokens base + 2 tokens/KB
**Críticas permitidas:** UI layouts, diseño mockups, devtools
**Desaconsejadas:** errores terminal, JSON, archivos pequeños
**Salida:** Advertencia sobre costo (no bloquea)

---

## Integración

### Requisitos
- Python 3.7+
- `jq` (para parsing JSON en bash)
- Scripts en `D:\AI\Cerberus\scripts/`
- Configs en `D:\AI\Cerberus\rules/`

### Activación
1. Copiar hooks a `.git/hooks/` o sistema de pre/post hooks
2. Hacer ejecutables: `chmod +x hooks/*.sh`
3. Registrar en Claude Code settings o pre-commit hooks

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

## Impacto

**Fase 1 (5 hooks):** -35% tokens/sesión

| TK | Impacto |
|---|---|
| TK-044 (Thinking) | -20% |
| TK-045 (Router) | -15% |
| TK-047 (Cleaner) | -25% |
| TK-049 (No auto-docs) | -8% |
| TK-050 (Images) | -12% |

---

## Configuración

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

## Próximas Fases

**Fase 2 (Próxima sprint):**
- TK-048: Sandwich model detector (2-fase execution)
- Refinamiento de thresholds basado en datos reales
- Rolear a todas 16 satélites

**Fase 3 (Manual):**
- TK-046: Sub-agentes (decisión estratégica, no automatizable)

---

**Última actualización:** 2026-06-01 | **Status:** Fase 1 COMPLETA
