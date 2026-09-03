---
id: CANON-ADOPT
kind: debt
title: Adopcion incompleta de la estructura canonica de la flota (DGX-424)
status: open
severity: P2
origin: detected
satd_family: CONFIG_DEBT
close_check: {"cmd": "python gates/canon_adoption.py", "expect": "exit_zero"}
created: 2026-09-01
scope: fleet
detector: {"rule": "canon_adoption/criterios_incompletos", "confidence": 1.0}
---

## Context

Medido por `gates/canon_adoption.py`, que es el mismo comando que cierra esta ficha:
**este repo cumple 8 de 11 criterios**.

Esta ficha la GENERA el migrador, no una mano. Si se borra, `python tools/apply_canon.py
--repo <ruta> --apply` la vuelve a escribir con la medicion del momento.

## Lo que falta en este repo, y por que importa cada cosa

- **spec_tipado** - `SPEC.md` sigue el esqueleto viejo, sin front-matter tipado (`spec_version: 2`). Mientras siga en prosa, ningun gate puede leer que ES este repo.
- **spec_requisitos** - `SPEC.md` no tiene requisitos EARS con su `verify:`. Un requisito sin comando es prosa.
- **tasks_retirado** - `tasks/` sigue vivo junto a `ledger/`. **Es deliberado**: Luis voto que el kit va primero, porque retirarlo deja tres gates del pre-push sin sujeto.

## Acceptance

`python gates/canon_adoption.py` sale 0. No hay criterio parcial: el gate imprime todos con su
OK o su NO y sale 1 mientras quede uno.

## Diseno completo

`Atlas/docs/agent_findings/2026-09-01_estructura_canonica_de_la_flota_diseno.md` y el contrato
para el kit en `Atlas/docs/LEDGER_CONTRACT.md`.
