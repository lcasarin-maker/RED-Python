# REGLA #21 — POST-SESSION RETROSPECTIVE CHECKLIST

**Origen de inspiración:** [timothyjrainwater-lab/multi-agent-coordination-framework](https://github.com/timothyjrainwater-lab/multi-agent-coordination-framework) — "Post-Debrief Retrospective"  
**Adopción:** 2026-05-17 FASE 9 (enforcement tier 3 — test-enforced)

---

## QUÉ ES

Estandarizar retrospectiva obligatoria al final de cada sesión. Antes de contexto cerrarse (COMPACT/CLEAR), agente responde 5 preguntas estructuradas. Output JSON-parseable, embebido en HISTORIAL.md.

**Por qué:** timothyjrainwater requiere "mandatory questions surface builder observations before context close". Previene que aprendizajes se pierdan y gap detection se atrasa.

---

## TEMPLATE: Retrospectiva Obligatoria

Cada sesión DEBE tener sección así en HISTORIAL.md:

```markdown
## SESIÓN [FECHA] — [AGENT_NAME]

### RETROSPECTIVE

**JSON:**
```json
{
  "session_date": "2026-05-17T20:15:33Z",
  "agent": "Claude",
  "project": "Protocolo Agentes",
  "answers": {
    "q1_learning": "Qué aprendiste que NO era obvio?",
    "q2_violation": "Qué regla violaste (si acaso)? O NINGUNO.",
    "q3_next_agent": "Qué debería el próximo agente saber?",
    "q4_protocol_gap": "Qué falta en AGENT_SAFETY.md o AGENT_ONBOARDING.md?",
    "q5_token_efficiency": {
      "efficient": true/false,
      "estimate_tokens": 50000,
      "actual_tokens": 45000,
      "note": "Brevemente por qué sí/no fue eficiente"
    }
  }
}
```

### 5 PREGUNTAS OBLIGATORIAS

**Q1: ¿Qué aprendiste que NO era obvio?**
- Respuesta: 1-3 frases
- Scope: Lecciones sobre protocolo, patterns, gaps
- Ejemplo: "Los conflictos en HISTORIAL.md ocurren cuando 2 agentes escriben misma sesión simultáneamente. Esto requiere 3-way merge."

**Q2: ¿Qué regla violaste (si acaso)?**
- Respuesta: "REGLA #X — descripción" O "NINGUNO"
- Si violation: Explica cómo se detectó + cómo se resolvió
- Ejemplo: "REGLA #13 — Modified 4 files sin auto-commit. Resuelto: commit c47e92 agrega cambios con mensaje."

**Q3: ¿Qué debería el próximo agente saber?**
- Respuesta: Contexto que NO está documentado en STATUS.md CAMPO 6
- Scope: State subtle, conflicts encountered, shortcuts/landmines, human preferences Luis expressed
- Ejemplo: "Luis prefers projects en paralelo si son independientes. Aequitas_OS y RED-Python no tienen dependencias, pero Declutter sí necesita Protocolo Agentes REGLA #15 tests primero."

**Q4: ¿Qué falta en AGENT_SAFETY.md o AGENT_ONBOARDING.md?**
- Respuesta: Feature/instruction missing que habría evitado confusion
- Scope: Protocol gaps, edge cases not covered, safety guardrail needed
- Ejemplo: "AGENT_ONBOARDING.md no menciona que .secrets/ es centralizado en raíz, no por proyecto. Agente_Inmobiliario tiene su propio .env, que confunde."

**Q5: ¿Token budget fue eficiente?**
- Respuesta: {efficient: true/false, estimate: N, actual: N, note: "..."}
- efficient = true si (actual / estimate) < 1.1 (10% overhead acceptable)
- efficient = false si overhead > 10% o early COMPACT fue necesario
- Ejemplo: 
  ```json
  {
    "efficient": true,
    "estimate_tokens": 50000,
    "actual_tokens": 48500,
    "note": "COMPACT ejecutado en msg 45. Resumen tomó 2K tokens. Overall efficiency 97%."
  }
  ```

---

## INTEGRATION: HISTORIAL.md Format

**Después de cada tarea, antes de COMPACT/CLEAR, agente DEBE añadir:**

```markdown
## SESIÓN 2026-05-17 PARTE 7 — PHASE 1 IMPLEMENTATION

**Tarea:** Crear REGLA #21 + REGLA #22

**Cambios:** 
- N5_REGLA_21_POST_SESSION_RETROSPECTIVE.md (creado)
- SOURCES_OF_TRUTH.md (creado)
- AGENT.md (actualizado — +4 líneas REGLA #21 reference)
- tests/test_regla_21_retrospective.py (creado)

**Documentación:** Cambios en CLAUDE.md, AGENT_ONBOARDING.md linked

**Estado:** ✅ COMPLETO (PR-ready, tests passing)

### RETROSPECTIVE

**JSON:**
```json
{
  "session_date": "2026-05-17T20:15:33Z",
  "agent": "Claude",
  "project": "Protocolo Agentes",
  "answers": {
    "q1_learning": "REGLA #21 aumenta overhead documentation pero detecta gaps más temprano. Retrospectives son obligatorias, no opcionales — enforcement está en git hook pre-push.",
    "q2_violation": "NINGUNO",
    "q3_next_agent": "Sources of Truth Index (REGLA #22) necesita ser actualizado cada vez que una nueva REGLA se crea o una existente cambia de autoridad. Git hook debería validar.",
    "q4_protocol_gap": "AGENT_ONBOARDING.md no menciona que retrospectives son JSON-parseable — agentes pueden exportar automáticamente a DB. Necesita clarificación.",
    "q5_token_efficiency": {
      "efficient": true,
      "estimate_tokens": 40000,
      "actual_tokens": 38500,
      "note": "No fue necesario COMPACT. REGLA #21-22 creation fue más directo que estimado."
    }
  }
}
```

---

## ENFORCEMENT: Git Hook pre-push

**Locación:** `.git/hooks/pre-push`

**Lógica:**
```bash
# Check: Latest SESIÓN in HISTORIAL.md has RETROSPECTIVE section
if ! grep -q "### RETROSPECTIVE" HISTORIAL.md; then
  echo "ERROR: Latest session missing RETROSPECTIVE section. Add answers to Q1-Q5 before pushing."
  exit 1
fi

# Check: RETROSPECTIVE has valid JSON
if ! grep -A 20 "### RETROSPECTIVE" HISTORIAL.md | grep -q "\"q1_learning\""; then
  echo "ERROR: RETROSPECTIVE JSON incomplete or malformed. Verify all 5 questions answered."
  exit 1
fi

exit 0
```

---

## REGLA #21 SPIRIT

✅ **Mandatory** — Cada sesión DEBE tener retrospective antes de COMPACT/CLEAR
✅ **Structured** — 5 preguntas específicas (no free-form)
✅ **Machine-readable** — JSON format para parseo automático
✅ **Actionable** — Detecta gaps, violations, learning, next steps
✅ **Small overhead** — 10-15 min por sesión (después de trabajo completo)

---

**Diferencia vs timothyjrainwater:** Ellos requieren manual post-debrief. Nosotros lo automatizamos via git hook + JSON export a protocol_state.db.**

