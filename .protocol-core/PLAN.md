# PLAN — CoderCerberus (plan canónico único)

**Estado:** master `c86dd43` | gate APPROVED | 17/17 satélites sincronizados | 323 tests
**Nota:** el registro histórico de planes ejecutados (P1–P7, remediación profunda) vive en
`git log` + `HISTORIAL.md`. Este archivo es el **plan forward**, no un log. Tareas
operativas sueltas → `TODO.md`. Tareas con escalación → `cerberus/pending_tasks.json`.

---

## PLAN DE REMEDIACIÓN — post-auditoría adversarial (Fases 0–3, 2026-05-30)

**Principio rector:** atacar **B2 primero** — el enforcement-de-letra es el bloqueador que
*regenera* a todos los demás. Sin cerrarlo, lo que se limpia se re-pudre.

### P0 — Cerrar B2: enforcement letra→espíritu  🔴 [RAÍZ, primero]
| # | Acción | Validación empírica |
|---|--------|---------------------|
| 0.1 | `audit_10d` TK-039: check de `Path.exists()` → "referenciado en hook/cron/CLI activo" | Script espectral de prueba → DEBE fallar |
| 0.2 | D8/D9: detectar `pytest.raises` sin `assert` y aserciones que no discriminan (AST, no regex) | Test "siempre pasa" → DEBE bloquear |
| 0.3 | Meta-test: todo `scripts/*.py` debe estar en ruta activa O en `deprecated/` | Falla si hay huérfanos |

### P1 — Matar VC-118 (residuo de refactor)  🟠
| # | Acción | Validación |
|---|--------|-----------|
| 1.1 | Integrar `vulture`/`pyflakes` como gate (dead code/imports/params) | Import muerto → bloqueado |
| 1.2 | S8 "Simplicity Pass" de prosa → gate post-refactor obligatorio | — |

### P2 — Desfragilizar el gate  🟠
| # | Acción | Validación |
|---|--------|-----------|
| 2.1 | `reasoning_lock`: NO contar fallos-de-gate como `consecutive_failures` | Reintentos de commit no deadlockean |
| 2.2 | Auto-reparar drift legítimo: `sync_binding --update` automático en pre-commit | Commit de doc core sin paso manual |

### P3 — Desacoplar sync  🟠 [B4]
- 3.1 Separar "Núcleo Inmutable" (synced) de estado local (no synced) — ¿SPEC.md debe ir a 17 repos?
- 3.2 Sync incremental/batch en vez de bloquear el commit core con D12 de 17 satélites.

### P4 — Purga estructural restante  🟡 [B6]
- `deprecated/` (154 archivos): sesión dedicada de eliminación formal con aprobación.
- Consolidar 16→~10 carpetas (post-sync; actualizar base-set `audit_10d:327` + refs).
- `golden_standard.yaml` (81KB): separar tablas markdown del índice YAML.
- `PROTOCOLO_GLOBAL` (dirs vacíos) en 9 satélites no-Quenza.

### P5 — Cerrar brecha catálogo↔ejecución  🔴 [B1, continuo]
- Regla nueva: cada vicio del Golden Standard requiere un test que **falle sin su prevención**.
- Auditar cobertura real de los 286 flaws (enforcement vivo vs solo doc).

---

## Secuencia
```
P0 (raíz) → P1 → P2 → [P3 ∥ P4] → P5 (continuo)
```
P0 es no-negociable primero: es el único que impide la re-acumulación de entropía.

## Métrica de éxito global
Remediado cuando **un vicio del catálogo introducido a propósito es bloqueado por el gate
en ruta activa** — es decir, catálogo = ejecución, sin brecha.
