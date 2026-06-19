# Satellite Onboarding

This is the minimal contract for bringing a repo under CC supervision without
turning onboarding into a long manual.

## Purpose

Establish the repo's real shape, make the active contract visible, and hand the
repo to supervision with explicit debt instead of hidden assumptions.

## Authority

This document owns onboarding behavior. `AGENT.md` only points here.

## Inputs

- Current tree state.
- Git remote and branch state.
- Existing docs, tests, and learning artifacts.
- Foreign changes already present.

## Flow

### 1. Orient

- Read `README.md`, `STATUS.md`, `AGENT.md`, and the main entry points.
- Identify the repo purpose, core flows, and English drift.
- Map the tree and separate active code from legacy residue.

### 2. Normalize

- Inspect all foreign changes.
- Classify each one as absorb, validate, discard, or quarantine.
- Resolve conflicts, duplicates, stubs, mocks, and dead paths.
- Keep only useful changes and normalize noisy ones.

### 3. Prove

- Run smoke tests and repo-specific tests.
- Run the automatic test-surface report so new gaps are visible immediately.
- Add missing tests for the current contract when coverage is thin.
- Re-run the tests after normalization lands.

### 4. Publish

- Confirm the GitHub remote exists.
- Apply the GitHub visibility policy template in
  `docs/templates/GITHUB_VISIBILITY_POLICY.md`.
- Keep the repo private by default.
- If the repo is public, request explicit authorization before keeping it that
  way.
- Record the GitHub home state and authorization status in
  `docs/supervision/GITHUB_HOME.md`.

### 5. Hand off

- Link the repo to CC supervision.
- Publish the learning flow.
- Move the repo into steady supervision cadence.
- Close onboarding only when remaining debt is explicit.

## Non-negotiables

- Foreign changes are always reviewed.
- Onboarding never skips work just because it was already in the tree.
- The worktree must end clean or with bounded, documented debt.

## Exit criteria

- The repo explains itself in English.
- The repo has a stable entry point.
- The repo has tests that prove the contract.
- The GitHub home state is recorded.
- Any public visibility is explicitly authorized or explicitly pending.
- CC can supervise the repo without re-reading the whole tree.
