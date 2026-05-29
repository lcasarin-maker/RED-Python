# Test Quality Checklist — CoderCerberus V0.02
# ESTE ARCHIVO ES INFORMATIVO — la evaluación es automática.
# audit_10d.py imprime el reporte [CHECKLIST AUTO-EVALUACION] en cada run.
# pytest imprime el reporte [REPORTE AUTO CALIDAD DE TESTS] al terminar.
# No necesitas completar nada manualmente.

---

## Qué se evalúa automáticamente

| Grupo | Check | Herramienta |
|-------|-------|-------------|
| F4    | ¿Hay tests con None/0/''? | D9 + pytest hook |
| G4    | ¿Algún test cubre 5+ funciones? | D9 + pytest hook |
| H1    | ¿CI tiene continue-on-error en tests? | D9 |
| C1    | ¿xfail sin criterio de remoción? | D9 (bloquea commit) |
| C2    | ¿skip sin justificación? | D9 (bloquea commit) |
| B1    | ¿assert True literal? | D9 (bloquea commit) |
| B2    | ¿test sin ninguna aserción? | D9 (bloquea commit) |
| J1    | ¿os.environ modificado en test? | D9 (bloquea commit) |
| J3    | ¿mock.patch sobre scripts.*? | D9 (bloquea commit) |
| J4    | ¿paths absolutos hardcodeados? | D9 (bloquea commit) |

## Qué NO se puede automatizar (riesgos aceptados en vibe coding)

| Grupo | Riesgo | Por qué no es automatable |
|-------|--------|---------------------------|
| I1    | IA escribió código Y tests | No hay forma de saber quién revisó qué |
| I2    | Test verifica comportamiento incorrecto | Requiere entender la intención del código |
| I4    | Nadie revisó los tests independientemente | Proceso, no código |
| F1    | Solo happy path | Requiere saber qué constituye un caso límite para cada función |
| G1    | Líneas cubiertas sin aserciones | Requiere integrar coverage + tracking de aserciones |

**Aviso permanente:** En vibe coding con IA, antes de declarar una feature completa,
verifica que al menos 1 test falla si eliminas la lógica principal del feature.
Esta es la única verificación que no puede hacerse sola.

---

## Cierre de sesión — checklist manual (P5.2 / VC-114)

Antes de cerrar una sesión de desarrollo:

- [ ] **Hallazgos registrados**: Todo defecto o deuda técnica detectada tiene ítem en PLAN.md con ID, evidencia, fix propuesto y done-criteria.
- [ ] SPEC.md actualizado si cambió whitelist o arquitectura.
- [ ] HISTORIAL.md con bitácora + retrospectiva JSON.
- [ ] `.agent_state.json` actualizado.

---

## Gaps de cobertura a cubrir en sprints futuros (P4.5)

Los siguientes escenarios límite no están cubiertos por tests automáticos actuales y deben añadirse al alcanzar las funciones relevantes:

| Gap | Escenario | Función afectada |
|-----|-----------|-----------------|
| Vol-1 | Iterable con >1 000 ítems | Cualquier función que filtre/agrupe |
| Vol-2 | Archivo con >10 000 líneas | Parsers de SPEC.md, audit_10d |
| Cal-1 | Fecha 31 diciembre → año nuevo | Lógica de fechas en retrospectivas |
| Cal-2 | Fecha 29 febrero (año bisiesto) | Cualquier cálculo de delta días |
| Cal-3 | Cambio horario DST (si aplica) | Timestamps en HISTORIAL.md |
