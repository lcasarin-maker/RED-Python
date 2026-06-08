# Control_Procesal Validation Recheck

**Fecha:** 2026-06-06  
**Scope:** validar los resultados recientes de la auditoria continuada por Claude sobre `Control_Procesal`

## What Was Rechecked

1. `CONTRATO_INFERIDO.md` y `README.md` afirman que la Fase 3 esta completada y que las claims
   fueron validadas con pruebas ejecutables.
2. `tests/test_parity.py` fue agregado para verificar paridad entre HTML, servidor y storage.
3. `scripts/servidor_pdf.py` fue extendido para servir `ControlProcesal_POE_v14.html`,
   `scripts/app.js` y `data_aequitas.json` como recursos estaticos.
4. `ControlProcesal_POE_v14.html` ya no carga `scripts/app.js` y ahora inicializa con
   `inicializarControlProcesal()` esperando al servidor antes de cargar datos.

## Empirical Results

### Static parity suite

Command:

```powershell
python -m pytest -q tests\test_parity.py
```

Result:

```text
9 passed in 0.05s
```

Interpretation:

- The parity checks are consistent with the current source tree.
- They are mostly static source inspection, so they do not prove end-to-end browser behavior by
  themselves.

### Full test suite

Command:

```powershell
python -m pytest -q
```

Result:

```text
1 failed, 14 passed in 59.87s
FAILED tests/test_expedientes_perf.py::test_expedientes_endpoint_speed - TimeoutError
```

Interpretation:

- The repository is not fully green at the moment of recheck.
- The claimed "all validated" / "FASE 3 completada" status is too strong if read literally against
  the current suite, because `/expedientes` still has a failing performance test.

## Line-Level Evidence

- Bootstrap now waits for the server before loading data: `ControlProcesal_POE_v14.html:4748-4766`.
- Static resource serving was added in the backend: `scripts/servidor_pdf.py:244-308`.
- The performance test still enforces a `<500ms` target on `/expedientes`: `tests/test_expedientes_perf.py:21-50`.

## Validation Verdict

**Partially validated.**

- Verified: the bootstrap race from Fase 2 is fixed, and the static parity checks pass.
- Not fully verified: the full executable suite is not green because `/expedientes` still fails the
  dedicated performance test in the current checkout.

## Recommended Audit Language

Use:

- "Static parity checks pass."
- "The bootstrap race is fixed."
- "The full suite still has one failing performance test on `/expedientes`."

Avoid:

- "All claims validated."
- "FASE 3 completed" unless the failing performance test is resolved or explicitly excluded.

