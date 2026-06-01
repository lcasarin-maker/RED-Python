# SOURCES OF TRUTH — Coder Cerberus V0.02
**REGLA #22 — Índice de Fuentes de Autoridad**

Este documento es el índice canónico de todos los conceptos del protocolo y sus archivos de autoridad.
Cada entrada especifica si el concepto es una SPEC (implementación técnica) o POLICY (mandato conductual).

---

## Índice de Fuentes

| Concepto | Archivo Autorizado | Tipo |
|----------|-------------------|------|
| Versión del protocolo | AGENT.md | SPEC |
| Mandatos Sistema S1-S9 | PROTOCOL_SYSTEM.md | SPEC |
| Mandatos Conducta B1-B11 | PROTOCOL_BEHAVIOR.md | POLICY |
| Memory Bank / Cerebro | SPEC.md | SPEC |
| Golden Standard split y canónico | Golden_Standard/golden_standard.yaml + Golden_Standard/golden_standard_*.yaml | SPEC |
| Loader de conocimiento y project insights | protocol_engine/knowledge_loader.py | SPEC |
| Ingestión canónica de aprendizajes satélite | protocol_engine/knowledge_loader.py | SPEC |
| Recomendaciones de project insights | protocol_engine/knowledge_loader.py | SPEC |
| Mapa funcional del proyecto | docs/MAPA_FUNCIONAL_CERBERUS.md | SPEC |
| Inventario tecnico generado | .protocol/codebase_map.json | SPEC |
| Handoff + Checksums | .agent_state.json | SPEC |
| Audit Trail sesiones | HISTORIAL.md | SPEC |
| Auditoría 12 dominios | scripts/run_security_audit_12d.py | SPEC |
| Pre-edit guard (PreToolUse) | scripts/pre_edit_guard.py | SPEC |
| Pre-commit gatekeeper | scripts/run_compliance_tests.py | SPEC |
| Sincronización protocolo | scripts/sync_binding.py | SPEC |
| Control Plane CLI | scripts/protocol_cli.py | SPEC |
| Token tracker / cost metering | scripts/track_tokens.py | SPEC |
| Validación chunks | scripts/validate_chunking.py | SPEC |
| Proof empírica | scripts/check_empirical_proof.py | SPEC |
| Higiene encoding | scripts/audit_hygiene.py | SPEC |
| Permisos agentes | scripts/audit_permissions.py | SPEC |
| Budget de tokens | TOKEN_BUDGET.md | POLICY |
| Distribución global segura | scripts/global_sync_safe.py | SPEC |
| Extracción contexto | scripts/smart_context_extractor.py | SPEC |
| Compresión historial | scripts/compress_historial.py | SPEC |
| Caché reglas | scripts/cache_protocol_rules.py | SPEC |
| Export retrospectiva | scripts/export_retrospective.py | SPEC |
| Trigger compresión | scripts/trigger_context_compression.py | SPEC |
| Optimizador tokens | scripts/token_optimizer.py | SPEC |
| Orquestador pre-COMPACT | scripts/compact_automation_helper.py | SPEC |
| Scheduler mantenimiento | scripts/automation_scheduler.py | SPEC |
| Utilidades core | scripts/core_utils.py | SPEC |

## Nota de mantenimiento

- `docs/MAPA_FUNCIONAL_CERBERUS.md` es la vista humana del sistema.
- `Golden_Standard/golden_standard.yaml` es el manifest de conocimiento agnóstico cargado por `cerberus.get_golden_standard()`, y los catálogos físicos viven en `Golden_Standard/golden_standard_*.yaml`.
- `docs/DEBT_LEDGER.md` es el inventario canónico de deuda del workspace; todo backlog, drift histórico y deuda externa debe rastrearse ahí antes de abrir trabajo nuevo.
- `protocol_engine.get_project_insights()` expone los patrones de referencia de proyectos externos como conocimiento agnóstico reutilizable.
- `protocol_engine.get_project_insight_recommendations()` convierte esos patrones en recomendaciones por dominio.
- `scripts/track_tokens.py` analiza `transcript.jsonl` y expone `/cost` vía `scripts/protocol_cli.py`.
- `.protocol/codebase_map.json` es la vista generada automaticamente para inventario tecnico.
- Cuando cambien scripts, documentos de autoridad o proyectos satelite, actualiza ambos si el mapa funcional queda desfasado.

---

## Referencias REGLAS #0–22

- **REGLA #0** — Constitución base del protocolo → AGENT.md
- **REGLA #1** — Rigor 6D (S1) → PROTOCOL_SYSTEM.md
- **REGLA #2** — Brain-First (S2) → PROTOCOL_SYSTEM.md
- **REGLA #3** — Bio-Containment (S3) → PROTOCOL_SYSTEM.md
- **REGLA #4** — Modularidad (S4) → PROTOCOL_SYSTEM.md
- **REGLA #5** — Anti-Slop (S5) → PROTOCOL_SYSTEM.md
- **REGLA #6** — Large File Safety (S6) → PROTOCOL_SYSTEM.md
- **REGLA #7** — Anti-Shell (S7) → PROTOCOL_SYSTEM.md
- **REGLA #8** — Debt Tax (S8) → PROTOCOL_SYSTEM.md
- **REGLA #9** — Logging Mandatorio (S9) → PROTOCOL_SYSTEM.md
- **REGLA #10** — Doctrina Fallo (B1) → PROTOCOL_BEHAVIOR.md
- **REGLA #11** — Amnesia Obligatoria (B2) → PROTOCOL_BEHAVIOR.md
- **REGLA #12** — Angry Path (B3) → PROTOCOL_BEHAVIOR.md
- **REGLA #13** — Anti-Triunfalismo (B7) → PROTOCOL_BEHAVIOR.md
- **REGLA #14** — Anti-Deriva (B8) → PROTOCOL_BEHAVIOR.md
- **REGLA #15** — Root Cause (B9) → PROTOCOL_BEHAVIOR.md
- **REGLA #16** — Checkpointing (B10) → PROTOCOL_BEHAVIOR.md
- **REGLA #17** — Validación Deps (B11) → PROTOCOL_BEHAVIOR.md
- **REGLA #18** — Token Optimization (S18) → PROTOCOL_SYSTEM.md
- **REGLA #19** — Paridad Versión (S17) → PROTOCOL_SYSTEM.md
- **REGLA #20** — Chaos Monkey → scripts/verify_chaos_robustness.py
- **REGLA #21** — Post-Session Retrospective → HISTORIAL.md
- **REGLA #22** — Sources of Truth Index → SOURCES_OF_TRUTH.md

---

## SPEC vs POLICY

**GOVERNANCE MODEL — Coder Cerberus V0.02**

| Tipo | Definición | Autoridad | Ejemplos |
|------|-----------|-----------|---------|
| **SPEC** | Implementación técnica obligatoria — código, schemas, scripts | PROTOCOL_SYSTEM.md | run_security_audit_12d.py, core_utils.py, sync_binding.py |
| **POLICY** | Mandato conductual — reglas de razonamiento y comportamiento | PROTOCOL_BEHAVIOR.md | B1 Doctrina Fallo, B3 Angry Path, B7 Anti-Triunfalismo |

### SPEC

Implementación técnica obligatoria. Cualquier cambio requiere actualización de `scripts/` + test adversarial + `run_security_audit_12d.py` PASS.

### POLICY

Mandato conductual. Cualquier cambio requiere revisión humana en PROTOCOL_BEHAVIOR.md + entrada en HISTORIAL.md.

### Reglas de Governance

1. **SPEC** — Actualización de `scripts/` + test adversarial + `run_security_audit_12d.py` PASS.
2. **POLICY** — Revisión humana en PROTOCOL_BEHAVIOR.md + entrada en HISTORIAL.md.
3. **Conflictos** — SPEC prevalece sobre POLICY en decisiones técnicas; POLICY prevalece en conducta del agente.
4. **Versión** — Ambos tipos se versionan via `.agent_state.json` y propagados por `sync_binding.py`.

---

*Generado por: Coder Cerberus V0.02 | Última actualización: 2026-05-26*
- `docs/SPRINT_10_REPOS_EXTERNOS_Y_VIGILANCIA.md` — Matriz canónica del sprint 10 con decisiones INTEGRAR/COMPLEMENTAR/DESCARTAR/BACKLOG y lección de vigilancia en vivo.
