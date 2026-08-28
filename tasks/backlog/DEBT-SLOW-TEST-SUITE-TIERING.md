---
id: DEBT-SLOW-TEST-SUITE-TIERING
status: open
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
