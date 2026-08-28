---
id: DEBT-SLOW-TEST-SUITE-TIERING
status: closed
severity: P1
risk_score: 8
blast_radius: MEDIUM
category: debt
satd_family: TEST_DEBT
lifespan: introduced
tag: TEST
verification_command: "pytest -m 'not slow' --max-seconds 2.0"
---

# Technical Debt [TEST | TEST_DEBT]: Test Suite Latency & Missing Tiered Architecture (GS2-210)

## I · Issue (Deficiencia Identificada en red_python)
La suite de pruebas actual de `red_python` tarda **0.71s** en ejecutarse (excediendo el techo canónico de **2.0s** de `test_timer_guard`):
- **Duración Medida**: `0.71s` (Límite: `2.00s`).
- **Estado de Salida**: `rc=2` (`8 errors in 0.09s`).

Pruebas más lentas identificadas:
- Suite excedió el tiempo límite global de 2.0s.

## R · Rule / Mecanismo Implicado
- Regla Canónica: `GS2-210-zero-hardcoded-invariants` y `test_timer_guard`
- Invariante de Arquitectura: **Axioma de la Pirámide de Pruebas**: *El carril unitario de pre-commit debe ser $\le 2.0$s y 100% determinista en memoria. Pruebas de integración, GPU, red o I/O pesado deben marcarse con `@pytest.mark.slow` / `@pytest.mark.integration` y excluirse del pre-commit rápido.*

## A · Application (Remediación Requerida)
1. **Marcar Tests Pesados**: Decorar tests de integración con `@pytest.mark.slow` o `@pytest.mark.integration`.
2. **Configurar pyproject.toml / pytest.ini**:
   ```toml
   [tool.pytest.ini_options]
   markers = [
       "slow: tests that take > 0.2s or require external I/O",
       "integration: multi-component integration tests",
   ]
   addopts = "-m 'not slow and not integration'"
   ```
3. **Reducir Duración Unitario a $\le 2.0$s**: Asegurar que la suite por defecto corra en < 2.0 segundos.

```json queue-job
{
  "name": "tier_test_suite_red_python",
  "command": "pytest -m 'not slow'",
  "artifact": "tasks/backlog/DEBT-SLOW-TEST-SUITE-TIERING.md"
}
```

## Cierre — 2026-08-24
Ya implementado: `pytest.ini` ya tiene los markers `unit/integration/slow/e2e`
y `addopts = -m "not slow and not e2e"`. La suite real corre en 0.04-0.09s,
muy por debajo del techo de 2.0s. El `verification_command` del propio hallazgo
(`pytest -m 'not slow' --max-seconds 2.0`) usa una bandera que no existe en esta
instalación de pytest (`--max-seconds` no es un flag real ni de pytest ni de un
plugin instalado) — el "rc=2 / 8 errors" original era ese flag inválido
reventando la invocación, no la suite siendo lenta. Verificado con la
invocación real:

```
pytest -m 'not slow' -q  ->  33 passed in 0.05s
```

## Root Cause

The "Cierre — 2026-08-24" note above was itself the fraud: it diagnosed the
`--max-seconds` flag as bogus and stopped there, closing the ticket by
arguing the *instrument* was broken instead of making the finding's own
`verification_command` actually pass. `git log --all --oneline -- tasks/backlog/DEBT-SLOW-TEST-SUITE-TIERING.md`
shows the fraud-audit reverting that close in commit `d9fc277` ("fraud-audit
pass found DEBT-SLOW-TEST-SUITE-TIERING closed without its finding actually
resolving, reverting it to tasks/backlog/").

The diagnosis was correct (`--max-seconds` was not implemented anywhere in
this repo or any installed pytest plugin — confirmed again with
`grep -rn "max_seconds\|max-seconds" tests/ pytest.ini`, zero hits before
this fix) but "the flag doesn't exist" is not the same as "the finding is
resolved." The ticket's own verification_command names a real requirement
(GS2-210's test-pyramid axiom: the fast unit lane must stay ≤ 2.0s,
enforced, not just documented in prose) and nothing in the repo enforced it.

## Regression Test

`tests/conftest.py` now registers `--max-seconds` as a real pytest option
(`pytest_addoption`) and enforces it in `pytest_sessionfinish` by comparing
measured wall-clock session duration against the ceiling, failing the run
(`session.exitstatus = 1`) if exceeded. This is the negative control the
gain rule requires: the flag can now actually fail the build, not just be
silently ignored.

Negative control (the check CAN produce the "too slow" verdict):

```
$ pytest -m 'not slow' --max-seconds 0.001
...
FAILED: test session took 0.05s, exceeding --max-seconds=0.00s ceiling.
$ echo $?
1
```

Positive control (real suite, real ceiling):

```
$ pytest -m 'not slow' --max-seconds 2.0
...
33 passed in 0.05s
$ echo $?
0
```

## Verification Evidence

Ticket's own `verification_command`, run for real, exit code captured
explicitly (not read from a pipe):

```
$ pytest -m 'not slow' --max-seconds 2.0 -q; echo "EXIT:$?"
.................................                                        [100%]
33 passed in 0.05s
EXIT:0
```
