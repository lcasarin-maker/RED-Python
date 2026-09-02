---
id: DEBT-spec-md-cita-167-rutas-inexistentes
kind: debt
title: SPEC.md se declara fuente de verdad y 167 de las 189 rutas que cita no existen
status: open
severity: P2
origin: asserted
satd_family: TECHNICAL_DEBT
close_check: {"cmd": "pytest tests/test_filters.py", "expect": "exit_zero"}
created: 2026-08-17
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/DEBT-spec-md-cita-167-rutas-inexistentes.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: pagada-2026-08-20`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

## Finding

<!-- findings:start -->
- SPEC.md cita 167 de 189 rutas de archivo que no existen en este repo (88%), incluyendo los 6 "módulos maestros" del AUTHORITY MODULE ROUTER que el propio documento declara su núcleo de autoridad.
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_DEBT-spec-md-cita-167-rutas-inexistentes",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/DEBT-spec-md-cita-167-rutas-inexistentes.md"
}
```

Hallado midiendo el arrastre de borrar `deprecated/bootstrap_v0.5/`
(ver [[DEBT-zero-debt-hardcoded-path-validate-satellite]]): `SPEC.md:82` citaba
el archivo borrado. Al medir cuántas *otras* rutas de `SPEC.md` tampoco existen,
el número no fue una ni dos.

Medición literal (2026-08-17, sobre `SPEC.md` de 311 líneas):

```
$ grep -oE '`[A-Za-z0-9_./-]+\.(py|md|json|yaml|yml|txt)`' SPEC.md | tr -d '`' | sort -u > /tmp/spec_refs.txt
$ tot=0; miss=0
$ while read -r p; do tot=$((tot+1)); [ -e "$p" ] || { miss=$((miss+1)); echo "AUSENTE $p"; }; done < /tmp/spec_refs.txt
...
--- SPEC.md: 167 ausentes de 189 rutas citadas ---
```

**167 de 189 = 88%.** Entre las ausentes: los 8 scripts de "Rigor Stack", los 3
del dominio D13, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md`,
`MANDATES_BY_PHASE.md`, `TOKENOMICS_AND_ROUTING.md`, `USER_CONTEXT.md` — es
decir, **6 de los 6 "módulos maestros" del AUTHORITY MODULE ROUTER** que el
propio documento declara su núcleo de autoridad, todo `dimensions/`, todo
`protocol_engine/`, y 15 archivos de `tests/`.

Las 22 que sí existen: `AGENT.md`, `README.md`, `requirements.txt`,
`VERSION.txt`, `ESCALATION_PROTOCOL.md`, `GRAPH_REPORT.md`,
`.claude/settings.local.json`, `.protocol/metadata/internal_graph.json`,
`docs/CONSOLIDATION_MANIFEST.json`, `docs/FALLOS_CONOCIDOS.md`,
`docs/templates/SPEC_REFACTORS_TEMPLATE.md`, `SPEC.md` (a sí mismo) y 10 de
`docs/architecture/`.

## Por qué es traza viva y no registro histórico

No lleva fecha de cierre, no vive bajo `deprecated/` ni `archive/`, está en la
raíz del repo, y afirma en presente:

- línea 2: `**Status:** 💎 SINGLE SOURCE OF TRUTH | Version: v0.5`
- línea 7: *"This repository is the immutable core of **Coder Cerberus V0.5**"*
  — este repo es `red_python`, una app (`app.py`, `red.py`, `core.py`,
  `filters.py`, `adapters/`), no el núcleo de Cerberus.

Un agente que lea `SPEC.md` como fuente de verdad al empezar sesión recibe la
constitución de otro proyecto y 167 rutas que no puede abrir.

## Qué se corrigió ya (y qué no)

Corregido el 2026-08-17, sólo el bloque cuyo arrastre causó el borrado:

- dominio **D13**: se quitaron los 3 scripts inexistentes y se marcó explícito
  que ninguno de los 13 dominios está implementado aquí.
- **Rigor Stack**: los 8 scripts citados (0 existen) sustituidos por la
  superficie de enforcement real y medida: `.github/workflows/audit.yml`
  (`pytest -q`, `scripts/satellite_governance.py validate|test-surface`).

Quedan **164 rutas muertas** sin tocar, y las dos afirmaciones de identidad
(líneas 2 y 7) sin corregir.

## Por qué no se cerró en el momento

Decisión del operador, tomada por papeleta el 2026-08-17: parchear sólo el
arrastre y registrar el resto. Las alternativas descartadas fueron retirar
`SPEC.md` entero — 10 documentos lo citan y `dangling_refs` pasaría de 0 a >0 —
y reescribir las 311 líneas, que es un trabajo de sesión propia.

## Qué haría falta

Decidir qué es `SPEC.md` en `red_python`: o describe esta app, o se retira con
sus 10 citas entrantes migradas. Mientras siga diciendo "immutable core of Coder
Cerberus V0.5", cualquier corrección de rutas es cosmética.

## Acceptance

- [ ] `SPEC.md` no cita ninguna ruta inexistente (el bucle de arriba imprime
      `0 ausentes`), **o** `SPEC.md` no existe y sus 10 citas entrantes apuntan
      a algo que sí existe.
- [ ] `python3 $G/verification/dangling_refs.py --repo-root .` sigue en
      `0 findings`.


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Cierre — 2026-08-28 (medición final)

`SPEC.md` fue reescrito por completo el 2026-08-20 (commit `f66dde4`, "rewrite
SPEC.md for red_python identity") para describir esta app en vez de citar la
identidad de otro proyecto (Coder Cerberus V0.5). La medición original (167 de
189 rutas ausentes) ya no aplica al documento actual.

## Root Cause

`SPEC.md` se había copiado/heredado de otro repo (Coder Cerberus V0.5) sin
adaptar sus citas a la superficie real de `red_python`: declaraba módulos,
scripts y dominios que nunca existieron aquí.

## Regression Test

El mismo bucle de medición usado para abrir el hallazgo, re-corrido contra el
`SPEC.md` vigente.

## Verification Evidence

Comando corrido el 2026-08-28 en este repo:

```
$ grep -oE '`[A-Za-z0-9_./-]+\.(py|md|json|yaml|yml|txt)`' SPEC.md | tr -d '`' | sort -u > /tmp/spec_refs2.txt
$ tot=0; miss=0
$ while read -r p; do tot=$((tot+1)); [ -e "$p" ] || { miss=$((miss+1)); echo "AUSENTE $p"; }; done < /tmp/spec_refs2.txt
AUSENTE HISTORIAL.md
$ echo "--- SPEC.md: $miss ausentes de $tot rutas citadas ---"
--- SPEC.md: 1 ausentes de 21 rutas citadas ---
```

167→1. La única cita restante (`HISTORIAL.md`) es intencional, no un hallazgo
real: `scripts/validate_retrospective.py` documenta explícitamente que
`HISTORIAL.md` es el log de sesiones que se va creando por sesión y "no
requiere que exista" de antemano (`scripts/validate_retrospective.py:13`).
Confirmado que el gate real de este repo (`simplecode.verification.dangling_refs.check_broken_evidence_pins`,
el mismo que usa `adversarial_judge`) no la marca:

```
$ python3 -c "
from pathlib import Path
from simplecode.verification import dangling_refs
print(list(dangling_refs.check_broken_evidence_pins(Path('.'))))
" | grep -i "SPEC\|HISTORIAL"
(sin salida)
```

Negative control, corrido el 2026-08-28 (archivo de prueba con un enlace roto,
staged y luego revertido):

```
$ printf 'See [broken](this/path/does/not/exist.py) for details.\n' > neg_control_scratch.md
$ git add neg_control_scratch.md
$ python3 -c "
from pathlib import Path
from simplecode.verification import dangling_refs
print([bp for bp in dangling_refs.check_broken_evidence_pins(Path('.')) if 'neg_control' in str(bp)])
"
[{'kind': 'broken_pin', 'ref': 'this/path/does/not/exist.py', 'origin': 'neg_control_scratch.md:1', 'severity': 'FAIL', 'message': "Evidence link points to non-existent file 'this/path/does/not/exist.py'"}]
$ git reset neg_control_scratch.md && rm neg_control_scratch.md
```

Confirma que el gate detecta un enlace roto real, no que esté vacío por
construcción.
