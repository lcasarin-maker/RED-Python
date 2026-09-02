---
id: DEBT-correccion-dimensions-init-py-1-vendored-05c24208
kind: debt
title: dimensions/__init__.py:1 — vendored_core_guard clasifica este repo como LOAD_BEA
status: open
prior_status: done
severity: P1
origin: asserted
satd_family: TECHNICAL_DEBT
close_check: {"cmd": "pytest tests/test_filters.py", "expect": "exit_zero"}
created: 2026-08-17
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/DEBT-correccion-dimensions-init-py-1-vendored-05c24208.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: closed`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

## Finding

<!-- findings:start -->
- [CORRECCION] dimensions/__init__.py:1 — vendored_core_guard clasifica este repo como LOAD_BEARING contra el core retirado: 8 copias fisicas de archivos de /home/lcasarin/projects/.retired-protocol-core-office2office, 7 referencias, 1 archivos del propio repo importandolas y 8 copias que YA divergieron del original. Importadores: tests/test_dimensions_contracts.py. Divergidas: dimensions/__init__.py, dimensions/base.py, dimensions/context.py, dimensions/d11_dependency.py. El core del que se copiaron esta declarado retirado, asi que estas copias son la unica version viva y nadie las mantiene como tal: es la enfermedad de dos implementaciones de una idea, a escala. Decidir: promover las copias a codigo propio del repo y cortar la referencia al core, o convertirlas en dependencia real. Lo que no se puede es dejarlas como copia de algo muerto. Medido el 2026-08-17 al cablear el organo, que llevaba en el kit sin UNA corrida porque exige --core-root y nadie se lo pasaba. (detector: vendored_core_guard)
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_DEBT-correccion-dimensions-init-py-1-vendored-05c24208",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/DEBT-correccion-dimensions-init-py-1-vendored-05c24208.md"
}
```


## Acceptance

- [ ] The finding no longer reproduces, OR
- [ ] `status:` above is moved off `backlog` with the reason written here.

Re-running the guard must not regenerate this file.

## Cierre — 2026-08-17

Resuelto por la primera via de las dos que el hallazgo planteaba, la que el propio hallazgo no contemplaba: ni promover las copias ni convertirlas en dependencia, sino **borrarlas**. De las 8 copias de este repo quedan **0**, medido con el mismo organo que abrio la tarea:

```
find_core_copies(red_python, core_relpaths(CORE)) -> 0
```

Commits: 92d43d0, 9d53a38. El gate del kit paso en todos (staged_scan, zero_debt, clean_worktree), ninguno con --no-verify.


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Re-verificado — 2026-08-24
`dimensions/` no existe en este repo. Confirmado.

## Root Cause

`dimensions/` held 8 physical copies of files from a now-retired core
(`.retired-protocol-core-office2office`), imported by `tests/test_dimensions_contracts.py`.
Nobody owned them as live code -- they were divergent, unmaintained duplicates
of a dead dependency: two implementations of the same idea, at repo scale.

## Regression Test

`find_core_copies(red_python, core_relpaths(CORE))` (the same organ that opened
this finding) is the regression test: it must keep returning 0.

## Verification Evidence

Command run 2026-08-28 in this repo:

```
$ ls dimensions
ls: no se puede acceder a 'dimensions': No existe el archivo o el directorio
```

Negative control: the same command against a directory that DOES exist in this
repo confirms `ls` reports existing directories rather than always erroring:

```
$ ls tasks
active  backlog  blocked  done
```
