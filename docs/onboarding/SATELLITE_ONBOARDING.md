# Satellite Onboarding

This document explains how to bring a repo under CC supervision without losing
its original intent.

## Goal

Turn an existing repo into a clean, self-describing satellite that can be
audited, tested, and supervised on its own terms.

## Authority

If this document conflicts with `README.md`, `STATUS.md`, or `AGENT.md` about
onboarding behavior, this document wins. `AGENT.md` is only the entrypoint;
this page is the operational source of truth for onboarding.

## Inputs

- The repository tree as it exists now.
- The Git remote and branch state.
- Any foreign changes already present.
- Existing docs, tests, and learning artifacts.

## Required checks

1. Identify the actual purpose of the repo.
2. Detect conflict markers, duplicates, stubs, mocks, and dead paths.
3. Confirm whether the repo is already connected to GitHub.
4. Verify that the repository language is English or mark the drift.
5. Find the minimum set of entry points and core flows.
6. Check whether the repo has its own tests.
7. Run `python scripts/satellite_governance.py validate --root .`.
8. Run `python scripts/satellite_governance.py review-changes --root .` and
   classify every foreign diff before any cleanup is considered complete.

## Foreign changes policy

Foreign changes are not exempt from review. They are part of the audit scope
and must be explicitly handled before the onboarding pass closes.

Every foreign change must be one of:

- **absorb**: keep it because it is useful and consistent with the repo.
- **validate**: keep it only after proving it is correct and compatible.
- **discard**: remove it because it is stale, contradictory, or unsafe.
- **quarantine**: move it to `deprecated/` when it has value but should not stay
  live.

Rules:

1. Do not skip a change because it was made by someone else.
2. Do not leave a change unreviewed just because the tree is messy.
3. Do not close onboarding until the worktree is clean or the remaining debt is
   explicitly staged, documented, and approved.
4. If a change is useful but noisy, normalize it before keeping it.
5. If a change is not useful, remove it or quarantine it.

## Onboarding sequence

### 1. Observe

- Read `README.md`, `STATUS.md`, `AGENT.md`, and the main entry points.
- Map the tree.
- Separate legacy residue from active code.
- Inventory every foreign diff, including deletions, renames, and generated
  files.

### 2. Normalize

- Resolve merge conflicts.
- Remove or isolate foreign residue.
- Restore consistent naming.
- Keep only useful external changes.
- Review each foreign change and decide absorb, validate, discard, or quarantine.

### 3. Prove

- Run smoke tests.
- Add missing repo-specific tests.
- Fix code that fails the current contract.
- Re-run the tests after foreign-change decisions land.

### 4. Publish

- Ensure the GitHub remote exists.
- Keep the repository private unless explicitly approved otherwise.
- Record the repo URL and branch in the supervision notes.

### 5. Hand off to supervision

- Link the repo to CC.
- Publish the learning flow.
- Move the repository into regular supervision cadence.
- Keep using this onboarding contract as the baseline for later audits.
- Hand off only after the tree is clean and the remaining debt is explicit.

## Exit criteria

- The repo can explain itself in English.
- The repo has a stable entry point.
- The repo has tests that prove the contract.
- The repo has a place for learnings and a place for supervision.
- CC can monitor it without reading the whole tree again.
- The worktree is clean, or any remaining debt is explicitly accounted for.
