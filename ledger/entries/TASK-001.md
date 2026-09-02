---
id: TASK-001
kind: debt
title: Rename Spanish identifiers and file names to English
status: open
prior_status: done
severity: P3
origin: asserted
satd_family: TECHNICAL_DEBT
close_check: {"cmd": "pytest tests/test_filters.py", "expect": "exit_zero"}
created: 2026-07-31
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/TASK-001-rename-spanish-identifiers.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: cerrada-doctrina-retirada-2026-08-17`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

<!-- findings:start -->
- SP-011 (Cerberus governance): file names and Python identifiers outside third-party code must be descriptive English following PEP 8; red_python's application code predates that rule and is written in Spanish.
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_TASK-001",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/TASK-001-rename-spanish-identifiers.md"
}
```

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

## Root Cause

This task's only mandate was `SP-011` of the Cerberus governance doctrine,
cited verbatim in the Context section above. That protocol was removed from
this repo on 2026-08-17. A mass rename of Spanish identifiers has no
remaining justification once the rule requiring it is gone.

## Regression Test

None applicable -- there is no code defect to regress-test. If English
identifiers are ever wanted, that would be a fresh decision with its own
written rationale, not a resumption of this retired mandate.

## Verification Evidence

Command run 2026-08-28 in this repo:

```
$ grep -rn "SP-011\|Cerberus governance" --include="*.py" --include="*.md" . | grep -v TASK-001
(no output)
```

No file in this repo mentions `SP-011` or Cerberus governance outside this
closed task itself, confirming the doctrine that required the rename is gone.

Negative control: the same `grep` against this task file itself (which quotes
`SP-011` in its own Context section) DOES match, proving the search is not
silently empty by construction:

```
$ grep -n "SP-011" tasks/done/TASK-001-rename-spanish-identifiers.md
20:identifiers (SP-011). This project's application code predates that
```
