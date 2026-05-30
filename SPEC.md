# 🧠 SPEC.md — El Cerebro de la CoderCerberus (Memory Bank Coder Cerberus V0.1)
**Estado:** 💎 SINGLE SOURCE OF TRUTH | Versión: v0.3

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
5.  **Multi-Agent Patterns (futura escala):** Cuando Cerberus coordine múltiples agentes, los patrones validados son: *sequential pipeline* (planner→coder→reviewer), *fan-out/fan-in* (planner divide trabajo a N agentes paralelos, luego merge), *supervisor* (un agente despacha y revisa a los demás), *debate/critic* (dos agentes argumentan, tercero decide). Referencia operativa: `docs/SINTAXIS_MULTI_AGENT.md`.

---

## 🧠 TAXONOMÍA DE MEMORIA DEL AGENTE (3 Capas)
Formalización del bootstrap ritual y el manejo de contexto por capa:

| Capa | Contenido | Duración | Implementación en Cerberus |
|------|-----------|----------|---------------------------|
| **Short-term** | Contexto de la tarea actual, plan activo, conversación | Duración del run | Ventana de prompt + PLAN.md |
| **Long-term** | Hechos estables del proyecto: convenciones, reglas, whitelist | Indefinida (hasta cambio explícito) | `SPEC.md`, `AGENT.md`, `PROTOCOL_*.md` |
| **External** | Artefactos cross-session: historial de decisiones, checkpoints, handoffs | TTL configurable | `HISTORIAL.md`, `.agent_state.json`, `STATE CHECKPOINT` |

**Reglas de expiración obligatorias:**
- Short-term: expira al fin de cada tarea (nunca cargar contexto de tarea anterior sin releerlo)
- Long-term: podar entradas no referenciadas en 10+ sesiones; actualizar cuando `sync_binding.py` detecte cambios
- External: archivar entradas de HISTORIAL.md con más de 30 días vía `compress_historial.py`

**Scoping de memoria:** Solo inyectar lo que la tarea ACTUAL necesita. Cargar contexto completo = dilución de señal + costo innecesario + fuga de información entre tareas.

## 🦴 DATA SKELETON & UI LAYOUT

**Agent Handoff State** (`.agent_state.json`):
`{version, session_id, agent_name, tier, status, next_step, protocol_checksums:{AGENT.md, PROTOCOL_BEHAVIOR.md, PROTOCOL_SYSTEM.md, SPEC.md}, session_token_budget:{tokens_used_so_far, compressions_this_session[]}, known_agents[], agent_permissions{}}`

**Evidence Record** (`.protocol/evidence/*.json` — 1 por operación):
`{timestamp:ISO8601-UTC, agent_capability_tier:"TRUSTED"|"ISOLATED"|"AUDIT", action_invoked:str, verification_outcome:"APPROVED"|"BLOCKED"|"REPLAN", affected_deltas:[filepath]}`

**SQLite: retrospectives** (`protocol_state.db`):
`(id UUID PK, session_id TEXT, timestamp DATETIME, learning_1 TEXT, violation TEXT, next_agent_knows TEXT, protocol_gaps TEXT, token_efficiency FLOAT, export_status TEXT)`

**SQLite: alerts** (shared DB):
`(id INTEGER PK, level TEXT, category TEXT, message TEXT, details TEXT, timestamp DATETIME, resolved BOOL)`

**SQLite: token_events** (shared DB):
`(id INTEGER PK, event_type TEXT, tokens_saved INTEGER, action TEXT, timestamp DATETIME)`

## 🧹 AUDIT 8-DOMAIN VALIDATOR
- **D8: Test Coverage** — PRIMERO. Tests adversariales existen y desafían paths negativos (>50% archivos)
- **D1: Integridad** — whitelist forense, sin archivos zombi, paridad de versión
- **D2: Completitud** — SPEC.md presente y con secciones mandatarias; scripts core existen
- **D3: Claridad** — sin dead code, funciones nombradas con propósito claro
- **D4: Anti-Spaghetti** — sin ciclos de importación, max complejidad controlada
- **D5: Angry Path** — manejo real de errores (try/except no vacíos), chaos monkey certificado
- **D6: Anti-Slop** — sin tipado débil (Any), sin warnings, código limpio
- **D7: Seguridad** — sin secretos hardcodeados, sin patrones peligrosos en I/O

---

## 💻 TECH CONTEXT (Stack de Rigor)
- **Runtime:** Python 3.13 (UTF-8) | **Test Runner:** Pytest / Unittest.
- **Enforcers:** `scripts/audit_10d.py` (10D auditor — gatekeeper primario), `scripts/pre_edit_guard.py` (PreToolUse hook — prevención en tiempo real), `scripts/rigor_maestro.py` (Pre-commit gatekeeper).
- **Chaos Engine:** `scripts/chaos_monkey.py` (Validación de resiliencia).
- **Integridad:** Git Hooks obligatorios. Prohibición de manipulación de archivos vía shell directo.

---

## 🛡️ WHITELIST (Inventario de Guerra)
Solo estos archivos tienen permiso de existir en el núcleo:

### Manifiestos Maestro
- `.claudeignore`, `AGENT.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md`, `MANDATES_BY_PHASE.md`, `ESCALATION_PROTOCOL.md`, `GEMINI.md`, `GLOBAL_LEARNING.md`, `.agent_state.json`, `SPEC.md`, `VERSION.txt`, `TOKEN_BUDGET.md`, `PERMISSIONS.md`, `USER_CONTEXT.md`, `TOKENOMICS_AND_ROUTING.md`, `MATRIZ_AUTOMATIZACION_COMPLETA.md`, `.pre-commit-config.yaml`, `TODO.md`, `scripts/bump_version.py`, `auto_repair.py`, `README.md`, `CHECKLIST.md`, `SOURCES_OF_TRUTH.md`, `.claude/settings.json`, `.github/workflows/cerberus-gatekeeper.yaml`

### Scripts Core (Músculo)
- `scripts/audit_10d.py` (10D auditor — gatekeeper primario), `scripts/pre_edit_guard.py` (PreToolUse hook), `scripts/audit_6d_expanded.py` (File chunking validation), `scripts/rigor_maestro.py`, `scripts/global_sync_safe.py`, `scripts/token_tracker.py`, `scripts/core_utils.py`.
- `scripts/chaos_monkey.py` (6 escenarios reales A-F), `scripts/install_hooks.sh` (setup inicial de git hooks — Linux/macOS), `scripts/install_hooks.ps1` (setup inicial de git hooks — Windows, P6.4), `scripts/install_cerberus.ps1` (Windows native installer, B2).
- `scripts/self_improvement_loop.py` (loop autónomo: audit+chaos+suite → HISTORIAL.md).
- `scripts/token_manager.py` (v2.0: OutputCompressor + ContextStore + ContextExtractor + TokenOptimizer + CLI `--compact`).
- `scripts/review_queue.py` (Fase F: cola de revision humana → `.protocol/review_queue.json`).
- `scripts/review_reminder.py` (Fase F: notificacion Windows de commits pendientes).
- `scripts/setup_reminder_task.py` (Fase F: configura Task Scheduler — ejecutar una vez).
- `scripts/memory_compression_reme.py` (v1.1, ReMe-style advanced memory compression and markdown fallback engine).
- **Archivados en deprecated/purga_v002/**: `token_optimizer.py`, `smart_context_extractor.py`, `rtk_auto_compress.py`, `auto_commit_enforcer.py`, `promote_to_core.py`, `automation/autonomous_orchestrator.py`, `automation/auto_remediation.py`.
- `scripts/automation/auto_maestro.py`, `scripts/automation/heartbeat_monitor.py` (activos — orquestación de mantenimiento).
- `scripts/merge_semantic.py` (Rescatado: Fusión Semántica de HISTORIAL).
- `scripts/dashboard/server.py` (Rescatado: Dashboard de Observabilidad).
- `scripts/deadlock_resolver.py` (Rescatado: Resolución de Concurrencia).
- `scripts/verify_protocol_adoption.py` (v1.0, P5.1: Audita adopción real del protocolo en proyectos hijo — hook + auditor + tests).
- `scripts/setup_validate.py` (v1.0, P5.6: Bootstrap validator — 6 checks: Python, essential files, git, hook, registry, write access).
- `scripts/generate_golden_audit.py` (v1.0: Compiler script for generating the Golden Standard compliance report and database).
- `scripts/sync_binding.py` (v1.0, Claude Binding: Sincronizacion bidireccional de protocolo).
- `scripts/protocol_cli.py` (v1.0, Control Plane: Single authority for all protocol operations).
- `scripts/chunking_validator.py` (v1.0, PHASE 2: File chunking validation).
- `scripts/empirical_proof_checker.py` (v1.0, PHASE 2: Empirical proof validation).
- `scripts/evidence_logger.py` (v1.0, PHASE 3: Formal evidence logging with JSON schema).
- `scripts/global_sync_safe.py` (v2.0, PHASE 5: Safe multi-project protocol distribution).
- `scripts/clean_satellites.py` (v1.0: Purges deprecated files from satellite directories).
- `scripts/migrate_to_subtree.py` (v1.0: Automates Git Subtree migration for all active projects).
- `scripts/permission_auditor.py` (v1.0, PHASE 6: Agent permission safety gate).
- `scripts/install_agent_permissions.py` (v1.0, PHASE 6: Local safe permission installer).
- `scripts/hygiene_auditor.py` (v1.0, D6: encoding hygiene and legacy deprecation gate).
- `scripts/validate_data.py` (v1.0, REGLA #30: pre-commit data validation — credentials, pickle, encoding).
- `scripts/post_move_validator.py` (v1.0, REGLA #17: post-move test runner).
- `scripts/rollback_tester.py` (v1.0, REGLA #29: pre-push rollback accessibility verifier).
- `scripts/check_imports.py` (v1.0, import health check pre-pytest).
- `scripts/guardrail_strict.py` (v1.0, REGLA-CODE parity gate para REGLAS SISTEMA).
- `tests/test_sprint1_tier0.py` (Sprint 1 Tier 0 integration tests — incluye OutputCompressor via token_manager).
- `tests/test_infrastructure.py` (Sprint 6 / P5.3-P5.7: governance sentinels — hook existence, hard_excludes, domain count).
- `tests/test_golden_standard_compliance.py` (Dynamic compliance test verifying all 278 Golden Standard flaws).
- `tests/test_volume_calendar.py` (P4.5: Volume >1000 sessions + calendar boundary tests — 31 Dec, 29 Feb, UTC).
- `tests/test_performance.py` (P4.7: Performance budgets — audit_10d <120s, setup_validate <3s, adoption audit <15s).
- `scripts/self_improvement_loop.py` (v1.0, D8: Loop autónomo de auditoría — detecta gaps y los documenta en HISTORIAL.md sin modificar código).
- `scripts/validate_routing.py` (v1.0, REGLA #28: Validación de multi-agent routing en HISTORIAL.md).
- `scripts/validate_security_tier.py` (v1.0, REGLA #24: Validación de security boundaries y permisos de tier).
- `scripts/alerts_viewer.py` (v1.0, REGLA #6: CLI para visualizar alertas centralizadas — tabla alerts compartida con token_tracker and deadlock_resolver).
- `scripts/compress_historial.py` (v1.0, FASE 5: Token-saving — archives HISTORIAL.md sessions older than N days).
- `scripts/cache_protocol_rules.py` (v2.0, FASE 5: Token-saving — indexes PROTOCOL_SYSTEM.md + PROTOCOL_BEHAVIOR.md into .claude/cache/protocol_rules.json. 39 mandates cached for fast load.).
- `scripts/auto_export_retrospective.py` (v1.0, FASE 8: Auto-exports latest HISTORIAL.md session to JSON and/or SQLite DB).
- `scripts/smart_context_extractor.py` (v1.0, NIVEL 5: Smart context extraction from STATUS.md — -40% to -60% tokens).
- `scripts/headspace_auto_trigger.py` (v1.0, FASE 8: Context compression trigger — auto-activates when usage >75%).
- `scripts/token_optimizer.py` (v1.0, NIVEL 5: Token-saving orchestrator — coordinates compress, cache, context extraction).
- `scripts/compact_automation_helper.py` (v1.0: Pre-COMPACT task orchestrator — compress, cache, export, headspace).
- `scripts/automation_scheduler.py` (v1.0: Interval-based scheduler for maintenance scripts — no external deps).
- `scripts/preflight_compliance.py` (v1.0, Barrier 1: AST codebase inventory — generates .protocol/codebase_map.json with all classes/functions/tests for agent visibility at startup).
- `scripts/auto_audit_loop.py` (v1.0: Retry-until-pass audit loop — runs audit_10d + protocol_cli doctor until clean pass).
- `scripts/handoff.py` (v1.0: Agent handoff package generator — reads STATUS.md, formats handoff context).
- `scripts/state_checkpoint_validator.py` (v1.0, REGLA #19: SHA256 checkpoint validator — detects malformed checkpoints in HISTORIAL.md).
- `scripts/fix_encoding.py` (v1.0: UTF-8 hygiene fixer — detects and fixes BOM, CRLF, soft hyphens per file).
- `scripts/setup_validate.py` (v2.0, REGLA #31: Bootstrap validator — Python 3.10+, essential protocol files).
- `scripts/auto_commit_enforcer.py` → **archivado en deprecated/purga_v002/** (auto-commits deshabilitados por protocolo).
- `scripts/promote_to_core.py` → **archivado en deprecated/purga_v002/** (promoción delegada a protocol_cli.py).
- `PROMPTS_RAPIDOS.md` (quick-reference prompts for common agent operations).
- `pytest.ini` (pytest configuration — test paths, markers, verbosity settings).
- `docs/ARQUITECTURA_3_CAPAS.md` (architecture doc: 3-layer governance Prose+Hooks+Tests).
- `docs/architecture/autogen_failure_analysis.md` (rationale for 3-tier enforcement vs AutoGen code-only governance).
- `docs/architecture/PERMISSIONS.md` (agent security tier matrix: Claude Tier1, Gemini Tier2, ChatGPT Tier3).
- `docs/architecture/TOKEN_ARCHITECTURE.md` (token optimization architecture reference).
- `docs/architecture/TOKEN_CLI_OPTIMIZATION.md` (CLI token optimization guide).
- `docs/architecture/VIBE_CODING_ERRORS_DOCTRINE.md` (core vibe coding error doctrine — 40+ principles).
- `docs/architecture/VIBE_CODING_ERRORS_DOCTRINE_PART_2.md` (vibe coding doctrine continuation).
- `docs/architecture/VIBE_CODING_ERRORS_DOCTRINE_PART_3.md` (vibe coding doctrine continuation).
- `docs/architecture/N5_REGLA_21_POST_SESSION_RETROSPECTIVE.md` (REGLA #21 retrospective format specification).
- `docs/architecture/N6_REGLA_24_SECURITY_BOUNDARIES.md` (REGLA #24 security boundaries — 3-tier sandbox model).
- `docs/architecture/N6_REGLA_30_DATA_VALIDATION_AT_BOUNDARIES.md` (REGLA #30 data validation at system frontiers).
- `docs/architecture/MANUAL_MAESTRO.md` (Coder Cerberus master operations manual).
- `docs/architecture/AGENT_ONBOARDING_RULES.md` (agent onboarding rules reference card).
- `docs/CONSOLIDATION_MANIFEST.json` (consolidation audit manifest — tracks script merges).
- `docs/DIRECTRICES_FUNDACIONALES.md` (foundational directives for CoderCerberus protocol).
- `docs/FALLOS_CONOCIDOS.md` (known failures registry — pre-existing deuda técnica).
- `GLOBAL_LEARNING.md` (cross-session learnings extracted from HISTORIAL.md; canonical at root per TK-007).
- `docs/PATRONES_TECNICOS.md` (technical patterns reference — anti-patterns and solutions).
- `docs/REFERENCIA_RAPIDA.md` (quick reference card for protocol commands and scripts).
- `docs/SINTAXIS_MULTI_AGENT.md` (multi-agent coordination syntax and handoff patterns).
- `scripts/helpers.py` (v1.0, Shared utilities: consolidación de funciones helper para refactored scripts).
- `.github/workflows/protocol.yaml` (GitHub CI: unittest, rigor_maestro, global sync dry-run, human review gate P4.6).
- `.github/pull_request_template.md` (P4.6: PR template con checkbox de revisión humana — CI lo verifica en cada PR).
- `cerberus/__init__.py` (Consolidated knowledge-base package init).
- `cerberus/knowledge_loader.py` (Golden Standard yaml/md knowledge loader).
- `tests/test_project_insights_integration.py` (Project insights integration test suite).

### Reference & Documentation
- `docs/MAPA_FUNCIONAL_CERBERUS.md` (Functional map of Coder Cerberus core and satellite ecosystems).
- `docs/archive/PLAN_PHASE1_CONTROL_PLANE.md` (Implementation plan for Control Plane).
- `docs/archive/APP_JS_IMPLEMENTATION.md` (57-function implementation plan for Control_Procesal).
- `docs/archive/CODIGO_FALTANTE_D7.md` (D7 Code Completeness audit).
- `docs/archive/CERBERUS_EXTRACTION_COMPLETE.md` (Complete audit of 150+ deprecated files + 23 scripts; foundation for reboot from zero).
- `docs/archive/PHASE_2_COMPLETION.md` (Spectral Script Resolution: extraction and deprecation of token_optimizer, deadlock_resolver, and 5 non-functional scripts).
- `00 audit/00_CONSTITUCION_CERBERUS.md`, `00 audit/01_AUDITORIA_LOCAL.md`, `00 audit/02_AUDITORIA_REPOSITORIOS.md`, `00 audit/03_EVOLUCION_GOLDEN_STANDARD.md`, `00 audit/04_CONTEXTO_EJECUCION.md`, `00 audit/README_ORDEN_DE_EJECUCION.md`, `00 audit/results/external_repositories_audit.md`

### Templates Generativos
- `templates/SPEC_FEATURES_TEMPLATE.md` (Plantilla estructurada para nuevas features).
- `templates/SPEC_BUGS_TEMPLATE.md` (Plantilla estructurada para resolución de bugs).
- `templates/SPEC_REFACTORS_TEMPLATE.md` (Plantilla estructurada para refactorizaciones).

### Git Hooks & Config
- `scripts/hooks/post-commit`, `scripts/hooks/pre-commit`, `scripts/hooks/pre-push`, `.gitignore`, `.cursorrules`, `HISTORIAL.md`, `scripts/__init__.py`, `pytest.ini`.
- `.claude/` (Carpeta de configuración de Claude Code).
- `.claude/CLAUDE.md` (Project-specific binding for Claude agents, v0.3).
- `.claude/.gitignore` (Exclusion rules for Claude Code temporary files).
- `.claude/settings.local.json` (Local Claude Code settings).
- `.claude/settings.template.json` (Reviewed safe Claude Code permissions template).
- `PRE_DELIVERY_CHECKLIST.md` (Checklist de Autoevaluación Agente).
- `.protocol/cleanup_log.json` (D6 workspace cleanup log).
- `.protocol/rollback_manifest.json` (D6 rollback instructions).
- `.protocol/evidence/.gitkeep` (Evidence directory placeholder).
- `.protocol/evidence/audit.json`, `.protocol/evidence/sync.json`, `.protocol/evidence/promote.json` (PHASE 3 operation evidence).
- `.protocol/metadata/REGISTRY.json` (Active project registry — source of truth for registered projects and sync state. Migrated from .CoderCerberus/ in P8.1).
- `Golden_Standard/BIBLIOTECA_VICIOS_VIBE_CODING.md` (Reference library: 110 VC vicios for adversarial audits).
- `Golden_Standard/BIBLIOTECA_VICIOS_TESTING_EVALUACION.md` (Reference library: 104 VT vicios for adversarial audits).
- `Golden_Standard/BIBLIOTECA_TOKENOMICS_CONTEXTO.md` (Reference library: 41 TK items for tokenomics audits).
- `Golden_Standard/golden_standard.yaml` (Consolidated YAML format library mapping).

### Registered Projects (MANDATORY SYNC)
**Fuente canónica:** `.protocol/metadata/REGISTRY.json` — no duplicar inventarios de archivos aquí.
Los archivos de cada proyecto externo pertenecen a su propio repositorio, no a SPEC.md de Cerberus.
Cerberus propaga a cada proyecto: `scripts/audit_10d.py`, `scripts/pre_edit_guard.py`, `scripts/rigor_maestro.py`, `scripts/core_utils.py`, `scripts/chaos_monkey.py`, `.claude/settings.json`.

Proyectos registrados con inventario detallado (ver REGISTRY.json):
- **Sistemas_Estocasticos_Ruleta** (status: active, path: `D:\GoogleDrive\AI\Sistemas_Estocasticos_Ruleta`)
- **Control_Procesal** (status: active, path: `D:\GoogleDrive\AI\Control_Procesal`)
- **Quenza** (status: active, path: `D:\GoogleDrive\AI\Quenza`)
- **Cuenza_Legacy** (status: legacy, path: `D:\GoogleDrive\AI\Quenza/01 Cuenza 2025`)
- **Declutter** (status: active, path: `D:\GoogleDrive\AI\Declutter`)
- **RED-Python** (status: active, path: `D:\GoogleDrive\AI\RED-Python`)
- **Agente_Inmobiliario** (status: active, path: `D:\GoogleDrive\AI\Agente_Inmobiliario`)

Proyectos bajo gestión Cerberus sin inventario detallado:
- **Aequitas_OS**, **Alesa Inc**, **Amparo Pensiones**, **Blog_Ciudadano_X**, **Calculadora de sueldos**, **Calculadora_Plazos**, **Imagen_Corporativa_Aequitas**, **Indices_Financieros**, **Maletin Homeopatia**, **Referencias**

---

## 🚀 ACTIVE CONTEXT
- **Estado:** Implementación de Coder Cerberus V0.1 (Fusión e Integración Deprecated Completada).
- **Meta:** Cumplimiento total del Protocolo CoderCerberus V0.3.
- **Riesgo Crítico:** Ignorar el Mandato S9 (Logging) por pereza.

---
**Coder Cerberus V0.1 — Inmunidad Total.**
