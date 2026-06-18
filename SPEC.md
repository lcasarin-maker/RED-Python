# 🧠 SPEC.md — The Brain of CoderCerberus (CoderCerberus Memory Bank V0.5)
**Status:** 💎 SINGLE SOURCE OF TRUTH | Version: v0.5

---

## 🏗️ ARCHITECTURE AND PURPOSE
This repository is the immutable core of **Coder Cerberus V0.5**. Its mission is to eliminate silent AI failure through defensive architecture, multi-agent orchestration, and zero-trust auditing.

### 🧭 AUTHORITY MODULE ROUTER
Cerberus's authority core is made of 6 master modules dynamically linked into the operational constitution:
1. **00_EVIDENCE_AND_THREAT_MODEL.md**: References the threat model and forensic analysis.
2. **PROTOCOL_BEHAVIOR.md**: Linguistic reasoning and behavior rules (Caveman Mode, Luis Treatment).
3. **PROTOCOL_SYSTEM.md**: Physical rules, I/O prohibitions, and agent confinement.
4. **MANDATES_BY_PHASE.md**: Phase-by-phase workflows and sequential directives.
5. **TOKENOMICS_AND_ROUTING.md**: Extreme context-efficiency strategies, mandatory grep, and model routing.
6. **USER_CONTEXT.md**: Identity, interests, style, and logistics of operator Luis Casarín.

---

## 🎨 SYSTEM PATTERNS (Design Philosophy)
1.  **Brain-Muscle:** `SPEC.md` defines reality; `PROTOCOL_SYSTEM.md` executes the technical enforcement.
2.  **Angry Path Dominance:** The main flow is failure; success is the residue of an error not yet found.
3.  **Bio-Containment:** Strict isolation of AI-generated modules behind immutable interfaces.
4.  **Global Symmetry:** Local improvement -> Core promotion -> 1:1 synchronization.
5.  **Multi-Agent Patterns (future scale):** When Cerberus coordinates multiple agents, the validated patterns are: *sequential pipeline* (planner→coder→reviewer), *fan-out/fan-in* (planner splits work across N parallel agents, then merges), *supervisor* (one agent dispatches and reviews the others), *debate/critic* (two agents argue, a third decides). Operational reference: `docs/SINTAXIS_MULTI_AGENT.md`.

---

## 🧠 AGENT MEMORY TAXONOMY (3 Layers)
Formalization of the bootstrap ritual and layered context handling:

| Layer | Content | Duration | Cerberus implementation |
|------|-----------|----------|---------------------------|
| **Short-term** | Current task context, active plan, conversation | Duration of the run | Prompt window + PLAN.md |
| **Long-term** | Stable project facts: conventions, rules, whitelist | Indefinite (until explicit change) | `SPEC.md`, `AGENT.md`, `PROTOCOL_*.md` |
| **External** | Cross-session artifacts: decision history, checkpoints, handoffs | Configurable TTL | `HISTORIAL.md`, `.agent_state.json`, `STATE CHECKPOINT` |

**Mandatory expiration rules:**
- Short-term: expires at the end of each task (never load prior task context without rereading it)
- Long-term: prune entries not referenced in 10+ sessions; update when `sync_binding.py` detects changes
- External: archive `HISTORIAL.md` entries older than 30 days via `compress_historial.py`

**Memory scoping:** Only inject what the CURRENT task needs. Loading the full context = signal dilution + unnecessary cost + information leakage across tasks.

## 🦴 DATA SKELETON & UI LAYOUT

**Agent Handoff State** (`.agent_state.json`):
`{version, session_id, agent_name, tier, status, next_step, protocol_checksums:{AGENT.md, PROTOCOL_BEHAVIOR.md, PROTOCOL_SYSTEM.md, SPEC.md}, session_token_budget:{tokens_used_so_far, compressions_this_session[]}, known_agents[], agent_permissions{}}`

**Evidence Record** (`.protocol/evidence/*.json` — 1 per operation):
`{timestamp:ISO8601-UTC, agent_capability_tier:"TRUSTED"|"ISOLATED"|"AUDIT", action_invoked:str, verification_outcome:"APPROVED"|"BLOCKED"|"REPLAN", affected_deltas:[filepath]}`

**SQLite: retrospectives** (`protocol_state.db`):
`(id UUID PK, session_id TEXT, timestamp DATETIME, learning_1 TEXT, violation TEXT, next_agent_knows TEXT, protocol_gaps TEXT, token_efficiency FLOAT, export_status TEXT)`

**SQLite: alerts** (shared DB):
`(id INTEGER PK, level TEXT, category TEXT, message TEXT, details TEXT, timestamp DATETIME, resolved BOOL)`

**SQLite: token_events** (shared DB):
`(id INTEGER PK, event_type TEXT, tokens_saved INTEGER, action TEXT, timestamp DATETIME)`

## 🧹 AUDIT 12-DOMAIN VALIDATOR (12D)
- **D1: Integrity** — forensic whitelist, no zombie files, version parity
- **D2: Completeness** — full control plane; core scripts exist and have tests
- **D3: Clarity** — no dead code, functions named with clear purpose
- **D4: Anti-Spaghetti** — no import cycles, max complexity, god-node fan-in
- **D5: Angry Path** — real error handling (non-empty try/except)
- **D6: Anti-Slop** — no weak typing (Any), no filterwarnings without justification
- **D7: Security** — no hardcoded secrets, no dangerous I/O patterns
- **D8: Adversarial coverage** — tests that truly falsify; negative paths covered
- **D9: Test purity** — no assert True, no permanent xfail, no skip without a date
- **D10: Tokenomics** — manifests under limit, OutputCompressor in orchestrators
- **D11: Trivy SCA** — no critical CVEs in dependencies
- **D12: Satellite drift** — satellites aligned with the core protocol version
- **D13: Validation Debt** — audit debt recorded, remediated, automated post-mortem (scripts: `satellite_validation_debt.py`, `postmortem_validation_analysis.py`, `audit_d13_validation_debt.py`)

---

## 💻 TECH CONTEXT (Rigor Stack)
- **Runtime:** Python 3.13 (UTF-8) | **Test Runner:** Pytest / Unittest.
- **Enforcers:** `scripts/run_security_audit_12d.py` (12D auditor - primary gatekeeper), `scripts/pre_edit_guard.py` (PreToolUse hook - real-time prevention), `scripts/run_compliance_tests.py` (pre-commit gatekeeper).
- **Validation Debt (D13):** `scripts/satellite_validation_debt.py` (registry API), `deprecated/bootstrap_v0.5/validate_satellite_functional.py` (empirical proof), `scripts/postmortem_validation_analysis.py` (systemic analysis), `scripts/audit_d13_validation_debt.py` (D13 domain auditor).
- **Chaos Engine:** `scripts/verify_chaos_robustness.py` (resilience validation).
- **Integrity:** Mandatory Git hooks. No direct shell file manipulation.

---

## 🛡️ WHITELIST (War Inventory)
Only these files are allowed to exist in the core:

### Allowed Subdirectories
- **`rules/`** — Rules and protocol_engine artifact subproject. Full structure allowed: `.agent_state.json`, `SPEC.md`, `scripts/`, `protocol_engine/`, `tests/`, `.claude/`, `.github/`, `docs/` with operational artifact content (non-zombie).
- ~~**`Golden_Standard/`**~~ — **REMOVED**. GS moved to the independent repo `D:\AI\VibeCoding_GoldenStandard`. Cerberus consumes it via an external path; no local copy exists.
- **`deprecated/`** — Archive of deprecated scripts/files. Full content allowed as temporary quarantine.
- **`auditorias/`** — Audits by date. Test and evidence content allowed.
- **`docs/`** — Architecture and procedure documentation.

### Master Manifests
- `.claudeignore`, `AGENT.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md`, `MANDATES_BY_PHASE.md`, `ESCALATION_PROTOCOL.md`, `GEMINI.md`, `GLOBAL_LEARNING.md`, `.agent_state.json`, `SPEC.md`, `VERSION.txt`, `TOKEN_BUDGET.md`, `PERMISSIONS.md`, `USER_CONTEXT.md`, `TOKENOMICS_AND_ROUTING.md`, `MATRIZ_AUTOMATIZACION_COMPLETA.md`, `.pre-commit-config.yaml`, `scripts/bump_version.py`, `README.md`, `CHECKLIST.md`, `SOURCES_OF_TRUTH.md`, `DEPRECATION_LOG.md`, `GRAPH_REPORT.md`, `project_cerberus_interior_debt.md`, `.claude/settings.json`, `.github/workflows/cerberus-gatekeeper.yaml`

### Core Scripts (Muscle)
- `scripts/run_security_audit_12d.py` (12D auditor — gatekeeper primario), `scripts/pre_edit_guard.py` (PreToolUse hook), `scripts/run_compliance_tests.py`, `scripts/global_sync_safe.py`, `scripts/track_tokens.py`, `scripts/core_utils.py`.
- `scripts/verify_chaos_robustness.py` (6 escenarios reales A-F), `scripts/install_hooks.sh` (setup inicial de git hooks — Linux/macOS), `scripts/install_hooks.ps1` (setup inicial de git hooks — Windows, P6.4), `scripts/install_cerberus.ps1` (Windows native installer, B2).
- `scripts/run_self_improvement.py` (autonomous loop: audit+chaos+suite -> HISTORIAL.md).
- `scripts/manage_tokens.py` (v2.0: OutputCompressor + ContextStore + ContextExtractor + TokenOptimizer + `--compact` CLI).
- `scripts/manage_review_queue.py` (Phase F: human review queue -> `.protocol/review_queue.json`).
- `scripts/send_review_reminder.py` (Phase F: Windows notification for pending commits).
- `scripts/setup_reminder_task.py` (Phase F: configures Task Scheduler - run once).
- `scripts/compress_memory_context.py` (v1.1, ReMe-style advanced memory compression and markdown fallback engine).
- **Archived in deprecated/purga_v002/**: `token_optimizer.py`, `smart_context_extractor.py`, `rtk_auto_compress.py`, `auto_commit_enforcer.py`, `promote_to_core.py`, `automation/autonomous_orchestrator.py`, `automation/auto_remediation.py`.
- `scripts/monitor_projects.py`, `scripts/monitor_heartbeat.py` (active - maintenance orchestration).
- `scripts/lint_knowledge.py` (v1.0, G2: Wiki & Knowledge Linter - audits broken links, orphans, and GS schemas).
- `scripts/remediation_engine.py` (v1.0: Auto-remediation engine for deterministic fixes and logical-failure queueing).
- `scripts/setup_scheduler_task.ps1` (v1.0: Registers the background monitor task in Windows Scheduled Tasks).
- `scripts/resolve_historial_conflicts.py` (rescued: semantic HISTORIAL merge).
- `scripts/serve_dashboard.py` (rescued: observability dashboard).
- `scripts/resolve_deadlocks.py` (rescued: concurrency resolution).
- `scripts/verify_protocol_adoption.py` (v1.0, P5.1: audits real protocol adoption in child projects - hook + auditor + tests).
- `scripts/setup_validate.py` (v1.0, P5.6: bootstrap validator - 6 checks: Python, essential files, git, hook, registry, write access).
- `scripts/sync_binding.py` (v1.0, Claude Binding: bidirectional protocol synchronization).
- `scripts/protocol_cli.py` (v1.0, Control Plane: single authority for all protocol operations).
- `scripts/validate_chunking.py` (v1.0, PHASE 2: file chunking validation).
- `scripts/check_empirical_proof.py` (v1.0, PHASE 2: empirical proof validation).
- `scripts/log_evidence.py` (v1.0, PHASE 3: formal evidence logging with JSON schema).
- `scripts/global_sync_safe.py` (v2.0, PHASE 5: safe multi-project protocol distribution).
- `scripts/clean_satellites.py` (v1.0: purges deprecated files from satellite directories).
- `scripts/migrate_to_subtree.py` (v1.0: automates Git Subtree migration for all active projects).
- `scripts/repair_protocol_junction.py` (v1.0, Sprint 3.9/STEP 3: auto-repairs satellite `.protocol-core` binding. Model **junction** -> Cerberus's living root (derived from `__file__` = self-heal); replaces subtree-pull (S19). Pure `classify`/`repair_action` (testable); `junction_status` gathers Windows probes (reparse tag, readlink). Idempotent and SAFE: never deletes a real dir (`not_junction`->skip_unsafe); only repairs dangling/wrong_target/missing. Root cause fixed: junctions pointed to missing `Cerberus\rules` after the Cerberus reorg -> enforcement dead across the 17. CLI `--repo-root | --all | --dry-run`).
- `tests/test_repair_junction.py` (v1.0, Sprint 3.9: tests for the pure classification/decision logic - the risk is never touching a real user dir).
- `scripts/audit_permissions.py` (v1.0, PHASE 6: agent permission safety gate).
- `scripts/audit_hygiene.py` (v1.0, D6: encoding hygiene and legacy deprecation gate).
- **v0.5 Hooks activos:**
  - `scripts/enforce_thinking_limits.py` (TK-044: thinking limits enforcer for responses)
  - `scripts/model_router.py` (TK-045: Router inteligente de modelos por tarea)
  - `scripts/tool_result_cleaner.py` (TK-047: Limpiador de resultados de herramientas)
  - `scripts/block_auto_docs.py` (TK-049: automatic docs generation blocker)
  - `scripts/image_cost_detector.py` (TK-050: image cost detector)
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
- `scripts/run_self_improvement.py` (v1.0, D8: autonomous audit loop - detects gaps and documents them in HISTORIAL.md without modifying code).
- `scripts/validate_routing.py` (v1.0, RULE #28: validates multi-agent routing in HISTORIAL.md).
- `scripts/validate_security_tier.py` (v1.0, RULE #24: validates security boundaries and tier permissions).
- `scripts/view_alerts.py` (v1.0, REGLA #6: CLI para visualizar alertas centralizadas — tabla alerts compartida con token_tracker and deadlock_resolver).
- `dimensions/d13_observable.py` (Sprint 28.5: D13 Observable Behavior moved into the package, HOOK channel - consolidates the four d13_* scripts (token meter+tiktoken, decision logger, divergence detector, D13Report); `observe_session` sums transcript tokens; wired through discourse_hook.py; replaces the standalone scripts, S19).
- `tests/test_d13_observable_behavior.py` (Sprint 24: Tests para D13 — 12 casos token/decisiones/divergencias).
- `dimensions/d3_dead_code.py` (Sprint 28.5: D3 Dead Code wired to the gate via REGISTRY - ruff F + vulture dead defs only; replaces inline `audit_dead_code` and the theater `d3_dead_code_enhanced` (S19); missing binary -> UNAVAILABLE).
- `dimensions/d11_dependency.py` (Sprint 28.5: D11 Dependency wired to the gate via REGISTRY - consolidated Trivy SCA (replaces inline `audit_d11_validate_sca_trivy`, S19) + PyPI freshness for outdated/yanked; Trivy missing -> UNAVAILABLE, offline -> WARN; replaces the theater `d11_dependency_enhanced`).
- `dimensions/d7_security.py` (Sprint 28.5: D7 Data Security wired to the gate via REGISTRY - secret/injection regex (preserved from the inline version) + bandit SAST (HIGH→FAIL, missing→UNAVAILABLE); no Trivy (D11 owns it); Semgrep deferred; replaces inline `audit_d7_data_security` + theater `d7_security_enhanced`, S19).
- `dimensions/d14_discourse_rigor.py` (Sprint 28.5: D14 Discourse Rigor moved into the package, HOOK channel - audits the agent response via `audit_response`, not the repo; the gate skips it; real clarity/ambiguity/evidence/cot metrics; replaces the standalone script, S19).
- `scripts/discourse_hook.py` (Sprint 28.5: runtime Stop hook - extracts the prose from the last assistant message in the JSONL transcript and runs D14.audit_response; WARN-only, exit 0; wired in `.claude/settings.json` hooks.Stop. Makes D14 enforceable in practice).
- `scripts/generate_dimension_registry.py` (Sprint 28.5 Step 1: generates `dimension_registry.json` - derives it from the repo channel/wiring/binary/real-test status per dimension).
- `dimension_registry.json` (Sprint 28.5: ledger committeado de dimensiones; fresh-gated; documenta verdad inerte — 9/14 fully-wired, dual-impl D3/D7/D11, hook D13/D14).
- `dimensions/base.py` (Sprint 28.5 Paso 2: contrato `Dimension` + `Finding` + `Status` con UNAVAILABLE — insumo ausente nunca PASS silencioso).
- `dimensions/context.py` (Sprint 28.5 Step 2: `AuditContext` - single pass, file list + AST cached once).
- `dimensions/__init__.py` (Sprint 28.5 Step 2: `REGISTRY` - single source of truth for dimensions; the gate loops over it).
- `requirements.txt` (Sprint 28.5: direct dependency manifest - single pinned source of truth; PyYAML runtime + pytest test; real input for Trivy/D11. Replaces CI fallback theater).
- `scripts/compress_historial.py` (v1.0, FASE 5: Token-saving — archives HISTORIAL.md sessions older than N days; soporta --auto para stop hook).
- `scripts/lint_protocol_docs.py` (v1.0, PI-021: semantic Wiki lint - detects broken refs, inconsistent versions, and contradictions across protocol docs).
- `scripts/generate_graph_report.py` (v1.0, PI-020: generates GRAPH_REPORT.md + graph.json with the satellite graph, adoption, and protocol god-nodes).
- `scripts/check_deprecation_log.py` (v1.0, S24: Valida que archivos staged en deprecated/ tienen entrada en DEPRECATION_LOG.md).
- `scripts/cache_protocol_rules.py` (v2.0, FASE 5: Token-saving — indexes PROTOCOL_SYSTEM.md + PROTOCOL_BEHAVIOR.md into .claude/cache/protocol_rules.json. 39 mandates cached for fast load.).
- `scripts/export_retrospective.py` (v1.0, FASE 8: Auto-exports latest HISTORIAL.md session to JSON and/or SQLite DB).
- `scripts/internal_graph.py` (v1.2, C3/Federated: Layer 1 graph (AST) + Layer 2 (Obsidian docs doc↔doc and doc→code via `documents` edges). `extraction_status` distinguishes failure from emptiness; `extraction_is_trustworthy()` prevents false green. `_auto_detect_targets` includes protocol_engine. Phase 2b: `_build_symbol_aliases` resolves [[short_name]]→full id with uniqueness guard).
- `tests/test_internal_graph.py` (v1.0, C3: Tests para Grafo Capa 1 interno).
- `scripts/alignment_checker.py` (v1.2, Phase 2c CLOSED: code (Layer 1) ↔ docs (Layer 2) alignment linter. `critical_symbols` = **documentable** god_nodes (`_is_documentable_symbol` excludes `*_py_path` artifacts and symbols outside the repo namespaces; entry points are NO LONGER critical). code_orphans→FAIL; doc_orphans→WARN advisory (a doc without links is hygiene, not correctness failure). **Opt-in** gate via `.protocol/align_gate.enabled` marker (`align_gate_enabled`/`gate_exit_code`): blocking where content debt was paid, advisory on undocumented satellites (anti-brick). CLI command `align-check`. In Cerberus: 100% critical coverage (14 god_nodes documented in `docs/architecture/CODE_MAP.md`), gate ACTIVE).
- `tests/test_alignment_checker.py` (v1.2, Phase 2c: linter tests - documentable predicate, artifact exclusion, non-critical entry points, opt-in gate).
- `docs/architecture/CODE_MAP.md` (Phase 2c: critical code surface map - 14 god_nodes across the 5 core modules with `[[refs]]` resolved by the linter; satisfies the critical coverage invariant).
- `scripts/check_clean_worktree.py` (v1.0, VC-141: detects skipped changes / partial commits. Pure function `worktree_is_clean`; blocks pre-commit if the working tree is dirty after staging. Escape CERBERUS_ALLOW_PARTIAL=1).
- `tests/test_clean_worktree.py` (v1.0, VC-141: tests for clean working tree detection + adoption idempotence).
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
- `docs/FALLOS_CONOCIDOS.md` (known failures registry - pre-existing technical debt).
- `GLOBAL_LEARNING.md` (cross-session learnings extracted from HISTORIAL.md; canonical at root per TK-007).
- `docs/PATRONES_TECNICOS.md` (technical patterns reference — anti-patterns and solutions).
- `docs/REFERENCIA_RAPIDA.md` (quick reference card for protocol commands and scripts).
- `docs/SINTAXIS_MULTI_AGENT.md` (multi-agent coordination syntax and handoff patterns).
- `scripts/helpers.py` (v1.0, shared utilities: helper function consolidation for refactored scripts).
- `.github/workflows/protocol.yaml` (GitHub CI: unittest, rigor_maestro, global sync dry-run, human review gate P4.6).
- `.github/pull_request_template.md` (P4.6: PR template with human review checkbox - CI verifies it on every PR).
- `protocol_engine/__init__.py` (Consolidated knowledge-base package init).
- `protocol_engine/knowledge_loader.py` (Golden Standard yaml/md knowledge loader).
- `tests/test_project_insights_integration.py` (Project insights integration test suite).

### Reference & Documentation
- `docs/MAPA_FUNCIONAL_CERBERUS.md` (Functional map of Coder Cerberus core and satellite ecosystems).
- `CERBERUS_CONCEPTUAL_FRAMEWORK.md` (Cerberus v0.5 identity document - single source on what Cerberus IS).
- `00 audit/00_CONSTITUCION_CERBERUS.md`, `00 audit/01_AUDITORIA_LOCAL.md`, `00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md` (living doctrine, three pillars: definition + package usage in §5, local audit, satellite audit. `02_AUDITORIA_REPOSITORIOS`/`03`/`04` and the order README - merged into `00 §5` - deprecated in `deprecated/audit_doctrine_legacy/2026-06-06/`).

### Templates Generativos
- `docs/templates/SPEC_FEATURES_TEMPLATE.md` (Plantilla estructurada para nuevas features).
- `docs/templates/SPEC_BUGS_TEMPLATE.md` (structured bug resolution template).
- `docs/templates/SPEC_REFACTORS_TEMPLATE.md` (Plantilla estructurada para refactorizaciones).

### Git Hooks & Config
- `scripts/hooks/post-commit`, `scripts/hooks/pre-commit`, `scripts/hooks/commit-msg`, `scripts/hooks/pre-push`, `.gitignore`, `.cursorrules`, `HISTORIAL.md`, `scripts/__init__.py`, `pytest.ini`.
- `scripts/check_handoff_freshness.py` (VC-140: enforcement de continuidad — hook commit-msg), `HANDOFF.template.md` (plantilla de relevo), `HANDOFF.md` (relevo vivo entre agentes).
- `.claude/` (Claude Code configuration folder).
- `.claude/CLAUDE.md` (Project-specific binding for Claude agents, v0.3).
- `.claude/.gitignore` (Exclusion rules for Claude Code temporary files).
- `.claude/settings.local.json` (Local Claude Code settings).
- `.claude/settings.template.json` (Reviewed safe Claude Code permissions template).
- `PRE_DELIVERY_CHECKLIST.md` (agent self-review checklist).
- `.protocol/cleanup_log.json` (D6 workspace cleanup log).
- `.protocol/rollback_manifest.json` (D6 rollback instructions).
- `.protocol/evidence/.gitkeep` (Evidence directory placeholder).
- `.protocol/evidence/audit.json`, `.protocol/evidence/sync.json`, `.protocol/evidence/promote.json` (PHASE 3 operation evidence).
- `.protocol/metadata/REGISTRY.json` (Active project registry — source of truth for registered projects and sync state. Migrated from .CoderCerberus/ in P8.1).
- `.protocol/metadata/internal_graph.json` (Internal project dependency graph registry — source of truth for Capa 1 dependencies).
- **[EXTERNAL]** `D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml` (manifest/index) + `golden_standard_*.yaml` (catalogs: coding_vices, testing_vices, tokenomics, project_insights). Independent repo - do not copy here.
- **[DEPRECADO en GS]** `deprecated/knowledge_snapshots/BIBLIOTECA_VICIOS_VIBE_CODING.md`, `BIBLIOTECA_VICIOS_TESTING_EVALUACION.md`, `BIBLIOTECA_TOKENOMICS_CONTEXTO.md` — viven en `VibeCoding_GoldenStandard/deprecated/`.

### Registered Projects (MANDATORY SYNC)
**Canonical source:** `.protocol/metadata/REGISTRY.json` - do not duplicate file inventories here.
Los archivos de cada proyecto externo pertenecen a su propio repositorio, no a SPEC.md de Cerberus.
Cerberus propaga a cada proyecto: `scripts/run_security_audit_12d.py`, `scripts/pre_edit_guard.py`, `scripts/run_compliance_tests.py`, `scripts/core_utils.py`, `scripts/verify_chaos_robustness.py`, `.claude/settings.json`.

Registered projects (canonical source: REGISTRY.json - 17 active satellites):
- **Frankenstein**, **Aequitas_OS**, **Agente_Inmobiliario**, **Blog_Ciudadano_X**, **Calculadora de sueldos**, **Calculadora_Plazos**, **Control_Procesal**, **Declutter**, **Imagen_Corporativa_Aequitas**, **Indices_Financieros**, **Maletin Homeopatia**, **Quenza**, **RED-Python**, **Referencias**, **Sistemas_Estocasticos_Ruleta**
- Paths: `D:\AI\<name>` - see REGISTRY.json for adoption status (hook/auditor/tests) per satellite.

Cerberus-managed projects without a detailed inventory:
- **Aequitas_OS**, **Alesa Inc**, **Amparo Pensiones**, **Blog_Ciudadano_X**, **Calculadora de sueldos**, **Calculadora_Plazos**, **Imagen_Corporativa_Aequitas**, **Indices_Financieros**, **Maletin Homeopatia**, **Referencias**

---

## 🩹 REMEDIATION PLAN — PHASE A (DESIGN, 2026-06-06)
**Axes:** GS→Cerberus · Design→Code. No code (Phase B) until all of Phase A is approved (S2 Brain-First).

**Root finding:** internal debts are instances of vices already cataloged in GS; ~100/139 VC are in `DOC_ONLY` state (prose without hook/test) - the same "ceremonial validation" pattern. The citeable anchor (`golden_standard_ref` + VC/VT/TK/PI IDs) **already exists** in CERBERUS_CONTRACT.md; it only needs to be enforced.

**Debt → GS vice mapping (each remediation cites its VC):**
| Deuda | Ancla GS | Estado GS |
|---|---|---|
| #1 monolithic `.protocol/metadata/golden_standard_audit.json` blob | VC-048 Monolithic memory | PREVENTED |
| #4 TK-031 measures the full transcript | VC-051 Context saturation + VC-052 | DOC_ONLY |
| #5 audit doctrine in prose (RED-Python case) | VC-067 Implicit policies + VC-092 + VC-108 | DOC_ONLY |
| #3/#6 grafo sin capa interna | VC-069 Dependencias no mapeadas + VC-066 | PREVENTED |
| #2 68 scripts | VC-064 Caja negra + VC-040 | DOC_ONLY |

**G3 (canon→anchor) merges into C5:** the anchor already exists; the work is the gate that verifies `golden_standard_ref`. The GS side is filed as a finding via `Inbox/cerberus/` (Direction 2 of the contract), not by editing the curated Wiki.

**Decisiones G-items APROBADAS (2026-06-06, Luis):**
- **G1 (option B) - GS function.** The GS ingestion pipeline only accepts VC/VT/TK/PI; the 3 architecture refs (Karpathy LLM-Wiki, graphify, Obsidian) are NOT vices. A new **"Reference Library / Prior Art"** section is added to KNOWLEDGE_SOURCES.md (GS contract change, curator action). Prior-art is consultable, not enforced rules.
- **G2 - GS function.** **Lint** operation that audits GS knowledge (not satellite code). Detects: bidirectional orphans (Wiki↔YAML), gaps (VC `DOC_ONLY` without downstream), contradictions (divergent severity/status, broken refs). Output: lint_report.md (audit only, no mutation). Script lint_knowledge.py lives in the GS repo; Cerberus invokes/consumes it.
- **G4 → C1 (Cerberus function).** Decision: **surgical cache now, SQLite deferred.** The `_GOLDEN_CACHE` pattern already exists in `protocol_engine/knowledge_loader.py`; ~8 lines, zero schema risk. SQLite = new dependency (B11) + 6 consumers at risk, not justified for one user. Anchor VC-048.
- **Collapses:** G3→C5 (anchor already exists; only the gate is missing) · G4→C1 · G1→new section in the GS contract. The only substantive new G design is G2 (Lint).

**Phase B order (after design approval):** **✅ C4 DONE** → **✅ C1 DONE** → **✅ C3 DONE (2026-06-06)** → C5 gates+anchor (VC-067) → [C2 deferred]. Each item: PLAN.md + Angry Path + green gate + rollback, ≤50 lines/turn.

**C1 closed (VC-048):** `load_golden_standard_audit()` now memoizes in `_GOLDEN_AUDIT_CACHE` (process cache, `_GOLDEN_CACHE` pattern); empty loads from a missing file are NOT cached. No call-site changes (S19). Gate `test_audit_db_is_memoized` + 8/8 compliance PASS. SQLite deferred.

**C3 closed (VC-069):** Internal Layer 1 graph implemented using `graphify` v0.8.33. Extracts code relations (`calls`, `imports`, `references`) in a temporary staging area that is then cleaned up to avoid contaminating the repo. The `_only_python` filter preserves node id consistency. Writes `.protocol/metadata/internal_graph.json` (Layer 2 deconflicted name). Integrity validated by tests and the auditor.

**Federated graph architecture - Phase 1 CLOSED (2026-06-07):** All 3 layers implemented and unit-tested. Layer 1 (code AST, `internal_graph.py`), Layer 2 (Obsidian docs doc↔doc + doc→code via `documents`), Layer 3 (ecosystem, `generate_graph_report.build_graph_json` merges `proj:doc`). 5 adversarial-audit findings corrected (extraction_status, node_id by path, vault candidates, trustworthy contract, doc→code edges). **Phase 2c CLOSED (2026-06-07):** `alignment_checker.py` v1.2 - "critical symbol" narrowed to the 14 documentable god_nodes (excluding `*_py_path` artifacts + `ast`; entry_points are no longer critical); doc_orphans downgraded to WARN advisory; gate **opt-in** (`.protocol/align_gate.enabled` marker) to avoid bricking undocumented satellites. Content debt paid: `docs/architecture/CODE_MAP.md` documents the 14 hubs -> **100% critical coverage, gate ACTIVE in Cerberus** (exit 0). Layer 3 live-merge will populate when satellites generate their local graphs (adoption pending Luis's go-ahead). Auto-detect protocol_engine bug fixed. **STEP 3 - satellite binding REPAIRED (2026-06-07):** root cause = `.protocol-core` junctions pointing to missing `Cerberus\rules` after the Cerberus reorg -> enforcement dead across the 17. `repair_protocol_junction.py` repointed the 14 git-backed satellites (3 gitless omitted: Frankenstein, Alesa Inc, Amparo Pensiones) to the junction→living-root model. Luis's decision "**repair the junction only, no hook**": Cerberus pre-commit/pre-push hooks were neutralized on the satellites (Cerberus's pre-commit runs the 12D auto-audit against the satellite and ALWAYS fails -> would brick the 14 repos; the design of a satellite-aware gate is left for a separate sprint) and local `.protocol/metadata/internal_graph.json` files were generated in the 14 (Layer 3 source). The `align_gate.enabled` marker was NOT propagated (anti-brick). **OPEN DEBT:** (3-d) reconcile `global_sync_safe.py`/`migrate_to_subtree.py` (they still do subtree-pull, obsolete model - S19) and design the lightweight satellite gate. **STEP 4 - Layer 3 POPULATED (2026-06-07):** `generate_graph_report.py` merged the repaired satellites' `layer2_docs` -> `.protocol/metadata/global_ecosystem_graph.json` with 125 nodes (1 core + 17 satellites + 107 real doc-nodes) / 138 edges (107 has_doc + 17 core→satellite adoption + 14 doc→doc); idempotent. **DEBT (contaminated AST):** each satellite's `layer1_ast` graphed Cerberus code via the `.protocol-core` junction (does not affect Layer 3, which uses only `layer2_docs`); future fix: `_auto_detect_targets` must exclude `.protocol-core`.

**C4 closed (VC-051) - re-diagnosed root cause:** It was NOT a missing watermark. `observe_session()` (`dimensions/d13_observable.py`) already partitioned the transcript at the last `/compact`, but it looked for `type=="summary"`, which this Claude Code version never emits; the real marker is `isCompactSummary:true`. Fix = **1 line** (key change), with no changes to `discourse_hook`/`compact_automation_helper`/`pre_edit_guard` (enforcement intact, S19). Verified: 2 gate tests PASS + real transcript 2,657,769 -> 13,014 tokens.

**C4 follow-on closed (TK-031, second axis) - message axis removed from blocking:** with tokens measured correctly, blocking still depended on `over_msgs OR over_tokens` in `discourse_hook.py`; a tool-heavy turn can accumulate >=40 `assistant` messages with low token counts (real case: 62 msgs / 13K tokens) -> productive work gets re-blocked. Luis's decision: **the block depends ONLY on tokens**; msgs is informational only. `_check_and_flag_compact` now uses `if over_tokens:`. No changes to `pre_edit_guard` (S19). NEW gate (previously uncovered): 3 tests in `tests/test_discourse_hook.py` PASS.

**VC-140 closed (Continuity Norm, Sprint 3.6) - agent handoff is mandatory:** real Luis problem (uses Codex/Gemini/Claude and runs out of tokens mid-task -> context loss). GS layer: vice **VC-140 "Continuity gap / orphan handoff"** -> `PREVENTED`, mech `check_handoff_freshness`. Cerberus layer: git **`commit-msg`** hook (agnostic - works with any `git commit`) that blocks if there are substantive changes without a fresh `HANDOFF.md` (fixed ESTADO/SIGUIENTE/VERIFICAR schema). Escape `[skip-handoff]`/`CERBERUS_SKIP_HANDOFF=1`. Canonical live `HANDOFF.md` artifact (history in HISTORIAL.md); template `HANDOFF.template.md`. Propagation: `install_hooks.sh/.ps1` now install `commit-msg` -> satellites inherit it. Gate: 6 tests in `tests/test_handoff_freshness.py` + end-to-end blocking/escape verification + compliance/ratchet 16/16.

---

## 🚀 ACTIVE CONTEXT
- **Status:** CoderCerberus V0.5 - operational. Internal audit completed 2026-06-05.
- **Goal:** Full GS → Cerberus → Test coverage for each VC/TV/TK PREVENTED/REMEDIATED.
- **Critical Risk:** State claims without VERIFIED/INFERRED/ASSUMED (PI-020).
- **Known debt:** SPEC.md references older-version docs/scripts - clean progressively with lint_protocol_docs.py.

---
**Coder Cerberus V0.5 — Inmunidad Total.**
