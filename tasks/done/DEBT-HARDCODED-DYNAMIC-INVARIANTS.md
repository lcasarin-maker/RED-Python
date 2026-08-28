---
id: DEBT-HARDCODED-DYNAMIC-INVARIANTS
status: done
severity: P1
risk_score: 9
blast_radius: HIGH
category: debt
satd_family: CODE_DESIGN_DEBT
lifespan: introduced
tag: BUG
verification_command: "pytest"
---

# Technical Debt [BUG | CODE_DESIGN_DEBT]: Universal Anti-Hardcoding Invariant & Dynamic Resource Resolution

## I · Issue (Deficiencia Identificada en red_python)
Auditoría de flota con Simplecode actualizado detectó 2 puntos de literales y constantes estáticas (*hardcoding*) en red_python:
- **hardcoded_timeout**: 2 ocurrencias

Estos valores producen acoplamiento al entorno de desarrollo, colisiones de red, fallos por timeout bajo carga y posibles desbordamientos de buffers o tokens (Reglas canónicas GS2-210 a GS2-214).

## R · Rule / Mecanismo Implicado
- Regla Canónica: `GS2-210-zero-hardcoded-invariants` y `GS2-214-machine-executable-task-contracts`
- Invariante de Diseño: **Regla de Oro de Resolución Dinámica**: *Todo valor dependiente de escala de entrada, hardware, entorno o infraestructura debe resolverse en runtime.*

## A · Application (Muestreo de Evidencias en red_python)
### Ejemplos de hardcoded_timeout:
- `red.py:135:    while not done_event.wait(timeout=5):`
- `tests/test_red_core_behaviour.py:76:    scanner._thread.join(timeout=5)`

## C · Conclusion & Required Resolution
1. Adoptar `simplecode.utils.dynamic_resolution` para:
   - `get_repo_root()` en lugar de rutas absolutas `/home/...`.
   - `get_safe_workers()` en lugar de números fijos de hilos.
   - `get_ephemeral_port()` o `os.getenv` en lugar de puertos hardcodeados.
   - `compute_dynamic_headspace()` para tokens de LLMs.
   - `compute_proportional_timeout()` para llamadas de I/O y subprocess.
2. Refactorizar los 2 puntos detectados hacia resolución dinámica.

```json queue-job
{
  "name": "remediate_hardcoded_invariants_red_python",
  "command": "pytest",
  "artifact": "tasks/backlog/DEBT-HARDCODED-DYNAMIC-INVARIANTS.md"
}
```

## Cierre — 2026-08-24
Los 2 hallazgos no son timeouts de I/O de red o subproceso — son otra cosa,
y `compute_proportional_timeout(payload_size_bytes, ...)` exige un tamaño de
payload que ninguno de los dos tiene de forma natural:

- `red.py:135` — `done_event.wait(timeout=5)` es el intervalo de sondeo de un
  bucle que solo existe para imprimir "... still scanning" mientras un hilo de
  fondo escanea el filesystem; no es un timeout de fallo (el escaneo no se
  aborta ni se trata como error al cumplirse), es la cadencia del heartbeat de
  progreso. Forzar `compute_proportional_timeout` aquí exigiría inventar un
  `payload_size_bytes` (¿cuántos directorios habrá? no se sabe hasta escanear)
  solo para satisfacer la regla — box-ticking, no una mejora real.
- `tests/test_red_core_behaviour.py:76` — `thread.join(timeout=5)` es una red
  de seguridad estándar de test para no colgar la suite si un hilo no
  termina; es el patrón usual en cualquier test de threading en Python, no un
  timeout operacional de producción.

Cerrado con esta justificación en vez de aplicar el utilitario donde no
encaja (YAGNI). Si `red.py:135` necesitara ajustarse alguna vez, la cadencia
del heartbeat es la variable relevante, no el tamaño de un payload.

## Root Cause

The fleet-wide `hardcoded_timeout` detector flagged 2 bare `timeout=5` literals
in this repo as generic hardcoded-invariant debt, matching the pattern without
distinguishing what kind of timeout each one is. Neither is an I/O or
subprocess timeout the `compute_proportional_timeout(payload_size_bytes, ...)`
utility is designed for: one is a progress-heartbeat poll interval with no
natural payload size, the other is a standard test-suite safety net against a
hung thread.

## Regression Test

None added -- applying `compute_proportional_timeout` here would require
fabricating a `payload_size_bytes` neither call site has, which is box-ticking
against the letter of GS2-210, not a real fix (YAGNI). If the heartbeat cadence
or test safety margin ever needs to change, it's a direct edit to the literal,
not a call to the dynamic-resolution utility.

## Verification Evidence

Command run 2026-08-28 in this repo:

```
$ grep -n "timeout=" red.py tests/test_red_core_behaviour.py
red.py:142:    while not done_event.wait(timeout=_SCAN_PROGRESS_POLL_INTERVAL_S):
tests/test_red_core_behaviour.py:77:    scanner._thread.join(timeout=5)
```

`red.py`'s heartbeat interval is now named (`_SCAN_PROGRESS_POLL_INTERVAL_S =
5`, `red.py:30`) instead of a bare literal, making its purpose explicit at the
definition site; it was not routed through `compute_proportional_timeout` for
the reason above. `tests/test_red_core_behaviour.py:77` is an unchanged test
safety net, same reasoning.

Negative control: COULD_NOT_RUN. The `hardcoded_timeout` detector that opened
this finding is not present in the currently vendored
`.simplecode/runtime.zip` (`grep -rli hardcoded_timeout` over its unpacked
contents returns nothing), so it cannot be re-run against a tracked scratch
file to confirm it still fires on a real violation. This closure narrows the
exemption to the two specific heartbeat/test call sites named above by
argument, not by re-running the original instrument -- flagged here rather
than papered over.
