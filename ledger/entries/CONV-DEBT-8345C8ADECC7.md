---
id: CONV-DEBT-8345C8ADECC7
kind: debt
title: CONV DEBT 8345C8ADECC7
status: open
severity: P2
origin: asserted
satd_family: TEST_DEBT
close_check: {"cmd": "pytest tests/test_filters.py", "expect": "exit_zero"}
created: 2026-08-22
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/CONV-DEBT-8345C8ADECC7.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: done`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

# Conversational Debt [BUG]: Deuda_T_cnica_documentada

**Source:** `git://red_python/78ec88b9` (Line/ID #78ec88b9)

## I · Issue (Deficiencia Identificada)
> "Deuda Técnica documentada"

<!-- findings:start -->
- conversational-debt: commit `78ec88b9` (`Squashed '.protocol-core/' changes from 2f537c2..63d2f2a`) is cited generically as "Deuda Técnica documentada" with no specific defect named -- the evidence is a raw squash-merge log of a vendored `.protocol-core/` subtree, not a description of a bug in red_python's own code.
<!-- findings:end -->

## R · Rule / Mecanismo Implicado (DGX-40)
- Componente afectado: `Deuda_T_cnica_documentada`
- Clasificación: `BUG`

## A · Application (Evidencia y Contexto Verbatim)
```text
Squashed '.protocol-core/' changes from 2f537c2..63d2f2a
63d2f2a feat(align): Fase 2c — align-check gate real (opt-in) con 0 deuda en Cerberus
6296143 docs(federated): actualiza citas de hash tras reescritura de subjects
f647e1e docs(federated): cierra Fase 1 (grafo federado 2 capas + ecosistema) y Fase 2 (alignment)
c9ef5dc feat(align): matching ergonomico por nombre corto (Fase 2b) [skip-handoff]
eb534bb fix(graph): incluye protocol_engine en auto-detect de targets [skip-handoff]
179408f feat(governance): VC-141 — regla "no eludir cambios pendientes" (idempotencia + detector pre-commit)
971c
```

## C · Conclusion & Resolution
1. Diseñar prueba de regresión específica.
2. Corregir defecto y validar con suite de pruebas.

```json queue-job
{
  "name": "remediate_CONV-DEBT-8345C8ADECC7",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/CONV-DEBT-8345C8ADECC7.md"
}
```

## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Root Cause

The cited commit (`78ec88b9`) is a routine `git subtree`-style squash-merge of
a vendored `.protocol-core/` directory, harvested as generic "documented
technical debt" with no specific defect named. The subtree it merged was
itself retired shortly after: commit `14c85fd` ("remove retired protocol-core
bootstrap and align stale config test") deleted `.protocol-core/` entirely.
There was never a red_python code defect described here to fix -- only a
generic taxonomy label attached to a squash-merge log line.

## Regression Test

None applicable -- there is no code defect to regress-test; the directory the
evidence references no longer exists.

## Verification Evidence

Commands run 2026-08-28 in this repo:

```
$ git cat-file -e 78ec88b9 && echo EXISTS
EXISTS
$ ls .protocol-core
ls: no se puede acceder a '.protocol-core': No existe el archivo o el directorio
```

The commit is real and traceable, but its subject (`.protocol-core/`) is gone
from the tree, confirming there is no live code left to point a fix at.

Negative control: the same `ls` against a directory that DOES exist in this
repo confirms the command reports existing paths correctly, not silence by
construction:

```
$ ls tasks
active  backlog  blocked  done
```
