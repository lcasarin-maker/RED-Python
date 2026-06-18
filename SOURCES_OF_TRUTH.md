# SOURCES OF TRUTH - Coder Cerberus V0.02
**RULE #22 - Authority Source Index**

This document is the canonical index of all protocol concepts and their authority files.
Each entry states whether the concept is a SPEC (technical implementation) or POLICY (behavioral mandate).

---

## Sources Index

| Concept | Authorized File | Type |
|----------|-----------------|------|
| Protocol version | AGENT.md | SPEC |
| System mandates S1-S9 | PROTOCOL_SYSTEM.md | SPEC |
| Behavior mandates B1-B11 | PROTOCOL_BEHAVIOR.md | POLICY |
| Memory bank / brain | SPEC.md | SPEC |
| Golden Standard split and canonical manifest | `D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml` + `golden_standard_*.yaml` | SPEC |
| GS -> Cerberus consumer contract normalization | `scripts/normalize_golden_audit_consumer_contract.py` | SPEC |
| Knowledge loader and project insights | `protocol_engine/knowledge_loader.py` | SPEC |
| Canonical satellite learning ingestion | `protocol_engine/knowledge_loader.py` | SPEC |
| Project insight recommendations | `protocol_engine/knowledge_loader.py` | SPEC |
| Functional project map | `docs/MAPA_FUNCIONAL_CERBERUS.md` | SPEC |
| Generated technical inventory | `.protocol/codebase_map.json` | SPEC |
| Handoff + checksums | `.agent_state.json` | SPEC |
| Session audit trail | `HISTORIAL.md` | SPEC |
| 12-domain audit | `scripts/run_security_audit_12d.py` | SPEC |
| Pre-edit guard (PreToolUse) | `scripts/pre_edit_guard.py` | SPEC |
| Pre-commit gatekeeper | `scripts/run_compliance_tests.py` | SPEC |
| Protocol synchronization | `scripts/sync_binding.py` | SPEC |
| Control plane CLI | `scripts/protocol_cli.py` | SPEC |
| Token tracker / cost metering | `scripts/track_tokens.py` | SPEC |
| Chunk validation | `scripts/validate_chunking.py` | SPEC |
| Empirical proof | `scripts/check_empirical_proof.py` | SPEC |
| Encoding hygiene | `scripts/audit_hygiene.py` | SPEC |
| Agent permissions | `scripts/audit_permissions.py` | SPEC |
| Token budget | `TOKEN_BUDGET.md` | POLICY |
| Safe global distribution | `scripts/global_sync_safe.py` | SPEC |
| Context extraction | `scripts/smart_context_extractor.py` | SPEC |
| History compression | `scripts/compress_historial.py` | SPEC |
| Rule cache | `scripts/cache_protocol_rules.py` | SPEC |
| Retrospective export | `scripts/export_retrospective.py` | SPEC |
| Compression trigger | `scripts/trigger_context_compression.py` | SPEC |
| Token optimizer | `scripts/token_optimizer.py` | SPEC |
| Pre-COMPACT orchestrator | `scripts/compact_automation_helper.py` | SPEC |
| Maintenance scheduler | `scripts/automation_scheduler.py` | SPEC |
| Core utilities | `scripts/core_utils.py` | SPEC |

## Maintenance Notes

- `docs/MAPA_FUNCIONAL_CERBERUS.md` is the human-facing view of the system.
- `D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml` is the agnostic knowledge manifest loaded by `cerberus.get_golden_standard()`, and the physical catalogs live in `VibeCoding_GoldenStandard\golden_standard_*.yaml`. The local `Golden_Standard/` directory was removed. GS is a separate repo.
- `scripts/normalize_golden_audit_consumer_contract.py` must run after resynchronizing `.protocol/metadata/golden_standard_audit.json` from GS to remove circular mechanisms and keep `DOC_ONLY` honest with downstream verification.
- `docs/DEBT_LEDGER.md` is the canonical workspace debt inventory; all backlog, historical drift, and external debt must be tracked there before new work starts.
- `protocol_engine.get_project_insights()` exposes reference patterns from external projects as reusable agnostic knowledge.
- `protocol_engine.get_project_insight_recommendations()` converts those patterns into per-domain recommendations.
- `scripts/track_tokens.py` analyzes `transcript.jsonl` and exposes `/cost` through `scripts/protocol_cli.py`.
- `.protocol/codebase_map.json` is the generated technical inventory view.
- When scripts, authority docs, or satellite projects change, update both if the functional map drifts.

---

## Rules #0-22

- **RULE #0** - Base protocol constitution -> AGENT.md
- **RULE #1** - 6D rigor (S1) -> PROTOCOL_SYSTEM.md
- **RULE #2** - Brain-First (S2) -> PROTOCOL_SYSTEM.md
- **RULE #3** - Bio-Containment (S3) -> PROTOCOL_SYSTEM.md
- **RULE #4** - Modularity (S4) -> PROTOCOL_SYSTEM.md
- **RULE #5** - Anti-Slop (S5) -> PROTOCOL_SYSTEM.md
- **RULE #6** - Large File Safety (S6) -> PROTOCOL_SYSTEM.md
- **RULE #7** - Anti-Shell (S7) -> PROTOCOL_SYSTEM.md
- **RULE #8** - Debt Tax (S8) -> PROTOCOL_SYSTEM.md
- **RULE #9** - Mandatory Logging (S9) -> PROTOCOL_SYSTEM.md
- **RULE #10** - Failure doctrine (B1) -> PROTOCOL_BEHAVIOR.md
- **RULE #11** - Mandatory amnesia (B2) -> PROTOCOL_BEHAVIOR.md
- **RULE #12** - Angry Path (B3) -> PROTOCOL_BEHAVIOR.md
- **RULE #13** - Anti-triumphalism (B7) -> PROTOCOL_BEHAVIOR.md
- **RULE #14** - Anti-drift (B8) -> PROTOCOL_BEHAVIOR.md
- **RULE #15** - Root Cause (B9) -> PROTOCOL_BEHAVIOR.md
- **RULE #16** - Checkpointing (B10) -> PROTOCOL_BEHAVIOR.md
- **RULE #17** - Dependency validation (B11) -> PROTOCOL_BEHAVIOR.md
- **RULE #18** - Token Optimization (S18) -> PROTOCOL_SYSTEM.md
- **RULE #19** - Version parity (S17) -> PROTOCOL_SYSTEM.md
- **RULE #20** - Chaos Monkey -> `scripts/verify_chaos_robustness.py`
- **RULE #21** - Post-session retrospective -> `HISTORIAL.md`
- **RULE #22** - Sources of Truth index -> `SOURCES_OF_TRUTH.md`

---

## SPEC vs POLICY

**GOVERNANCE MODEL - Coder Cerberus V0.02**

| Type | Definition | Authority | Examples |
|------|-----------|-----------|---------|
| **SPEC** | Mandatory technical implementation - code, schemas, scripts | PROTOCOL_SYSTEM.md | run_security_audit_12d.py, core_utils.py, sync_binding.py |
| **POLICY** | Behavioral mandate - reasoning and conduct rules | PROTOCOL_BEHAVIOR.md | B1 Failure doctrine, B3 Angry Path, B7 Anti-triumphalism |

### SPEC

Mandatory technical implementation. Any change requires a `scripts/` update + adversarial test + `run_security_audit_12d.py` PASS.

### POLICY

Behavioral mandate. Any change requires human review in `PROTOCOL_BEHAVIOR.md` + an entry in `HISTORIAL.md`.

### Governance rules

1. **SPEC** - Update `scripts/` + adversarial test + `run_security_audit_12d.py` PASS.
2. **POLICY** - Human review in `PROTOCOL_BEHAVIOR.md` + entry in `HISTORIAL.md`.
3. **Conflicts** - SPEC wins over POLICY for technical decisions; POLICY wins for agent behavior.
4. **Versioning** - Both types are versioned through `.agent_state.json` and propagated by `sync_binding.py`.

---

*Generated by: Coder Cerberus V0.02 | Last updated: 2026-05-26*
- `docs/sprint3_4_triage_giants.md` - Active triage of external sprints (live reference).
