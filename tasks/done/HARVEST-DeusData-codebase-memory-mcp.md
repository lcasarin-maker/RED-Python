---
id: HARVEST-DeusData-codebase-memory-mcp
kind: task
title: "Evaluar adopción: mecanismo cosechado por Atlas (DeusData-codebase-memory-mcp)"
status: done
severity: P3
origin: asserted
satd_family: HARVEST_SUGGESTION
close_check: {"cmd": "python3 -m pytest -q tests/test_premisas_de_fichas_descartadas.py::test_red_python_no_analiza_codigo_fuente", "expect": "exit_zero"}
created: 2026-09-09
closed_at: 2026-09-26
closure_type: void_wontfix
reason: "DESCARTADA tras revision: la premisa del dictamen de Atlas (que red_python remueve codigo muerto de codebases Python) es falsa; red_python borra directorios vacios (SPEC.md REQ-0001)."
evidence: {"pass": "tasks/evidence/HARVEST-DeusData-codebase-memory-mcp.pass.txt", "fail": "tasks/evidence/HARVEST-DeusData-codebase-memory-mcp.fail.txt", "e2e": "tasks/evidence/HARVEST-DeusData-codebase-memory-mcp.e2e.txt"}
evidence:
  pass: tasks/evidence/HARVEST-DeusData-codebase-memory-mcp.pass.txt
  fail: tasks/evidence/HARVEST-DeusData-codebase-memory-mcp.fail.txt
  e2e: tasks/evidence/HARVEST-DeusData-codebase-memory-mcp.e2e.txt
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

## Root Cause

La sugerencia se escribio sobre una premisa equivocada del proyecto: el dictamen (corregido el 2026-09-09, DGX-503) afirma que el mandato de red_python es «remover funciones vacias/codigo muerto de codebases Python». Medido el 2026-09-26: `SPEC.md` REQ-0001 dice «clasificar directorios vacios segun sus filtros y exclusiones», y en el codigo del producto (fuera de tests, archive, deprecated) hay 0 archivos que importen `ast`, `libcst` o `networkx`. red_python no analiza codigo fuente.

## Regression Test

El close_check es el test que mide la premisa del descarte (ver el front-matter); su control negativo va en `.fail.txt`.

## Verification Evidence

Los tres artefactos del front-matter: `.pass.txt` (el comando sale 0 con la decision registrada), `.fail.txt` (control negativo: el mismo comando sobre la ficha ANTES de registrar la decision salia rc=1, «sin campo accepted en el frontmatter»), `.e2e.txt` (la lectura de SPEC.md y la busqueda en el codigo que sustentan el descarte).
