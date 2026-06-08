# Purge Plan - Control_Procesal - Fase 0

## Verdict

Fase 0 is not clean enough to advance to Fase 1.

The repo is now private on GitHub, but the local tree still contains old or contradictory Cerberus satellite controls.

## Root Cause

Control_Procesal appears to have been used as a Cerberus satellite during previous protocol versions. The repo now mixes:

- A v0.5 state file claiming current governance.
- v0.3 and V0.02 active Git hooks.
- A `.protocol-core` link that resolves to a missing or incompatible path.
- Tests and agent permissions that still reference old audit mechanics.

This creates security theater: the project looks governed, but the active mechanisms are not coherent.

## Purge Scope

### Must neutralize before Fase 1

1. Archive current `.git/hooks/pre-commit`, `.git/hooks/pre-push`, and `.git/hooks/post-commit` as Fase 0 evidence or under a local deprecated reference.
2. Remove the active broken `.protocol-core` link from the live root.
3. Remove untracked `scripts/__pycache__/`.
4. Stop trusting `.agent_state.json` as current handoff; either archive it or regenerate after Fase 1.

### Preserve as reference

1. Existing `deprecated/` content, because it documents prior POE versions and removed docs/scripts.
2. `.protocol/evidence/` files, pending later review, because they may help reconstruct past claims.
3. `POSTMORTEM_CERBERUS_FALLO.md`, because it has direct reference value for why satellite controls failed.

### Review in later phases, not now

1. `tests/test_fortaleza_v4_core.py`
2. `tests/test_resilience_v57.py`
3. `tests/test_v55_rigor.py`
4. `scripts/permission_auditor.py`
5. `.claude/settings.template.json`

These may be useful only if the repo contract explicitly includes Cerberus satellite governance. Otherwise they are likely control-plane theater inside a product repo.

## Proposed Non-Invasive Sequence

1. Create a `deprecated/cerberus_satellite_legacy_2026-06-05/` reference folder inside Control_Procesal.
2. Copy or move legacy hook contents into that folder for traceability.
3. Remove active hooks from `.git/hooks/` or replace them with inert sample names.
4. Move `.agent_state.json` and `.claude/` into deprecated if the repo is to be audited only from outside.
5. Remove `.protocol-core` broken link.
6. Remove `scripts/__pycache__/`.
7. Re-run `git status --short --branch`.
8. Only after clean Fase 0, decide Fase 1 contract: declared README or inferred contract.

## Stop Condition

Do not push local code to GitHub until:

- Git status is clean.
- `.protocol-core` no longer emits warnings.
- No active hook claims obsolete Cerberus versions.
- The repo has a declared or inferred contract path for Fase 1.
