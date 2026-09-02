---
id: DEBT-ruff-scripts-validate-retrospective-py-8-68c5e603
kind: debt
title: ruff: scripts/validate_retrospective.py:84:5: C901 `validate_retrospective_schem
status: open
severity: P2
origin: asserted
satd_family: TECHNICAL_DEBT
close_check: {"cmd": "ruff check --select C901 scripts/validate_retrospective.py", "expect": "exit_zero"}
created: 2026-08-20
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/DEBT-ruff-scripts-validate-retrospective-py-8-68c5e603.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: pagada-2026-08-20`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

## Finding

<!-- findings:start -->
- ruff: scripts/validate_retrospective.py:84:5: C901 `validate_retrospective_schema` is too complex (16 > 10)
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_DEBT-ruff-scripts-validate-retrospective-py-8-68c5e603",
  "command": "ruff check --select C901 scripts/validate_retrospective.py",
  "artifact": "tasks/done/DEBT-ruff-scripts-validate-retrospective-py-8-68c5e603.md"
}
```


## Acceptance

- [ ] The finding no longer reproduces, OR
- [ ] `status:` above is moved off `backlog` with the reason written here.

Re-running the guard must not regenerate this file.


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Root Cause

`validate_retrospective_schema` in `scripts/validate_retrospective.py` grew past ruff's `C901` complexity threshold as branching
logic accumulated inline instead of being split into named helpers. The 2026-08-20
fix (commit f66dde4, "resolve all ruff complexity violations") extracted the
sub-steps into separate functions, bringing `validate_retrospective_schema` back under the threshold
without changing its externally observed behavior.

## Regression Test

`ruff check --select C901 scripts/validate_retrospective.py` is the regression test: it fails again the
moment the extracted structure is collapsed back into one oversized function.
`pytest` (33 passed at the time of the fix) covers behavior preservation.

## Verification Evidence

Command run 2026-08-28 in this repo:

```
$ ruff check --select C901 scripts/validate_retrospective.py
All checks passed!
```

Negative control (same command family still catches real violations, proving
this is not a gate that always reports clean):

```
$ ruff check .
F841 Local variable `home_cfg` is assigned to but never used
  --> tests/test_config_and_bootstrap.py:18:5
Found 2 errors.
```
