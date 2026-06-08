# GS — Principles (Foundational Knowledge)

**Source:** `deprecated/docs_archive_legacy/N_MODULOS/` (integrated + recovered)
**Status:** ACTIVE | **Levels:** 5 | **Modules:** 17

---

## Five Levels of Governance

```
┌──────────────────────────────────────────────────────┐
│  PRINCIPLES — Foundational Knowledge                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  LEVEL_1: INTEGRITY          (4 modules)             │
│  ├─ M1: Core Principles (epistemology, rigor)        │
│  ├─ M2: Usability & Design                           │
│  ├─ M3: Angry Path (adversarial thinking)            │
│  └─ M4: Errors & Secrets (handling, no leaks)        │
│                                                      │
│  LEVEL_2: OPERATION          (5 modules)             │
│  ├─ M1: Fundamentals (startup, bootstrap)            │
│  ├─ M2: User & Scope (audience, boundaries)          │
│  ├─ M3: Flows & State (transitions, consistency)     │
│  ├─ M4: Orchestration & Tokenomics (gates, cost)     │
│  └─ M5: Audit & Git (traceability, version control) │
│                                                      │
│  LEVEL_3: VALIDATION         (Integrated)            │
│  └─ Regression, angry path, secrets, errors, status  │
│                                                      │
│  LEVEL_4: GUARDS             (3 modules)             │
│  ├─ M1: Prohibitions (hard stops, no-gos)            │
│  ├─ M2: Mandatory Operatives (must-dos)              │
│  └─ M3: Models & Risks (threat modeling)             │
│                                                      │
│  LEVEL_5: TOKEN SAVING       (3 modules)             │
│  ├─ M1: Diagnostics (visibility, metrics)            │
│  ├─ M2: Leaks & Solutions (waste patterns, fixes)    │
│  └─ M3: External Software (tool selection)           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Reading Order (Recommended)

### **Tier 1: Non-Negotiable (Start here)**

1. **LEVEL_1/M1_Principles** (30 min)
   - *Why:* Foundational epistemology; underpins everything
   - *Core:* Integrity, zero-warning, pessimism, continuous improvement

2. **LEVEL_4/M1_Prohibitions** (10 min)
   - *Why:* Hard stops; tells you what NOT to do
   - *Core:* What is forbidden; no workarounds

### **Tier 2: Operational (Then read)**

3. **LEVEL_2/M1_Fundamentals** (15 min)
   - *Why:* Startup ritual and bootstrap
   - *Core:* How to begin safely

4. **LEVEL_3_Validation** (20 min)
   - *Why:* Gate before closure; mandatory checks
   - *Core:* Regression, angry path, secrets, status

### **Tier 3: Context & Risk (Reference as needed)**

5. **LEVEL_2/M2_User_Scope** — Who are we building for?
6. **LEVEL_4/M3_Models_Risks** — Threat modeling and risk mitigation
7. **LEVEL_5** — Token optimization and tool selection

---

## Structure

| Level | Focus | Binding Authority | Enforcement |
|-------|-------|-------------------|-------------|
| **L1: Integrity** | Epistemological rigor, zero-warning tolerance, algorithmic pessimism | Non-negotiable | By Design + S1-S9 gates |
| **L2: Operation** | User scope, state flow, tokenomics, audit | Operational | By Workflow (4-phase machine) |
| **L3: Validation** | Gate criteria before closure | Verification | By Test + Audit suite |
| **L4: Guards** | Prohibitions, mandatory operatives, risk models | Enforcement | By Hook + Blocking gate |
| **L5: Token Saving** | Efficiency, cost optimization, visibility | Optimization | By Monitoring + Reporting |

---

## Correlation to Patterns

Each Principle maps to related Vices:

| Level | Maps To | Example |
|-------|---------|---------|
| **L1: Integrity** | VC-001..017 (Epistemology) | Assume failure until proven |
| **L2: Operation** | VC-018..046, VT-035..115 (Process, Flow) | Surgical editing, verification gates |
| **L3: Validation** | VT-001..022 (Oracles), VC-096 (Tests) | Tests as gate, not decoration |
| **L4: Guards** | VC-111..114, VT-105..107 (Governance) | Executable guards, not wishes |
| **L5: Token Saving** | TK-001..027 (Tokenomics) | Minimize waste; maximize signal |

See `Patterns/CORRELATION_MATRIX.md` for full mapping.

---

## File Structure

```
GS/Principles/
├── README.md               (this directory)
├── INDEX.md               (this file)
│
├── LEVEL_1_Integrity/
│   ├── INDEX.md           (Level 1 overview)
│   ├── M1_Principles.md   (Core: epistemology, rigor, pessimism)
│   ├── M2_Usability.md    (Design: simplicity, clarity)
│   ├── M3_Angry_Path.md   (Adversarial: 3 ways to break)
│   └── M4_Errors.md       (Error handling, secret management)
│
├── LEVEL_2_Operation/
│   ├── INDEX.md           (Level 2 overview)
│   ├── M1_Fundamentals.md (Startup: bootstrap, state init)
│   ├── M2_User_Scope.md   (Audience, boundaries, context)
│   ├── M3_Flows_State.md  (State transitions, consistency)
│   ├── M4_Tokenomics.md   (Gates, cost visibility, budgets)
│   └── M5_Audit_Git.md    (Traceability, version control)
│
├── LEVEL_3_Validation/
│   └── Validation.md      (Regression, angry path, secrets, status)
│
├── LEVEL_4_Guards/
│   ├── INDEX.md           (Level 4 overview)
│   ├── M1_Prohibitions.md (Hard stops, no-gos)
│   ├── M2_Mandatory.md    (Must-dos, requirements)
│   └── M3_Risk_Models.md  (Threat modeling)
│
└── LEVEL_5_TokenSaving/
    ├── INDEX.md           (Level 5 overview)
    ├── M1_Diagnostics.md  (Visibility, metrics)
    ├── M2_Leaks.md        (Waste patterns, fixes)
    └── M3_Tools.md        (External software selection)
```

---

## Integration with GS/Patterns

**Principle ← → Vice relationship:**

- Violations of Principles manifest as Vices
- Vices reveal principle weaknesses
- Guards (L4) prevent vices

Example: If VC-001 (incompetence assumed) is observed → LEVEL_1/M1 violated → strengthen peer review.

See `GS/Patterns/CORRELATION_MATRIX.md` for exhaustive mapping.

---

## Sourcing & Maintenance

**Golden Rules:**

1. **Principles are immutable** unless consensus (very rare)
   - Never soften a prohibition
   - Never weaken integrity rule
   - Only clarify or extend

2. **Derived from reality**
   - Each principle came from observed failures (vices)
   - Backed by evidence from projects

3. **Agent-Agnostic & Project-Agnostic**
   - No Claude-specific guidance (use Binding)
   - No project names (use project docs)

4. **Actionable**
   - Every principle maps to a guard, test, or hook
   - Not aspirational; not recommendations

---

## Do NOT Include

- Agent-specific guidance (Claude, Gemini, ChatGPT) → Use Binding
- Project-specific details → Use project documentation
- Tool recommendations (Pytest, Deptry, etc.) → Use project_insights
- Temporary workarounds → Use HISTORIAL.md

**Principles are eternal truths. Tools and projects are ephemeral.**

---

## Legacy

Original documents (deprecated/docs_archive_legacy/N_MODULOS/):
- All 17 modules integrated here
- Kept in deprecated/ as read-only archive
- See `deprecated/DECOMMISSIONED.txt` for audit trail

---

## How to Use

1. **As a Gate:** Before each phase, verify compliance with relevant level
2. **As a Troubleshoot:** When something fails, check which principle is violated
3. **As a Design:** When building new system, consult L1-L4 sequentially
4. **As a Reference:** When ambiguous, principles break ties

---

## Next: Understand Vices

After understanding Principles, read `GS/Patterns/` to see how violations manifest.

Together, Principles + Patterns form the **complete governance system**.
