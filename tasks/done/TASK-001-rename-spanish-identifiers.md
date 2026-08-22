---
id: TASK-001
title: Rename Spanish identifiers and file names to English
status: cerrada-doctrina-retirada-2026-08-17
priority: medium
created: 2026-07-31
verification_command: "pytest tests/test_filters.py"
satd_family: TECHNICAL_DEBT
risk_score: 7
blast_radius: LOW
---

## Context

Cerberus governance requires descriptive English names for files and
identifiers (SP-011). This project's application code predates that
rule. The rename is deliberately gradual: adoption does not touch
application code, because a mass rename and a governance change in the
same commit make both impossible to review.

## Definition of done

- File names and Python identifiers outside third-party code are
  descriptive English following PEP 8.
- The project's own test suite passes after each rename batch.
- No stale references remain (grep for the old names).

## Cierre — 2026-08-17

**Doctrina retirada.** La única autoridad de esta tarea era `SP-011` de la
gobernanza Cerberus, citada textualmente en el Context de arriba: *"Cerberus
governance requires descriptive English names for files and identifiers
(SP-011)"*. Ese protocolo se borró de este repo el 2026-08-17 y no queda un
solo `.py` que lo mencione.

No se cierra por difícil ni por costosa: se cierra porque **quien la exigía ya
no existe**, y un renombrado masivo de identificadores en un código escrito en
español no tiene otro sustento que ese mandato. Si alguna vez se quiere en
inglés, será una decisión del repo con su propia razón escrita, no la herencia
de un protocolo retirado.

El archivo se conserva, como las tres tareas de vendorización: sellado, no
borrado.


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.