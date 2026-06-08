# adapters/codex — OpenAI Codex / Cursor Adapter

Codex y Cursor tienen capacidades limitadas de automatización externa.

## Archivo de binding

`.cursorrules` en root — leído automáticamente por Cursor.

## Equivalencia disponible

| Mecanismo Cerberus | Codex/Cursor equivalente |
|--------------------|--------------------------|
| Claude hooks | ❌ No disponible |
| Pre-commit | ✅ Funciona (git-level) |
| Scheduled Tasks | ✅ Funciona (OS-level) |
| `.cursorrules` | ✅ Leído automáticamente |

## Estado actual

`.cursorrules` existe en root pero no está sincronizado con la versión
más reciente del protocolo. Pendiente actualizar.

## Gap pendiente

Cursor no ejecuta scripts Python como hooks. La automatización real
es únicamente pre-commit + schtasks.
