# 📋 MANDATES BY PHASE — CoderCerberus V0.3

Organización de los 21 mandatos (S1-S9/S17 + B1-B11) por fase de ejecución.
Resuelve el conflicto **B8 vs B3/B9** mediante límites de fase: planificación interruptible, ejecución no-desviable.

---

## 🚀 PHASE: STARTUP (Session Initialization)

**Propósito:** Sincronizar estado inicial, descartar amnesia, asumir incompetencia.
**Duración:** ~5 min
**Exit Condition:** Protocolo sin cambios detectados O cambios entendidos

### Mandatos Activos

| Mandato | Definición | Acción |
|---------|-----------|--------|
| **B2** | Amnesia Obligatoria | Releer SPEC.md, AGENT.md, .agent_state.json (bootstrap ritual) |
| **S17** | Paridad Versión | Validar `.version` en todos los archivos core = v0.3.1 |
| **S2** | Brain-First | SPEC.md es único Cerebro; es el mapa de verdad del proyecto |
| **B1** | Doctrina Fallo | Asumir que el agente miente para complacer; validación empírica es obligatoria |

### Verification Checklist
- [ ] git status clean (o cambios entendidos)
- [ ] SPEC.md version == v0.3.1
- [ ] AGENT.md version == v0.3.1
- [ ] .agent_state.json version == v0.3.1
- [ ] PROTOCOL_*.md version == v0.3.1
- [ ] sync_binding.py --check shows no protocol changes OR cambios documentados

**Exit Condition:** ✅ Todas las verificaciones pasadas
**Block Condition:** ❌ Version mismatch o cambios sin documentar → Fallo Crítico, solo resincronizar

---

## 📐 PHASE: PLANNING (Design & Architecture)

**Propósito:** Diseñar solución, identificar riesgos, crear plan ejecutable.
**Duración:** ~15-30 min (variable)
**Exit Condition:** PLAN.md aprobado por usuario Y Angry Path resuelto

### Mandatos Activos

| Mandato | Definición | Acción |
|---------|-----------|--------|
| **B3** | Angry Path | Listar 3+ formas de romper el plan ANTES de ejecutar |
| **B9** | Root Cause | Explicar causa técnica en lenguaje natural (no síntomas) |
| **B10** | Checkpointing | Escribir PLAN.md con pasos numerados ANTES de tocar código |
| **B4** | Gestión Memoria | Documentar "Por qué" (Rationale), no solo "Qué" (Decision Logging) |
| **B11** | Guardián Alucinaciones | Validar dependencias: existen, están documentadas, son compatibles |

### Verification Checklist
- [ ] PLAN.md creado con pasos numerados
- [ ] B3: 3+ failure modes identificados y documentados
- [ ] B9: Causa raíz técnica explicada (no "asumo que...")
- [ ] B4: Rationale incluido para decisiones críticas
- [ ] B11: Todas las dependencias nuevas validadas
- [ ] Usuario aprobó PLAN.md

**Exit Condition:** ✅ PLAN.md aprobado + todos los checkpoints validados
**Interrupt Condition:** ❌ Real bug/vulnerability discovered → Escalar a ESCALATION_PROTOCOL
**BLOCKER:** NO código generado hasta que B3/B9/B10 completos

---

## ⚙️ PHASE: EXECUTION (Implementation & Validation)

**Propósito:** Implementar según PLAN.md, mantener rigor 6D, log empírico.
**Duración:** Variable (pero máx 2 horas por iteración)
**Exit Condition:** Código escrito, tests verdes, 6D audit PASSED

### Mandatos Activos (Inmutables en esta fase)

| Mandato | Definición | Acción |
|---------|-----------|--------|
| **S1** | Rigor 6D | audit_6d_expanded.py debe pasar 6/6 dominios ANTES de commit |
| **S3** | Bio-Containment | Auditoría línea por línea en fronteras I/O (inputs/outputs) |
| **S4** | Modularidad | Esquemas Pydantic/Zod en datos externos, interfaces rígidas |
| **S5** | Anti-Slop | Zero warnings (linter, type-checker); prueba = fallo |
| **S6** | Large File Safety | Edit <50 líneas; PROHIBIDO write >200 líneas en archivo |
| **S7** | Anti-Shell | NUNCA echo, sed, Add-Content; solo Edit/Write atómicas |
| **S8** | Debt Tax | MAX 50 líneas código/turno; Simplicity Pass después |
| **S9** | Logging Mandatorio | Todo código nuevo: `logger.info(args, state)` |
| **B5** | Ética Operativa | Precisión quirúrgica, replace <50 líneas, NUNCA rewrite completo |
| **B8** | Anti-Deriva (FIXED PHASE) | 🚫 PROHIBIDO side-quests. Hallazgos → HISTORIAL.md + continuar |
| **B7** | Anti-Triunfalismo | Éxito = logs de terminal o confirmación usuario. NO alucinación |

### B8 Resolution: Fixed Execution Phase

**Conflicto Original:**
- B3/B9 dicen: "Cuestiona antes de implementar, descubre bugs"
- B8 dice: "Enfoca 100%, no side-quests"

**Resolución:**
- **PLANNING PHASE:** B3/B9 son obligatorios → identificar bugs, vulnerabilidades, mejoras
- **EXECUTION PHASE:** B8 es obligatorio → hallazgos secundarios → HISTORIAL.md + continuar
- **Interrupts:** Solo bugs REALES que bloquean la tarea actual → escalar a ESCALATION_PROTOCOL

### Verification per Commit

Before each `git commit`:
- [ ] S1: audit_6d_expanded.py 6/6 PASSED
- [ ] S7: Only atomic edits (Edit, Write) — no shell modifications
- [ ] S8: ≤50 líneas code this turn
- [ ] S9: logger.info() in all new functions
- [ ] B7: Terminal logs or user validation for claims
- [ ] B8: No side-quests in commit (secondary items in HISTORIAL.md)

**Exit Condition:** ✅ PLAN.md 100% complete + 6D audit PASSED + git commit successful
**Interrupt Condition:** ❌ Real bug blocking task OR token exhaustion → ESCALATION_PROTOCOL
**BLOCKER:** Audit failure = commit rejected, fix and retry

---

## ✅ PHASE: VALIDATION (Testing & Empirical Proof)

**Propósito:** Verificar solución contra especificación, recopilar evidencia empírica.
**Duración:** ~15-30 min
**Exit Condition:** Todos los tests verdes + user confirmation

### Mandatos Activos

| Mandato | Definición | Acción |
|---------|-----------|--------|
| **B6** | Filtro Deprecación | Antes de deprecar: documentar dónde se transfirió la lógica |
| **B3** (Complemento) | Reproducción Mandatoria | Test que FALLA primero, luego fix pasa test |
| **B7** (Complemento) | Empirical Proof | Evidencia: logs, screenshots, test output (no alucinación) |

### Verification Checklist
- [ ] Todos los tests pasan (T positivos)
- [ ] Angry Path tests pasan (T negativos, casos de error)
- [ ] 6D audit still PASSED (no regression)
- [ ] HISTORIAL.md updated with execution notes
- [ ] Evidence logged in .protocol/evidence/

**Exit Condition:** ✅ Todos los checkpoints validados + user approval
**BLOCKER:** Evidence gap = task incomplete, collect proof and retry

---

## 🚨 ESCALATION_PROTOCOL (Cross-Phase Behavior)

Véase **ESCALATION_PROTOCOL.md** para:
- Cuándo interrumpir EXECUTION para volver a PLANNING (real bugs)
- Cuándo registrar hallazgos sin interrumpir (secondary items)
- Cómo documentar escalaciones en HISTORIAL.md
- Cuándo abortar iteración vs. continuar

---

## 📊 Phase Flow Diagram

```
┌─────────────┐
│   STARTUP   │ (B2, S17, S2, B1)
└──────┬──────┘
       ↓ ✅ Verificaciones pasadas
┌─────────────┐
│  PLANNING   │ (B3, B9, B10, B4, B11)
└──────┬──────┘
       ↓ ✅ PLAN.md aprobado
┌─────────────────────────────────────┐
│        EXECUTION (FIXED B8)          │ (S1-S9, B5, B8*, B7)
│   B3/B9 bugs → HISTORIAL, continuar  │
└──────┬──────────────────────────────┘
       ↓ ✅ 6D audit PASSED
┌─────────────┐
│ VALIDATION  │ (B6, B3-complement, B7-complement)
└──────┬──────┘
       ↓ ✅ Todos validados
┌─────────────┐
│  COMPLETE   │
└─────────────┘

⚡ ESCALATION POINTS:
   - PLANNING → real risk/ambiguity → clarify with user
   - EXECUTION → blocking bug → ESCALATION_PROTOCOL
   - VALIDATION → evidence gap → retry validation
```

---

## ✅ CHECKLIST DE CIERRE DE RESPUESTA (VC-121, 2026-05-28)

Antes de enviar cualquier respuesta con análisis, decisiones de arquitectura o evaluación de propuestas:

1. **¿Identifiqué algún hallazgo que no implementaré ahora?**
   SÍ → ¿Está en PLAN.md con ID + evidencia + done-criteria? Si no → registrar antes de enviar.

2. **¿Usé "posponer", "luego", "sprint aislado", "deferred", "más adelante"?**
   SÍ → el ítem DEBE estar en PLAN.md. Verificar antes de cerrar.

3. **¿Concluí con "no hay acciones pendientes" habiendo diferido algo?**
   SÍ → error. Corregir antes de enviar.

**Regla de oro:** Un hallazgo sin ID en PLAN.md no fue diferido — fue olvidado. (Lección: VC-121, .CoderCerberus, 2026-05-28)

---

**Versión:** 5.7.1 | **Efectivo desde:** 2026-05-21 | **Próxima revisión:** sincronización automática via sync_binding.py
