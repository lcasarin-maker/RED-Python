---
id: TASK-RED-01
kind: debt
title: Desacoplamiento de God-Nodes y Telemetría Agregada de Flota
status: done
severity: P3
origin: asserted
satd_family: CODE_DESIGN_DEBT
close_check: {"cmd": "python3 -m pytest tests/test_graph_report.py -q", "expect": "exit_zero"}
created: 2026-08-30
closed_at: 2026-09-03
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

# TASK-RED-01: Desacoplamiento de God-Nodes y Telemetría Agregada de Flota

## 1. Descripción del Problema
1. Los diagnósticos multi-satélite deben mantenerse desacoplados de los árboles de importación de cada proyecto analizado para evitar falsos positivos de dependencias circulares (Lección Cerberus D4). **Resuelto: ver nota arriba.**
2. `GRAPH_REPORT.md` requiere integrarse con el modelo de censo de `simplecode fleet`. **Resuelto: `to_fleet_catalog_rows()` exporta filas con los mismos nombres de campo que `.simplecode/fleet_catalog.json` (`has_hooks`), mas `has_gates_auditor`/`has_tests`/`adoption_pct`.**

## 2. Objetivos
- Diseñar scripts de diagnóstico como herramientas hoja independientes que analicen el sistema de archivos sin importar módulos internos de los satélites. **Cumplido: `graph_report.scan_fleet`/`scan_satellite`.**
- Exportar métricas de salud de paquetes Python compatibles con el esquema de `fleet_catalog.json`. **Cumplido: `graph_report.to_fleet_catalog_rows`.**
