# adapters/ — Agent Integration Layer

CoderCerberus v0.5 is **agent-agnostic**. The core (scripts/, rules/, AGENT.md) works
the same for every agent. This folder contains the **adapters** that connect that
core to each specific tool.

## Arquitectura

```
Cerberus/
├── scripts/      ← logic (pure Python, no agent deps)
├── rules/        ← config (YAML/JSON, no agent deps)
├── AGENT.md      ← universal protocol
├── .pre-commit-config.yaml  ← git-level (agent-agnostic)
└── adapters/
    ├── claude/   ← Claude Code adapter
    ├── gemini/   ← Gemini CLI adapter
    ├── chatgpt/  ← ChatGPT Projects adapter
    └── codex/    ← OpenAI Codex adapter
```

## Principle

Each tool’s configuration files MUST live at the path the tool expects
(for example, `.claude/settings.json` for Claude Code). The adapters in this folder are
the **conceptual source of truth** - they document which scripts are used, how they are
triggered, and what still needs to be implemented for each agent.

## Current status

| Agent   | Automatic hooks | Pre-commit | Scheduled | Level |
|----------|------------------|------------|-----------|-------|
| Claude   | ✅ complete       | ✅          | ✅         | Full  |
| Gemini   | ⚠️ prose only     | ✅          | ✅         | Partial |
| ChatGPT  | ⚠️ prose only     | ✅          | ✅         | Partial |
| Codex    | ❌ pending        | ✅          | ✅         | Minimal |
