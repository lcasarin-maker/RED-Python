# Golden Standard — Pure Knowledge Repository

**Status:** ACTIVE v2.0 | **Scope:** Agent-agnostic, Project-agnostic | **Owner:** Cerberus Core

---

## Architecture

```
GS/ (Pure Knowledge)
├── Principles/        (Foundational ideas, levels 1-5)
├── Patterns/          (Anti-patterns, vices, failures)
├── Tokenomics/        (Cost models, efficiency rules)
└── INDEX.md           (this file)

project_insights/     (Transitional, Project-Specific)
├── raw/              (Raw learnings from projects)
├── analysis/         (Analysis: where does it belong?)
├── PI-promotion.yaml (Active transformations)
└── .archive/         (Historical/superseded)
```

---

## Principles (Purity Layer)

Source: Legacy `N_MODULOS/` structure, canonicalized for agent-agnostic consumption.

| Level | Focus | Binding |
|-------|-------|---------|
| **L1: Integrity** | Epistemology, rigor, pessimism | Non-negotiable |
| **L2: Operation** | Users, state, flows, tokenomics | Operational |
| **L3: Validation** | Verification strategies | Validation gate |
| **L4: Guards** | Prohibitions, requirements, risks | Enforcement |
| **L5: TokenSaving** | Efficiency, cost optimization | Optimization |

See `Principles/` for detailed modules.

---

## Patterns (Anti-Pattern Catalog)

**Status:** ✅ INTEGRATED & DEDUPLICATED | 265 entries across 3 catalogs

See `Patterns/README.md` for master index.

**Coding Vices (VC)** — 123 entries
- [INDEX](Patterns/Coding_Vices/INDEX.md) | Categories I-VIII
- Root causes: Epistemology, Process, State, Architecture, Environment, Governance, Security, Replacement

**Testing Vices (VT)** — 115 entries
- [INDEX](Patterns/Testing_Vices/INDEX.md) | Categories I-III
- Oracles, Simulation, Flow/Discovery evasion patterns

**Tokenomics (TK)** — 27 entries
- [INDEX](Patterns/Tokenomics/INDEX.md) | Critical Leaks + Memory + Ingestion + Output
- Context management, efficiency, signal/noise ratio

**Cross-links:** Integrated; see `Patterns/DEDUP_LOG.yaml` for consolidation audit.

**Legacy:** Deprecated MDs integrated (read-only archive at `deprecated/DECOMMISSIONED.txt`)

---

## Project Insights (Transitional, Ephemeral)

**NOT part of pure GS.** Separate folder for project-specific learnings.

Raw observations → Analysis → Promotion to GS (or Archive)

See `../project_insights/` for active transformations.

---

## Sourcing & Maintenance

1. **Principles** are immutable unless consensus (very rare)
2. **Patterns** grow from observed failures; each pattern must be:
   - **Falsifiable** (can detect via test/hook)
   - **Actionable** (clear prevention)
   - **Agnos** (no project/agent specifics)
3. **Project_Insights** feed new patterns into GS; non-promoted insights age to archive

See `project_insights/PI-promotion.yaml` for active work.

---

## Do NOT put in GS

- Project names, dates, team assignments
- Tool recommendations (Deptry, Trivy, etc.) — those are `project_insights`
- Temporary fixes or one-off workarounds
- Agent-specific guidance (use binding docs for that)

GS is the *why*, not the *how*.
