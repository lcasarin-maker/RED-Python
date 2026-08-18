# RULE #21 - Post-session retrospective checklist

**Inspiration:** [timothyjrainwater-lab/multi-agent-coordination-framework](https://github.com/timothyjrainwater-lab/multi-agent-coordination-framework) - "Post-Debrief Retrospective"
**Adoption:** 2026-05-17 Phase 9
**Enforcement:** RULE #21 [TEST-ENFORCED] — corregido el 2026-08-17. Hasta esa
fecha el documento declaraba "enforcement tier 3 - test-enforced" y NINGUN test
de `tests/` mencionaba la regla ni la retrospectiva (`grep -rl 'REGLA_21\|RULE
#21\|retrospectiv' tests/` no devolvia nada) -- afirmar un test que no existe
es la misma mentira que un inventario que nombra archivos borrados.

Pagado, no ocultado: `scripts/validate_retrospective.py` implementa el
esquema de las 5 preguntas (extrae la ultima sesion de `HISTORIAL.md`, parsea
su bloque `### RETROSPECTIVE` y valida las claves `q1..q5`), y
`tests/test_regla_21_retrospective.py` lo prueba con una bateria RED: rompe a
proposito cada cosa que la regla prohibe (clave faltante, JSON malformado,
seccion `RETROSPECTIVE` ausente, `q5_token_efficiency` con forma o tipos
incorrectos, `q2_violation` vacio) y comprueba que el validador SI lo detecta.
Demostrado saboteando el validador (`validate_retrospective_schema` forzado a
devolver `[]` siempre) y confirmando que 5 de los 15 tests fallan contra esa
version rota antes de restaurarla -- un test que nunca ha fallado no ha
demostrado nada, y este si fallo cuando se le rompio a proposito lo que debia
atrapar.

**RULE #22** [PROSE-ONLY] (Sources of Truth Index, SPEC vs POLICY --
catalogada en `docs/architecture/AGENT_ONBOARDING_RULES.md`) es una regla
DISTINTA que este documento nunca definio por si mismo, solo la mencionaba de
pasada junto a la #21 (mismo "Enforcement", mismo "Task: Create RULE #21 +
RULE #22" de ejemplo). Su sujeto real es `SOURCES_OF_TRUTH.md` -- confirmado
por el propio historial vendorizado de este repo
(`tests/automation_test_regla_22_sources_index.py`, borrado junto con el resto
de `.protocol-core/`) -- y ese archivo se borro el 2026-08-17 (commit
`1b2ede2`, mensaje: "borrados por existir unicamente para Cerberus/Golden
Standard"). Escribir hoy un test que exija `SOURCES_OF_TRUTH.md` resucitaria,
el mismo dia, exactamente lo que otro commit acaba de borrar por sobrar.
No es "no soy capaz de probarlo"; es "el propio repo ya decidio que no lo
necesita". Clasificacion honesta: retirada -- nadie, ni humano ni codigo, la
aplica hoy, y no se espera que alguien lo haga. `[PROSE-ONLY]` es la exencion
mas cercana que el detector de goodcode entiende (sus dos unicos marcadores
son `[FUTURE]` y `[PROSE-ONLY]`; no tiene vocabulario para "retirada") -- el
argumento real esta escrito aqui, no en la etiqueta.

---

## What it is

Make a mandatory retrospective at the end of every session. Before context is closed
(COMPACT/CLEAR), the agent answers 5 structured questions. Output must be JSON-parseable
and embedded in `HISTORIAL.md`.

## Mandatory retrospective template

Each session must include a section like this in `HISTORIAL.md`:

```markdown
## SESSION [DATE] - [AGENT_NAME]

### RETROSPECTIVE

**JSON:**
```json
{
  "session_date": "2026-05-17T20:15:33Z",
  "agent": "Claude",
  "project": "Protocolo Agentes",
  "answers": {
    "q1_learning": "What did you learn that was not obvious?",
    "q2_violation": "What rule did you violate, if any? Or NONE.",
    "q3_next_agent": "What should the next agent know?",
    "q4_protocol_gap": "What is missing in AGENT_SAFETY.md or AGENT_ONBOARDING.md?",
    "q5_token_efficiency": {
      "efficient": true,
      "estimate_tokens": 50000,
      "actual_tokens": 45000,
      "note": "Brief reason why it was or was not efficient"
    }
  }
}
```

### The 5 required questions

**Q1: What did you learn that was not obvious?**
- 1-3 sentences.
- Scope: protocol lessons, patterns, gaps.

**Q2: What rule did you violate, if any?**
- Answer: `RULE #X - description` or `NONE`.
- If there was a violation, explain how it was detected and resolved.

**Q3: What should the next agent know?**
- Context that is not already in `STATUS.md` field 6.
- Include subtle state, conflicts, shortcuts, landmines, and human preferences.

**Q4: What is missing in AGENT_SAFETY.md or AGENT_ONBOARDING.md?**
- The missing instruction or guardrail that would have prevented confusion.

**Q5: Was the token budget efficient?**
- Answer:

```json
{
  "efficient": true,
  "estimate_tokens": 50000,
  "actual_tokens": 48500,
  "note": "COMPACT executed at message 45. Summary took 2K tokens. Overall efficiency 97%."
}
```

---

## HISTORIAL.md integration

After each task, before COMPACT/CLEAR, the agent must append:

```markdown
## SESSION 2026-05-17 PART 7 - PHASE 1 IMPLEMENTATION

**Task:** Create RULE #21 + RULE #22

**Changes:**
- N5_REGLA_21_POST_SESSION_RETROSPECTIVE.md (created)
- SOURCES_OF_TRUTH.md (created)
- AGENT.md (updated)
- tests/test_regla_21_retrospective.py (created)

**Documentation:** Changes in CLAUDE.md, AGENT_ONBOARDING.md linked

**Status:** COMPLETE

### RETROSPECTIVE

**JSON:**
```json
{
  "session_date": "2026-05-17T20:15:33Z",
  "agent": "Claude",
  "project": "Protocolo Agentes",
  "answers": {
    "q1_learning": "RULE #21 adds documentation overhead but detects gaps earlier.",
    "q2_violation": "NONE",
    "q3_next_agent": "Update RULE #22 whenever a new rule appears or authority changes.",
    "q4_protocol_gap": "AGENT_ONBOARDING.md does not mention JSON-parseable retrospectives.",
    "q5_token_efficiency": {
      "efficient": true,
      "estimate_tokens": 40000,
      "actual_tokens": 38500,
      "note": "No COMPACT was needed."
    }
  }
}
```
```

---

## Git hook enforcement

The pre-push hook must verify that the latest session in `HISTORIAL.md` includes a
`RETROSPECTIVE` section with valid JSON and the five required answers.

---

## Spirit of Rule #21

- Mandatory.
- Structured.
- Machine-readable.
- Actionable.
- Small overhead.
