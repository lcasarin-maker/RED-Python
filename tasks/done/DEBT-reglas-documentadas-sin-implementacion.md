---
id: DEBT-reglas-documentadas-sin-implementacion
title: cinco RULE #N documentadas como aplicadas, y nada las aplica
status: pagada-2026-08-17
created: 2026-08-17
verification_command: "pytest tests/test_filters.py"
satd_family: TECHNICAL_DEBT
risk_score: 7
blast_radius: LOW
severity: P2
category: debt
lifespan: introduced
tag: BUG
---

## Finding

<!-- findings:start -->
- rule_drift: RULE #15 -- documented as enforced but no implementation found
- rule_drift: RULE #21 -- documented as enforced but no implementation found
- rule_drift: RULE #22 -- documented as enforced but no implementation found
- rule_drift: RULE #24 -- documented as enforced but no implementation found
- rule_drift: RULE #30 -- documented as enforced but no implementation found
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_DEBT-reglas-documentadas-sin-implementacion",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/DEBT-reglas-documentadas-sin-implementacion.md"
}
```

`dangling_refs` (goodcode) reporta 5 FAIL en este repo:

```
[FAIL] (rule_drift) RULE #15 -- documented as enforced but no implementation found
[FAIL] (rule_drift) RULE #21 -- idem
[FAIL] (rule_drift) RULE #22 -- idem
[FAIL] (rule_drift) RULE #24 -- idem
[FAIL] (rule_drift) RULE #30 -- idem
```

Son reglas de la doctrina Cerberus, que se exorcizó de este repo el 2026-08-17.
`SPEC.md:152` además cita `scripts/validate_security_tier.py` como el
implementador de la #24, y ese archivo **no existe aquí** — era de cuenza y se
borró el mismo día.

Un documento que declara una regla *enforced* cuando nada la aplica es la misma
mentira que un inventario que nombra archivos borrados: afirma algo falso sobre
el presente.

## Por qué bloquea algo concreto

Es el **único hallazgo de flota** que impide cablear `dangling_refs` como gate
vivo: medido el 2026-08-17, bloquearía 1 de 11 repos, y ese uno es éste.

## Qué haría falta

Por cada una de las cinco: o se implementa, o se borra la afirmación de que está
aplicada. Lo que no vale es dejarla dicha.

## Acceptance

- [x] `dangling_refs --repo .` devuelve 0 hallazgos de `rule_drift`.

## Cierre — 2026-08-17

Cada una resuelta por lo que **el propio documento decía**, no por conveniencia:

| regla | qué pasaba | resolución |
|---|---|---|
| #30 | su doc declara «enforcement tier 1 — **prose-enforced**» | `[PROSE-ONLY]`: se le puso el marcador que el detector entiende, en vez de dejar la contradicción |
| #21, #22 | su doc declaraba «tier 3 — **test-enforced**» y **no existe ese test** — `grep -rl 'RULE #21\|retrospectiv' tests/` no devuelve nada | `[PROSE-ONLY]`, y la corrección escrita en el documento |
| #24 | `SPEC.md:152` citaba `scripts/validate_security_tier.py`, que **no existe aquí** — era de cuenza | `[PROSE-ONLY]` y cita muerta fuera |
| #15 | su mención vive en `FASE_8_FINDINGS.md`, un informe que dice que la regla **NO se cumple** | `[FUTURE]`: leerlo como «documentada y aplicada» era al revés de lo que dice |
| #28 | **apareció al arreglar las otras cinco**: citaba `scripts/validate_routing.py`, que tampoco existe | `[PROSE-ONLY]` |

Ninguna se marcó exenta para que el gate pasara: en las cinco primeras el
marcador refleja lo que el documento ya afirmaba de sí mismo, y la #21 llevaba
una afirmación **falsa** que se corrigió, no se ocultó.

```
[dangling_refs] 0 findings -- no unresolved references found
```

Con esto `dangling_refs` pasa a **0/11** en la flota y puede cablearse como gate
vivo.

## Corrección — 2026-08-17 (mismo día, pase posterior)

El cierre de arriba trató `#21` y `#22` como el mismo caso ("misma doc, mismo
caso") y a ambas las dejó en `[PROSE-ONLY]`. Investigado más a fondo, no son
la misma regla — `docs/architecture/AGENT_ONBOARDING_RULES.md` cataloga
`#21 Post-session retrospective` y `#22 Sources of Truth Index (SPEC vs
POLICY)` como dos entradas distintas — y sólo una de las dos era testeable:

| regla | qué es | resolución final |
|---|---|---|
| #21 | Retrospectiva de 5 preguntas en JSON al cierre de sesión | **`[TEST-ENFORCED]`**: `scripts/validate_retrospective.py` (esquema) + `tests/test_regla_21_retrospective.py` (15 tests, batería RED que rompe el validador a propósito y prueba que 5 tests fallan contra la versión saboteada) |
| #22 | Índice de Sources of Truth (`SOURCES_OF_TRUTH.md`, tabla SPEC/POLICY) | **retirada** (no `[PROSE-ONLY]` de verdad): su sujeto se borró el mismo 2026-08-17 (commit `1b2ede2`) como doctrina Cerberus vendorizada. Escribir un test la resucitaría el mismo día que otro commit la borró por sobrar. Queda marcada `[PROSE-ONLY]` sólo porque el detector no tiene marcador para "retirada" — el argumento vive en `docs/architecture/N5_REGLA_21_POST_SESSION_RETROSPECTIVE.md` |

```
$ python3 -m pytest tests/test_regla_21_retrospective.py -q
15 passed in 0.03s

# saboteado (validate_retrospective_schema forzado a devolver [] siempre):
$ python3 -m pytest tests/test_regla_21_retrospective.py -q
5 failed, 10 passed in 0.07s

[dangling_refs] 0 findings -- no unresolved references found   (rc=0, sin cambios)
```


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Root Cause

Five documented `RULE #N` entries claimed to be enforced (test-enforced or
prose-enforced) when nothing in the repo actually applied them -- in one case
(#24) the doc cited an implementer file (`scripts/validate_security_tier.py`)
that never existed here. A sixth (#28) surfaced while fixing the first five.
Each was a documentation claim about the present that was false.

## Regression Test

`tests/test_regla_21_retrospective.py` (15 tests) is the regression test for
#21, including a RED battery that sabotages `validate_retrospective_schema` to
prove 5 of the 15 fail against a broken validator (not just that they pass).
The other rules (#15, #22, #24, #28, #30) were retired or marked
`[PROSE-ONLY]` in their source docs rather than test-enforced, since their
subjects were retired doctrine, not live code.

## Verification Evidence

Commands run 2026-08-28 in this repo:

```
$ test -f tests/test_regla_21_retrospective.py && echo EXISTS
EXISTS
$ pytest tests/test_regla_21_retrospective.py -q
15 passed in 0.04s
```

Negative control, re-run 2026-08-28 (sabotage `validate_retrospective_schema`
to always `return []`, then restore it):

```
$ pytest tests/test_regla_21_retrospective.py -q
FAILED tests/test_regla_21_retrospective.py::test_missing_answer_key_is_caught
FAILED tests/test_regla_21_retrospective.py::test_missing_all_five_questions_reports_all_five
FAILED tests/test_regla_21_retrospective.py::test_q5_wrong_shape_is_caught
FAILED tests/test_regla_21_retrospective.py::test_q5_wrong_field_types_are_caught
FAILED tests/test_regla_21_retrospective.py::test_empty_q2_violation_is_caught
5 failed, 10 passed in 0.08s
$ # restored scripts/validate_retrospective.py
$ pytest tests/test_regla_21_retrospective.py -q
15 passed in 0.04s
```