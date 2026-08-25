---
id: DEBT-correccion-dimensions-init-py-1-vendored-05c24208
title: dimensions/__init__.py:1 — vendored_core_guard clasifica este repo como LOAD_BEA
status: closed
created: 2026-08-17
---

## Finding

<!-- findings:start -->
- [CORRECCION] dimensions/__init__.py:1 — vendored_core_guard clasifica este repo como LOAD_BEARING contra el core retirado: 8 copias fisicas de archivos de /home/lcasarin/projects/.retired-protocol-core-office2office, 7 referencias, 1 archivos del propio repo importandolas y 8 copias que YA divergieron del original. Importadores: tests/test_dimensions_contracts.py. Divergidas: dimensions/__init__.py, dimensions/base.py, dimensions/context.py, dimensions/d11_dependency.py. El core del que se copiaron esta declarado retirado, asi que estas copias son la unica version viva y nadie las mantiene como tal: es la enfermedad de dos implementaciones de una idea, a escala. Decidir: promover las copias a codigo propio del repo y cortar la referencia al core, o convertirlas en dependencia real. Lo que no se puede es dejarlas como copia de algo muerto. Medido el 2026-08-17 al cablear el organo, que llevaba en el kit sin UNA corrida porque exige --core-root y nadie se lo pasaba. (detector: vendored_core_guard)
<!-- findings:end -->

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