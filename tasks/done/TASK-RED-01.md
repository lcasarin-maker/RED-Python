---
id: TASK-RED-01
kind: debt
title: Make fleet telemetry distinguish file presence from canonical adoption
status: done
closed_at: 2026-09-26
severity: P3
origin: asserted
satd_family: CODE_DESIGN_DEBT
close_check: {"cmd": "python3 -m pytest -q tests/test_graph_report.py::test_tres_archivos_inertes_no_reciben_adopcion_ni_cien_por_ciento_de_adopcion", "expect": "exit_zero"}
created: 2026-08-30
evidence:
  pass: tasks/evidence/TASK-RED-01.pass.txt
  fail: tasks/evidence/TASK-RED-01.fail.txt
  e2e: tasks/evidence/TASK-RED-01.e2e.txt
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/backlog/TASK-RED-01-decouple-god-nodes-and-aggregated-telemetry.md el 2026-09-01. -->

> **Implementado el 2026-09-03 en `scripts/graph_report.py`.** `GRAPH_REPORT.md`
> existia en este repo sin NINGUN generador -- ningun `.py` del repo lo referenciaba,
> confirmado por busqueda exhaustiva. Era un artefacto huerfano de una herramienta
> externa ("Cerberus"), no algo que este repo pudiera regenerar. `graph_report.py`
> es el generador real: solo `Path.is_dir()`/`Path.glob()`/`Path.rglob()`, sin un solo
> `import` ni `sys.path.insert` hacia un satelite. `scripts/satellite_governance.py`
> (ya existente en este repo) ya seguia el mismo principio via `subprocess`, asi que
> el patron "diagnostico = herramienta hoja" no era nuevo aqui, solo faltaba
> aplicarlo al generador de GRAPH_REPORT.md especificamente.

# TASK-RED-01: Telemetría de flota sin falsos positivos de adopción

## Reapertura — 2026-09-10

La garantía de herramienta hoja sigue resuelta: `graph_report.py` no importa
módulos de los satélites. La métrica que publica es falsa. Marca `full` y
`100%` cuando encuentra cualquier `.pre-commit-config.yaml` no vacío, cualquier
`gates/*.py` y cualquier `test_*.py`; no ejecuta gates, no comprueba que el
hook los invoque, ni verifica el contrato canónico. Un repositorio con tres
archivos inertes obtiene la misma etiqueta que uno sincronizado y verificable.

## Definition of done

- El informe llama a sus indicadores actuales `presencia`, nunca `adopción`.
- Si publica adopción canónica, usa una fuente verificable del runtime de
  Simplecode y representa explícitamente `could_not_run` cuando esa fuente no
  está disponible.
- La prueba negativa construye un satélite con los tres archivos inertes y
  demuestra que no se le asigna `full` ni `100%` de adopción.
- Se conserva la prueba de aislamiento: ningún diagnóstico importa código del
  satélite evaluado.

## 1. Descripción del Problema
1. Los diagnósticos multi-satélite deben mantenerse desacoplados de los árboles de importación de cada proyecto analizado para evitar falsos positivos de dependencias circulares (Lección Cerberus D4). **Resuelto: ver nota arriba.**
2. `GRAPH_REPORT.md` requiere integrarse con el modelo de censo de `simplecode fleet`. **Resuelto: `to_fleet_catalog_rows()` exporta filas con los mismos nombres de campo que `.simplecode/fleet_catalog.json` (`has_hooks`), mas `has_gates_auditor`/`has_tests`/`presence_pct`** (renombrado de `adoption_pct` el 2026-09-26, ver el cierre de la reapertura).

## 2. Objetivos
- Diseñar scripts de diagnóstico como herramientas hoja independientes que analicen el sistema de archivos sin importar módulos internos de los satélites. **Cumplido: `graph_report.scan_fleet`/`scan_satellite`.**
- Exportar métricas de salud de paquetes Python compatibles con el esquema de `fleet_catalog.json`. **Cumplido: `graph_report.to_fleet_catalog_rows`.**


## Cierre de la reapertura — 2026-09-26

El informe pasa a llamar a sus indicadores PRESENCIA: `presence_pct`/`presence_label`, encabezados «Presencia completa/parcial», «Sin presencia», y una linea que dice que no mide adopcion canonica; el JSON ya no trae `adoption_pct`. No publica adopcion canonica (no hay fuente que citar), asi que no aplica representar `could_not_run`. La prueba negativa construye un satelite con un hook `repos: []`, un `gates/nada.py` vacio y un test trivial: obtiene 100% de presencia y el informe nunca lo llama adopcion. Se conserva `test_no_importa_modulos_del_satelite`.

## Root Cause

`graph_report.py` derivaba una etiqueta de «adopcion» (`full`, `100%`) de la mera existencia de tres archivos: un `.pre-commit-config.yaml` no vacio, cualquier `gates/*.py` y cualquier `test_*.py`. Un repositorio con tres archivos inertes obtenia la misma etiqueta que uno sincronizado y verificable. La causa no era el calculo, era el NOMBRE: presencia de archivos publicada como adopcion.

## Regression Test

`python3 -m pytest -q tests/test_graph_report.py::test_tres_archivos_inertes_no_reciben_adopcion_ni_cien_por_ciento_de_adopcion` construye ese satelite inerte y exige que el informe (markdown y JSON) hable de presencia y nunca de adopcion.

## Verification Evidence

Los tres artefactos del front-matter: `.pass.txt`, `.fail.txt` (con los dos mutantes plantados y matados: el titulo «Full adoption» y la clave `adoption_pct`) y `.e2e.txt`.
