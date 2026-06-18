# adapters/gemini — Gemini CLI Adapter

Gemini does not have an automatic hook system equivalent to Claude Code.
The equivalent automation is achieved via the **manual startup ritual** (`GEMINI.md`).

## Binding file (fixed path at repo root)

`GEMINI.md` - must live at repo root so Gemini CLI can read it.

## Manual Claude → Gemini hook equivalence

The scripts that Claude Code runs automatically must be run by Gemini
when the operator starts the session:

```bash
# Equivalent to PreToolUse session-init
python scripts/preflight_compliance.py
python scripts/sync_binding.py --check

# Equivalent to Stop (at session end)
python scripts/track_tokens.py --session-end
python scripts/compress_historial.py --auto
```

## Partial automation available

Pre-commit and Scheduled Tasks are **agent-agnostic** - they work the same for Gemini:
- `.pre-commit-config.yaml` — 11 hooks locales
- Cerberus-Heartbeat, MonitorProjects, SyncSatellites, GlobalSync (Windows Task Scheduler)

## Open gap

Gemini Gems / system prompt does not support external code execution.
The only real automation available is: pre-commit + `schtasks` + manual ritual.
