# adapters/ — Capa de Integración por Agente

CoderCerberus v0.5 es **agent-agnostic**. El núcleo (scripts/, rules/, AGENT.md) funciona
igual para cualquier agente. Esta carpeta contiene los **adaptadores** que conectan ese
núcleo a cada herramienta específica.

## Arquitectura

```
Cerberus/
├── scripts/      ← lógica (Python puro, sin deps de agente)
├── rules/        ← config (YAML/JSON, sin deps de agente)
├── AGENT.md      ← protocolo universal
├── .pre-commit-config.yaml  ← git-level (agente-agnóstico)
└── adapters/
    ├── claude/   ← Claude Code adapter
    ├── gemini/   ← Gemini CLI adapter
    ├── chatgpt/  ← ChatGPT Projects adapter
    └── codex/    ← OpenAI Codex adapter
```

## Principio

Los archivos de configuración de cada tool DEBEN estar en el path que el tool exige
(ej: `.claude/settings.json` para Claude Code). Los adaptadores en esta carpeta son la
**fuente de verdad conceptual** — documentan qué scripts se usan, cómo se activan, y
qué falta implementar en cada agente.

## Estado actual

| Agente   | Hooks automáticos | Pre-commit | Scheduled | Nivel |
|----------|------------------|------------|-----------|-------|
| Claude   | ✅ completo       | ✅          | ✅         | Full  |
| Gemini   | ⚠️ solo prose     | ✅          | ✅         | Parcial |
| ChatGPT  | ⚠️ solo prose     | ✅          | ✅         | Parcial |
| Codex    | ❌ pendiente      | ✅          | ✅         | Mínimo |
