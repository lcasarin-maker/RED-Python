# LEVEL 5: TOKEN SAVING — Efficiency & Visibility

**Source:** `deprecated/N_MODULOS/N5_M*.md` (recovered)
**Authority:** Operational | **Binding Rule:** S9 (Logging)

---

## Three Modules

| Module | Content | Critical? |
|--------|---------|-----------|
| **M1: Diagnostics** | Visibility, metrics, observability | ⭐ HIGH |
| **M2: Leaks & Solutions** | Waste patterns, cost optimization | ⭐ HIGH |
| **M3: External Software** | Tool selection, vendor assessment | ⭐ MEDIUM |

---

## Core Principle

**Tokens are the currency of thought.** Minimize waste. Maximize signal.

---

## Diagnostics (M1)

Every session must track:
- **Input tokens:** What context did I load? (bytes, lines, files)
- **Output tokens:** What did I generate? (response length, logs)
- **Reprocessing:** Did I load the same block twice? (waste)
- **Latency:** How long between request and response? (cost proxy)

**Visibility = Control.** If you cannot measure it, you cannot optimize it.

---

## Leaks & Solutions (M2)

Identify and fix:

| Leak | Pattern | Fix |
|------|---------|-----|
| **Repro Context** | Same block loaded N times | Separate stable core + volatile buffer |
| **Poda Primitiva** | Full files for one question | Extract sections, enrich with context |
| **Salida Verbosa** | Preambles, explanations, padding | Restrict format + length |
| **Exploration Tax** | Blind search before structure | Use indices, maps, skeleton reads |
| **Log Bloat** | Raw command output satures | Compress, filter before delivery |

---

## Tool Selection (M3)

Before adopting a tool:
1. **Cost:** Does it save tokens or burn them?
2. **Coupling:** Does it create dependencies?
3. **Falsifiability:** Can we measure its value?
4. **Alignment:** Does it fit protocol principles?

If you cannot answer all four, **do not adopt**.

---

## Integration with Other Levels

- **L1 (Integrity):** Observability must be honest, not ornamental
- **L2 (Operation):** Gates must show token budget and actual spend
- **L3 (Validation):** Tests must report memory and compute costs
- **L4 (Guards):** Prohibit unbounded operations (loops, recursion, buffering)

---

## Enforcement

**Binding Authority:** S9 (Logging), via monitors and observers

- S9: `logger.info(args, state)` in every new function
- Monitors track token usage per operation
- Gates block if budget exceeded

---

## Related Vices

- **TK-001..027** (Tokenomics vices) → All modules
- **VC-048** (Memory monolithic) → M2 (segregation)
- **VC-085** (Observability ornamental) → M1 (visibility)

See `GS/Patterns/Tokenomics/` for details.

---

## Reading

This is the **last level** to read. Read only after mastering L1-L4.

- If you optimize tokens first, you optimize the wrong thing
- If you have integrity and gates, tokens follow naturally
- L5 is polish, not foundation
