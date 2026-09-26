---
id: CANON-ADOPT
kind: debt
title: Adopcion incompleta de la estructura canonica de la flota (DGX-424)
status: done
severity: P2
origin: detected
satd_family: CONFIG_DEBT
close_check: {"cmd": "python .simplecode/run.py simplecode.verification.canon_adoption --root .", "expect": "exit_zero"}
created: 2026-09-01
closed_at: 2026-09-26
evidence:
  pass: tasks/evidence/CANON-ADOPT.pass.txt
  fail: tasks/evidence/CANON-ADOPT.fail.txt
  e2e: tasks/evidence/CANON-ADOPT.e2e.txt
scope: fleet
detector: {"rule": "canon_adoption/criterios_incompletos", "confidence": 1.0}
---

## Context

Medido por `gates/canon_adoption.py`, que es el mismo comando que cierra esta ficha:
**este repo cumple 9 de 11 criterios**.

Esta ficha la GENERA el migrador, no una mano. Si se borra, `python tools/apply_canon.py
--repo <ruta> --apply` la vuelve a escribir con la medicion del momento.

## Lo que falta en este repo, y por que importa cada cosa

- **spec_requisitos** - `SPEC.md` no tiene requisitos EARS con su `verify:`. Un requisito sin comando es prosa.
- **tasks_retirado** - `tasks/` sigue vivo junto a `ledger/`. **Es deliberado**: Luis voto que el kit va primero, porque retirarlo deja tres gates del pre-push sin sujeto.


## Nota post-cierre (2026-09-26)

La medicion de esta ficha (9 de 11) quedo vieja: hoy el kit mide 15 criterios y este repo cumple los 15 (`adopcion del canon en red_python: 15/15 criterios`). `gates/canon_adoption.py` ya no existe; el comando que cierra la ficha es el modulo del kit, que es el que `backlog-verifier` acepta (forma de modulo, no de ruta de script).

## Acceptance

`python .simplecode/run.py simplecode.verification.canon_adoption --root .` sale 0. No hay criterio parcial: el gate imprime todos con su
OK o su NO y sale 1 mientras quede uno.

## Diseno completo

`Atlas/docs/agent_findings/2026-09-01_estructura_canonica_de_la_flota_diseno.md` y el contrato
para el kit en `Atlas/docs/LEDGER_CONTRACT.md`.

## Root Cause

La ficha la generaba el migrador con la medicion del momento (9 de 11 criterios: faltaban requisitos EARS con `verify:` en `SPEC.md` y `tasks/` seguia vivo junto a `ledger/`). El kit despues fijo `tasks/` como casa unica y agrego criterios; el repo los fue cumpliendo y nadie volvio a correr la medicion ni cerro la ficha.

## Regression Test

`python .simplecode/run.py simplecode.verification.canon_adoption --root .` sale 0 solo si cumple TODOS los criterios. El hook de pre-commit `adopcion del canon (DGX-424) sin regresion` lo corre en cada commit.

## Verification Evidence

Los tres artefactos del front-matter: `.pass.txt` (15/15), `.fail.txt` (control negativo: `SPEC.md` con `spec_version: 1` hace fallar `spec_tipado`, archivo restaurado), `.e2e.txt` (el comando sobre el arbol restaurado).
