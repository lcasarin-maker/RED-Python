---
id: DEBT-zero-debt-hardcoded-path-validate-satellite
title: zero_debt bloquea deprecated/bootstrap_v0.5/validate_satellite_functional.py — hardcoded_path
status: backlog
created: 2026-08-17
---

## Finding

Hallado midiendo el baseline de los 5 órganos antes de tocar nada de RULE
#21/#22, no como parte de ese trabajo — no está en el `dangling_refs` que
motivó la sesión, es un organo distinto.

```
$ python3 $K/worktree/zero_debt.py --root . --mode zero --gate
[zero-debt] files scanned: 18  findings: 1  files with findings: 1
[zero-debt] violations: 1
  - deprecated/bootstrap_v0.5/validate_satellite_functional.py (1 findings)
BLOCKED [zero-debt] - policy is zero debt, with no grandfathering.
rc=1
```

Detector puntual (confirmado corriendo cada `PATTERN_DETECTORS` /
`AGENT_THREAT_DETECTORS` de goodcode contra el archivo):

```
HIT: hardcoded_path
```

Causa: `satellite_path: str = "D:\\AI\\Control_Procesal"` aparece dos veces
(líneas 47 y 163) como valor por defecto — una ruta Windows absoluta de otra
máquina, del mismo linaje vendorizado de Cerberus que esta sesión estuvo
purgando (`deprecated/bootstrap_v0.5/` es justo la carpeta que las
correcciones `9d53a38` y `6737bd0` del mismo día vaciaron parcialmente).

No es deuda nueva introducida por esta sesión: el archivo no se tocó. Es
deuda preexistente que nunca se había registrado — `zero_debt` con
`--mode zero` no perdona por fecha, y el archivo, aunque vive en
`deprecated/`, sigue *tracked* por git y por eso cuenta.

## Por qué no se arregló en el momento

Fuera del alcance de la tarea asignada (RULE #21/#22 y los cinco órganos
específicos que esa tarea nombra). Registrarlo aquí en vez de tocar código
fuera de ese alcance sin pedirlo.

## Qué haría falta

Reemplazar el default hardcodeado `"D:\\AI\\Control_Procesal"` en las dos
líneas (47, 163) por un parámetro sin valor por defecto, una variable de
entorno, o borrar el archivo entero si — como el resto de
`deprecated/bootstrap_v0.5/`, `dimensions/`, y el perfil de satélite ya
borrados esta misma sesión — es cruft de Cerberus que ya no aplica aquí.

## Acceptance

- [ ] `python3 $K/worktree/zero_debt.py --root . --mode zero --gate` devuelve
      `rc=0` (0 violations).
