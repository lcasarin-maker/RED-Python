# adapters/gemini — Gemini CLI Adapter

Gemini no tiene sistema de hooks automáticos equivalente a Claude Code.
La automatización equivalente se logra via **ritual de inicio manual** (GEMINI.md).

## Archivo de binding (path fijo en root)

`GEMINI.md` — debe estar en root para que Gemini CLI lo lea.

## Equivalencia manual de hooks Claude → Gemini

Los scripts que Claude Code ejecuta automáticamente, Gemini los ejecuta
si el operador los corre al inicio de sesión:

```bash
# Equivalente a PreToolUse session-init
python scripts/preflight_compliance.py
python scripts/sync_binding.py --check

# Equivalente a Stop (al cerrar sesión)
python scripts/track_tokens.py --session-end
python scripts/compress_historial.py --auto
```

## Automatización parcial disponible

Pre-commit y Scheduled Tasks son **agent-agnostic** — funcionan igual para Gemini:
- `.pre-commit-config.yaml` — 11 hooks locales
- Cerberus-Heartbeat, MonitorProjects, SyncSatellites, GlobalSync (Windows Task Scheduler)

## Gap pendiente

Gemini Gems / system prompt no soporta ejecución de código externo.
La única automatización real disponible es: pre-commit + schtasks + ritual manual.
