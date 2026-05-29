# PATRONES_TECNICOS.md — Patrones de Implementacion Criticos
**Fuente:** Regla #19, Regla #28, TOKEN_BUDGET framework | **Rescatado:** 2026-05-24

Tres patrones tecnicos de alta prioridad extraidos del protocolo v3.0. Ninguno de los tres estaba implementado en Cerberus V0.02 al momento del rescate.

---

## PATRON 1: State Checkpoint (Regla #19)

### Que es
HISTORIAL.md como maquina de estados donde cada checkpoint es un snapshot completo del estado del sistema.

### Cuando usarlo
Despues de cambios significativos (>50 lineas o arquitectonicos).

### Formato de checkpoint en HISTORIAL.md
```markdown
## SESION [DATE] PARTE [N] — [TAREA]

### STATE CHECKPOINT

**Timestamp:** 2026-05-24 15:30
**Agent:** Claude
**Project:** Cerberus
**Status:** COMPLETE

**Files Modified:**
- HISTORIAL.md (N insertions, N deletions)
- STATUS.md (N insertions, N deletions)

**State Hash:**
HISTORIAL.md: sha256=abc123...
STATUS.md:    sha256=def456...

**Concurrent Write Detection:**
[OK] No conflicting writes detected
[OK] No other agent modified these files in last 5 mins
[OK] HISTORIAL.md entry chain is linear (no forks)

**Next State Prerequisites:**
- [ ] All commits pushed to remote
- [ ] HISTORIAL.md is single source of truth
- [ ] No uncommitted changes remain
```

### Implementacion Python
```python
import hashlib

def compute_state_hash(file_path: str) -> str:
    """SHA256 del contenido del archivo. Para deteccion de conflictos."""
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Uso al final de sesion:
critical_files = ['HISTORIAL.md', 'STATUS.md', '.agent_state.json']
state_hashes = {f: compute_state_hash(f) for f in critical_files}
```

### Reducer logic para conflictos concurrentes
```
IF otro_agente.timestamp > mi_timestamp THEN
    Leer su entrada HISTORIAL.md
    Estrategia merge: "Sus docs + Mi implementacion" (docs tienen prioridad si contradicen)
ELSE
    Continuar normalmente
```

---

## PATRON 2: Multi-Agent Routing (Regla #28)

### Que es
HISTORIAL.md como message bus centralizado para coordinar multiples agentes/sesiones.

### Reglas de routing
1. **HISTORIAL.md es el bus:** Cada agente DEBE escribir su sesion. Formato: `## SESION [ID] — [Agent] — [Fecha]`
2. **Routing por CAMPO 5:** Si dos agentes tocan la misma REGLA → CONFLICTO → 3-way merge. Si tocan reglas diferentes → merge automatico.
3. **Formato JSON normalizado** en la retrospectiva de sesion:

```json
{
  "session_id": "uuid",
  "agent_name": "Claude|Gemini|Human",
  "rules_touched": [19, 28, 29],
  "files_modified": ["STATUS.md", "HISTORIAL.md"],
  "state_hash": "sha256_of_final_state",
  "conflict_detected": false,
  "next_agent_should_know": "..."
}
```

### Casos de uso
- **Serial (Claude → Gemini):** Claude escribe SESION 1, Gemini lee HISTORIAL.md y escribe SESION 2. Sin conflicto.
- **Concurrente (dos agentes tocan misma REGLA):** Pre-commit hook detecta conflict marker → bloquea → human review.
- **Proyectos paralelos:** Repos diferentes → no hay conflicto → ambos commits OK.

### Script de validacion existente
`scripts/validate_routing.py` — verifica formato JSON en retrospectivas antes de commit.

---

## PATRON 3: Token Budget Framework

### Estructura del contexto (200K tokens)
```
Total: 200,000 tokens
├─ Base Context (inmutable): 50,000 tokens
│  ├─ System prompt: ~10K
│  ├─ SPEC.md + AGENT.md + manifests: ~20K
│  ├─ Plan file: ~10K
│  └─ Memory files: ~10K
├─ Working Space: 100,000 tokens
│  └─ Implementation, tool calls, responses
└─ Headroom (margen de seguridad): 20,000 tokens
   └─ Checkpoint de compresion activado a 130K usados
```

### Reglas de headroom
| Tokens restantes | Estado | Accion |
|------------------|--------|--------|
| > 20K | SAFE | Continuar normalmente |
| 20-30K | WARNING | Comprimir antes de siguiente operacion grande |
| < 20K | HARD STOP | Parar + comprimir + nueva sesion |

### Schema .agent_state.json (agregar a cada sesion)
```json
{
  "session_token_budget": {
    "session_start_tokens": 0,
    "base_context_tokens": 50000,
    "tokens_used_so_far": 0,
    "tokens_remaining_headroom": 20000,
    "compressions_this_session": [],
    "reversals_and_costs": []
  }
}
```

### Escalacion por reversals
Si `cumulative_waste > 30000` O `reversal_count > 2` en la misma tarea:
1. Log en HISTORIAL.md con analisis
2. Preguntar al usuario: "3+ reversals detectados. Tokens desperdiciados: 30K+. Opciones: A) continuar, B) revision de arquitectura, C) enfoque diferente"

---

## ESTADO DE IMPLEMENTACION

| Patron | Implementado | Ubicacion |
|--------|-------------|-----------|
| State Checkpoint (Regla #19) | PARCIAL | `scripts/validate_routing.py` tiene parte |
| Multi-Agent Routing (Regla #28) | PARCIAL | `scripts/validate_routing.py` |
| Token Budget | NO | Pendiente en `.agent_state.json` schema |

**Tarea pendiente:** Actualizar `.agent_state.json` con campo `session_token_budget`.
