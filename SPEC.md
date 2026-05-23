# 🧠 SPEC.md — El Cerebro de la CoderCerberus (Memory Bank Coder Cerberus V0.1)
**Estado:** 💎 SINGLE SOURCE OF TRUTH | Versión: v0.02

---

## 🏗️ ARQUITECTURA Y PROPÓSITO
Este repositorio es el núcleo inmutable del **Coder Cerberus V0.1**. Su misión es erradicar el fallo silencioso de la IA mediante arquitectura defensiva y auditoría de confianza cero.

### 🧭 ENRUTADOR DE MÓDULOS DE AUTORIDAD (MODULE ROUTER)
El núcleo de autoridad de Cerberus está compuesto por 6 módulos maestros enlazados dinámicamente en la constitución operativa:
1. **00_EVIDENCE_AND_THREAT_MODEL.md**: Referenciado al modelo de amenazas y análisis forense.
2. **PROTOCOL_BEHAVIOR.md**: Reglas de razonamiento lingüístico y comportamiento (Modo Cavernícola, Trato Luis).
3. **PROTOCOL_SYSTEM.md**: Reglas físicas, prohibiciones de I/O y confinamiento del agente.
4. **MANDATES_BY_PHASE.md**: Flujos de trabajo y directivas secuenciales por fase.
5. **TOKENOMICS_AND_ROUTING.md**: Estrategias extremas de eficiencia de contexto, Grep Mandatorio y ruteo de modelos.
6. **USER_CONTEXT.md**: Identidad, intereses, estilo y logística del operador Luis Casarín.

---

## 🎨 SYSTEM PATTERNS (Filosofia de Diseno)
1.  **Cerebro-Musculo:** `SPEC.md` dicta la realidad; `SYSTEM.md` ejecuta el castigo tecnico.
2.  **Angry Path Dominance:** El flujo principal es el fallo; el exito es el residuo de un error no encontrado.
3.  **Bio-Containment:** Aislamiento estricto de modulos generados por IA tras interfaces inmutables.
4.  **Simetria Global:** Mejora local -> Promocion Core -> Sincronizacion 1:1.

---

## 🦴 DATA SKELETON & UI LAYOUT (Mandatario)
- **Data Entities:** [Definir esquemas y relaciones aqui antes de codificar]
- **UI Structure:** [Definir Flex/Grid y layouts explicitos aqui]
- **Enforcement:** El auditor 6D fallará si esta sección está vacía o desactualizada.

## 🧹 AUDIT 6-DOMAIN VALIDATOR
- **D1: Code Structure** — sin warnings, type safety, whitelist, version parity
- **D2: Functionality** — tests pass, no silent errors
- **D3: Human Validation** — empirical proof required (screenshots, logs)
- **D4: Security & I/O** — no hardcoded secrets, Pydantic/Zod at boundaries
- **D5: State Integrity** — critical files non-empty, valid JSON, checksums
- **D6: Workspace Hygiene** — audit corrupt encoding, unsafe legacy scripts, and generated cleanup artifacts; `doctor --fix` repairs supported hygiene issues.

---

## 💻 TECH CONTEXT (Stack de Rigor)
- **Runtime:** Python 3.13 (UTF-8) | **Test Runner:** Pytest / Unittest.
- **Enforcers:** `scripts/audit_6d.py` (v5.0 Whitelist), `scripts/rigor_maestro.py` (Pre-commit gatekeeper).
- **Chaos Engine:** `scripts/chaos_monkey.py` (Validación de resiliencia).
- **Integridad:** Git Hooks obligatorios. Prohibición de manipulación de archivos vía shell directo.

---

## 🛡️ WHITELIST (Inventario de Guerra)
Solo estos archivos tienen permiso de existir en el núcleo:

### Manifiestos Maestro
- `.claudeignore`, `AGENT.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md`, `MANDATES_BY_PHASE.md`, `ESCALATION_PROTOCOL.md`, `GEMINI.md`, `GLOBAL_LEARNING.md`, `.agent_state.json`, `SPEC.md`, `VERSION.txt`, `TOKEN_BUDGET.md`, `PERMISSIONS.md`, `USER_CONTEXT.md`, `TOKENOMICS_AND_ROUTING.md`, `MATRIZ_AUTOMATIZACION_COMPLETA.md`, `.pre-commit-config.yaml`, `TODO.md`, `scripts/bump_version.py`, `auto_repair.py`

### Scripts Core (Músculo)
- `scripts/audit_6d.py`, `scripts/rigor_maestro.py`, `scripts/global_sync_v5.py`, `scripts/promote_to_core.py`, `scripts/auto_commit_enforcer.py`, `scripts/rtk_auto_compress.py`, `scripts/handoff.py`, `scripts/token_tracker.py`, `scripts/install_hooks.sh`, `scripts/core_utils.py`, `scripts/run_audit_loop.py`.
- `scripts/chaos_monkey.py` (Inyectado para v5.0).
- `scripts/token_optimizer.py` (Rescatado: Optimización Fina).
- **Context Engineering (Nivel 5)**: `scripts/memory_compression_reme.py`, `scripts/prompt_cache_control.py`, `scripts/smart_context_extractor.py`, `scripts/token_optimizer_mcp.py`, `scripts/tool_deduplication.py`, `scripts/context_engineering.py`.
- **Demonios de Orquestación (24/7)**: `scripts/automation/autonomous_orchestrator.py`, `scripts/automation/auto_remediation.py`, `scripts/automation/auto_maestro.py`, `scripts/automation/heartbeat_monitor.py`.
- `scripts/merge_semantic.py` (Rescatado: Fusión Semántica de HISTORIAL).
- `scripts/dashboard/server.py` (Rescatado: Dashboard de Observabilidad).
- `scripts/deadlock_resolver.py` (Rescatado: Resolución de Concurrencia).
- `scripts/sync_binding.py` (v1.0, Claude Binding: Sincronizacion bidireccional de protocolo).
- `scripts/protocol_cli.py` (v1.0, Control Plane: Single authority for all protocol operations).
- `scripts/audit_6d_expanded.py` (v1.0, PHASE 2: 5-domain silent failure enforcement).
- `scripts/chunking_validator.py` (v1.0, PHASE 2: File chunking validation).
- `scripts/empirical_proof_checker.py` (v1.0, PHASE 2: Empirical proof validation).
- `scripts/evidence_logger.py` (v1.0, PHASE 3: Formal evidence logging with JSON schema).
- `scripts/global_sync_safe.py` (v2.0, PHASE 5: Safe multi-project protocol distribution).
- `scripts/permission_auditor.py` (v1.0, PHASE 6: Agent permission safety gate).
- `scripts/install_agent_permissions.py` (v1.0, PHASE 6: Local safe permission installer).
- `scripts/hygiene_auditor.py` (v1.0, D6: encoding hygiene and legacy deprecation gate).
- `.github/workflows/protocol.yaml` (GitHub CI: unittest, rigor_maestro, global sync dry-run).

### Reference & Documentation
- `docs/archive/PLAN_PHASE1_CONTROL_PLANE.md` (Implementation plan for Control Plane).
- `docs/archive/APP_JS_IMPLEMENTATION.md` (57-function implementation plan for Control_Procesal).
- `docs/archive/CODIGO_FALTANTE_D7.md` (D7 Code Completeness audit).
- `docs/archive/CERBERUS_EXTRACTION_COMPLETE.md` (Complete audit of 150+ deprecated files + 23 scripts; foundation for reboot from zero).
- `docs/archive/PHASE_2_COMPLETION.md` (Spectral Script Resolution: extraction and deprecation of token_optimizer, deadlock_resolver, and 5 non-functional scripts).

### Templates Generativos
- `templates/SPEC_FEATURES_TEMPLATE.md` (Plantilla estructurada para nuevas features).
- `templates/SPEC_BUGS_TEMPLATE.md` (Plantilla estructurada para resolución de bugs).
- `templates/SPEC_REFACTORS_TEMPLATE.md` (Plantilla estructurada para refactorizaciones).

### Git Hooks & Config
- `scripts/hooks/post-commit`, `scripts/hooks/pre-commit`, `scripts/hooks/pre-push`, `.gitignore`, `.cursorrules`, `HISTORIAL.md`, `scripts/__init__.py`.
- `.claude/` (Carpeta de configuración de Claude Code).
- `.claude/CLAUDE.md` (Project-specific binding for Claude agents, v5.7).
- `.claude/.gitignore` (Exclusion rules for Claude Code temporary files).
- `.claude/settings.local.json` (Local Claude Code settings).
- `.claude/settings.template.json` (Reviewed safe Claude Code permissions template).
- `PRE_DELIVERY_CHECKLIST.md` (Checklist de Autoevaluación Agente).
- `.protocol/cleanup_log.json` (D6 workspace cleanup log).
- `.protocol/rollback_manifest.json` (D6 rollback instructions).
- `.protocol/evidence/.gitkeep` (Evidence directory placeholder).
- `.protocol/evidence/audit.json`, `.protocol/evidence/sync.json`, `.protocol/evidence/promote.json` (PHASE 3 operation evidence).
- `deprecated/.vibecoderproof/REGISTRY.json` (Deprecated; moved to `deprecated/.vibecoderproof`).
- `deprecated/.vibecoderproof/backups/` (Deprecated; moved to `deprecated/.vibecoderproof`).

### Registered Projects (MANDATORY SYNC)
- **Sistemas_Estocasticos_Ruleta** (status: active, registered 2026-05-21)
  - **Core Implementation:** `QuantEdge_Calculator_V5.html`, `validar_paper.js`, `test_v5.js`
  - **Phase Documentation:** `PHASE_2_WEEK_1_COMPLETION.md`, `PHASE_3_4_COMPLETION.md`, `COMPLETION_REPORT_V5.md`
  - **Audit Trail:** `HISTORIAL.md`
  - **Reference Documents:** `QuantEdge_Paper.md`, `PLAN_CAPITAL_PROPIO_QUANTEDGE.md`, `PLAN_MONETIZACION_IDEA.md`, `EVALUACION_INGRESOS_QUANTEDGE.md`, `MANUAL_GENERACION_INGRESOS.md`, `RESUMEN_EJECUTIVO_INGRESOS.md`, `PROTOCOLO_MATCHED_BETTING.md`, `MAPA_ASIMETRIAS_APUESTAS_BOLSA_CRYPTO.md`, `MAPA_ASIMETRIAS_NO_APUESTAS.md`, `PHASE_2_DOCUMENTATION_PLAN.md`
  - **Configuration:** `.claude/launch.json`
  - **Archive (Deprecated):** `archive/QuantEdge_Calculator_v3.html`, `archive/QuantEdge_Calculator_v4.html`, `archive/DEBUG_OPTIMIZATION_v4.md`
  - **Scripts (Helper):** `scripts/validate_routing.py`, `scripts/validate_security_tier.py`

- **Control_Procesal** (status: active, registered 2026-05-23)
  - **Core Implementation:** `ControlProcesal_POE_v14.html`, `data_aequitas.json`, `storage_poe.json`
  - **Phase Documentation:** `APP_JS_IMPLEMENTATION.md`, `CODIGO_FALTANTE_D7.md`
  - **Configuration:** `.claude/settings.template.json`, `.claude/settings.local.json`
  - **Launchers:** `ARRANCAR_SERVIDOR.bat`
  - **Scripts:** `scripts/app.js`, `scripts/servidor_pdf.py`, `scripts/styles.css`, `scripts/token_tracker.py`, `scripts/chaos_monkey.py`, `scripts/core_utils.py`, `scripts/rigor_maestro.py`, `scripts/audit_6d.py`

- **Quenza** (status: active, registered 2026-05-23)
  - **Launchers & Core scripts:** `Correr-Cuenza.cmd`, `Correr-Legacy-Cuenza.cmd`, `Correr-Quenza.cmd`, `Parar-Cuenza.cmd`, `Parar-Legacy-Cuenza.cmd`, `Parar-Quenza.cmd`, `run-legacy.ps1`, `run.ps1`, `stop-legacy.ps1`, `stop.ps1`
  - **Reference & Parity Docs:** `AUDITORIA_PARIDAD_1_1_QUENZA_2026.md`, `AUDITORIA_PARIDAD_LEGACY_VIVO_2026_05_18.md`, `CHANGELOG_TECNICO.md`, `CHECKLIST_RUNTIME.md`, `DECISION_STACK_1_1.md`, `DECOMPILACION_FACTURACION_FASE4.md`, `FASE_0_INVENTARIO_LEGACY.md`, `GUIA_APAGADO.md`, `MATRIZ_PARIDAD_1_1.md`, `PARIDAD_DATOS_SQLSERVER_POSTGRES.md`, `PROTOCOLO_OPERATIVO_QUENZA_2026.md`, `VALIDACIONES.md`, `README.md`, `ROADMAP.md`
  - **Active Scripts:** `migration_tools/import_cfdi.py`, `migration_tools/migrate_data.py`, `scripts/auto_commit_enforcer.py`, `scripts/validate_routing.py`, `scripts/validate_security_tier.py`, `scripts/core_utils.py`, `scripts/rigor_maestro.py`, `scripts/chaos_monkey.py`, `scripts/chunking_validator.py`, `scripts/empirical_proof_checker.py`, `scripts/token_tracker.py`, `scripts/audit_6d.py`
  - **Tests & Tools:** `tests/test_parity_baseline.py`, `tests/test_fortaleza_v4_core.py`, `tests/test_resilience_v57.py`, `tests/test_v55_rigor.py`, `tools/legacy-seed-admin.sql`, `tools/reset_db.py`, `tools/shadow_comparator.py`, `tools/shadow_test_2.py`

- **Cuenza_Legacy** (status: legacy side-project, registered 2026-05-23)
  - **VB & ASP.NET Forms:** `01 Cuenza 2025/LineasServicio.aspx`, `01 Cuenza 2025/LineasServicio.aspx.vb`, `01 Cuenza 2025/LineasServicioAgregar.aspx`, `01 Cuenza 2025/LineasServicioAgregar.aspx.vb`, `01 Cuenza 2025/Login.aspx`, `01 Cuenza 2025/Login.aspx.designer.vb`, `01 Cuenza 2025/Login.aspx.vb`, `01 Cuenza 2025/MasterPageCuenza.Master`, `01 Cuenza 2025/MasterPageCuenza.Master.vb`, `01 Cuenza 2025/PronosticoPrograma.aspx`, `01 Cuenza 2025/PronosticoPrograma.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaAgregar.aspx`, `01 Cuenza 2025/PronosticoProgramaAgregar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaAutorizar.aspx`, `01 Cuenza 2025/PronosticoProgramaAutorizar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaCancelar.aspx`, `01 Cuenza 2025/PronosticoProgramaCancelar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaModificar.aspx`, `01 Cuenza 2025/PronosticoProgramaModificar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaV2.aspx`, `01 Cuenza 2025/PronosticoProgramaV2.aspx.vb`, `01 Cuenza 2025/Servicios.aspx`, `01 Cuenza 2025/Servicios.aspx.vb`, `01 Cuenza 2025/ServiciosAgregar.aspx`, `01 Cuenza 2025/ServiciosAgregar.aspx.vb`, `01 Cuenza 2025/Usuarios.aspx`, `01 Cuenza 2025/Usuarios.aspx.vb`, `01 Cuenza 2025/UsuariosAgregar.aspx`, `01 Cuenza 2025/UsuariosAgregar.aspx.vb`, `01 Cuenza 2025/Web.config`, `01 Cuenza 2025/aDefault.aspx`, `01 Cuenza 2025/aDefault.aspx.vb`, `01 Cuenza 2025/licenses.licx`

- **RED-Python** (status: active, registered 2026-05-23)
  - **Core Implementation:** `app.py`, `config.py`, `core.py`, `filters.py`, `red.py`, `red.spec`, `shell_integration.py`
  - **Reference & Parity Docs:** `PROMPTS_RAPIDOS_v3.md`, `PROTOCOLO_GLOBAL`, `USAR_RTK_Y_HEADROOM.md`, `VALIDACIONES.md`, `deprecated/ESTRATEGIA_AGENTES.md`
  - **Configuration:** `.headroom.config`, `requirements.txt`
  - **Active Scripts:** `scripts/validate_routing.py`, `scripts/validate_security_tier.py`, `scripts/run_incremental_audit.py`, `scripts/auto_commit_enforcer.py`, `scripts/core_utils.py`, `scripts/rigor_maestro.py`, `scripts/chaos_monkey.py`, `scripts/token_tracker.py`, `scripts/audit_6d.py`
  - **Tests & Tools:** `tests/test_functional.py`, `tests/test_integration.py`, `tests/test_main.py`, `tests/test_rollback.py`, `tests/test_fortaleza_v4_core.py`, `tests/test_resilience_v57.py`, `tests/test_v55_rigor.py`

---

### Sistemas_Estocasticos_Ruleta — Archivos Autorizados
- Core: `QuantEdge_Calculator_V5.html`, `validar_paper.js`, `test_v5.js`
- Reference: `QuantEdge_Paper.md`
- Audit Trail: `HISTORIAL.md`
- Documentation: `PHASE_2_WEEK_1_COMPLETION.md`, `PHASE_3_4_COMPLETION.md`, `COMPLETION_REPORT_V5.md`, `PLAN_CAPITAL_PROPIO_QUANTEDGE.md`, `PLAN_MONETIZACION_IDEA.md`, `EVALUACION_INGRESOS_QUANTEDGE.md`, `MANUAL_GENERACION_INGRESOS.md`, `RESUMEN_EJECUTIVO_INGRESOS.md`, `PROTOCOLO_MATCHED_BETTING.md`, `MAPA_ASIMETRIAS_APUESTAS_BOLSA_CRYPTO.md`, `MAPA_ASIMETRIAS_NO_APUESTAS.md`, `PHASE_2_DOCUMENTATION_PLAN.md`
- Configuration: `.claude/launch.json`
- Archive (Deprecated): `archive/QuantEdge_Calculator_v3.html`, `archive/QuantEdge_Calculator_v4.html`, `archive/DEBUG_OPTIMIZATION_v4.md`
- Scripts: `scripts/validate_routing.py`, `scripts/validate_security_tier.py`

### Control_Procesal — Archivos Autorizados
- Core: `ControlProcesal_POE_v14.html`, `data_aequitas.json`, `storage_poe.json`
- Documentation: `APP_JS_IMPLEMENTATION.md`, `CODIGO_FALTANTE_D7.md`
- Launchers: `ARRANCAR_SERVIDOR.bat`
- Scripts: `scripts/app.js`, `scripts/servidor_pdf.py`, `scripts/styles.css`, `scripts/token_tracker.py`, `scripts/chaos_monkey.py`, `scripts/core_utils.py`, `scripts/rigor_maestro.py`, `scripts/audit_6d.py`

### Quenza — Archivos Autorizados
- Launchers: `Correr-Cuenza.cmd`, `Correr-Legacy-Cuenza.cmd`, `Correr-Quenza.cmd`, `Parar-Cuenza.cmd`, `Parar-Legacy-Cuenza.cmd`, `Parar-Quenza.cmd`, `run-legacy.ps1`, `run.ps1`, `stop-legacy.ps1`, `stop.ps1`
- Reference Docs: `AUDITORIA_PARIDAD_1_1_QUENZA_2026.md`, `AUDITORIA_PARIDAD_LEGACY_VIVO_2026_05_18.md`, `CHANGELOG_TECNICO.md`, `CHECKLIST_RUNTIME.md`, `DECISION_STACK_1_1.md`, `DECOMPILACION_FACTURACION_FASE4.md`, `FASE_0_INVENTARIO_LEGACY.md`, `GUIA_APAGADO.md`, `MATRIZ_PARIDAD_1_1.md`, `PARIDAD_DATOS_SQLSERVER_POSTGRES.md`, `PROTOCOLO_OPERATIVO_QUENZA_2026.md`, `VALIDACIONES.md`, `README.md`, `ROADMAP.md`, `docs/CHANGELOG_MODULOS/CHANGELOG_M1_HISTORICO.md`, `docs/ROADMAP_MODULOS/ROADMAP_M1_FASES.md`
- Scripts: `migration_tools/import_cfdi.py`, `migration_tools/migrate_data.py`, `scripts/auto_commit_enforcer.py`, `scripts/validate_routing.py`, `scripts/validate_security_tier.py`, `scripts/core_utils.py`, `scripts/rigor_maestro.py`, `scripts/chaos_monkey.py`, `scripts/chunking_validator.py`, `scripts/empirical_proof_checker.py`, `scripts/token_tracker.py`, `scripts/audit_6d.py`
- Tests & Tools: `tests/test_parity_baseline.py`, `tests/test_fortaleza_v4_core.py`, `tests/test_resilience_v57.py`, `tests/test_v55_rigor.py`, `tools/legacy-seed-admin.sql`, `tools/reset_db.py`, `tools/shadow_comparator.py`, `tools/shadow_test_2.py`

### Cuenza_Legacy — Archivos Autorizados
- Forms & Logic: `01 Cuenza 2025/LineasServicio.aspx`, `01 Cuenza 2025/LineasServicio.aspx.vb`, `01 Cuenza 2025/LineasServicioAgregar.aspx`, `01 Cuenza 2025/LineasServicioAgregar.aspx.vb`, `01 Cuenza 2025/Login.aspx`, `01 Cuenza 2025/Login.aspx.designer.vb`, `01 Cuenza 2025/Login.aspx.vb`, `01 Cuenza 2025/MasterPageCuenza.Master`, `01 Cuenza 2025/MasterPageCuenza.Master.vb`, `01 Cuenza 2025/PronosticoPrograma.aspx`, `01 Cuenza 2025/PronosticoPrograma.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaAgregar.aspx`, `01 Cuenza 2025/PronosticoProgramaAgregar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaAutorizar.aspx`, `01 Cuenza 2025/PronosticoProgramaAutorizar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaCancelar.aspx`, `01 Cuenza 2025/PronosticoProgramaCancelar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaModificar.aspx`, `01 Cuenza 2025/PronosticoProgramaModificar.aspx.vb`, `01 Cuenza 2025/PronosticoProgramaV2.aspx`, `01 Cuenza 2025/PronosticoProgramaV2.aspx.vb`, `01 Cuenza 2025/Servicios.aspx`, `01 Cuenza 2025/Servicios.aspx.vb`, `01 Cuenza 2025/ServiciosAgregar.aspx`, `01 Cuenza 2025/ServiciosAgregar.aspx.vb`, `01 Cuenza 2025/Usuarios.aspx`, `01 Cuenza 2025/Usuarios.aspx.vb`, `01 Cuenza 2025/UsuariosAgregar.aspx`, `01 Cuenza 2025/UsuariosAgregar.aspx.vb`, `01 Cuenza 2025/Web.config`, `01 Cuenza 2025/aDefault.aspx`, `01 Cuenza 2025/aDefault.aspx.vb`, `01 Cuenza 2025/licenses.licx`

### RED-Python — Archivos Autorizados
- Core: `app.py`, `config.py`, `core.py`, `filters.py`, `red.py`, `red.spec`, `shell_integration.py`
- Reference & Parity Docs: `PROMPTS_RAPIDOS_v3.md`, `PROTOCOLO_GLOBAL`, `USAR_RTK_Y_HEADROOM.md`, `VALIDACIONES.md`, `deprecated/ESTRATEGIA_AGENTES.md`
- Configuration: `.headroom.config`, `requirements.txt`
- Scripts: `scripts/validate_routing.py`, `scripts/validate_security_tier.py`, `scripts/run_incremental_audit.py`, `scripts/auto_commit_enforcer.py`, `scripts/core_utils.py`, `scripts/rigor_maestro.py`, `scripts/chaos_monkey.py`, `scripts/token_tracker.py`, `scripts/audit_6d.py`
- Tests: `tests/test_functional.py`, `tests/test_integration.py`, `tests/test_main.py`, `tests/test_rollback.py`, `tests/test_fortaleza_v4_core.py`, `tests/test_resilience_v57.py`, `tests/test_v55_rigor.py`

---

## 🚀 ACTIVE CONTEXT
- **Estado:** Implementación de Coder Cerberus V0.1 (Fusión e Integración Deprecated Completada).
- **Meta:** Cumplimiento total de la Biblia Anti-VibeCoder.
- **Riesgo Crítico:** Ignorar el Mandato S9 (Logging) por pereza.

---
**Coder Cerberus V0.1 — Inmunidad Total.**
