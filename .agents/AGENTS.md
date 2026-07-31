# AGENTS — red_python

Single governance hub for every agent working in this repository
(SP-001). No other governance file may exist at the root.

## Rules

1. All work is tracked as a file under `tasks/`.
2. Every session ends with a record under `audit/sessions/` and a
   line in `audit/AUDIT_TRAIL.md`.
3. `HANDOFF.md` is updated in the same commit as the work it describes.
4. The git hooks come from the pinned Cerberus installation and are
   never edited in place.

## Structure

The canonical structure is defined by the Golden Standard
(`knowledge/CANONICAL_STRUCTURE.md`) and enforced by
`scripts/audit.py` and the Cerberus pre-commit hook.
