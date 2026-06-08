# GS — Patterns (Anti-patterns & Vices)

**Scope:** Detected failure modes, coding vices, testing anti-patterns, tokenomics waste. Agent-agnostic, project-agnostic.

---

## Three Catalogs (Unified System)

```
┌─────────────────────────────────────────────────────┐
│  PATTERNS — Anti-Pattern Catalog                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Coding_Vices/     Testing_Vices/    Tokenomics/   │
│  ├─ INDEX.md       ├─ INDEX.md       ├─ INDEX.md   │
│  ├─ I_*            ├─ I_*            ├─ Critical_  │
│  ├─ II_*           ├─ II_*           ├─ I_Memory   │
│  ├─ III_*          ├─ III_*          ├─ II_Ingest │
│  ├─ ...            └─ ...            └─ III_Outpt │
│  └─ APPENDICES.md                                  │
│     (4-phase machine, operator profile, escalation)│
│                                                     │
│  Cross-links: ← VC ↔ VT ↔ TK →                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## At a Glance

| Catalog | Entries | Focus | Authority |
|---------|---------|-------|-----------|
| **Coding Vices (VC)** | 123 | Code generation, state, architecture | How agents fail in implementation |
| **Testing Vices (VT)** | 115 | Test oracles, simulation, coverage | Why oracles deceive |
| **Tokenomics (TK)** | 27 | Memory, context, output bloat | Cost optimization and signal/noise |

**Total:** ~265 distinct anti-patterns, fully cross-linked.

---

## Reading Order (First Time)

1. **[TK] Critical Leaks** (`Tokenomics/Critical_Leaks.md`)
   - *Why:* Highest-impact waste; teaches attention triage
   - *Time:* 5 min

2. **[VC] I: Epistemology** (`Coding_Vices/I_Epistemology.md`)
   - *Why:* Root causes; foundational errors
   - *Time:* 10 min

3. **[VT] I: Logic & Oracles** (`Testing_Vices/I_Logic_Oracles.md`)
   - *Why:* How to detect failures; empiricism
   - *Time:* 10 min

4. **[VC] II & III: Process & State** (browse)
   - *Why:* Operational failures and drift patterns
   - *Time:* Skim as needed

5. **[Appendices]** (`Coding_Vices/APPENDICES.md`)
   - *Why:* 4-phase state machine and escalation matrix
   - *Time:* 15 min (reference)

---

## Usage by Role

### **For AI Agents:**
Use to **detect, diagnose, prevent**.

1. **Detect**: Find symptom in VC/VT/TK
2. **Diagnose**: Read root cause
3. **Prevent**: Apply principle or guard

Example: Agent generates hardcoded function → matches VT-001 → understand tautology → apply test-first.

### **For Humans (Operators):**
Use to **govern, audit, escalate**.

1. **Audit**: Check if anti-patterns are present in system
2. **Escalate**: Route issues using Appendix C matrix
3. **Govern**: Enforce principle-based guards (tests, hooks)

---

## Sourcing & Maintenance

**Golden Rules:**

1. **No Simulation**
   - No stubs, mocks, placeholders masking problems
   - No "approved" without evidence
   - No xfail, skip, or tolerant warnings as green

2. **Falsifiable**
   - Each pattern must be detectable (test/hook possible)
   - Each principle must be actionable

3. **Agent-Agnostic**
   - No ChatGPT, Claude, Gemini specific guidance (use Binding for that)
   - Principle works for any LLM, tool, or agent

4. **Project-Agnostic**
   - No project names, dates, team assignments
   - No "Quenza specific" or "Sprint 5" details
   - Patterns are universal

---

## Cross-Links (Integration Map)

**Simulation Theater** — How real failures hide behind fake success:
- VC-118, 119, 121 (Zombie Compat, Lock Panic, AI Slop)
- VT-023, 033 (Mock Complacency, Wrapper Remediation)
- **Principle**: Never hide faults behind adapters; fix root causes

**False Oracles** — Why validation breaks with hidden assumptions:
- VC-015, 037 (Agent as Engineer, Blind Regeneration)
- VT-004, 014, 083 (Copy Expected, Circular Test, Approval Hardcoded)
- **Principle**: Oracles must be independent; separate test from implementation

**Context Bloat** — State explosion and forgotten requirements:
- VC-048, 052 (Monolithic Memory, Context Rot)
- TK-002, 004, 008 (Chat as Source, Setup Reexplained, Epistemological Segregation)
- **Principle**: Separate stable core from transient buffer; checkpoint before continuation

**Observability Failure** — Why logs deceive:
- VC-085, 102 (Ornamental Logging, Poor Debug)
- VT-074 (Observability Not Tested)
- TK-026 (Noisy Observability)
- **Principle**: Logs must be causal and actionable; compress noise before delivery

---

## Deduplication Log

See `DEDUP_LOG.yaml` for:
- Which concepts consolidate under one authority
- Why duplicates across catalogs were merged
- Cross-link mapping

**Summary:**
- One authority per concept (avoids drift)
- Cross-links instead of copies (single source of truth)
- 265 entries reduced to ~240 unique patterns (25 merged)

---

## Integration with Principles

Each principle in `GS/Principles/` maps to vices:

| Principle | Maps To | Example |
|-----------|---------|---------|
| L1: PESIMISMO (Pessimistic Realism) | VC-001..010 | Assume failure until proven |
| L2: OBSERVABILIDAD (Real-Time Signal) | VC-085, VT-074, TK-026 | Logs must be causal |
| L3: VALIDACION (Empirical Proof) | VT-001..022, VC-096 | Tests as gate, not decoration |
| L4: GUARDIAS (Enforcement) | VC-111..114, VT-105..107 | Guards must be executable |
| L5: AHORRO (Cost & Efficiency) | TK-001..027 | Minimize waste; maximize signal |

---

## File Structure

```
GS/Patterns/
├── README.md                    (this file)
├── DEDUP_LOG.yaml              (consolidation audit)
├── Coding_Vices/
│   ├── INDEX.md
│   ├── I_Epistemology.md        (VC-001..017)
│   ├── II_Process_Scope.md      (VC-018..046)
│   ├── III_State_Concurrency.md (VC-047..062)
│   ├── IV_Architecture.md       (VC-063..088)
│   ├── V_Environment.md         (VC-089..110)
│   ├── VI_Governance.md         (VC-111..114)
│   ├── VII_Security.md          (VC-115..117)
│   ├── VIII_Replacement.md      (VC-118..123)
│   └── APPENDICES.md            (4-phase, operator, escalation)
├── Testing_Vices/
│   ├── INDEX.md
│   ├── I_Logic_Oracles.md       (VT-001..022)
│   ├── II_Simulation.md         (VT-023..034)
│   └── III_Flow_Discovery.md    (VT-035..115)
└── Tokenomics/
    ├── INDEX.md
    ├── Critical_Leaks.md         (TK-F01..F03)
    ├── I_Memory.md              (TK-001..008)
    ├── II_Ingestion.md          (TK-009..019)
    └── III_Output.md            (TK-020..027)
```

---

## Do NOT Include in Patterns

- Tool recommendations (Deptry, Trivy, Pytest) → Use `project_insights/`
- Project-specific fixes ("for Quenza") → Use Binding or project docs
- Agent-specific guidance ("Claude Code should") → Use Binding
- Temporary workarounds → Use project HISTORIAL.md
- Team assignments or sprint metadata → Use project artifacts

**Patterns are eternal. Tools and projects are ephemeral.**

---

## Sourcing & Decommission

Original documents (deprecated/):
- `BIBLIOTECA_VICIOS_VIBE_CODING.md` → Coding_Vices/ (integrated)
- `BIBLIOTECA_VICIOS_TESTING_EVALUACION.md` → Testing_Vices/ (integrated)
- `BIBLIOTECA_TOKENOMICS_CONTEXTO.md` → Tokenomics/ (integrated)

**Deprecated is now READ-ONLY archive.** All updates go through GS/Patterns.

See `deprecated/DECOMMISSIONED.txt` for audit trail.
