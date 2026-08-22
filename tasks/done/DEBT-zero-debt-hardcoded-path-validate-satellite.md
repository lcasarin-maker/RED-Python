---
id: DEBT-zero-debt-hardcoded-path-validate-satellite
title: zero_debt bloquea deprecated/bootstrap_v0.5/validate_satellite_functional.py — hardcoded_path
status: pagada-2026-08-17
created: 2026-08-17
verification_command: "pytest tests/test_filters.py"
satd_family: TECHNICAL_DEBT
risk_score: 7
blast_radius: LOW
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

## Cierre — 2026-08-17

Resuelta por la tercera vía que la propia tarea contemplaba ("borrar el archivo
entero"), no parcheando el default. La razón para borrar y no corregir es que el
archivo **no puede correr**, medido:

```
$ python3 deprecated/bootstrap_v0.5/validate_satellite_functional.py
Traceback (most recent call last):
  File ".../deprecated/bootstrap_v0.5/validate_satellite_functional.py", line 19, in <module>
    from scripts.core_utils import setup_windows_utf8
ModuleNotFoundError: No module named 'scripts'
rc=1

$ python3 deprecated/bootstrap_v0.5/record_validation_debt_historical.py
    from scripts.satellite_validation_debt import register_validation_debt
ModuleNotFoundError: No module named 'scripts'
rc=1
```

Ni `scripts/core_utils.py` ni `scripts/satellite_validation_debt.py` existen en
este repo. Corregir la ruta `D:\AI\Control_Procesal` habría dejado un script que
sigue muriendo en la línea 19: el `hardcoded_path` era el síntoma que `zero_debt`
sabe ver, no la enfermedad.

`deprecated/` **no** es archivo histórico protegido: `SPEC.md:94` lo define como
*"Archive of deprecated scripts/files. Full content allowed as **temporary
quarantine**"*. Cuarentena temporal, no museo. Los dos archivos estaban *tracked*
por git, así que el borrado es reversible y no aplica la regla de renombrar en
vez de borrar (que protege datos sin rastrear).

Se borró también `record_validation_debt_historical.py`, del mismo directorio y
la misma clase: importa un módulo inexistente y pertenece al protocolo de
satélite. El directorio `deprecated/bootstrap_v0.5/` queda vacío y desaparece.

Arrastre corregido en el mismo commit (documentos que citaban lo borrado):

- `docs/VALIDATION_DEBT_SYSTEM.md` — **borrado**. Declaraba `Status: ACTIVE` y
  describía un sistema cuyos 4 componentes y 2 "Key Files" están ausentes los 6.
  Corregirlo no dejaba documento. La narrativa histórica del caso Control_Procesal
  que contaba sí se conserva, fechada y con capturas, en
  `deprecated/audits_legacy/2026-06-06/results_archive/exterior/Control_Procesal/2026-06-05/`.
- `SPEC.md` — bloque D13 y "Rigor Stack": citaban 8 scripts, **0 existen**.
  Sustituidos por la superficie de enforcement real (`.github/workflows/audit.yml`).

## Acceptance

- [x] `python3 $K/worktree/zero_debt.py --root . --mode zero --gate` devuelve rc=0.

```
$ python3 /home/lcasarin/projects/goodcode/worktree/zero_debt.py --root . --mode zero --gate
[zero-debt] mode: zero  lane: repo-wide
[zero-debt] files scanned: 18  findings: 0  files with findings: 0
[zero-debt] detectors excluded by volume: 0 ()
[zero-debt] could_not_run: 0
[zero-debt] corpus declarado (no juzgado): 0
[zero-debt] violations: 0
rc=0
```


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.