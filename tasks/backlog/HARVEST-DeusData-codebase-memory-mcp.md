---
id: HARVEST-DeusData-codebase-memory-mcp
kind: task
title: "Evaluar adopción: mecanismo cosechado por Atlas (DeusData-codebase-memory-mcp)"
status: open
severity: P3
origin: asserted
satd_family: HARVEST_SUGGESTION
close_check: {"cmd": "python -m tools.check_harvest_accepted tasks/backlog/HARVEST-DeusData-codebase-memory-mcp.md", "expect": "exit_zero", "porque": "Sugerencia de adopcion, no un defecto -- verifica que accepted.by/date/trigger este lleno y no sea el placeholder, patron de own_chats/tools/check_harvest_accepted.py (DGX-505)."}
created: 2026-09-09
---

## Qué es esto

Sugerencia de cosecha, no un defecto. Atlas (la KB compartida de la flota) leyó una fuente
externa y encontró mecanismos que podrían servirle a **este proyecto** específicamente, por
dominio. Nadie de red_python pidió esta evaluación -- es cosecha pasiva. **La decisión
de adoptar, adaptar o descartar es 100% de este proyecto.**

Cruzada antes de escribirse contra `.simplecode/fork_own.json` de este repo (si existe) para
evitar sugerir algo que ya está vendorizado -- ver DGX-505 en Atlas, donde `own_chats` cazó 3
falsos positivos de este tipo en el primer lote.

## Mecanismos encontrados, con su cita (tal como Atlas los verificó)

- El proyecto es un motor de inteligencia de código (Code Intelligence Engine) cuya función es analizar estructura de codebase: relaciones de llamadas, dependencias, entidades (funciones, clases, rutas HTTP), impacto de cambios — `knowledge/references/github_com_DeusData_codebase_memory_mcp.md:"The fastest and most efficient code intelligence engine for AI coding agents"` — radicalmente distinto del dominio de Atlas, que es una base de conocimiento sobre hardware, frameworks, experiencias y estrategia (no análisis de código fuente).

## Por qué se sugiere para red_python en concreto

El motor de grafo de código detecta explícitamente 'código muerto (funciones con cero invocadores)' vía análisis de dependencias -- exactamente el mandato de red_python (remueve funciones vacías/código muerto de codebases Python) -- pero el dictamen solo lo compara contra Atlas ('radicalmente distinto del dominio de Atlas') y nunca considera a red_python, concluyendo DOM.

## Procedencia

- Fuente original: https://github.com/DeusData/codebase-memory-mcp
- Dictamen de cosecha, ruta absoluta: `/home/lcasarin/projects/Atlas/docs/agent_findings/2026-09-06_cosecha_github_com_DeusData_codebase_memory_mcp.md`
- Corregido el 2026-09-09 (DGX-503): el dictamen original interrogó estos mecanismos sólo contra
  Atlas/aequitas_os porque la lista de flota de Atlas estaba rota (DGX-502) y no consideraba
  a red_python en absoluto.

## Lo que esta ficha NO decide

No dice que red_python deba adoptar nada. No mide si el código fuente es
production-ready, tiene licencia compatible, o pasa los propios gates de este repo -- eso lo
evalúa quien trabaje aquí, si decide que vale la pena mirarlo.
