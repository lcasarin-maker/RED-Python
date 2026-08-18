---
id: DEBT-reglas-documentadas-sin-implementacion
title: cinco RULE #N documentadas como aplicadas, y nada las aplica
status: backlog
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

- [ ] `dangling_refs --repo .` devuelve 0 hallazgos de `rule_drift`.
