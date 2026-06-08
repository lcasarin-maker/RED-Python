# TK-III: Output Compression & Observability (TK-020..042)

**Source:** `deprecated/BIBLIOTECA_TOKENOMICS_CONTEXTO.md` (Category III-IV)
**Status:** ACTIVE | **Entries:** 23 | **Date:** 2026-06-02
**Focus:** Output verbosity, prefill structures, diagnostic compression, FinOps

---

## Catalog: Output Control (TK-020..027)

| ID | Name | Symptom | Root Cause | Prevention |
|---|---|---|---|---|
| **TK-020** | Unrestricted Output | Long responses by default | Unbounded space | Define budget + format |
| **TK-021** | Format Variation | Variable structure | Wide distribution | Predefine structure |
| **TK-022** | Redundant Few-Shot | Repetitive examples | Unnecessary duplication | Minimal, dense, diverse |
| **TK-023** | Raw Logs | Command output saturates | Operational noise | Compress/filter before delivery |
| **TK-024** | Dense Compression | Loses decisions | Summary without invariants | Preserve critical facts |
| **TK-025** | Verbose Audit Reports | Findings lost in noise | Low signal density | Report findings + evidence + action |
| **TK-026** | Noisy Observability | Logs displace problem | Non-hierarchized signal | Causal summary + detail on demand |
| **TK-027** | Lexical Compression of Diagnostics | Verbose error traces lose context | Blind truncation | Controlled elisión (line limit + redundancy collapse + causal extraction) |

---

## Catalog: FinOps (TK-028..042)

| ID | Name | Prevention |
|---|---|---|
| **TK-028** | Context Caching | Mark reutilizable blocks, avoid reload |
| **TK-029** | Batch Processing | Group non-interactive work |
| **TK-030** | Capacity Matching | Choose minimum sufficient tier |
| **TK-031** | Context Compaction | Summarize + restart long sessions |
| **TK-032** | Cache Cliff | Manage TTL expiry + checkpoints |
| **TK-033** | Zero Headroom | Reserve safety margin |
| **TK-034** | Invisible Reversal Cost | Measure + register rollback |
| **TK-035** | Think vs Execute | Separate cognitive + action budgets |
| **TK-036** | Mode Blindness | Classify intent: think/execute/review |
| **TK-037** | Invisible Thresholds | Visible limits + automation |
| **TK-038** | Full State Reread | Index small state fields |
| **TK-039** | External Tools Unintegrated | Optimization must be in active path |
| **TK-040** | Unmeasured Savings | Before/after telemetry |
| **TK-041** | Invisible Quotas | Include limits, backoff, degradation |
| **TK-042** | Manifest Size Bloat | Trinity docstrings <150 lines (AGENT.md), compact (STATUS.md), curated (SPEC.md) |

---

## Principles (TK-P01..P11)

**Minimum sufficient context** → Include only decision-relevant info
**State external** → Persistent artifacts, not chat
**Phase separation** → Think/execute/review split
**Visible budget** → Know tokens remaining + risk
**Compress with invariants** → Summarize without losing decisions
**Measure first** → No savings without before/after
**Prune first** → Reduce noise before asking for inference

---

## Related

- **LEVEL_5/M2:** Leaks & Solutions
- **TK-P06..P11:** Positive principles
- **S18:** Token Optimization

