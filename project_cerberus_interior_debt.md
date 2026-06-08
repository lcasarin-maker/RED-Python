# Memoria de Remediación: Deudas Internas de Cerberus v0.5

## Deuda #1 — Caché de Auditoría Golden Standard (VC-048)
- **Problema:** Cargas monolíticas repetitivas de `golden_standard_audit.json` degradaban el rendimiento de la suite de tests.
- **Solución:** Implementación de caché quirúrgico en `load_golden_standard_audit()` en `protocol_engine/knowledge_loader.py` utilizando una variable global `_GOLDEN_AUDIT_CACHE` de proceso. Las llamadas vacías por archivo no encontrado no se cachean.
- **Verificación:** Test `test_audit_db_is_memoized` en `tests/test_golden_standard_compliance.py` pasa exitosamente.

## Deuda #3 — Grafo Capa 1 Interno (VC-069)
- **Problema:** Ausencia de mapeo de dependencias de código (calls, imports, references) en la Capa 1 de Cerberus.
- **Solución:** Adopción de `graphify` v0.8.33 instalado en entorno aislado. Extracción pura offline de AST en staging temporal, normalizado y guardado en `.protocol/metadata/internal_graph.json` (nombre deconflictado de Capa 2). El filtro `_only_python` previene ids no deterministas en staging.
- **Verificación:** 4 tests en `tests/test_internal_graph.py` verifican la derivación pura de huérfanos, god nodes (grado ≥ 8) y entry points.

## Deuda #4 — Optimización de Stop Hook (VC-051 / TK-031)
- **Problema:** En `scripts/discourse_hook.py`, el bloqueo del turno por tokens se activaba incorrectamente por cantidad de mensajes (msgs), interfiriendo con el trabajo legítimo con muchos turnos de pocas palabras.
- **Solución:**
  1. Se corrigió `observe_session()` en `dimensions/d13_observable.py` para detectar correctamente `isCompactSummary:true` en el transcript.
  2. Se eliminó el bloqueo por cantidad de mensajes (msgs), manteniéndolo como aviso informativo. El bloqueo real cuelga exclusivamente de tokens out (umbral 80K tokens out).
- **Verificación:** Suite `tests/test_discourse_hook.py` con 3 tests verificando el comportamiento sin bloqueo por msgs bajos/altos.
