# Tokenomics Vices (TK) — Complete Catalog

**Source:** `deprecated/BIBLIOTECA_TOKENOMICS_CONTEXTO.md` (integrated + deduplicated)
**Status:** ACTIVE | **Total:** 27 entries | **Categories:** 3

---

## Structure (Normalized — Sequential TK-001..042)

| Category | Range | Count | Focus | File | Priority |
|----------|-------|-------|-------|------|----------|
| **Critical Foundation** | TK-001..003 | 3 | Reprocessing, coarse-grained retrieval, output inflation | `I_Memory.md` | ⭐⭐⭐ |
| **I: Memory Governance** | TK-004..011 | 8 | Checkpoint, persistence, context decay, segregation | `I_Memory.md` | ⭐⭐⭐ |
| **II: Input Ingestion & Poda** | TK-012..022 | 11 | Retrieval chunking, exploration tax, primitiva poda | `II_Ingestion.md` | ⭐⭐ |
| **III: Output Compression** | TK-023..030 | 8 | Verbosity, prefilling, observability noise, signal compression | `III_Output.md` | ⭐⭐ |
| **Reserved for Future** | TK-031..042 | 12 | (Open for new discoveries) | — | — |

---

## Cross-Domain Links

These TKs correlate to Coding Vices (VC) and Testing Vices (VT):

- **Context Bloat** (TK-002, 004, 008) → See VC-048, VC-052 (State Entropy)
- **Observability Noise** (TK-026) → See VC-085 (Logging), VT-074 (Test Observability)
- **Setup Reexplained** (TK-004) → See VC-106 (Setup Phantom)
- **Poda Primitiva** (TK-F02) → See TK-009 (Semantic poda)

---

## Critical Foundation Leaks (Read First)

Start with **TK-001, TK-002, TK-003**: These are the **highest-impact waste patterns** affecting all tokenomics decisions.

- **TK-001**: Reprocessing Tax (Repro Context repeated N times)
- **TK-002**: Coarse-Grained Retrieval (Poda Primitiva)
- **TK-003**: Output Inflation (Verbose Response Bloat)

---

## Reading Path

**Foundation (Essential) — TK-001..003:**
1. `I_Memory.md` (Section: Critical Foundation) — Reprocessing, poda, output bloat

**Operational:**
2. `I_Memory.md` (Section: Memory Governance) — Checkpoints and state persistence (prevents forgetting between sessions)
3. `II_Ingestion.md` — Input poda and retrieval efficiency (TK-012..022)
4. `III_Output.md` — Output compression and verbosity control (TK-023..030)

---

## Format

Each TK entry:

```
| TK-NNN | Leak / Vice | Symptom | Root Cause | Principle |
```

**Scope:** Token-waste patterns. Agent-agnostic, project-agnostic.

---

## Deduplication (Normalized)

See DEDUP_LOG.yaml:
- **TK-001** (Reprocessing Tax — formerly F01) is foundation authority
- **TK-004** (Memory Segregation — formerly TK-008) is authority for context memory organization
- **TK-005** (Chat as Source — formerly TK-002) connects to VC-048 (Monolithic Memory)
- **TK-027** (Observability Noise — formerly TK-026) connects to VC-085, VT-074

**Positive Principles Migration:**
- **TK-P01..P11** moved to Principles/LEVEL_5_TokenSaving/M3_Positive_Principles.md (NOT anti-patterns)

---

## Metadata

- **Total tokens in deprecated:** ~120-150 (variable by context)
- **Avg cost per waste pattern identified:** ~5-10 tokens saved per application
- **ROI:** Identifying ONE leak often saves 50+ tokens in session

---

## Integration Note

Tokenomics Vices are the **control layer** for Coding and Testing Vices execution:
- A VC-048 (context bloat) execution error costs tokens → TK-008 governs how to structure memory
- A VT-074 (observability failure) in logs → TK-026 governs log compression

All three catalogs form a **unified governance system**, not independent lists.
