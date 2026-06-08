# 🧠 SPEC.md — El Cerebro de la CoderCerberus (Memory Bank Coder Cerberus V0.5)
**Estado:** 💎 SINGLE SOURCE OF TRUTH | Versión: v0.5

---

## 🏗️ ARQUITECTURA Y PROPÓSITO
Este repositorio es el núcleo inmutable del **Coder Cerberus V0.5**. Su misión es erradicar el fallo silencioso de la IA mediante arquitectura defensiva, multi-agente y auditoría de confianza cero.

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
1.  **Cerebro-Musculo:** `SPEC.md` dicta la realidad; `PROTOCOL_SYSTEM.md` ejecuta el castigo tecnico.
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

## 🧹 AUDIT 12-DOMAIN VALIDATOR (12D)
- **D1: Integridad** — whitelist forense, sin archivos zombi, paridad de versión
- **D2: Completitud** — control plane completo; scripts core existen y tienen tests
- **D3: Claridad** — sin dead code, funciones nombradas con propósito claro
- **D4: Anti-Spaghetti** — sin ciclos de importación, max complejidad, god-node fan-in
- **D5: Angry Path** — manejo real de errores (try/except no vacíos)
- **D6: Anti-Slop** — sin tipado débil (Any), sin filterwarnings sin justificación
- **D7: Seguridad** — sin secretos hardcodeados, sin patrones peligrosos en I/O
- **D8: Cobertura adversarial** — tests que falsifican realmente; paths negativos cubiertos
- **D9: Pureza de tests** — sin assert True, sin xfail permanente, sin skip sin fecha
- **D10: Tokenomics** — manifiestos ≤ límite, OutputCompressor en orquestadores
- **D11: SCA Trivy** — sin CVEs críticos en dependencias
- **D12: Satellite drift** — satélites alineados a versión del protocolo core
- **D13: Validation Debt** — deudas de auditoría registradas, remediadas, post-mortem automático (scripts: `satellite_validation_debt.py`, `postmortem_validation_analysis.py`, `audit_d13_validation_debt.py`)

---

## 💻 TECH CONTEXT (Stack de Rigor)
- **Runtime:** Python 3.13 (UTF-8) | **Test Runner:** Pytest / Unittest.
- **Enforcers:** `scripts/run_security_audit_12d.py` (12D auditor — gatekeeper primario), `scripts/pre_edit_guard.py` (PreToolUse hook — prevención en tiempo real), `scripts/run_compliance_tests.py` (Pre-commit gatekeeper).
- **Validation Debt (D13):** `scripts/satellite_validation_debt.py` (registry API), `deprecated/bootstrap_v0.5/validate_satellite_functional.py` (empirical proof), `scripts/postmortem_validation_analysis.py` (systemic analysis), `scripts/audit_d13_validation_debt.py` (auditor domain D13).
- **Chaos Engine:** `scripts/verify_chaos_robustness.py` (Validación de resiliencia).
- **Integridad:** Git Hooks obligatorios. Prohibición de manipulación de archivos vía shell directo.

---

## 🛡️ WHITELIST (Inventario de Guerra)
Solo estos archivos tienen permiso de existir en el núcleo:

### Subdirectorios Permitidos
- **`rules/`** — Sub-proyecto de reglas y artefactos protocol_engine. Estructura completa permitida: `.agent_state.json`, `SPEC.md`, `scripts/`, `protocol_engine/`, `tests/`, `.claude/`, `.github/`, `docs/` con contenido de artefactos operacionales (non-zombie).
- ~~**`Golden_Standard/`**~~ — **ELIMINADO**. GS migró a repo independiente `D:\AI\VibeCoding_GoldenStandard`. Cerberus lo consume por ruta externa; no existe copia local.
- **`deprecated/`** — Archivo de scripts/archivos deprecados. Contenido completo permitido como cuarentena temporal.
- **`auditorias/`** — Auditorías por fecha. Contenido de pruebas y evidencia permitido.
- **`docs/`** — Documentación de arquitectura y procedimientos.

### Manifiestos Maestro
- `.claudeignore`, `AGENT.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md`, `MANDATES_BY_PHASE.md`, `ESCALATION_PROTOCOL.md`, `GEMINI.md`, `GLOBAL_LEARNING.md`, `.agent_state.json`, `SPEC.md`, `VERSION.txt`, `TOKEN_BUDGET.md`, `PERMISSIONS.md`, `USER_CONTEXT.md`, `TOKENOMICS_AND_ROUTING.md`, `MATRIZ_AUTOMATIZACION_COMPLETA.md`, `.pre-commit-config.yaml`, `scripts/bump_version.py`, `README.md`, `CHECKLIST.md`, `SOURCES_OF_TRUTH.md`, `DEPRECATION_LOG.md`, `GRAPH_REPORT.md`, `project_cerberus_interior_debt.md`, `.claude/settings.json`, `.github/workflows/cerberus-gatekeeper.yaml`

### Scripts Core (Músculo)
- `scripts/run_security_audit_12d.py` (12D auditor — gatekeeper primario), `scripts/pre_edit_guard.py` (PreToolUse hook), `scripts/run_compliance_tests.py`, `scripts/global_sync_safe.py`, `scripts/track_tokens.py`, `scripts/core_utils.py`.
- `scripts/verify_chaos_robustness.py` (6 escenarios reales A-F), `scripts/install_hooks.sh` (setup inicial de git hooks — Linux/macOS), `scripts/install_hooks.ps1` (setup inicial de git hooks — Windows, P6.4), `scripts/install_cerberus.ps1` (Windows native installer, B2).
- `scripts/run_self_improvement.py` (loop autónomo: audit+chaos+suite → HISTORIAL.md).
- `scripts/manage_tokens.py` (v2.0: OutputCompressor + ContextStore + ContextExtractor + TokenOptimizer + CLI `--compact`).
- `scripts/manage_review_queue.py` (Fase F: cola de revision humana → `.protocol/review_queue.json`).
- `scripts/send_review_reminder.py` (Fase F: notificacion Windows de commits pendientes).
- `scripts/setup_reminder_task.py` (Fase F: configura Task Scheduler — ejecutar una vez).
- `scripts/compress_memory_context.py` (v1.1, ReMe-style advanced memory compression and markdown fallback engine).
- **Archivados en deprecated/purga_v002/**: `token_optimizer.py`, `smart_context_extractor.py`, `rtk_auto_compress.py`, `auto_commit_enforcer.py`, `promote_to_core.py`, `automation/autonomous_orchestrator.py`, `automation/auto_remediation.py`.
- `scripts/monitor_projects.py`, `scripts/monitor_heartbeat.py` (activos — orquestación de mantenimiento).
- `scripts/lint_knowledge.py` (v1.0, G2: Wiki & Knowledge Linter — audita links rotos, huérfanos y schemas GS).
- `scripts/remediation_engine.py` (v1.0: Auto-remediation engine for deterministic fixes and queueing of logical failures).
- `scripts/setup_scheduler_task.ps1` (v1.0: Registers the background monitor task in Windows Scheduled Tasks).
- `scripts/resolve_historial_conflicts.py` (Rescatado: Fusión Semántica de HISTORIAL).
- `scripts/serve_dashboard.py` (Rescatado: Dashboard de Observabilidad).
- `scripts/resolve_deadlocks.py` (Rescatado: Resolución de Concurrencia).
- `scripts/verify_protocol_adoption.py` (v1.0, P5.1: Audita adopción real del protocolo en proyectos hijo — hook + auditor + tests).
- `scripts/setup_validate.py` (v1.0, P5.6: Bootstrap validator — 6 checks: Python, essential files, git, hook, registry, write access).
- `scripts/sync_binding.py` (v1.0, Claude Binding: Sincronizacion bidireccional de protocolo).
- `scripts/protocol_cli.py` (v1.0, Control Plane: Single authority for all protocol operations).
- `scripts/validate_chunking.py` (v1.0, PHASE 2: File chunking validation).
- `scripts/check_empirical_proof.py` (v1.0, PHASE 2: Empirical proof validation).
- `scripts/log_evidence.py` (v1.0, PHASE 3: Formal evidence logging with JSON schema).
- `scripts/global_sync_safe.py` (v2.0, PHASE 5: Safe multi-project protocol distribution).
- `scripts/clean_satellites.py` (v1.0: Purges deprecated files from satellite directories).
- `scripts/migrate_to_subtree.py` (v1.0: Automates Git Subtree migration for all active projects).
- `scripts/repair_protocol_junction.py` (v1.0, Sprint 3.9/PASO 3: auto-repara el binding `.protocol-core` de satélites. Modelo **junction** → raíz viva de Cerberus (derivada de `__file__` = self-heal); reemplaza subtree-pull (S19). `classify`/`repair_action` puras (testeables); `junction_status` reúne probes Windows (reparse tag, readlink). Idempotente y SEGURO: nunca borra un dir real (`not_junction`→skip_unsafe); solo repara colgantes/wrong_target/missing. Causa raíz reparada: junctions apuntaban a `Cerberus\rules` inexistente tras reorganizar Cerberus → enforcement muerto en los 17. CLI `--repo-root | --all | --dry-run`).
- `tests/test_repair_junction.py` (v1.0, Sprint 3.9: tests de la lógica pura de clasificación/decisión — el riesgo es jamás tocar un dir real del usuario).
- `scripts/audit_permissions.py` (v1.0, PHASE 6: Agent permission safety gate).
- `scripts/audit_hygiene.py` (v1.0, D6: encoding hygiene and legacy deprecation gate).
- **v0.5 Hooks activos:**
  - `scripts/enforce_thinking_limits.py` (TK-044: Enforcer de límites de thinking en respuestas)
  - `scripts/model_router.py` (TK-045: Router inteligente de modelos por tarea)
  - `scripts/tool_result_cleaner.py` (TK-047: Limpiador de resultados de herramientas)
  - `scripts/block_auto_docs.py` (TK-049: Bloqueador de generación automática de docs)
  - `scripts/image_cost_detector.py` (TK-050: Detector de costo de imágenes)
- `scripts/validate_data.py` (v1.0, REGLA #30: pre-commit data validation — credentials, pickle, encoding).
- `scripts/validate_post_move.py` (v1.0, REGLA #17: post-move test runner).
- `scripts/verify_rollback.py` (v1.0, REGLA #29: pre-push rollback accessibility verifier).
- `scripts/check_imports.py` (v1.0, import health check pre-pytest).
- `scripts/detect_rule_code_drift.py` (v1.0, REGLA-CODE parity gate para REGLAS SISTEMA).
- `tests/test_sprint1_tier0.py` (Sprint 1 Tier 0 integration tests — incluye OutputCompressor via token_manager).
- `tests/test_infrastructure.py` (Sprint 6 / P5.3-P5.7: governance sentinels — hook existence, hard_excludes, domain count).
- `tests/test_golden_standard_compliance.py` (Dynamic compliance test verifying all 278 Golden Standard flaws).
- `tests/test_volume_calendar.py` (P4.5: Volume >1000 sessions + calendar boundary tests — 31 Dec, 29 Feb, UTC).
- `tests/test_performance.py` (P4.7: Performance budgets — run_security_audit_12d <120s, setup_validate <3s, adoption audit <15s).
- `tests/test_remediation_engine.py` (v1.0: Tests for background remediation and Windows Toast notifications).
- `tests/test_lint_knowledge.py` (v1.0: Tests for Wiki links, orphans, and Golden Standard YAML integrity).
- `scripts/run_self_improvement.py` (v1.0, D8: Loop autónomo de auditoría — detecta gaps y los documenta en HISTORIAL.md sin modificar código).
- `scripts/validate_routing.py` (v1.0, REGLA #28: Validación de multi-agent routing en HISTORIAL.md).
- `scripts/validate_security_tier.py` (v1.0, REGLA #24: Validación de security boundaries y permisos de tier).
- `scripts/view_alerts.py` (v1.0, REGLA #6: CLI para visualizar alertas centralizadas — tabla alerts compartida con token_tracker and deadlock_resolver).
- `dimensions/d13_observable.py` (Sprint 28.5: D13 Observable Behavior migrada al paquete, canal HOOK — consolida los 4 scripts d13_* (token meter+tiktoken, decision logger, divergence detector, D13Report); `observe_session` suma tokens del transcript; cableada vía discourse_hook.py; reemplaza los standalone, S19).
- `tests/test_d13_observable_behavior.py` (Sprint 24: Tests para D13 — 12 casos token/decisiones/divergencias).
- `dimensions/d3_dead_code.py` (Sprint 28.5: D3 Dead Code REAL cableada al gate vía REGISTRY — ruff F + vulture solo defs muertas; reemplaza el inline `audit_dead_code` y el teatro `d3_dead_code_enhanced` (S19); binario ausente → UNAVAILABLE).
- `dimensions/d11_dependency.py` (Sprint 28.5: D11 Dependency REAL cableada al gate vía REGISTRY — Trivy SCA consolidado (reemplaza inline `audit_d11_validate_sca_trivy`, S19) + frescura PyPI outdated/yanked; Trivy ausente → UNAVAILABLE, offline → WARN; reemplaza el teatro `d11_dependency_enhanced`).
- `dimensions/d7_security.py` (Sprint 28.5: D7 Data Security REAL cableada al gate vía REGISTRY — regex secretos/inyección (del inline, preservado) + bandit SAST (HIGH→FAIL, ausente→UNAVAILABLE); sin trivy (d11 lo posee); semgrep diferido; reemplaza inline `audit_d7_data_security` + teatro `d7_security_enhanced`, S19).
- `dimensions/d14_discourse_rigor.py` (Sprint 28.5: D14 Discourse Rigor migrada al paquete, canal HOOK — auditа la respuesta del agente vía `audit_response`, no el repo; el gate la salta; clarity/ambiguity/evidence/cot reales; reemplaza el script standalone, S19).
- `scripts/discourse_hook.py` (Sprint 28.5: Stop hook del canal runtime — extrae la prosa del último mensaje assistant del transcript JSONL y corre D14.audit_response; WARN-only, exit 0; cableado en .claude/settings.json hooks.Stop. Hace a D14 enforcar de verdad).
- `scripts/generate_dimension_registry.py` (Sprint 28.5 Paso 1: genera `dimension_registry.json` — deriva del repo canal/wiring/binario/test-real por dimensión).
- `dimension_registry.json` (Sprint 28.5: ledger committeado de dimensiones; fresh-gated; documenta verdad inerte — 9/14 fully-wired, dual-impl D3/D7/D11, hook D13/D14).
- `dimensions/base.py` (Sprint 28.5 Paso 2: contrato `Dimension` + `Finding` + `Status` con UNAVAILABLE — insumo ausente nunca PASS silencioso).
- `dimensions/context.py` (Sprint 28.5 Paso 2: `AuditContext` — pasada única, file-list + AST cacheados una vez).
- `dimensions/__init__.py` (Sprint 28.5 Paso 2: `REGISTRY` — única fuente de verdad de dimensiones; el gate corre el loop sobre ella).
- `requirements.txt` (Sprint 28.5: manifiesto de deps directas — única fuente de verdad pinneada; PyYAML runtime + pytest test; input real para Trivy/d11. Reemplaza el fallback-teatro del CI).
- `scripts/compress_historial.py` (v1.0, FASE 5: Token-saving — archives HISTORIAL.md sessions older than N days; soporta --auto para stop hook).
- `scripts/lint_protocol_docs.py` (v1.0, PI-021: Wiki-Lint semántico — detecta refs rotas, versiones inconsistentes y contradicciones entre docs de protocolo).
- `scripts/generate_graph_report.py` (v1.0, PI-020: Genera GRAPH_REPORT.md + graph.json con grafo de satélites, adopción y god-nodes del protocolo).
- `scripts/check_deprecation_log.py` (v1.0, S24: Valida que archivos staged en deprecated/ tienen entrada en DEPRECATION_LOG.md).
- `scripts/cache_protocol_rules.py` (v2.0, FASE 5: Token-saving — indexes PROTOCOL_SYSTEM.md + PROTOCOL_BEHAVIOR.md into .claude/cache/protocol_rules.json. 39 mandates cached for fast load.).
- `scripts/export_retrospective.py` (v1.0, FASE 8: Auto-exports latest HISTORIAL.md session to JSON and/or SQLite DB).
- `scripts/internal_graph.py` (v1.2, C3/Federada: Grafo Capa 1 (AST) + Capa 2 (docs Obsidian doc↔doc y doc→código vía aristas `documents`). `extraction_status` distingue fallo de vacío; `extraction_is_trustworthy()` evita falso-verde. `_auto_detect_targets` incluye protocol_engine. Fase 2b: `_build_symbol_aliases` resuelve [[nombre_corto]]→id completo con guard de unicidad).
- `tests/test_internal_graph.py` (v1.0, C3: Tests para Grafo Capa 1 interno).
- `scripts/alignment_checker.py` (v1.2, Fase 2c CERRADA: Linter de alineación Código (Capa 1) ↔ Docs (Capa 2). `critical_symbols` = god_nodes **documentables** (`_is_documentable_symbol` excluye artefactos `*_py_path` y símbolos fuera de los namespaces del repo; los entry_points YA no son críticos). code_orphans→FAIL; doc_orphans→WARN advisory (un doc sin links es higiene, no falla de correctitud). Gate **opt-in** vía marcador `.protocol/align_gate.enabled` (`align_gate_enabled`/`gate_exit_code`): bloqueante donde se pagó la deuda de contenido, advisory en satélites no documentados (anti-brick). Comando CLI `align-check`. En Cerberus: cobertura crítica 100% (14 god_nodes documentados en `docs/architecture/CODE_MAP.md`), gate ACTIVO).
- `tests/test_alignment_checker.py` (v1.2, Fase 2c: Tests del linter — predicado documentable, exclusión de artefactos, entry_points no críticos, gate opt-in).
- `docs/architecture/CODE_MAP.md` (Fase 2c: mapa de la superficie crítica de código — 14 god_nodes de los 5 módulos núcleo con `[[refs]]` que el linter resuelve; satisface el invariante de cobertura crítica).
- `scripts/check_clean_worktree.py` (v1.0, VC-141: detector de cambios eludidos / commit parcial. Función pura `worktree_is_clean`; bloquea en pre-commit si el working tree queda sucio tras stagear. Escape CERBERUS_ALLOW_PARTIAL=1).
- `tests/test_clean_worktree.py` (v1.0, VC-141: tests del detector de working tree limpio + idempotencia de adopción).
- `scripts/trigger_context_compression.py` (v1.0, FASE 8: Context compression trigger — auto-activates when usage >75%).
- `scripts/compact_automation_helper.py` (v1.0: Pre-COMPACT task orchestrator — compress, cache, export, headspace).
- `scripts/pre_compact_evaluator.py` (v1.0: PreCompact hook — snapshot de estado antes de compactar: git dirty, tests, zombies; siempre exit 0, nunca bloquea /compact).
- `scripts/preflight_compliance.py` (v1.0: AST codebase inventory — genera .protocol/codebase_map.json).
- `scripts/handoff.py` (v1.0: Agent handoff package generator — reads STATUS.md, formats handoff context).
- `scripts/validate_state_checkpoint.py` (v1.0, REGLA #19: SHA256 checkpoint validator — detects malformed checkpoints in HISTORIAL.md).
- `scripts/fix_encoding.py` (v1.0: UTF-8 hygiene fixer — detects and fixes BOM, CRLF, soft hyphens per file).
- `scripts/setup_validate.py` (v2.0, REGLA #31: Bootstrap validator — Python 3.10+, essential protocol files).
- **deprecated/purga_v002/**: `token_optimizer.py`, `smart_context_extractor.py`, `auto_commit_enforcer.py`, `promote_to_core.py`, `rtk_auto_compress.py`, `automation/autonomous_orchestrator.py`, `automation/auto_remediation.py` — archivados, no referenciar.
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
- `protocol_engine/__init__.py` (Consolidated knowledge-base package init).
- `protocol_engine/knowledge_loader.py` (Golden Standard yaml/md knowledge loader).
- `tests/test_project_insights_integration.py` (Project insights integration test suite).

### Reference & Documentation
- `docs/MAPA_FUNCIONAL_CERBERUS.md` (Functional map of Coder Cerberus core and satellite ecosystems).
- `CERBERUS_CONCEPTUAL_FRAMEWORK.md` (Documento de identidad de Cerberus v0.5 — fuente única sobre qué ES Cerberus).
- `00 audit/00_CONSTITUCION_CERBERUS.md`, `00 audit/01_AUDITORIA_LOCAL.md`, `00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md` (doctrina viva, tres pilares: definición + uso del paquete en §5, auditoría local, auditoría de satélites. `02_AUDITORIA_REPOSITORIOS`/`03`/`04` y el README de orden — fusionado en `00 §5` — deprecados en `deprecated/audit_doctrine_legacy/2026-06-06/`).

### Templates Generativos
- `docs/templates/SPEC_FEATURES_TEMPLATE.md` (Plantilla estructurada para nuevas features).
- `docs/templates/SPEC_BUGS_TEMPLATE.md` (Plantilla estructurada para resolución de bugs).
- `docs/templates/SPEC_REFACTORS_TEMPLATE.md` (Plantilla estructurada para refactorizaciones).

### Git Hooks & Config
- `scripts/hooks/post-commit`, `scripts/hooks/pre-commit`, `scripts/hooks/commit-msg`, `scripts/hooks/pre-push`, `.gitignore`, `.cursorrules`, `HISTORIAL.md`, `scripts/__init__.py`, `pytest.ini`.
- `scripts/check_handoff_freshness.py` (VC-140: enforcement de continuidad — hook commit-msg), `HANDOFF.template.md` (plantilla de relevo), `HANDOFF.md` (relevo vivo entre agentes).
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
- `.protocol/metadata/internal_graph.json` (Internal project dependency graph registry — source of truth for Capa 1 dependencies).
- **[EXTERNO]** `D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml` (manifest/index) + `golden_standard_*.yaml` (catálogos: coding_vices, testing_vices, tokenomics, project_insights). Repo independiente — no copiar aquí.
- **[DEPRECADO en GS]** `deprecated/knowledge_snapshots/BIBLIOTECA_VICIOS_VIBE_CODING.md`, `BIBLIOTECA_VICIOS_TESTING_EVALUACION.md`, `BIBLIOTECA_TOKENOMICS_CONTEXTO.md` — viven en `VibeCoding_GoldenStandard/deprecated/`.

### Registered Projects (MANDATORY SYNC)
**Fuente canónica:** `.protocol/metadata/REGISTRY.json` — no duplicar inventarios de archivos aquí.
Los archivos de cada proyecto externo pertenecen a su propio repositorio, no a SPEC.md de Cerberus.
Cerberus propaga a cada proyecto: `scripts/run_security_audit_12d.py`, `scripts/pre_edit_guard.py`, `scripts/run_compliance_tests.py`, `scripts/core_utils.py`, `scripts/verify_chaos_robustness.py`, `.claude/settings.json`.

Proyectos registrados (fuente canónica: REGISTRY.json — 17 satélites activos):
- **Frankenstein**, **Aequitas_OS**, **Agente_Inmobiliario**, **Blog_Ciudadano_X**, **Calculadora de sueldos**, **Calculadora_Plazos**, **Control_Procesal**, **Declutter**, **Imagen_Corporativa_Aequitas**, **Indices_Financieros**, **Maletin Homeopatia**, **Quenza**, **RED-Python**, **Referencias**, **Sistemas_Estocasticos_Ruleta**
- Paths: `D:\AI\<nombre>` — ver REGISTRY.json para estado de adopción (hook/auditor/tests) por satélite.

Proyectos bajo gestión Cerberus sin inventario detallado:
- **Aequitas_OS**, **Alesa Inc**, **Amparo Pensiones**, **Blog_Ciudadano_X**, **Calculadora de sueldos**, **Calculadora_Plazos**, **Imagen_Corporativa_Aequitas**, **Indices_Financieros**, **Maletin Homeopatia**, **Referencias**

---

## 🩹 PLAN DE REMEDIACIÓN — FASE A (DISEÑO, 2026-06-06)
**Ejes:** GS→Cerberus · Diseño→Código. Ningún código (Fase B) hasta que toda Fase A esté aprobada (S2 Brain-First).

**Hallazgo raíz:** las deudas internas son instancias de vicios YA catalogados en el GS; ~100/139 VC están en estado `DOC_ONLY` (prosa sin hook/test) — el mismo patrón "validación ceremonial". El anchor citeable (`golden_standard_ref` + IDs VC/VT/TK/PI) **ya existe** en CERBERUS_CONTRACT.md; falta *enforcarlo*.

**Anclaje deuda → vicio GS (cada remediación cita su VC):**
| Deuda | Ancla GS | Estado GS |
|---|---|---|
| #1 blob `.protocol/metadata/golden_standard_audit.json` monolítico | VC-048 Memoria monolítica | PREVENTED |
| #4 TK-031 mide transcript entero | VC-051 Saturación contextual + VC-052 | DOC_ONLY |
| #5 doctrina auditoría en prosa (caso RED-Python) | VC-067 Políticas implícitas + VC-092 + VC-108 | DOC_ONLY |
| #3/#6 grafo sin capa interna | VC-069 Dependencias no mapeadas + VC-066 | PREVENTED |
| #2 68 scripts | VC-064 Caja negra + VC-040 | DOC_ONLY |

**G3 (canon→anchor) se fusiona en C5:** el anchor ya existe; el trabajo es el gate que verifica `golden_standard_ref`. El lado GS se deposita como hallazgo vía `Inbox/cerberus/` (Direction 2 del contrato), no editando el Wiki curado.

**Decisiones G-items APROBADAS (2026-06-06, Luis):**
- **G1 (opción B) — función GS.** El pipeline de ingesta GS solo admite VC/VT/TK/PI; las 3 refs de arquitectura (Karpathy LLM-Wiki, graphify, Obsidian) NO son vicios. Se añade una sección nueva **"Reference Library / Prior Art"** a KNOWLEDGE_SOURCES.md (cambio de contrato GS, acción de curador). Registro de prior-art consultable, NO reglas con enforcement.
- **G2 — función GS.** Operación **Lint** que audita el conocimiento GS (no código satélite). Detecta: huérfanos bidireccionales (Wiki↔YAML), gaps (VC `DOC_ONLY` sin downstream), contradicciones (severidad/estado divergentes, refs rotas). Salida: lint_report.md (solo audita, no muta). Script lint_knowledge.py vive en repo GS; Cerberus lo invoca/consume.
- **G4 → C1 (función Cerberus).** Decisión: **caché quirúrgico ahora, SQLite diferido.** Patrón `_GOLDEN_CACHE` ya existe en `protocol_engine/knowledge_loader.py`; ~8 líneas, cero riesgo de esquema. SQLite = nueva dependencia (B11) + 6 consumidores en riesgo, no justificado para 1 usuario. Ancla VC-048.
- **Colapsos:** G3→C5 (anchor ya existe; falta el gate) · G4→C1 · G1→sección nueva en contrato GS. Único diseño G "nuevo" sustantivo: G2 (Lint).

**Orden Fase B (tras aprobar diseño):** **✅ C4 HECHO** → **✅ C1 HECHO** → **✅ C3 HECHO (2026-06-06)** → C5 gates+anchor (VC-067) → [C2 diferido]. Cada item: PLAN.md + Angry Path + gate verde + rollback, ≤50 líneas/turno.

**C1 cerrado (VC-048):** `load_golden_standard_audit()` ahora memoiza en `_GOLDEN_AUDIT_CACHE` (caché de proceso, patrón `_GOLDEN_CACHE`); cargas vacías por archivo ausente NO se cachean. Sin cambios de call-site (S19). Gate `test_audit_db_is_memoized` + compliance 8/8 PASS. SQLite diferido.

**C3 cerrado (VC-069):** Grafo Capa 1 interno implementado usando `graphify` v0.8.33. Extrae relaciones de código (`calls`, `imports`, `references`) en un staging temporal que luego se limpia para evitar contaminar el repo. Filtro `_only_python` preserva la consistencia de los node ids. Escribe el artefacto `.protocol/metadata/internal_graph.json` (nombre deconflictado de Capa 2). Integridad validada en tests y con el auditor.

**Arquitectura Federada de Grafos — Fase 1 CERRADA (2026-06-07):** Las 3 capas implementadas y unit-testeadas. Capa 1 (AST código, `internal_graph.py`), Capa 2 (docs Obsidian doc↔doc + doc→código vía `documents`), Capa 3 (ecosistema, `generate_graph_report.build_graph_json` mergea `proj:doc`). 5 hallazgos de auditoría adversarial corregidos (extraction_status, node_id por ruta, vault candidates, contrato trustworthy, edges doc→código). **Fase 2c CERRADA (2026-06-07):** `alignment_checker.py` v1.2 — "símbolo crítico" acotado a los 14 god_nodes documentables (excluidos artefactos `*_py_path` + `ast`; entry_points dejan de ser críticos); doc_orphans degradados a WARN advisory; gate **opt-in** (marcador `.protocol/align_gate.enabled`) para no brickear satélites no documentados. Deuda de contenido pagada: `docs/architecture/CODE_MAP.md` documenta los 14 hubs → **cobertura crítica 100%, gate ACTIVO en Cerberus** (exit 0). La Capa 3 live-merge se poblará cuando los satélites generen sus grafos locales (adopción pendiente del go de Luis). Bug auto-detect protocol_engine corregido. **PASO 3 — binding satélites REPARADO (2026-06-07):** causa raíz = junctions `.protocol-core` apuntando a `Cerberus\rules` (inexistente) tras reorganizar Cerberus → enforcement muerto en los 17. `repair_protocol_junction.py` repuntó los 14 satélites con git (3 sin git omitidos: Frankenstein, Alesa Inc, Amparo Pensiones) al modelo junction→raíz viva. Decisión de Luis "**solo reparar junction, sin hook**": se neutralizaron los pre-commit/pre-push Cerberus de los satélites (el pre-commit corre el auto-audit 12D de Cerberus contra el satélite y SIEMPRE falla → brickearía los 14 repos; el diseño de un gate satélite-aware queda para un sprint aparte) y se generó `.protocol/metadata/internal_graph.json` local en los 14 (fuente de la Capa 3). El marcador `align_gate.enabled` NO se propagó (anti-brick). **DEUDA ABIERTA:** (3-d) reconciliar `global_sync_safe.py`/`migrate_to_subtree.py` (aún hacen subtree-pull, modelo obsoleto — S19) y diseñar el gate satélite ligero.

**C4 cerrado (VC-051) — causa raíz re-diagnosticada:** NO era falta de watermark. `observe_session()` (`dimensions/d13_observable.py`) ya particionaba el transcript en el último `/compact`, pero buscaba la clave `type=="summary"` que esta versión de Claude Code nunca emite; el marcador real es `isCompactSummary:true`. Fix = **1 línea** (cambio de clave), sin tocar `discourse_hook`/`compact_automation_helper`/`pre_edit_guard` (enforcement intacto, S19). Verificado: 2 tests gate PASS + transcript real 2,657,769 → 13,014 tokens.

**C4-followon cerrado (TK-031, 2º eje) — eje-msgs eliminado del bloqueo:** con tokens ya bien medidos, el bloqueo seguía colgando de `over_msgs OR over_tokens` en `discourse_hook.py`; un turno con muchas herramientas acumula ≥40 mensajes `assistant` con tokens bajos (caso real 62 msgs / 13K tokens) → re-bloqueo de trabajo productivo. Decisión Luis: **el bloqueo cuelga SOLO de tokens**; msgs queda como aviso informativo. `_check_and_flag_compact` ahora usa `if over_tokens:`. Sin tocar `pre_edit_guard` (S19). Gate NUEVO (antes sin cobertura): 3 tests en `tests/test_discourse_hook.py` PASS.

**VC-140 cerrado (Norma de Continuidad, Sprint 3.6) — relevo entre agentes obligatorio:** problema real de Luis (opera Codex/Gemini/Claude y se queda sin tokens a mitad de tarea → pérdida de contexto). Capa GS: vicio **VC-140 "Brecha de continuidad / handoff huérfano"** → `PREVENTED`, mech `check_handoff_freshness`. Capa Cerberus: hook git **`commit-msg`** (agnóstico — corre con cualquier `git commit`) que bloquea si hay cambios sustantivos sin `HANDOFF.md` fresco (esquema fijo ESTADO/SIGUIENTE/VERIFICAR). Escape `[skip-handoff]`/`CERBERUS_SKIP_HANDOFF=1`. Artefacto canónico `HANDOFF.md` vivo (histórico en HISTORIAL.md); plantilla `HANDOFF.template.md`. Propagación: `install_hooks.sh/.ps1` ahora instalan `commit-msg` → satélites heredan. Gate: 6 tests `tests/test_handoff_freshness.py` + bloqueo/escape verificados end-to-end + compliance/ratchet 16/16.

---

## 🚀 ACTIVE CONTEXT
- **Estado:** CoderCerberus V0.5 — operacional. Auditoría interior completada 2026-06-05.
- **Meta:** Cobertura total GS → Cerberus → Test para cada VC/TV/TK PREVENTED/REMEDIATED.
- **Riesgo Crítico:** Afirmaciones de estado sin VERIFIED/INFERRED/ASSUMED (PI-020).
- **Deuda conocida:** SPEC.md tiene referencias a docs/scripts de versiones anteriores — limpiar progresivamente con lint_protocol_docs.py.

---
**Coder Cerberus V0.5 — Inmunidad Total.**
