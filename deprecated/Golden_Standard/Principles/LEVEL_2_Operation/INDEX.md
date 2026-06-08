# LEVEL 2: OPERATION — Workflow & State Management

**Source:** `deprecated/N_MODULOS/N2_M*.md` (recovered)
**Authority:** Binding | **Binding Rule:** B10 (Checkpointing)

---

## Five Modules

| Module | Content | Critical? | Maps To Vice |
|--------|---------|-----------|--------------|
| **M1: Fundamentals** | Startup ritual, bootstrap, state initialization | ✅ YES | VC-089..106 |
| **M2: User & Scope** | Audience definition, boundaries, context | ✅ YES | VC-025, VC-067 |
| **M3: Flows & State** | State transitions, consistency, synchronization | ✅ YES | VC-047..062 |
| **M4: Orchestration & Tokenomics** | Gates, cost visibility, budgets | ✅ YES | TK-001..008 |
| **M5: Audit & Git** | Traceability, version control, checkpoints | ✅ YES | VC-054, VC-057 |

---

## Startup Ritual (M1)

Every session MUST:
1. `git status` — verify branch and cleanliness
2. Read AGENT.md (lines 1-46, 2 min)
3. Read SPEC.md (lines 1-50, 3 min)
4. Load canonical state from HISTORIAL.md
5. Proceed only if zero conflicts

---

## State Management (M3)

### Mutable vs. Immutable
- **Immutable (Core):** Principles, contracts, IDs
- **Mutable (Session):** Variables, context, flow state

Keep them separate. Version immutable. Checkpoint mutable before change.

### Synchronization
Before modifying state:
1. Verify current filesystem matches memory
2. Load latest from canonical source
3. Calculate delta
4. Apply change atomically
5. Persist immediately

---

## Gates & Visibility (M4)

Every phase gate requires:
- **Input criteria** (what must exist before entry)
- **Output criteria** (what must exist to exit)
- **Cost visibility** (token budget visible)
- **Evidence** (logs, tests, checkpoints)

No gate is optional. No exceptions.

---

## Reading Path

1. **M1_Fundamentals.md** — Startup (mandatory first step)
2. **M3_Flows_State.md** — State transitions
3. **M4_Tokenomics.md** — Gates and budgets
4. **M5_Audit_Git.md** — Traceability
5. **M2_User_Scope.md** — Context and boundaries

---

## Enforcement

**Binding Authority:** B10 (Checkpointing), S2 (Brain-First)

- B10: PLAN.md with numbered steps BEFORE code
- S2: Update SPEC.md before code

---

## Related Vices

- **VC-027** (Plan not externalized) — Write physical plan
- **VC-048** (Memory monolithic) — Separate core from volatile
- **VC-057** (Version parity broken) — Single version source
- **TK-002** (Chat as source) — Maintain external ledger

See `GS/Patterns/` for details.
