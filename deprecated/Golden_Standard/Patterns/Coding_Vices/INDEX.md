# Coding Vices (VC) — Complete Catalog

**Source:** `deprecated/BIBLIOTECA_VICIOS_VIBE_CODING.md` (integrated + deduplicated)
**Status:** ACTIVE | **Total:** 123 entries | **Categories:** 8

---

## Structure

Each category is a separate markdown file for readability.

| Category | Range | Count | Focus | File |
|----------|-------|-------|-------|------|
| **I: Epistemology & Behavior** | VC-001..017 | 17 | Foundational errors (incompetence, optimism, proof) | `I_Epistemology.md` |
| **II: Process & Scope** | VC-018..046 | 29 | Execution failures (blind fixes, premature closure, ambiguity) | `II_Process_Scope.md` |
| **III: State & Concurrency** | VC-047..062 | 16 | State entropy (drift, merge, deadlock) | `III_State_Concurrency.md` |
| **IV: Architecture & Interface** | VC-063..088 | 26 | Design fragility (docs, coupling, testing, config) | `IV_Architecture.md` |
| **V: Environment Degradation** | VC-089..110 | 22 | Preconditions (discovery, audit, security, infrastructure) | `V_Environment.md` |
| **VI: Exclusions & Nomenclature** | VC-111..114 | 4 | Governance (whitelists, propagation, naming, remediation) | `VI_Governance.md` |
| **VII: Supply Chain & Atomicity** | VC-115..117 | 3 | Security & integrity (eval, deps, state persistence) | `VII_Security.md` |
| **VIII: Zombie Compatibility** | VC-118..123 | 6 | Replacement anti-patterns (shims, lock-in, AI slop, staging) | `VIII_Replacement.md` |

---

## Cross-Domain Links

These VCs correlate to Testing Vices (VT) and Tokenomics (TK):

- **Simulation Theater** (VC-118, 119, 121) → See VT-023, VT-033 (Testing)
- **False Oracles** (VC-015, 037) → See VT-004, VT-014, VT-083 (Testing)
- **Context Bloat** (VC-048, 052) → See TK-002, TK-004, TK-008 (Tokenomics)
- **Observability** (VC-085, 102) → See VT-074, TK-026 (Testing + Tokenomics)
- **State Drift** (VC-057, 062) → See TK-008 (Tokenomics)

---

## Reading Path

**Foundational (First):**
1. `I_Epistemology.md` — Why agents fail before execution

**Operational (Second):**
2. `II_Process_Scope.md` — How execution goes wrong
3. `III_State_Concurrency.md` — Why state becomes toxic

**Defensive (Third):**
4. `IV_Architecture.md` — Designing against fragility
5. `V_Environment.md` — Validating preconditions

**Meta (Last):**
6. `VI_Governance.md` — Governing exclusions and naming
7. `VII_Security.md` — Supply chain and atomicity
8. `VIII_Replacement.md` — Zombie compatibility patterns

---

## Format

Each VC entry follows:

```
| VC-NNN | Name | Symptom | Root Cause | Principle |
```

**Legend:**
- **Symptom**: Observable failure mode
- **Root Cause**: Why it happens (theoretical)
- **Principle**: Agent-agnostic prevention rule

---

## Deduplication Notes

See `DEDUP_LOG.yaml` for consolidation decisions.

- VC-118 (Zombie Compat) is authoritative; VT entries cross-link
- VC-085 (Observability) is authoritative; VT-074, TK-026 cross-link
- VC-048 (Memory) crosses to TK-008; TK is authoritative for context governance

---

## Appendices (from Original)

See `APPENDICES.md` for:
- A: Operator Profile & Semantic Translation
- B: 4-Phase Temporal State Machine
- C: Escalation & Interruption Matrix
