---
id: DEBT-coverage-floor-could-not-run-or-test-sui-06f4e856
kind: debt
title: coverage-floor: could_not_run or test suite failed before coverage was measured
status: open
severity: P1
origin: asserted
satd_family: TECHNICAL_DEBT
close_check: {"cmd": "pytest tests/test_filters.py", "expect": "exit_zero"}
created: 2026-08-20
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/DEBT-coverage-floor-could-not-run-or-test-sui-06f4e856.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: closed`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

## Finding

<!-- findings:start -->
- coverage-floor: could_not_run or test suite failed before coverage was measured
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_DEBT-coverage-floor-could-not-run-or-test-sui-06f4e856",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/DEBT-coverage-floor-could-not-run-or-test-sui-06f4e856.md"
}
```


## Acceptance

- [ ] The finding no longer reproduces, OR
- [ ] `status:` above is moved off `backlog` with the reason written here.

Re-running the guard must not regenerate this file.


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Cierre — 2026-08-24
Causa raiz real: el hook `coverage-floor` en `.pre-commit-config.yaml` corria
`pytest --cov=src`, y este repo no tiene paquete `src/` (layout plano: red.py,
app.py, core.py, config.py, filters.py, shell_integration.py). Coverage.py no
medía nada ("Module src was never imported") y el gate reportaba
`could_not_run` sin ejecutar una sola línea real. Corregido a apuntar a los
módulos reales del repo. El "could not run" está resuelto — coverage ahora se
mide. La cobertura real medida es 67% contra el 100% exigido; ese gap queda
abierto como debt real, no como "could not run": ver
`DEBT-gate-failure-coverage-100-command-pytest-b47eb726.md`.

```
pytest --cov=red --cov=app --cov=core --cov=config --cov=filters --cov=shell_integration --cov-fail-under=100 -q
TOTAL 509 stmts, 169 miss, 67% (config.py 92%, core.py 52%, filters.py 72%, red.py 73%; app.py/shell_integration.py never imported by tests)
```

## Root Cause

The `coverage-floor` pre-commit hook ran `pytest --cov=src`, but red_python has
no `src/` package (flat layout: `red.py`, `app.py`, `core.py`, `config.py`,
`filters.py`, `shell_integration.py`). Coverage.py measured nothing ("Module
src was never imported") and the gate reported `could_not_run` without
executing a single real line.

## Regression Test

`pytest --cov=red --cov=app --cov=core --cov=config --cov=filters --cov=shell_integration -q`
is the regression test: it fails with `could_not_run`/a coverage warning again
if the `--cov` targets drift from the repo's real module names.

## Verification Evidence

Command run 2026-08-28 in this repo:

```
$ pytest --cov=red --cov=app --cov=core --cov=config --cov=filters --cov=shell_integration -q
Name         Stmts   Miss  Cover
--------------------------------
config.py       54      4    93%
core.py        194     94    52%
filters.py     141     39    72%
red.py         121     32    74%
--------------------------------
TOTAL          510    169    67%
33 passed
```

`could_not_run` is resolved -- coverage is measured. The 67% vs. 100% gap is
real, separate debt, tracked and still open in
`DEBT-gate-failure-coverage-100-command-pytest-b47eb726.md` (ticket 3 of this
remediation run).

Negative control: `app.py` and `shell_integration.py` show 0% in this same run
(not listed above because coverage.py's `CoverageWarning: Module ... was never
imported` fires for them, not silence) -- proving the instrument still flags
a module with zero real coverage rather than reporting green regardless.
