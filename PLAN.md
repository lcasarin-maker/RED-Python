# PLAN — CoderCerberus (plan canónico único)

**Estado:** master `c86dd43` | gate APPROVED | 17/17 satélites sincronizados | 323 tests
**Nota:** el registro histórico de planes ejecutados (P1–P7, remediación profunda) vive en
`git log` + `HISTORIAL.md`. Este archivo es el **plan forward**, no un log. Tareas
operativas sueltas → `TODO.md`. Tareas con escalación → `cerberus/pending_tasks.json`.

---

## PLAN DE REMEDIACIÓN — post-auditoría adversarial (Fases 0–3, 2026-05-30)

**Principio rector:** atacar **B2 primero** — el enforcement-de-letra es el bloqueador que
*regenera* a todos los demás. Sin cerrarlo, lo que se limpia se re-pudre.

### P0 — Cerrar B2: enforcement letra→espíritu  ✅ HECHO (f087132, 18a366c, eb48f12)
| # | Acción | Validación empírica | Estado |
|---|--------|---------------------|--------|
| 0.1 | `audit_10d` TK-039: añade dirección inversa — script que existe pero nadie referencia = espectral | Sonda espectral → 1 huérfano; repo → 0 | ✅ `audit_script_orphans` |
| 0.2 | D9: `assert exc`/`assert exc.value` tras `pytest.raises` = no discrimina (AST). "raises sin assert" ya estaba enforced | 6/6 casos AST; 0 falsos positivos | ✅ `_check_nondiscriminating_raises_assert` |
| 0.3 | Meta-test: todo `scripts/*.py` en ruta activa O en `deprecated/` | Falla si hay huérfanos; +2 tests regresión | ✅ cableado a veredicto D10 |

> **Nota P2.1 (deuda activa):** el `reasoning_lock` se re-disparó 3× durante P0 al contar
> corridas de verificación/commits `--no-verify` como `consecutive_failures`. Confirma la
> urgencia de P2.1. Workaround actual: `protocol_cli.py unlock`.

### P1 — Matar VC-118 (residuo de refactor)  🟡 (1.1 hecho, 1.2 parcial)
| # | Acción | Validación | Estado |
|---|--------|-----------|--------|
| 1.1 | Gate dead-code vía ruff pyflakes `F` (imports/vars/f-strings muertos) | sonda → bloqueada; repo → 0; +3 tests | ✅ `497d513` (`audit_dead_code`→D6); purgadas 21 violaciones |
| 1.2 | S8 "Simplicity Pass" | Complejidad C901>10 como DEUDA visible (16 funcs) | 🟡 visibilidad ✅; **gate duro = sprint de refactor de 16 funcs, diferido** |

> Hallazgo (gobernanza de salida): `protocol_cli.py unlock` resetea `.agent_state.json` pero
> NO limpia el banner de deadlock en STATUS.md → artefacto stale (TK-043). Pendiente: que
> `unlock` también lo limpie.

### P2 — Desfragilizar el gate  🟠
| # | Acción | Validación | Estado |
|---|--------|-----------|--------|
| 2.1 | `reasoning_lock`: NO contar fallos-de-gate como `consecutive_failures` | Centinela CF=99 + rigor sin flag → no muta | ✅ `ce1f3c7` (`--track-lock` opt-in) |
| 2.2 | Auto-reparar drift legítimo: `sync_binding --update` automático en pre-commit | protocolo staged → refresca; sin protocolo → no toca; +3 tests | ✅ `command_check._auto_refresh_protocol_hash` — targeted: solo si el commit incluye archivo de protocolo (drift externo sigue detectable) |

> Bonus P2: `test_setup_validate_py_is_fast` era flaky (medición única en el borde 1s) → best-of-3 <2s.

### P3 — Desacoplar sync  ✅ HECHO (16f1a7b) [B4]
Modelo elegido: **releases versionados**. D12 ya NO compara byte-a-byte; verifica que cada
satélite esté en la versión de protocolo del core (`VERSION.txt`). Micro-ediciones dentro de
una versión no disparan drift → el core itera libre. Propagación por release (bump VERSION.txt
+ sync deliberado). **Probado:** commit de `audit_10d.py` (synced) pasó el gate completo SIN
`--no-verify` ni resync — el impuesto de la sesión (−17 resyncs/commit) eliminado.
- Pendiente menor: comando `protocol_cli propagate` (azúcar sobre `global_sync_safe --apply`) para el bump de release.

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
