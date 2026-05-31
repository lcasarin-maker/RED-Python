# PLAN — CoderCerberus (plan canónico único, modelo de sprints)

**Estado:** master `1562a28`+ · **349 tests verde** · C901 = 0 · 17/17 satélites en v0.3 ·
gate desacoplado (D12 por versión) · Sprint 3.1/3.2/3.3 cerrados (ratchet de circularidad activo).
**Nota:** este archivo es el **plan forward**, no un log. El detalle de lo ejecutado vive en
`git log` + `HISTORIAL.md`. Hallazgos de cobertura: `docs/P5_coverage_ledger.md`.

Consolida dos hilos de trabajo: la **remediación de gate** (Claude, P0–P6) y los **sprints de
refactor** (Gemini, renombrado + simplicity). Unificados aquí en sprints numerados.

---

## ✅ SPRINTS COMPLETADOS (historial breve)

### Sprint 0 — Remediación del gate (Claude)  ✅
Enforcement letra→espíritu y desacople. Commits `f087132`→`35c1c1c`.
- **Gate endurecido:** scripts espectrales (`audit_script_orphans`→D10), dead-code ruff `F`
  (`audit_dead_code`→D6, 21 violaciones purgadas), `assert exc` no-discriminante en
  `pytest.raises` (D9 AST), complejidad C901 visible como DEUDA.
- **Desfragilizado:** `reasoning_lock` ya no se alimenta de corridas de gate/post-commit
  (`--track-lock` opt-in); auto-refresh targeted de `protocol_hash`; test de timing de-flaky.
- **P3 desacople:** D12 valida **adopción de versión** (`VERSION.txt`), no byte-a-byte →
  el core itera libre, eliminado el impuesto de resync de 17 satélites por commit.
- **P4 purga:** `deprecated/` (12 trackeados, 17/17 satélites limpios) + 8 entradas stale del base-set.
- **P6.1:** detección de huérfanos generalizada a todo el árbol (scripts recursivo + cerberus/tools/dashboard).

### Sprint 1 — Renombrado descriptivo + aplanado (Gemini)  ✅
Commits `a3a9e80` + `a2591b3`. `audit_10d.py`→`run_security_audit_12d.py`,
`rigor_maestro.py`→`run_compliance_tests.py`, +otros; aplanado de carpetas; guías a 12D;
golden_standard.yaml unificado. (Dejó refs colgantes a nombres viejos → Sprint 4.3.)

### Sprint 2 — Simplicity Pass / C901<10 (Gemini)  🟡 CERRANDO
Las 16 funciones C901>10 refactorizadas a complejidad <10 con "Zero-Change Contract".
**Estado: STAGED, C901=0, 341/342 tests** (`implementation_plan.md` = su plan).
- Falta: 1 test rojo (REGLA #21 — la sesión de HISTORIAL de Gemini sin `### RETROSPECTIVE`),
  agregar RETROSPECTIVE → 342/342 → commitear los 6 scripts staged.

---

## 🎯 SPRINTS FORWARD

### Sprint 3 — Cobertura real catálogo↔ejecución (era P5)  🔴 CRÍTICO
**Hallazgo central (verificado):** la "cobertura 100%" es teatro. Cobertura real failing-first
≈ **12%** (36/305). El verificador (`test_physical_validation_exists`) solo chequea que el string
del mecanismo exista como `def`/literal — no que discrimine. Es circular (el generador que escribe
el string es uno de los archivos escaneados). Ver `docs/P5_coverage_ledger.md`.

| # | Acción | Validación (failing-first) |
|---|--------|----------------------------|
| 3.1 ✅ | **TK-044/045 fantasma** removidos + guard `test_listed_tokenomics_ids_have_detail_rows` (`c7c392b`) | Failing-first verde |
| 3.2 ✅ | **VC-115/116/117** tests reales (`85e9a3e`): VC-115/116 lockean prevención; VC-117 reveló hueco real → fix `core_utils.write_json_atomic` cableado en los 2 escritores de estado | 3 tests + 346/346 |
| 3.3 ✅ | **Circularidad — flip total vía RATCHET:** medido empíricamente, excluir el generador expone **170 IDs / 8 mecanismos** circulares (no 11), dominado por 2 catch-alls gigantes: `test_behavioral_compliance`←119 VC, `test_d10_tokenomics`←42 TK (+ 6 chicos). Voltear a gate-duro de golpe rompería con 170 fallos → ratchet: baseline congelado `circularity_baseline.json` + `tests/test_catalog_circularity_ratchet.py` exige `circular_actual ⊆ baseline`. **Efecto: todo vicio NUEVO mapeado a fallback rompe el gate (failing-first inmediato).** Probado en ambas direcciones | `current⊆baseline` + 349 verde |
| 3.4 | **Drenar los 170 circulares por lotes** (ratchet baja al remover IDs drenados). Prioridad: los 2 gigantes son catch-alls many-to-one (1 nombre→N vicios = teatro por construcción) → requieren descomponer en tests discriminantes por ID/grupo. Triage por severidad desde el ledger (VT setup/discovery, VC seguridad restantes, TK-P principios sin ejecutor) | Cada lote: vicio a propósito → gate lo bloquea + ID removido del baseline |

### Sprint 4 — Cero código desconectado + higiene de rename (era P6.2/6.3)  🟠
| # | Acción | Validación |
|---|--------|-----------|
| 4.1 | **Dead defs:** funciones/clases definidas pero nunca referenciadas (alcanzabilidad tipo vulture, controlado). Informativo primero, gate después | Def huérfana introducida → detectada; baseline 0 falsos positivos |
| 4.2 | **Satélites:** verificar que no haya código desconectado en `.protocol-core/` ni en código propio del satélite | Sonda en satélite → detectada |
| 4.3 | **Refs colgantes del rename:** `generate_golden_audit.py:138,186` y `.claude/CLAUDE.md` aún citan `audit_10d`/`rigor_maestro` | grep de nombres viejos en código/docs activos = 0 |
| 4.4 | **C901 gate-duro:** ahora que es 0, volver C901>10 compuerta de commit (cierra P1.2 del todo) | Función nueva con complejidad >10 → bloqueada |

---

## 📦 BACKLOG (diferido, bajo beneficio/alto riesgo)
- Split de `golden_standard.yaml` (separar tablas markdown del índice YAML) — frágil, tarea dedicada.
- Consolidar carpetas restantes / `PROTOCOLO_GLOBAL` dirs vacíos en satélites — cosmético.
- `protocol_cli propagate` (azúcar sobre `global_sync_safe --apply`) para el bump de release.
- `unlock` debe limpiar el banner de deadlock en STATUS.md (artefacto stale TK-043).
- Política P2.2: decidir si el auto-refresh de hash debe ampliarse o restringirse.

## Métrica de éxito global
Remediado cuando **un vicio del catálogo introducido a propósito es bloqueado por el gate en
ruta activa** — catálogo = ejecución, sin brecha. Hoy: ~12% real → meta del Sprint 3.

## Secuencia
```
[Sprint 0,1 ✅] → Sprint 2 (cerrar) → Sprint 3 (cobertura real, CRÍTICO) → Sprint 4 (desconexión+higiene)
```
