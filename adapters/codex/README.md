# adapters/codex — OpenAI Codex / Cursor Adapter

Codex and Cursor have limited external automation capabilities.

## Binding file

`.cursorrules` at repo root - read automatically by Cursor.

## Available equivalence

| Cerberus mechanism | Codex/Cursor equivalent |
|--------------------|--------------------------|
| Claude hooks | ❌ Not available |
| Pre-commit | ✅ Works (git-level) |
| Scheduled Tasks | ✅ Works (OS-level) |
| `.cursorrules` | ✅ Read automatically |

## Current status

`.cursorrules` exists at repo root but is not synchronized with the
latest protocol version. It still needs an update.

## Open gap

Cursor does not run Python scripts as hooks. Real automation is only
pre-commit + `schtasks`.
