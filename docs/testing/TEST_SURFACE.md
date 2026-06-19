# Test Surface

RED-Python keeps the test surface visible so onboarding does not rely on
memory.

## What it does

- Profiles the current repo surfaces.
- Compares those surfaces against the tests already present.
- Reports covered, partial, and missing areas.

## Automatic run

The test surface report is part of the satellite governance flow:

- `python scripts/satellite_governance.py validate --root .`
- `python scripts/satellite_governance.py test-surface --root .`
- The GitHub workflow runs `test-surface` in strict mode so new gaps fail fast.

## Rule

- Keep adding tests as the repo evolves.
- Do not assume the initial onboarding suite is exhaustive.
- Treat missing surfaces as visible work, not hidden memory.
