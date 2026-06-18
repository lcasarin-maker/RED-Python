# RED-Python

RED-Python is a satellite project supervised by CC. Its job is to remove empty
or effectively empty directories safely, with a clear CLI, a GUI, and a
minimal governance layer for onboarding, supervision, and learning transfer.

## What this repo is

- A standalone Python application for directory cleanup.
- A CC-supervised satellite with its own docs, tests, and learning flow.
- A repo that should stay in English, with low-ambiguity contracts and
  evidence-backed changes.

## What this repo is not

- It is not a copy of CC.
- It is not a documentation mirror.
- It is not a place for theatrical stubs, mocks, or dead links.

## Operating model

- `AGENT.md` points to the onboarding contract and keeps the entrypoint small.
- `docs/onboarding/` describes how to understand and normalize the repo.
- `docs/supervision/` describes how CC supervises ongoing work.
- `docs/learning/` describes how local discoveries flow upstream to CC and, if
  stable, to GS.
- `docs/DEBT_LEDGER.md` tracks active operational debt.
- Foreign changes are never ignored; they are reviewed, absorbed, validated, or
  discarded before the onboarding pass closes.
- `Wiki/` is the lightweight navigable vault used by CC audits.
- `tests/` contains repo-specific checks that prove the satellite still works.

## Quick start

```bash
pip install -r requirements.txt
python red.py
python -m pytest -q
```

## Main entry points

- `red.py` launches the GUI when run without arguments.
- `red.py --scan PATH ...` runs the CLI scanner.
- `scripts/satellite_governance.py` validates the satellite contract and
  produces structured learning packets.
- `scripts/satellite_governance.py review-changes` lists worktree changes so
  foreign diffs cannot be skipped during onboarding.

## Audit contract

External audit and satellite onboarding rules live in:

- [00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md](00%20audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md)
- [docs/onboarding/SATELLITE_ONBOARDING.md](docs/onboarding/SATELLITE_ONBOARDING.md)
- [docs/supervision/SATELLITE_SUPERVISION.md](docs/supervision/SATELLITE_SUPERVISION.md)
- [docs/learning/SATELLITE_LEARNING_FLOW.md](docs/learning/SATELLITE_LEARNING_FLOW.md)

## Repository layout

- `core.py` contains the scanner and cleaner logic.
- `filters.py` contains the cleanup rules.
- `dimensions/` contains the audit dimensions.
- `scripts/` contains governance and protocol helpers.
- `project_insights/` stores transient candidate insights.
- `learnings/` is the upstream learning registry.

## GitHub

This repo already has a GitHub remote configured as `origin`. Keep the remote
private when publishing satellite work and verify visibility before onboarding
new consumers.
