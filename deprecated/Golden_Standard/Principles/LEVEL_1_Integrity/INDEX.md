# LEVEL 1: INTEGRITY — Non-Negotiable Rigor

**Source:** `deprecated/N_MODULOS/N1_M*.md` (recovered)
**Authority:** Binding | **Binding Rule:** S1-S9, S17

---

## Four Modules

| Module | Content | Critical? | Maps To Vice |
|--------|---------|-----------|--------------|
| **M1: Principles** | Core epistemology (integrity, zero-warning, pessimism, continuous improvement) | ✅ YES | VC-001..010 |
| **M2: Usability & Design** | Simplicity, clarity, topological minimalism | ✅ YES | VC-016, VC-089 |
| **M3: Angry Path** | Adversarial thinking (3 ways to break every design) | ✅ YES | VC-025, VC-026 |
| **M4: Errors & Secrets** | Error handling (4 elements), credential management | ✅ YES | VC-108, VC-093 |

---

## Core Principles (M1)

### INTEGRIDAD TOTAL
The priority is Mathematical, Logical, and Architectural Integrity. Code is not "good" unless it is verifiable.

### ZERO-WARNING TOLERANCE
Every warning is a potential error. Agent MUST apply corrective actions immediately.

### PESSIMISTIC REALISM (PESIMISMO ALGORÍTMICO)
All code or state is considered `BROKEN_UNTIL_PROVEN_STABLE`:

1. **Mute Evidence**: Forbidden to declare "complete" or "successful" with adjectives (efficient, perfect). Only test output or logs are valid.
2. **Uncertainty List**: Agent MUST list which parts of code/rules HAVE NOT been mechanically verified THIS TURN.
3. **Memory Distrust**: Agent cannot trust what it "believes" it did in prior turns; must re-verify filesystem if uncertain.

### ORGANIC GRANULARITY (DICHOTOMY)
Functionality splits into:
- **Stable Core:** Assumptions, invariants, contracts (change rarely)
- **Volatile Buffer:** Variables, session state, flow context (change constantly)

Keep separation explicit. Never mix them.

### PERPETUAL CONTINUOUS IMPROVEMENT (REFORZADO)
The Protocol is a living organism that evolves from projects toward the core.

1. **Protocol Feedback Loop**: When an agent detects a deficiency or improvement in a project (e.g., shallow smoke test), MUST:
   - **Identify** the weakness
   - **Propagate** change to protocol core rules
   - **Notify** that improvement is now global

2. **Mandatory Rescue**: Before deprecating or deleting old instruction files, agent MUST audit 100% of content to extract valuable logic.

3. **Sync on Close**: Apply Rule #17 (mass_sync.py) to ensure change is visible in all nodes.

### TRUTH SOURCE
Executable code and tests are the only truth.

---

## Reading Path

1. **M1_Principles.md** (10 min) — Foundational epistemology
2. **M3_Angry_Path.md** (10 min) — How to think adversarially
3. **M2_Usability.md** (5 min) — Simplicity over cleverness
4. **M4_Errors.md** (5 min) — Error handling mandate

---

## Related Vices

If violated, expect these failure modes:

- **VC-001** (Incompetence Assumed) — Treat all output as hypothesis
- **VC-008** (Operational Optimism) — Assume failure until proven
- **VC-015** (Agent as Autonomous Engineer) — Human retains responsibility
- **VC-087** (Warning Normalized) — Zero warnings in health paths

See `GS/Patterns/Coding_Vices/I_Epistemology.md` for details.

---

## Enforcement

**Binding Authority:** S1 (Rigor 12D), S5 (Anti-Slop)

- S1: Run security_audit_12d.py before commit
- S5: Zero warnings; test failure = code failure; evidence-based verification

---

## Appendices

See `Patterns/Coding_Vices/APPENDICES.md` for:
- Operator Profile (business strategist perspective)
- 4-Phase Temporal State Machine
- Escalation & Interruption Matrix
