# PROMPTS RÁPIDOS — CoderCerberus v0.02
Activadores + métricas de uso. Solo usar si CONDICIÓN = verdad.

---

## 1. REANUDAR SESIÓN
**Cuándo:** Toda sesión nueva O después de compactación
**Acción:**
```
git status
python scripts/sync_binding.py --check
```
**Condición de éxito:** No hay conflictos de protocolo. Branch limpia.

## 2. PENSAR EN VOZ ALTA (Reasoning Checkpoint)
**Cuándo:** Antes de tocar código. Bloqueador = "No sé por dónde empezar"
**Acción:** Explicar causa raíz en natural + 3 Angry Paths + precondiciones
**Condición de éxito:** Puedo escribir PLAN.md con pasos numerados

## 3. NO ENTIENDO (Blockers)
**Cuándo:** >2 supuestos sin verificar en el SPEC
**Acción:** Documentar supuestos en HISTORIAL.md + detenerse
**Condición de éxito:** No avanzo sin preguntar. Umbral B9 respetado.

## 4. GASTAR MENOS TOKENS
**Cuándo:** Contexto >30 msgs O Ctx % > 60%
**Acción:** `/compact` O reducir respuesta a 5 líneas prosa + código
**Condición de éxito:** Siguiente turno reutiliza cache prompt (<300 tokens input)

## 5. MIEDO DE ROMPER ALGO
**Cuándo:** Voy a ejecutar destructive op (git push, edit config, delete)
**Acción:** (1) commit estado limpio, (2) 3 Angry Paths, (3) pytest -v, (4) LUEGO ejecutar
**Condición de éxito:** Tests pasan antes de destructive op. Git log muestra checkpoint.

## 6. TAREA GRANDE (>5 turnos)
**Cuándo:** Plan requiere múltiples turnos OR cambios en 5+ archivos
**Acción:** PLAN.md numerado + B3 Angry Path + checkpoint git cada 3 turnos
**Condición de éxito:** PLAN.md existe. Cada 3 turnos hay commit funcional.

## 7. ANTES DE SALIR
**Cuándo:** Final de sesión. OBLIGATORIO si: protocolo modificado OR cambios sin commit
**Acción:** 
```
git commit (si cambios pendientes)
python scripts/sync_binding.py --update (si protocolo modificado)
python scripts/sync_binding.py --check (validar update)
HISTORIAL.md: Documentar retrospective JSON (B21)
```
**Condición de éxito:** git status = limpio. sync_binding --check = sin cambios pendientes.

---

**Uso:** Copiar bloque SI condición es verdad. No usar "por si acaso".
**Métrica:** Si 5+ sesiones usan el mismo template, es validado.
