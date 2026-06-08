# TK-I: Memory Governance (TK-001..008)

**Source:** `deprecated/BIBLIOTECA_TOKENOMICS_CONTEXTO.md` (Category I)
**Status:** ACTIVE | **Entries:** 8 | **Date:** 2026-06-02
**Focus:** Checkpoint, persistence, context decay, epistemological segregation

---

## Critical Leaks

| Leak | Symptom | Root Cause | Fix |
|---|---|---|---|
| **TK-F01** | Reprocessing stable context | Reuse not modeled | Separate stable + volatile context |
| **TK-F02** | Primitive pruning | Full doc for small query | Extract relevant fragments only |
| **TK-F03** | Excess verbal output | No output budget | Restrict format + length |

---

## Catalog

| ID | Name | Symptom | Root Cause | Prevention |
|---|---|---|---|---|
| **TK-001** | Missing Checkpoint | New session restarts | Ephemeral state | Physical/logical summary before close |
| **TK-002** | Chat Memory as Authority | Thread switch loses state | No external persistence | State outside chat (SPEC.md, STATUS.md) |
| **TK-003** | Context Bleed | Project change contaminates context | Fuzzy task boundary | Checkpoint before switching objective |
| **TK-004** | Reexplained Setup | Every session rebuilds | Preconditions not external | Minimal startup checklist |
| **TK-005** | Handoff Prose-Heavy | Continuity needs full history | Non-normalized state | Atomic: objective + state + evidence + risk + action |
| **TK-006** | Manual History Merge | Resolving conflicts | Semantic state absent | Merge by decisions + invariants, not raw text |
| **TK-007** | Duplicate Authorit | Contradicting copies | No canonical core | Single source + archive copies |
| **TK-008** | Epistemological Segregation | Reprocessing stable specs | Invariants mixed with variables | Immutable Core + Transitional Buffer |

---

## Architecture

**Trinity of Memory:**
1. **AGENT.md** (Core, <150 lines) — Governance
2. **STATUS.md** (Delta, atomic structure) — Current state
3. **SPEC.md** (Reference) — Authority

**Principle:** Chat is ephemeral; truth is on disk.

---

## Related

- **TK-P02:** State external to chat
- **LEVEL_5/M1:** Diagnostics (memory architecture)
- **S2:** Brain-First (SPEC.md authority)

