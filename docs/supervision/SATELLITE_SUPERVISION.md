# Satellite Supervision

CC supervision keeps the satellite honest after onboarding.

## Role

- Onboarding sets the contract.
- Supervision keeps the contract true.
- Supervision handles debt, drift, and promotion without rewriting history.

## What CC watches

- Diff quality.
- Test and doc agreement.
- Learning packets.
- Wiki health.
- GitHub home state.
- Visibility stays private by default unless public use is explicitly
  authorized.
- Use `docs/templates/GITHUB_VISIBILITY_POLICY.md` as the reusable policy
  surface.

## Routine checks

### Per change

- Classify every foreign change.
- Reject quiet drift.
- Keep only useful edits.
- Re-run tests when the contract changes.

### Per learning

- Capture a structured packet.
- Deduplicate before promotion.
- Route it as local, CC-reusable, or GS-candidate.

### Per audit

- Re-run the structure validator.
- Re-run the tests.
- Re-run the automatic test-surface report.
- Verify the GitHub workflow still runs validation and strict surface checks.
- Check the wiki vault for orphans and broken links.
- Reconcile `docs/supervision/GITHUB_HOME.md` with the real remote.

## CC rules

1. CC supervises; it does not own the repo.
2. The satellite keeps its own tests and docs.
3. Nothing moves upstream unless it is repeatable and useful.
4. Foreign changes are never skipped.
5. History is only rewritten when the contract requires it.

## Escalate when

- tests fail after a foreign change
- docs drift away from code
- a stub or mock replaces real behavior
- a learning is reusable but not yet generalized
- a foreign change has not been classified

## Healthy state

- audits are green or debt is explicit
- the wiki vault is solid
- the learning queue is current
- the repo is understandable without tribal knowledge
- the GitHub home record is explicit
- any public visibility is authorized or tracked as open debt
- the GitHub workflow exists and keeps the contract enforced
- the worktree is clean or justified
