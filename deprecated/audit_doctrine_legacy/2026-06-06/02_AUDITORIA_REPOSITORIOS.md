# 02 - External repository audit

## 0. Objective

Audit the external repositories listed in `04_CONTEXTO_EJECUCION.md` to extract
capabilities, heuristics, metrics, and operational logic that can strengthen Coder Cerberus.

The extraction must not copy dependencies, contaminate the Golden Standard with brand names,
or create redundancy.

> Note: the canonical Golden Standard is handled separately in `03_EVOLUCION_GOLDEN_STANDARD.md`.
> This phase audits third-party repositories, not GS.

---

## 1. Scope

For each external repository:

1. Identify its main function.
2. Classify it into one or more Cerberus dimensions.
3. Extract the vice, failure, or problem it mitigates.
4. Extract the underlying operational logic.
5. Abstract that logic into agnostic knowledge.
6. Compare the logic against the Golden Standard.
7. Determine whether it adds a new rule, metric, heuristic, enforcement pattern, or nothing new.
8. Determine whether it should be integrated, complemented, discarded, or backlogged.
9. Determine whether the capability should be:
   - implemented as a Golden Standard rule;
   - implemented as a scanner;
   - implemented as a hook;
   - implemented as a runner;
   - implemented as a pipeline;
   - implemented as a skill;
   - implemented as an agent;
   - documented only;
   - discarded.

---

## 2. Mandatory method per repository

For each repository:

1. Read the README.
2. Read the main documentation.
3. Inspect the code structure if the README is not enough.
4. Identify which vice, failure, or risk it prevents.
5. Identify the mechanism or operational logic.
6. Classify it into one or more Cerberus dimensions.
7. Abstract the logic as an agnostic principle.
8. Compare against:
   - Cerberus dimensions, principles, and gaps;
   - when relevant, the documentary interface of the external Golden Standard, without treating it as an active submodule.
9. Determine real novelty.
10. Emit a decision.

---

## 3. Cerberus dimensions for classification

1. D1 Structure integrity and purity.
2. D2 Control-plane completeness.
3. D3 Clarity, style, and complexity.
4. D4 Anti-spaghetti and isolation.
5. D5 Angry path and robustness.
6. D6 Anti-theater and anti-slop.
7. D7 Data security and containment.
8. D8 Adversarial coverage.
9. D9 Test purity and falsifiability.
10. D10 Tokenomics and context hygiene.
11. D11 SCA Trivy.
12. D12 Satellite drift (release adoption).

---

## 4. Abstraction rules

Forbidden in the Golden Standard:

- installation commands;
- brand names;
- repository names;
- concrete dependencies;
- language-specific instructions;
- third-party paths or configurations.

Allowed:

- principles;
- metrics;
- heuristics;
- blocking conditions;
- detection patterns;
- falsifiability criteria;
- enforcement strategies;
- governance models;
- architecture criteria;
- efficiency patterns.

---

## 5. Mandatory format

```text
Repository:
URL:
[FACT] Documented function:
[FACT] Relevant mechanism:
[INFERENCE] Vice mitigated:
[INFERENCE] Agnostic logic:
Cerberus dimension:
Related Golden Standard:
Status against GS:
Decision: INTEGRATE / COMPLEMENT / DISCARD / BACKLOG
Justification:
Suggested implementation path:
```

---

## 6. Mandatory matrix

```markdown
| Repository | Main Function | Cerberus Dimension | Vice Mitigated | Operational Logic | Agnostic Abstraction | GS Status | Decision |
|---|---|---|---|---|---|---|---|
```

---

## 7. Inaccessible or weakly documented repositories

If a repository does not have enough documentation:

```text
Repository:
URL:
Limitation:
[ASSUMPTION] Probable function:
Confidence level:
Inference risk:
Decision:
```

Do not invent facts.
Mark all deductions as `[ASSUMPTION]`.

---

## 8. Decision criteria

### INTEGRATE

Use when the repository adds a new, relevant, uncovered, and executable logic.

### COMPLEMENT

Use when the logic already exists partially, but the repository adds a metric, enforcement,
or extra heuristic.

### DISCARD

Use when the logic is already covered or not relevant.

### BACKLOG

Use when the logic is interesting, but not critical or not mature yet.

---

## 9. Capability categories to look for

1. Static validation.
2. Linting.
3. Token control.
4. Mutation testing.
5. Vulnerability scanning.
6. Agent management.
7. Secret detection.
8. Dead dependency detection.
9. Test coverage.
10. Assertion quality.
11. Rate limiting.
12. Token budgeting.
13. Cost observability.
14. Duplicate-code detection.
15. Git hooks.
16. Pre-commit governance.
17. Supply-chain security.
18. Dependency risk.
19. Code-query security.
20. Enforcement architecture.

---

## 10. Target repositories

Audit the repositories defined in `04_CONTEXTO_EJECUCION.md`.

---

## 11. Deliverable

Return a final report with:

- the repository matrix,
- new capabilities,
- discarded repositories,
- backlog repositories.

---

## Explicit exclusion

- GS is not audited here as a generic external repository.
- GS is audited later as the canonical external source and as the contract Cerberus consumes.
