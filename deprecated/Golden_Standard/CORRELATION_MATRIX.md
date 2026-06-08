# Correlation Matrix — Principles ↔ Patterns (Vices)

**Purpose:** Show how violations of Principles manifest as Vices, and how Vices reveal principle weaknesses.

**Structure:** Each principle maps to related vices. Use this to:
- **Detect:** If you see a vice, what principle is violated?
- **Prevent:** If you want to enforce a principle, what vices guard against?
- **Audit:** Is the system healthy? Check principle compliance via vice absence.

---

## LEVEL 1: INTEGRITY ↔ Coding Vices (Epistemology)

| Principle | VC Family | Vices | Prevention |
|-----------|-----------|-------|-----------|
| **INTEGRIDAD TOTAL** (Math, Logic, Architecture) | I: Epistemology | VC-001, VC-002, VC-003 | Treat all output as hypothesis until validation |
| **ZERO-WARNING TOLERANCE** (Every warning = error) | I: Epistemology | VC-087 (Warning Normalized) | Gate: Fail on any warning in health path |
| **PESIMISMO ALGORÍTMICO** (Broken until proven) | I: Epistemology | VC-008 (Operational Optimism), VC-038 (Victory Premature) | Assume failure; require empirical proof |
| **CONTINUOUS IMPROVEMENT** (Protocol evolves) | I: Epistemology | VC-010 (Failure not converted to doctrine), VC-046 (Rescue pre-deprecation omitted) | Extract value from all failures; register as doctrine |

---

## LEVEL 2: OPERATION ↔ Process & State Vices

| Module | VC/VT Family | Vices | Prevention |
|--------|--------------|-------|-----------|
| **M1: Fundamentals** (Startup ritual) | V: Environment | VC-089..106 (Discovery, audit, setup) | Execute mandatory startup checklist |
| **M2: User & Scope** (Boundaries) | II: Process | VC-025 (Assumptions), VC-067 (Implicit policies) | Document scope explicitly; verify constraints |
| **M3: Flows & State** (Transitions) | III: State | VC-047..062 (Memory, concurrency, drift) | Separate stable core from volatile; checkpoint |
| **M4: Gates & Tokenomics** | TK-001..008 | TK-002 (Chat as source), TK-004 (Setup reexplained) | Maintain external ledger; persist state |
| **M5: Audit & Git** (Traceability) | II & III | VC-054 (Decentralized state), VC-057 (Version parity) | Single source of truth; version everything |

---

## LEVEL 3: VALIDATION ↔ Testing Vices

| Gate | VT Family | Vices | Prevention |
|------|-----------|-------|-----------|
| **Regression Suite** | I: Logic | VT-020..022 (Coverage theater) | Oracles must fail on real breaks; no tautologies |
| **Angry Path** | III: Flow | VT-035..050 (Evasion, xfail) | Adversarial tests; prohibit skip/xfail as green |
| **Secrets Audit** | IV: Architecture | VC-108 (Boundary security) | Scan for hardcoded credentials; reject placeholders |
| **Error Handling** | IV: Architecture | VC-085 (Logging), VT-074 (Observability not tested) | 4-element errors; logs must be causal |
| **Status.md Updated** | TK: Observability | TK-026 (Noisy observability) | Structured status with evidence and next step |

---

## LEVEL 4: GUARDS ↔ Governance & Security Vices

| Guard | VC Family | Vices | Enforcement |
|-------|-----------|-------|------------|
| **M1: Prohibitions** | VII: Security | VC-115..117 (Eval, deps, atomic writes) | Hard gates; no exceptions |
| **M2: Mandatory Operatives** | VI: Governance | VC-111..114 (Exclusions, propagation, naming) | Required actions; block if missing |
| **M3: Risk Models** (Threat modeling) | V: Environment | VC-093 (Security optimistic), VC-094 (Mixed controls) | Model threats; require mitigations |

---

## LEVEL 5: TOKEN SAVING ↔ Tokenomics & Observability Vices

| Optimization | TK/VC/VT | Vices | Prevention |
|--------------|----------|-------|-----------|
| **Diagnostics** (Visibility) | TK-008, VC-085, VT-074 | TK-026 (Noisy), VC-085 (Ornamental), VT-074 (Not tested) | Causal logging; compress noise |
| **Leaks** (Waste patterns) | TK-001..008 | TK-002, TK-004, TK-009 | Separate core from buffer; poda selectiva |
| **Tool Selection** | TK-013 (Inflated schemas) | Unnecessary dependencies bloat context | Measure ROI; audit coupling |

---

## Cross-Domain Integration

### Simulation Theater Family
**Root:** L1 (Integrity violated)
**Manifestation:** VC-118 (Zombie Compat) ← VT-023 (Mock Complacency) ← TK-002 (Chat as source)
**Prevention:** Don't hide faults; fix root causes

### False Oracle Family
**Root:** L3 (Validation gate missing)
**Manifestation:** VT-004 (Copy Expected) ← VC-015 (Agent as Engineer) ← VC-037 (Blind Regeneration)
**Prevention:** Separate oracle from implementation; independent verification

### Context Bloat Family
**Root:** L2 (State management violated)
**Manifestation:** VC-048 (Memory monolithic) ← TK-002 (Chat as source) ← TK-004 (Setup reexplained)
**Prevention:** Core + buffer separation; persist external state

### Observability Failure Family
**Root:** L1 (Zero-warning violated)
**Manifestation:** VC-085 (Ornamental Logging) ← VT-074 (Not tested) ← TK-026 (Noisy)
**Prevention:** Logs must be causal; compress signal; test observability

---

## Audit Checklist (Health Verification)

Use this to audit if the system is healthy:

### L1 Integrity
- [ ] Zero warnings in all phases?
- [ ] All output treated as hypothesis until proven?
- [ ] Failures converted to doctrine (registered as VC/VT/TK)?

### L2 Operation
- [ ] Startup ritual executed? (git status, AGENT.md, SPEC.md load)
- [ ] State persisted externally (not in chat)?
- [ ] Single version source maintained?

### L3 Validation
- [ ] Regression suite runs before closure?
- [ ] Angry path tested with real adversarial cases?
- [ ] No credentials in code? Status.md updated?

### L4 Guards
- [ ] Prohibitions enforced? (no workarounds)
- [ ] Mandatory operatives present? (required checks exist)
- [ ] Risk models documented?

### L5 Token Saving
- [ ] Token budget visible before and after?
- [ ] Observability is causal (not ornamental)?
- [ ] No unnecessary tool dependencies?

If ANY check fails → **STOP**. Fix before advancing.

---

## Reading Recommendation

1. **Understand Principles first** (L1-L5)
2. **Then learn Vices** (Patterns/) to see how violations manifest
3. **Use this matrix** to navigate between them
4. **Audit regularly** with the checklist above

Principles are the "why."
Vices are the "what breaks when."
This matrix is the bridge.
