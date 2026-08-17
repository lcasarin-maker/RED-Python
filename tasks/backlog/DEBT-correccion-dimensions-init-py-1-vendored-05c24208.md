---
id: DEBT-correccion-dimensions-init-py-1-vendored-05c24208
title: dimensions/__init__.py:1 — vendored_core_guard clasifica este repo como LOAD_BEA
status: backlog
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
