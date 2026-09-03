---
id: TASK-RED-01
kind: debt
title: Desacoplamiento de God-Nodes y Telemetría Agregada de Flota
status: open
severity: P3
origin: asserted
satd_family: CODE_DESIGN_DEBT
close_check: {"cmd": "", "expect": "exit_zero"}
created: 2026-08-30
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/backlog/TASK-RED-01-decouple-god-nodes-and-aggregated-telemetry.md el 2026-09-01. -->


# TASK-RED-01: Desacoplamiento de God-Nodes y Telemetría Agregada de Flota

## 1. Descripción del Problema
1. Los diagnósticos multi-satélite deben mantenerse desacoplados de los árboles de importación de cada proyecto analizado para evitar falsos positivos de dependencias circulares (Lección Cerberus D4).
2. `GRAPH_REPORT.md` requiere integrarse con el modelo de censo de `simplecode fleet`.

## 2. Objetivos
- Diseñar scripts de diagnóstico como herramientas hoja independientes que analicen el sistema de archivos sin importar módulos internos de los satélites.
- Exportar métricas de salud de paquetes Python compatibles con el esquema de `fleet_catalog.json`.
