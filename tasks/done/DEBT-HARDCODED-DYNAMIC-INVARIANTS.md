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
---

# Technical Debt [BUG | CODE_DESIGN_DEBT]: Universal Anti-Hardcoding Invariant & Dynamic Resource Resolution

## I · Issue (Deficiencia Identificada en red_python)
Auditoría de flota detectó 2 puntos de literales y constantes estáticas (*hardcoding*) en red_python:
- **hardcoded_timeout**: 2 ocurrencias

Estos valores producen acoplamiento al entorno de desarrollo, colisiones de red, fallos por timeout bajo carga y posibles desbordamientos de buffers o tokens (Regla canónica GS2-210).

## R · Rule / Mecanismo Implicado
- Regla Canónica: `GS2-210-zero-hardcoded-invariants`
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


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.