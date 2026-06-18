# adapters/chatgpt — ChatGPT Projects Adapter

ChatGPT Projects does not support code hooks or external script execution.
The equivalent automation is only via **system prompt** and **project instructions**.

## Binding file

There is no ChatGPT-specific root file (it uses the direct system prompt).
See `deprecated/docs_archive_legacy/INSTRUCCIONES_PLATAFORMAS/04_CHATGPT_PROJECTS_INSTRUCCIONES.md`
for the historical system prompt.

## Available equivalence

| Cerberus mechanism | ChatGPT equivalent |
|--------------------|--------------------|
| Claude hooks (PreToolUse, Stop) | ❌ Not available |
| Pre-commit | ✅ Works (git-level) |
| Scheduled Tasks | ✅ Works (OS-level) |
| Manual startup ritual | ⚠️ Prose only in the system prompt |

## Open gap

ChatGPT with Code Interpreter can run Python. If the operator
pastes a script output into chat, ChatGPT can process it.
That requires a manual flow, not an automatic one.

## Minimal recommended implementation

Add this to the ChatGPT Projects system prompt:
```
At the start of each session, mentally run:
1. Read AGENT.md lines 1-46
2. Read SPEC.md lines 1-50
3. Verify there are no conflicts before proceeding
```
