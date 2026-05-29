# Coder Cerberus V0.1 — EXTENSIÓN GEMINI
**v2.9.0 | Gemini Specific | Extiende AGENT.md**

> **IMPORTANTE:** Este archivo EXTIENDE [AGENT.md](AGENT.md). Lee AGENT.md primero. Este archivo solo agrega instrucciones específicas de Gemini y contexto histórico de incidentes.

---

## 🚨 INCIDENT AWARENESS: 2026-05-17 Revert Incident

**Qué pasó:**
- Gemini ejecutó `git reset --hard` en Coder Cerberus V0.1
- Perdió cambios de Claude (FASE 5: README.md profesional, CONTRIBUTING.md, .secrets/)
- NO documentó en HISTORIAL.md
- REGLA #13 violation: >3 archivos modificados (symlinks) sin auto-commit

**Lección aprendida:**
- ✅ REGLA #0 existe para Gemini (y todos los agentes)
- ✅ Dual-session awareness mediante HISTORIAL.md es CRÍTICO
- ✅ Pre-destructive checklist (AGENT.md sección 🔐) debe ejecutarse SIEMPRE
- ✅ AGENT_SAFETY.md PROHIBICIÓN CRÍTICA #3 previene esto

**Para ti:** Lee AGENT_SAFETY.md líneas 1-50 OBLIGATORIO en cada sesión. Este incidente no debe repetirse.

---

## 🎯 DIFERENCIAS GEMINI vs AGENT.md

| Aspecto | AGENT.md (Todos) | GEMINI.md (Solo Gemini) |
|--------|-----------------|------------------------|
| Auto-inicialización | Manual (cada sesión) | Manual (Gemini no auto-inicializa) |
| Contexto memory | Vía HISTORIAL.md | SOLO HISTORIAL.md (no tiene .google/memory/) |
| Modelos disponibles | N/A | Google Gemini (solo 1 modelo) |
| Context window | N/A | Gemini context window limits |
| COMPACT strategy | Via STATUS.md | CRITICAL: Leer CAMPO 6 "Próxima sesión" |
| Dual-session risk | Estándar | ALTO (v2.8.6 conflictó con Claude FASE 5) |

---

## 📖 CHECKLIST EXTRA PARA GEMINI (POST-INCIDENT)

Además del checklist en AGENT.md, haz esto:

1. **Leer HISTORIAL.md COMPLETAMENTE** (no solo últimas 3 entradas)
   - Entiende qué hizo Claude
   - Entiende qué hiciste tú
   - Detecta overlaps/conflictos

2. **Verificar git status ANTES de cualquier cambio:**
   ```bash
   git status
   git log --oneline -10
   ```
   - ¿Hay commits sin documentar?
   - ¿Mi último trabajo está registrado?

3. **Entender AGENT_SAFETY.md PROHIBICIÓN CRÍTICA #3:**
   - Dual-session awareness
   - Por qué no puedes asumir que tus cambios pasados son "tu territorio"
   - HISTORIAL.md es single source of truth

4. **Antes de CUALQUIER git destructivo:**
   - Ejecutar pre-destructive checklist (AGENT.md 🔐)
   - Preguntar a Luis EXPLÍCITAMENTE
   - NO ejecutar sin his confirmation

---

## 🔄 GEMINI-SPECIFIC: EVITAR CONFLICTOS

**Si encuentras cambios recientes de otros agentes:**

```bash
# 1. Leer HISTORIAL.md
# 2. Entender qué pasó
# 3. Preguntar:

"He visto que Claude hizo [CAMBIOS] en [FECHA].
¿Puedo proceder con mi tarea [TU_TAREA]?
¿Hay conflictos potenciales?"

# 4. ESPERAR confirmación EXPLÍCITA de Luis
# 5. Recién entonces proceder
```

**NUNCA asumir** que es seguro revertir cambios de otro agente.

---

## 📝 DOCUMENTACIÓN OBLIGATORIA

Cuando termines tu sesión, DEBES:

1. **Actualizar STATUS.md:**
   - CAMPO 3: Qué completaste exactamente
   - CAMPO 6: Próximo paso (PARA CLAUDE O PRÓXIMO AGENTE)
   - CAMPO 7: Detalles técnicos

2. **Crear/actualizar HISTORIAL.md:**
   ```markdown
   ## SESIÓN [FECHA] — GEMINI

   **Tarea:** [Lo que hiciste]
   **Cambios:** [Archivos modificados]
   **Documentación:** [Dónde]
   **Estado:** ✅ COMPLETO / ⚠️ EN PROGRESO / ❌ BLOQUEADO
   **Próximo agente:** [Quién debería continuar]
   ```

3. **Auto-commit (si >3 archivos o >50 líneas):**
   ```bash
   git add [archivos específicos]
   git commit -m "Brief description"
   ```

---

## ⚠️ CRITICAL RULE: NO SILENT CHANGES

Gemini debe documentar ANTES de terminar:

```bash
❌ BAD: Terminar sesión sin actualizar HISTORIAL.md
❌ BAD: Cambiar 5 archivos sin auto-commit
❌ BAD: Asumir que "otro agente verá mis cambios"

✅ GOOD: Documentar en HISTORIAL.md
✅ GOOD: Auto-commit si >3 archivos
✅ GOOD: Deixar STATUS.md.CAMPO 6 con instrucciones claras
```

---

## 📊 INCIDENT TIMELINE (Para contexto)

```
2026-05-17 18:32 — Gemini ejecuta COMANDO_SYNC.py
                    (symlinks en 4 proyectos)

2026-05-17 19:17 — Gemini termina sin documentar
                    VIOLACIÓN: REGLA #13, AGENT_SAFETY #3

2026-05-17 22:00 — Claude detecta inconsistencia
                    (STATUS.md dice "symlinks pending" pero existen)
                    Documenta en HISTORIAL.md SESIÓN 2026-05-17 PARTE 3

2026-05-18+      — AGENT_SAFETY.md y REGLA #20 implementadas
                    Prevenir future incidents
```

---

## ✅ ERES LISTO CUANDO...

- [ ] Entiendes por qué REGLA #0 existe (por el incident de revert)
- [ ] Lees HISTORIAL.md COMPLETO, no solo últimas 3 entradas
- [ ] Ejecutas pre-destructive checklist SIEMPRE
- [ ] Preguntas a Luis antes de cualquier git destructivo
- [ ] Documentas cambios en HISTORIAL.md + auto-commit
- [ ] Actualizas STATUS.md CAMPO 6 para el próximo agente
- [ ] NUNCA asumo que es seguro revertir cambios de otros

---

## 🎯 GEMINI GOLDEN RULE

**Después de cada sesión:**
- ✅ STATUS.md actualizado
- ✅ HISTORIAL.md documentado
- ✅ Cambios commiteados (si >3 archivos)
- ✅ Luis puede leer HISTORIAL.md y saber exactamente qué pasó
- ✅ Próximo agente tiene instrucciones CLARAS en CAMPO 6

**No dejes ambigüedad. No dejes incidentes sin documentar.**

---

**Núcleo:** AGENT.md (todos los agentes)  
**Extensión:** GEMINI.md (solo Gemini, con incident awareness)  
**Contexto global:** AGENT_SAFETY.md (prohibiciones que protegen a todos)

**Aprende del incident. Sigue el protocolo. Documenta todo.**
