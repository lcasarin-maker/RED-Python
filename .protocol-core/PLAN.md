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

---

# 🛡️ CAMPAÑA DE AUDITORÍA — SPRINTS 5+  (plan 2026-05-31, Sprints 0-4 ✅ cerrados)

> 8 instrucciones del usuario. Respuestas directas primero, luego sprints ejecutables.

## Respuestas directas
- **Q-A "¿en qué sprint se valida código desconectado?"** → **Sprint 4.1 ✅** (`tests/test_dead_defs.py`,
  gate de dead defs + removió 2 huérfanas). PERO tu regla *"warning/hallazgo no bloqueado = error"*
  va más allá → la captura **Sprint 5**: todo WARN/insight no-bloqueante se convierte a BLOCK o se corrige.
- **Q-C "¿algo que agregar a Golden Standard?"** → Sí. Aprendizajes de Sprints 3-4 aún no codificados
  como regla: ratchet de circularidad, honestidad DOC_ONLY, anti-cobertura many-to-one (1 test→N vicios),
  y tu propia regla de *batch-authorization* (Q-B). Mecanismo de ingestión de aprendizajes satélite. → **Sprint 9**.
- **Q-B (meta-regla)**: "analiza el plan completo y pide todas las autorizaciones de una vez" → la **aplico ahora**
  (AskUserQuestion batched al final de este turno) y la **codifico** como mandato en Sprint 9.

## Sprints
| # | Sprint | Item | Entregable / failing-first |
|---|--------|------|----------------------------|
| **5** | **Cero warnings tolerados** | A | Inventario de TODO warning/insight no-bloqueante (12D insights, ruff no-F, acciones WARN del GS). Cada uno → BLOCK o fix. Test: warning conocido reintroducido → gate bloquea |
| **6** | **Auditoría profunda de exclusiones** | G | Barrer whitelists/excludes/skips/`xfail`/`noqa`/`# type: ignore`/`pytest.skip`/`except…continue`. Cada exclusión: justificada-y-mínima o eliminada. Cero xfail-expected, cero stub/mock/placeholder. Test: exclusión injustificada nueva → detectada |
| **7** | **Naming descriptivo total** | E | Barrer `scripts/`+`tools`+hooks por nombres rimbombantes → descriptivos. REPLACE=DELETE+CREATE (`git mv`), propagar refs, re-sync 17 satélites, REGLA #29 rollback test |
| **8** | **Aplanado estructural + KISS** | F | Aplanar carpetas/subcarpetas donde se pueda; auditoría KISS (Fase 3.5 adecuación arquitectónica del 00-audit). Veredicto OPTIMAL/ADECUADO/SUBÓPTIMO/DEFECTUOSO por subsistema |
| **9** | **Golden Standard = conocimiento puro** | C,B | Codificar aprendizajes Sprints 3-4 como reglas ejecutables; mandato batch-authorization; mecanismo de ingestión de aprendizajes de los 17 satélites; GS siempre actualizado |
| **10** | **Repos externos + vigilancia en vivo** | D | 36 repos → matriz INTEGRAR/COMPLEMENTAR/DESCARTAR/BACKLOG; buscar repos extra en GitHub; deepdive token-saving + arquitectura simple; **investigación de vigilancia del agente en tiempo real (no post-hoc)** |
| **11** | **Auditoría 12D completa + veredicto** | D | Actualizar guías 00-04 al estado actual; correr auditoría adversarial; reporte bajo esquema obligatorio; APPROVED/REJECTED; **limpieza final** (root limpio: archivar `implementation_plan.md` stale, etc.) |

## Dependencias / secuencia
```
5,6 (endurecer+limpiar)  →  7,8 (reestructurar, destructivo, 1 sola ola de re-sync satélite)
10 (research, paralelo/background)  →  9 (GS absorbe aprendizajes)  →  11 (auditoría final + veredicto + limpieza)
```

## Higiene pendiente (detectada hoy)
- `implementation_plan.md` (untracked, root) = plan de Sprint 2 de Gemini, **stale** → archivar/eliminar en Sprint 11.
- `00 audit/` guías 00-04: rangos de ID stale (VT-001..110 / VC-001..119 / TK-001..041) vs catálogo actual; no reflejan DOC_ONLY ni el ratchet → refrescar en Sprint 11.1.
- **[Sprint 6 hallazgo]** `protocol_engine/` (el motor de reglas) está FUERA del scan de `_get_audit_files` (solo escanea scripts/tests/src) → no recibe D-suite. Es una brecha de cobertura, no una exclusión declarada. Evaluar ampliar el scan a `protocol_engine/` en Sprint 5 (riesgo: puede destapar violaciones latentes → endurecer con cuidado).

### Sprint 6 — exclusiones (CERRADO ✅)
- `test_all_scripts.exclude_names`: podado a minimal & real (verificado por exit-codes); stale+redundantes fuera; `run_compliance_tests` re-incluido.
- `test_p1_dead_code`: `skipif(ruff)` portable + **hard test** `test_ruff_is_installed_in_governed_repo` (ausencia = RED, no skip mudo).
- Auto-exención D-suite de 4 core: documentada con rationale (string-pattern self-reference) + **`tests/test_core_self_audit.py`** re-arma pureza D5 → limpiados 11 `except` mudos (incl. `except Exception: pass` ancho l.1312) en `run_security_audit_12d.py`, `core_utils.py`, `rule_collector.py`. Gate APPROVED.
