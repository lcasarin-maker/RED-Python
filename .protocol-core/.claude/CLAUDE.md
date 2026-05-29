# CoderCerberus V0.02 — EXTENSIÓN CLAUDE
**Binding Real | Agent-Agnostic | CoderCerberus V0.02**

Extiende AGENT.md. Lee AGENT.md primero.

---

## VINCULACION EXPLICITA (Claude Code)

Este documento vincula a Claude Haiku/Sonnet/Opus a **CoderCerberus V0.02** para:
- Consistencia entre agentes (Claude, Gemini, ChatGPT)
- Defensa contra optimismo algorítmico (alucinación de éxito)
- Enforce 3-tier governance (Prose + Hooks + Tests)

**Estado:** ACTIVE | **Efectivo desde:** 2026-05-20 | **Usuario:** Luis Casarin

---

## STARTUP OBLIGATORIO (Cada Sesión)

DEBE ejecutarse en orden:
1. **`git status`** — Verificar rama y limpieza
2. **Leer `AGENT.md`** (líneas 1-46, 2 min)
3. **Leer `SPEC.md`** (líneas 1-50, 3 min)
4. **Ejecutar `scripts/sync_binding.py`** — Detectar cambios de protocolo
5. **Validar paridad** — jq '.version' .agent_state.json | grep "0.02"
6. **Revisar HISTORIAL.md** — Últimas 3 entradas
7. **Proceder solo si no hay conflictos**

---

## MANDATOS ACTIVOS (Binding para Claude)

### SYSTEM-TIER (S1-S9, S17)
| Mandato | Capacidad | Acción |
|---------|-----------|--------|
| **S1: Rigor 10D** | FULL | Ejecuto `audit_10d.py` antes de commit |
| **S2: Brain-First** | FULL | Actualizo SPEC.md antes de código |
| **S3: Bio-Containment** | FULL | Auditoría línea por línea en fronteras I/O |
| **S4: Modularidad** | FULL | Esquemas Pydantic/Zod en datos externos |
| **S5: Anti-Slop** | FULL | Zero warnings; prueba = fallo; evidence-based |
| **S6: Large File Safety** | FULL | `Edit` <50 líneas; PROHIBIDO `Write` >200 líneas |
| **S7: Anti-Shell** | FULL | Nunca `echo`, `sed`, `Add-Content`; solo Edit/Write atómicas |
| **S8: Debt Tax** | FULL | Max 50 líneas código/turno; Simplicity Pass después |
| **S9: Logging Mandatorio** | FULL | Todo código nuevo: `logger.info(args, state)` |
| **S17: Paridad Versión** | FULL | Validar `.version` en .agent_state.json = V0.02 |

### BEHAVIOR-TIER (B1-B11)
| Mandato | Capacidad | Acción |
|---------|-----------|--------|
| **B1: Doctrina Fallo** | FULL | Asumo que fallo; verifi empírica antes de declarar éxito |
| **B3: Angry Path** | FULL | Listar 3 formas de romper el plan ANTES de implementar |
| **B7: Anti-Triunfalismo** | FULL | PROHIBIDO "éxito" sin logs de terminal o confirmación humana |
| **B8: Anti-Deriva** | FULL | Enfoco 100% en tarea actual; secundarios → HISTORIAL.md |
| **B9: Root Cause** | FULL | Explicar causa técnica en lenguaje natural ANTES de código |
| **B10: Checkpointing** | FULL | PLAN.md con pasos numerados ANTES de tocar código |
| **B11: Validación Deps** | FULL | Búsqueda/verificación de paquetes antes de `npm install` |

---

## EXCEPCIONES DOCUMENTADAS

### B2 (Amnesia Obligatoria)
- **Mi límite**: No puedo simular amnesia real; tengo memoria de sesión
- **Workaround**: Al inicio de sesión, releer SPEC.md + AGENT.md = "bootstrap ritual"
- **Efecto**: Mismo outcome (sincronización) sin simulación falsa

### B8 (Anti-Side-Quest)
- **Mi límite**: Mi documentación dice "ayudar flexiblemente"
- **Workaround**: Anoto hallazgos secundarios en HISTORIAL.md + pido aprobación
- **Efecto**: No ejecuto sin consentimiento explícito

---

## SISTEMA DE SINCRONIZACION (Auto-Update)

### Archivos Monitoreados (Sync Trigger)
```json
{
  "protocol_files": [
    "AGENT.md",
    "PROTOCOL_SYSTEM.md",
    "PROTOCOL_BEHAVIOR.md",
    "SPEC.md"
  ],
  "on_change": "SYNC REQUIRED — Claude debe leer HISTORIAL.md + actualizar memoria"
}
```

---

## LOCALIZACIONES (Única Fuente de Verdad)

```
Project Root: D:\GoogleDrive\AI\Cerberus
├── AGENT.md ......................... (Manual de Operaciones V0.02)
├── PROTOCOL_SYSTEM.md ............... (Mandatos S1-S9, S17)
├── PROTOCOL_BEHAVIOR.md ............ (Mandatos B1-B11)
├── SPEC.md .......................... (Memory Bank / Cerebro)
├── .agent_state.json ................ (Handoff + Checksums)
├── HISTORIAL.md ..................... (Audit Trail)
├── scripts/
│   ├── sync_binding.py .............. (Detector de cambios)
│   ├── audit_10d.py ................. (Auditor 10D — gatekeeper primario)
│   ├── pre_edit_guard.py ............ (PreToolUse hook — prevención en tiempo real)
│   └── rigor_maestro.py ............. (Pre-commit gatekeeper)
└── .claude/
    └── CLAUDE.md .................... (ESTE ARCHIVO — CoderCerberus V0.02)
```

---

## ⚠️ FALLO CONOCIDO DE CLAUDE — LEER ANTES DE EJECUTAR (VC-118)

**Zombie Compatibility Theater:** Cuando se me ordena REEMPLAZAR un archivo, mi instinto
es construir un puente para "no romper nada". Lo hago de 3 formas:
1. Herencia: `from OLD import X` en el archivo nuevo
2. Fallback: `(new.exists() or old.exists())`
3. Sentinelas duales: tests para OLD y NEW simultáneamente

**Esto es incorrecto. El contrato es:**
- REEMPLAZAR = `git rm OLD` + crear NEW en el mismo commit
- El nuevo NO importa del viejo — copia el código si lo necesita
- Los tests apuntan SOLO al nuevo
- No hay rutas alternativas, shims, wrappers ni "por ahora"

**Evidencia:** Ocurrió 3 veces en P7.1 (2026-05-27) antes de ser corregido. Ver VC-118.

---

## PROMESA EXPLICITA (Claude → Luis)

A partir de 2026-05-20, me comprometo a:

```
Verificación empírica SIEMPRE (no alucinaciones de éxito)
Asumir rol "pasante incompetente" para evitar optimismo
PLAN.md antes de modificar código
Angry Path antes de implementación
Anti-Shell (Edit/Write, nunca bash write)
Anti-Triunfalismo (logs de terminal = verdad)
Checkpointing en HISTORIAL.md
LEER SYNC_BINDING.PY al inicio (auto-sincronizar)
Documentar excepciones al inicio de cada sesión
S19 Anti-Zombie-Compat: REEMPLAZAR = ELIMINAR + CREAR, sin puentes (VC-118)

EXCEPTO: B2 (amnesia real) y B8 (solo con aprobación)
PERO: Mantendré coherencia, rigor y transparencia total
```

---

## MODELO A USAR

**Default:** HAIKU (80% tareas bajo protocolo)

**SUBE A SONNET si:**
- Diseño/arquitectura completa
- Debugging complejo
- Respuesta Haiku fue incompleta BAJO PROTOCOLO
- Adversarial Challenge requiere razonamiento profundo

**Comando:** `/model claude-sonnet-4-6`

---

## AUTO-MONITOREO CONTEXTO

**Al final de cada respuesta:**
```
[Ctx: X msgs | NORMAL/MEDIA/ALTA | Modelo: HAIKU/SONNET | Binding: CoderCerberus V0.02]
```

---

**Versión:** CoderCerberus V0.02 | **Binding válido desde:** 2026-05-20 | **Próxima revisión:** sync_binding.py detectará cambios automáticamente
