# Satellite Supervision

CC supervision keeps the satellite healthy after onboarding.

## Relationship to onboarding

- Onboarding defines the contract.
- Supervision keeps that contract true after the initial pass.
- The same foreign-change policy still applies once the repo is onboarded.
- If onboarding discovers new debt, supervision tracks the debt until it is
  either removed or explicitly justified.

## Purpose

Make sure the satellite stays:

- coherent
- testable
- English-first
- private when required
- aligned with its own contract
- useful upstream for CC and GS

## Supervision loops

### Per change

- Review the diff for foreign contamination.
- Check whether the change improves the repo or only adds noise.
- Confirm tests and docs still agree.
- Classify every foreign change instead of skipping it.
- Require an explicit absorb / validate / discard / quarantine decision.

### Per learning

- Capture the learning in a structured packet.
- Classify it as local, CC-reusable, or GS-candidate.
- Deduplicate before promotion.

### Per audit

- Re-run the satellite structure validator.
- Re-run tests.
- Re-read the wiki vault for orphans and broken links.
- Reconcile the recorded GitHub home in `docs/supervision/GITHUB_HOME.md`
  with the real remote and visibility state.

## CC supervision rules

1. CC is the supervisor, not the owner.
2. The satellite keeps its own docs and tests.
3. CC receives normalized learnings, not raw noise.
4. Nothing moves upstream unless it is repeatable and useful.
5. No retroactive rewriting of history unless the repo contract demands it.
6. A messy tree is not an excuse to ignore foreign changes.

## Escalation conditions

Escalate to CC when:

- tests fail after a foreign change
- docs drift away from code
- a stub or mock replaces real behavior
- token cost grows without a corresponding gain in clarity
- a learning looks reusable but is not yet generalized
- a foreign change has not been classified yet

## Exit criteria

The satellite is in good standing when:

- audits are green or have explicit, bounded debt
- the wiki vault is solid
- the learning queue is current
- the repo remains understandable without tribal knowledge
- the GitHub home record is current and its visibility state is explicit
- the worktree is clean or every remaining change is tracked and justified
