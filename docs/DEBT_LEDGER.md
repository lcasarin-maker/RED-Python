# Debt Ledger

This document is the canonical operational debt tracker for RED-Python.

## Scope

- Track only active debt that affects onboarding, supervision, runtime, tests,
  or publication.
- Historical archives and deprecated snapshots may remain in their original
  form if they are explicitly quarantined.
- Anything not listed here should be treated as either resolved or intentionally
  out of scope for the active tree.

## Current operational debt

1. The GitHub home is currently public and must remain explicitly recorded in
   `docs/supervision/GITHUB_HOME.md` until the visibility policy is resolved.
2. Historical language drift remains in archived and deprecated materials by
   design.

## Review rules

- Add new debt here before opening new cleanup work.
- Remove an item only after the fix is validated and published.
- If a debt item is intentionally deferred, mark it clearly with its reason and
  revisit date.
