---
id: DEBT-reglas-documentadas-sin-implementacion
title: cinco RULE #N documentadas como aplicadas, y nada las aplica
status: pagada-2026-08-17
created: 2026-08-17
---

## Finding

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
