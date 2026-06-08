# MAPA_FUNCIONAL_CERBERUS.md

Estado: vivo
Ultima revision: 2026-05-28

## Proposito

Este documento resume que es Cerberus, que partes lo componen y como se mantiene actualizado.
Complementa a `SPEC.md`, `SOURCES_OF_TRUTH.md` y al inventario generado en `.protocol/codebase_map.json`.
No reemplaza a los documentos de autoridad: solo los conecta con el codigo real del repositorio.

## Que es Cerberus

Cerberus es un marco de gobernanza y defensa para desarrollo asistido por IA.
Su trabajo no es "construir features" de producto, sino:

- impedir fallos silenciosos
- bloquear stubs, vacios y humo de codigo
- validar seguridad, pureza de tests e higiene del espacio de trabajo
- sincronizar el protocolo entre el core y los proyectos satelite
- conservar memoria operativa, evidencia y estado entre sesiones

## Mapa funcional por capas

### 1. Capa de autoridad

Define reglas, alcance y comportamiento esperado.

- `AGENT.md`
- `SPEC.md`
- `PROTOCOL_SYSTEM.md`
- `PROTOCOL_BEHAVIOR.md`
- `MANDATES_BY_PHASE.md`
- `TOKENOMICS_AND_ROUTING.md`
- `USER_CONTEXT.md`
- `SOURCES_OF_TRUTH.md`

Esta capa responde a preguntas como:

- que archivos mandan
- que puede o no puede hacer el agente
- como se interpreta el protocolo
- que debe leerse al inicio de cada sesion

### 2. Capa de enforcement

Contiene los verificadores que frenan cambios defectuosos.

- `scripts/run_security_audit_12d.py` para la auditoria forense principal
- `scripts/run_compliance_tests.py` para ejecutar la suite critica y bloquear el flujo si algo falla
- `scripts/pre_edit_guard.py` para prevenir errores antes de editar
- `scripts/audit_permissions.py` para revisar permisos y boundaries
- `scripts/audit_hygiene.py` para encoding, deprecacion y limpieza
- `scripts/validate_data.py` para validacion de datos y secretos
- `scripts/check_imports.py` para sanear imports y dependencias internas
- `scripts/verify_rollback.py` para verificar reversibilidad
- `scripts/validate_post_move.py` para validar movimientos o reubicaciones
- `scripts/setup_validate.py` para bootstrap y prerequisitos
- `scripts/validate_state_checkpoint.py` para validar checkpoints de estado

Esta capa responde a preguntas como:

- el cambio rompe reglas de calidad
- el codigo es seguro y auditable
- la suite de tests y auditorias sigue verde

### 3. Capa de coordinacion

Orquesta sincronizacion, consultas y automatizacion del protocolo.

- `scripts/protocol_cli.py` como punto de entrada operativo
- `scripts/sync_binding.py` para detectar y propagar cambios del protocolo central
- `scripts/global_sync_safe.py` para distribuir el protocolo a proyectos satelite
- `scripts/verify_protocol_adoption.py` para confirmar adopcion real
- `scripts/preflight_compliance.py` para inventariar el codigo antes de proponer cambios
- `scripts/handoff.py` para preparar contexto de traspaso

Esta capa responde a preguntas como:

- que cambio hay que sincronizar
- que proyectos estan bajo gestion
- como se propaga una actualizacion valida

### 4. Capa de memoria, contexto y evidencia

Conserva el estado de trabajo y la trazabilidad entre sesiones.

- `STATUS.md` para el estado actual
- `HISTORIAL.md` para el historial operativo
- `.agent_state.json` para checksums, locks y contexto persistente
- `.protocol/evidence/` para evidencia de auditorias y sincronizaciones
- `.protocol/metadata/REGISTRY.json` para el registro de proyectos
- `scripts/export_retrospective.py` para exportar retrospectivas
- `scripts/compress_historial.py` para compactar historial
- `scripts/manage_tokens.py` para compresion y optimizacion de contexto
- `scripts/track_tokens.py` para monitoreo de tokens
- `scripts/trigger_context_compression.py` para disparar compresion

Esta capa responde a preguntas como:

- en que quedo la sesion anterior
- que se ejecuto y con que resultado
- cuando conviene compactar contexto

### 5. Capa de soporte operativo

Herramientas complementarias para observabilidad y mantenimiento.

- `scripts/view_alerts.py`
- `scripts/resolve_deadlocks.py`
- `scripts/manage_review_queue.py`
- `scripts/send_review_reminder.py`
- `scripts/run_self_improvement.py`
- `scripts/resolve_historial_conflicts.py`
- `scripts/verify_chaos_robustness.py`
- `scripts/dashboard/`

## Que hace realmente el paquete `protocol_engine/`

El paquete Python `protocol_engine/` es liviano y sirve como capa de acceso a conocimiento y reglas.

- `protocol_engine/knowledge_loader.py` carga el Golden Standard como manifest + catálogos y ingesta aprendizajes satélite de forma canónica
- `docs/DEBT_LEDGER.md` centraliza la deuda del workspace para distinguir backlog, drift histórico, deuda externa y trabajo activo
- `protocol_engine/rules_engine.py` carga reglas YAML desde `protocol_engine/rules/` y valida con checks seguros
- `protocol_engine.get_project_insights()` expone los patrones de referencia de proyectos externos como conocimiento agnostico reutilizable
- `protocol_engine.ingest_satellite_learnings()` normaliza y deduplica nuevas lecciones para que entren al GS sin duplicidades
- `protocol_engine.get_project_insight_recommendations()` transforma esos patrones en recomendaciones accionables por dominio
- `protocol_engine/close_pending.py` y `protocol_engine/rule_collector.py` apoyan tareas de organizacion interna

En otras palabras:

- `scripts/` hace el trabajo
- `protocol_engine/` expone conocimiento y reglas reutilizables
- `docs/` explica el sistema

## Flujo funcional tipico

### Inicio de sesion

1. Leer `AGENT.md`, `SPEC.md`, `STATUS.md` y `SOURCES_OF_TRUTH.md`
2. Revisar `docs/MAPA_FUNCIONAL_CERBERUS.md` cuando se necesite orientacion rapida
3. Validar contexto y restricciones antes de tocar codigo

### Cambio tecnico

1. Editar el script o modulo que resuelve la necesidad real
2. Actualizar o agregar tests
3. Ejecutar `python scripts/run_security_audit_12d.py`
4. Ejecutar `python scripts/run_compliance_tests.py`
5. Registrar evidencia si aplica
6. Actualizar `STATUS.md` y `HISTORIAL.md`

### Sincronizacion de protocolo

1. Cambiar primero los documentos de autoridad si la regla cambio
2. Luego ajustar la implementacion en `scripts/` o `protocol_engine/`
3. Regenerar el inventario con `python scripts/preflight_compliance.py`
4. Validar con `python scripts/sync_binding.py --check`
5. Aplicar con `python scripts/sync_binding.py --sync` o `python scripts/global_sync_safe.py --apply`

## Orden de actualizacion

Sigue este orden cuando algo cambie:

1. Actualizar la fuente de autoridad correcta
2. Ajustar codigo y tests
3. Regenerar el mapa tecnico si cambio la estructura
4. Ejecutar auditorias y suites de rigor
5. Registrar evidencia, estado e historial
6. Reflejar el cambio en `SOURCES_OF_TRUTH.md` y en este documento si afecta al mapa

## Fuentes de referencia

- `README.md` para la descripcion general
- `SOURCES_OF_TRUTH.md` para el indice canonicamente correcto
- `SPEC.md` para la memoria del sistema y la whitelist
- `.protocol/codebase_map.json` para el inventario tecnico generado
- `D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml` como manifest y `golden_standard_*.yaml` para los patrones agnósticos — repo independiente, no copia local
- `docs/ARQUITECTURA_3_CAPAS.md` para el modelo de capas
- `docs/architecture/MANUAL_MAESTRO.md` para doctrina operativa

## Nota de mantenimiento

Si se agrega un nuevo script, regla, documento de autoridad o proyecto satelite, este mapa debe actualizarse en la misma sesion o en la siguiente sesion de mantenimiento, nunca de forma diferida sin registro.
- `docs/SPRINT_10_REPOS_EXTERNOS_Y_VIGILANCIA.md` documenta la matriz externa del sprint 10 y la vigilancia en vivo absorbida como conocimiento canónico.
