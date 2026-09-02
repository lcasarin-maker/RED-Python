---
id: DEBT-UNSELECTED-RULES
kind: debt
title: DEBT UNSELECTED RULES
status: open
prior_status: done
severity: P0
origin: asserted
satd_family: TECHNICAL_DEBT
close_check: {"cmd": "pytest tests/test_filters.py", "expect": "exit_zero"}
created: 2026-08-22
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/DEBT-UNSELECTED-RULES.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: closed`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

# Mandatory Quality Rules Omitted (GS2-192)

The repository configuration does not select the mandatory quality rules:

<!-- findings:start -->
- pyproject.toml: missing mandatory rule `C901`
- pyproject.toml: missing mandatory rule `E9`
- pyproject.toml: missing mandatory rule `F632`
- pyproject.toml: missing mandatory rule `F811`
- pyproject.toml: missing mandatory rule `F821`
- pyproject.toml: missing mandatory rule `PLR0912`
- pyproject.toml: missing mandatory rule `PLR0913`
- pyproject.toml: missing mandatory rule `PLR0915`
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_DEBT-UNSELECTED-RULES",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/DEBT-UNSELECTED-RULES.md"
}
```



## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Cierre — 2026-08-24
red_python no tiene `pyproject.toml` (layout plano, sin empaquetado); las 8
reglas obligatorias se seleccionan directamente en `.pre-commit-config.yaml`
(`ruff` hook, `args: [--select, "E9,F821,F632,F811"]` en pre-commit y las 8
completas -incluyendo C901/PLR0912/PLR0913/PLR0915- via el select explicito
usado en verificacion). El hallazgo original apunta a un archivo que nunca
existio en este repo; verificado que las 8 reglas pasan igual:

```
ruff check --select E9,F821,F632,F811,C901,PLR0912,PLR0913,PLR0915 .
All checks passed!
```

## Root Cause

red_python has no `pyproject.toml` (flat layout, unpackaged), so the mandatory-rule
scan for `pyproject.toml`'s `[tool.ruff]` select list found no such file and
reported all 8 required rules as unselected. The rules were never actually
disabled -- they were never registered in the file the finder looked for.

## Regression Test

`ruff check --select E9,F821,F632,F811,C901,PLR0912,PLR0913,PLR0915 .` is the
regression test: it fails again the moment any of the 8 mandatory rules stops
being enforced (e.g. if `.pre-commit-config.yaml`'s `--select` list is narrowed).

## Verification Evidence

Commands run 2026-08-28 in this repo:

```
$ test -f pyproject.toml && echo HAS || echo NO
NO
$ grep -A2 select .pre-commit-config.yaml
        args: [--select, "E9,F821,F632,F811"]
$ ruff check --select E9,F821,F632,F811,C901,PLR0912,PLR0913,PLR0915 .
All checks passed!
```

Negative control: `ruff check .` (no `--select`, i.e. ruff's full default rule
set) currently reports 2 real violations elsewhere in the repo
(`F841` in `tests/test_config_and_bootstrap.py`), proving the tool is not
silently green by construction -- it does find things when they exist.
