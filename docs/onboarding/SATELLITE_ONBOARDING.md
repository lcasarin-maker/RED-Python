# Satellite Onboarding

This document explains how to bring a repo under CC supervision without losing
its original intent.

## Goal

Turn an existing repo into a clean, self-describing satellite that can be
audited, tested, and supervised on its own terms.

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

## Onboarding sequence

### 1. Observe

- Read `README.md`, `STATUS.md`, and the main entry points.
- Map the tree.
- Separate legacy residue from active code.

### 2. Normalize

- Resolve merge conflicts.
- Remove or isolate foreign residue.
- Restore consistent naming.
- Keep only useful external changes.

### 3. Prove

- Run smoke tests.
- Add missing repo-specific tests.
- Fix code that fails the current contract.

### 4. Publish

- Ensure the GitHub remote exists.
- Keep the repository private unless explicitly approved otherwise.
- Record the repo URL and branch in the supervision notes.

### 5. Hand off to supervision

- Link the repo to CC.
- Publish the learning flow.
- Move the repository into regular supervision cadence.

## Exit criteria

- The repo can explain itself in English.
- The repo has a stable entry point.
- The repo has tests that prove the contract.
- The repo has a place for learnings and a place for supervision.
- CC can monitor it without reading the whole tree again.

