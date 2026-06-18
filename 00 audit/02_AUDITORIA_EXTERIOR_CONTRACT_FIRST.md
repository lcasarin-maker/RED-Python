# 02 - External Satellite Audit Contract

**Status:** active design  
**Primary use:** CC-supervised satellite onboarding and external review

---

## 0. Purpose

This document defines how CC audits a satellite repository from the outside.
The audit is not "run a few commands and declare victory". The goal is to
understand the repository, normalize the documentation, verify that the code
actually works, create or repair the satellite's own tests, and surface the
useful lessons back upstream.

---

## 1. Mandatory principles

1. **Understand first:** read the repo as it is, not as it should have been.
2. **Private by default:** a satellite should remain private unless explicitly
   authorized otherwise.
3. **Evidence over narrative:** every claim needs a file, log, test, command,
   or reproducible output.
4. **No theatrical tests:** mocks, stubs, or text-only assertions do not count
   as operational proof.
5. **Local repair first:** fix the satellite before importing outside changes.
6. **Upstream learning:** only normalized, repeated, and useful lessons move to
   CC and then to GS.

---

## 2. Audit phases

### Phase 0 - Profile and contamination review

Goal: understand the repo boundary and identify foreign residue.

Validate:

1. Git branch, remotes, and worktree state.
2. Project visibility and GitHub presence.
3. Active vs legacy tree: `deprecated/`, `archive/`, `old/`, `backup/`.
4. Conflict markers, duplicate docs, stubs, mocks, and dead files.
5. Language drift and mixed-content files.

Expected outputs:

```text
repo_profile.json
legacy_controls_inventory.json
purge_plan.md
privacy_check.md
```

### Phase 1 - Contract and onboarding

Goal: make the repo explain itself.

Validate or create:

1. `README.md` in English.
2. Satellite onboarding doc.
3. Satellite supervision doc.
4. Satellite learning flow doc.
5. A navigable wiki vault.

Expected outputs:

```text
SATELLITE_ONBOARDING.md
SATELLITE_SUPERVISION.md
SATELLITE_LEARNING_FLOW.md
Wiki/Index.md
```

### Phase 2 - Code and runtime reality

Goal: verify the code works before trusting the prose.

Validate:

1. Entry points.
2. Core flows.
3. Angry paths.
4. Dependency handling.
5. Actual behavior under test.

Expected outputs:

```text
execution_log.txt
smoke_test_report.md
runtime_findings.md
```

### Phase 3 - Satellite-owned tests

Goal: ensure the repo defends itself.

The satellite must have tests that cover:

1. Public contract behavior.
2. Edge cases and angry paths.
3. Regression risk from foreign changes.
4. Documentation or structure invariants if those are part of the contract.

Expected outputs:

```text
tests/
pytest_report.txt
```

### Phase 4 - Learning extraction

Goal: convert useful findings into structured knowledge.

Every learning should specify:

1. The problem.
2. The root cause.
3. The fix.
4. The evidence.
5. The scope.
6. Whether it stays local, is promoted to CC, or is general enough for GS.

Expected outputs:

```text
learning_packet.json
learning_review.md
```

### Phase 5 - GitHub and supervision

Goal: keep the satellite private, traceable, and supervised.

Validate:

1. GitHub remote exists.
2. Repository visibility is private when required.
3. CC supervision path is documented.
4. Changes are reviewable and reversible.

Expected outputs:

```text
github_surface_check.md
supervision_contract.md
```

### Phase 6 - Remediation and revalidation

Goal: close the loop.

A satellite audit is not complete until:

1. Findings are fixed or explicitly deferred.
2. Tests are updated.
3. Docs and code agree again.
4. The repo is revalidated against the same baseline.

Expected outputs:

```text
repair_plan.md
revalidation_report.md
```

---

## 3. Exit criteria

The satellite can be considered operational when:

1. It has a clear English contract.
2. It has its own tests.
3. Its wiki vault is solid and orphan-free.
4. The code and docs are aligned.
5. The upstream learning flow is active.
6. CC can supervise without guessing.

