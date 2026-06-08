# adapters/chatgpt — ChatGPT Projects Adapter

ChatGPT Projects no soporta hooks de código ni ejecución de scripts externos.
La automatización equivalente es únicamente via **system prompt** e **instrucciones de proyecto**.

## Archivo de binding

No existe un archivo específico de ChatGPT en root (usa system prompt directo).
Ver `deprecated/docs_archive_legacy/INSTRUCCIONES_PLATAFORMAS/04_CHATGPT_PROJECTS_INSTRUCCIONES.md`
para el system prompt histórico.

## Equivalencia disponible

| Mecanismo Cerberus | ChatGPT equivalente |
|--------------------|---------------------|
| Claude hooks (PreToolUse, Stop) | ❌ No disponible |
| Pre-commit | ✅ Funciona (git-level) |
| Scheduled Tasks | ✅ Funciona (OS-level) |
| Ritual manual inicio | ⚠️ Solo prose en system prompt |

## Gap pendiente

ChatGPT con Code Interpreter puede ejecutar Python. Si el operador
pega el output de un script en el chat, ChatGPT puede procesarlo.
Esto requiere flujo manual, no automático.

## Implementación mínima recomendada

Agregar al system prompt de ChatGPT Projects:
```
Al inicio de cada sesión, ejecuta mentalmente:
1. Leer AGENT.md líneas 1-46
2. Leer SPEC.md líneas 1-50  
3. Verificar que no hay conflictos antes de proceder
```
