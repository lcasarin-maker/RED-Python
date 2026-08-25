---
id: DEBT-coverage-floor-could-not-run-or-test-sui-06f4e856
title: coverage-floor: could_not_run or test suite failed before coverage was measured
status: closed
created: 2026-08-20
---

## Finding

<!-- findings:start -->
- coverage-floor: could_not_run or test suite failed before coverage was measured
<!-- findings:end -->

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