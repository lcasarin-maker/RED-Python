# TK-II: Input Ingestion & Pruning (TK-009..019)

**Source:** `deprecated/BIBLIOTECA_TOKENOMICS_CONTEXTO.md` (Category II)
**Status:** ACTIVE | **Entries:** 11 | **Date:** 2026-06-02
**Focus:** Semantic pruning, chunk recovery, exploration tax, intake optimization

---

## Catalog

| ID | Name | Symptom | Root Cause | Prevention |
|---|---|---|---|---|
| **TK-009** | Semantic Pruning | Whole files saturate | Document-level retrieval | Extract relevant sections |
| **TK-010** | Contextual Recovery | Chunks lose meaning | Orphaned fragments | Enrich with parent context |
| **TK-011** | Structured Delimiters | Instructions mix | Ambiguous boundaries | Separate role/context/task/output |
| **TK-012** | Exploration Tax | Tokens spent before acting | Blind exploration | Use indices, maps, directed reads |
| **TK-013** | Inflated Tool Schemas | Unused tools consume space | Anticipatory load | Defer tool loading |
| **TK-014** | Read Complete by Default | Large files sent whole | Low granularity | Read by ranges, skeleton, index |
| **TK-015** | Whole File for Point Doubt | Irrelevant info processed | Unlocalized query | Ask for specific section |
| **TK-016** | Giant Multi-Objective Prompt | Model divides attention | Overloaded objective | One concrete task per cycle |
| **TK-017** | Policies Narrated | Long policies repeated | Unstructured authorization | Represent as consultable matrix |
| **TK-018** | Backlog Mixed with Goal | Side ideas occupy window | Unprioritized laterals | Send to external queue |
| **TK-019** | Hierarchical Dependency Skeleton | Blind directory exploration | Low granularity mapping | Use semantic indices + skeletons |

---

## Prevention Strategies

1. **Read Directed** — Sections, not whole files
2. **Chunk with Context** — Fragments don't orphan
3. **Separate Concerns** — Role, context, task, output
4. **Index-Driven** — Maps before exploration
5. **Skeleton First** — Structure before detail
6. **Defer Loading** — Tools only when needed

---

## Related

- **TK-P01:** Minimal sufficient context
- **TK-P07:** Prune before reasoning
- **LEVEL_5/M2:** Leaks (fuga detection)

