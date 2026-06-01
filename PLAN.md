# PLAN — CoderCerberus (plan canónico único, modelo de sprints)

**Estado:** master `1562a28`+ · tests verde · C901 = 0 · 17/17 satélites en v0.3 ·
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
golden_standard.yaml convertido en manifest de catálogos (tokenomics/testing/coding/insights).

### Sprint 2 — Simplicity Pass / C901<10 (Gemini)  ✅ CERRADO
Las 16 funciones C901>10 fueron refactorizadas a complejidad <10 con "Zero-Change Contract".
El cierre histórico quedó absorbido en `HISTORIAL.md`; cualquier referencia al estado previo o al
`implementation_plan.md` es ya arqueología, no estado actual.

### Sprint 8 — Aplanado estructural + KISS  ✅
Se aplanaron entrypoints operativos que vivían en subcarpetas sin encapsulación real:
`scripts/serve_dashboard.py`, `scripts/monitor_projects.py` y `scripts/monitor_heartbeat.py`.
Auditoría KISS: `scripts/` quedó `OPTIMAL`; `protocol_engine/` sigue `ADECUADO` por su
namespace cohesivo de reglas YAML.

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

### Pre-S5 — Gate de deuda cero  ✅
Antes de abrir Sprint 5, el repositorio debe seguir cumpliendo todo esto en el gate vivo:
- `python scripts/run_security_audit_12d.py` → `APPROVED`.
- `python -m pytest tests/test_infrastructure.py tests/test_cerberus_core.py tests/test_dead_defs.py tests/test_p1_dead_code.py tests/test_sprint3_cost_metering.py tests/test_regla_6_token_tracking.py -q` → verde.
- `.protocol/review_queue.json` sin pendientes.
- Sin zombies operativos ni refs legacy activas en el árbol activo.
- `00 audit/` se usa como guía de auditoría; `00 audit/results/` es solo referencia histórica.
- Las preguntas/autorizaciones previsibles del plan se agrupan en una sola pasada antes de iniciar una corrida larga.

### Mapa de cobertura del prompt previo a S5
| Requisito del prompt | Sprint / archivo canónico | Estado |
|---|---|---|
| Validar código desconectado | Sprint 4.1 + `tests/test_dead_defs.py` | Cubierto |
| Regla "warning/hallazgo no bloqueado = error" | Sprint 5 | Por endurecer |
| Pedir todas las autorizaciones/preguntas de una vez | Sprint 9 | Cubierto |
| Agregar aprendizajes al Golden Standard | Sprint 9 | Cubierto |
| Auditar `whitelist` / `excludes` / `skips` | Sprint 6 | Cubierto en plan |
| Nombres descriptivos para scripts | Sprint 7 | Cubierto en plan |
| Aplanar estructura + auditoría KISS | Sprint 8 | Cubierto en plan |
| Investigación de vigilancia del agente en vivo | Sprint 10 | Cubierto en plan |
| Mantener el Golden Standard como conocimiento puro y vivo | Sprint 9 | Cubierto |
| Actualizar guía de auditoría y ejecutar auditoría | `00 audit/04_CONTEXTO_EJECUCION.md` + Sprint 11 | Cubierto |

---

### Sprint 16 — Cierre de deuda externa `Control_Procesal`  ✅
- `Control_Procesal` salió de `pending_sync` y quedó en `APPROVED` tras la sincronización frontend/backend.
- `app.js` quedó alineado con el HTML y no conserva stubs activos.
- Hecho cuando el satélite deja de figurar como bloqueante externo en el ledger.

### Sprint 17 — Purga de ruido en reportes generados  ✅
- Regenerar o reescribir `docs/golden_standard_audit_report.md` y `.protocol/metadata/golden_standard_audit.json`.
- Eliminar formulacion vieja, textos heredados y referencias historicas innecesarias.
- Hecho cuando los reportes generados describen solo el esquema actual.

### Sprint 18 — Sellado del historial y drift narrativo  ✅
- Compactar `HISTORIAL.md` para que conserve trazabilidad sin contaminar el relato operativo.
- Mantener `STATUS.md` y `PLAN.md` sin ambiguedades de estado o narrativa antigua.
- Hecho cuando el ruido historico queda sellado y separado del estado activo.

### Sprint 19 — Cierre del ledger de cobertura  ✅
- Cerrar o archivar `docs/P5_coverage_ledger.md` como referencia cerrada.
- Resolver los casos pendientes que aun se interpretan como faltantes de cobertura.
- Hecho cuando el ledger deja de representar deuda y pasa a referencia historica.

### Sprint 20 — Eliminacion de placeholders documentales  ✅
- Retirar o sellar como nota historica las referencias `[TODO]` de `ESCALATION_PROTOCOL.md` y `docs/architecture/N6_REGLA_24_SECURITY_BOUNDARIES.md`.
- Revisar cualquier otro placeholder documental residual que siga abierto.
- Hecho cuando no quedan marcadores de trabajo futuro en guias activas.

### Sprint 21 — Verificacion final de deuda absoluta cero  ✅
- Ejecutar auditoria completa, comprobacion de ledger y verificacion documental final.
- Congelar el estado limpio con evidencia de que no quedan items `ACTIVE`, `DEFERRED` ni `EXTERNAL`.
- Hecho cuando el root y el relato documental quedan en cero absoluto.

### Sprint 22 — Higiene de workspace y cierre de ruido de hooks  ✅
- Encapsular la limpieza de artefactos generados por hooks, colas de revisión, evidencias temporales y drift de línea final.
- Normalizar el estado de Git para que `git status` no quede sucio por cambios técnicos no funcionales tras auditorías o commits.
- Decidir qué salidas automáticas se conservan como evidencia y cuáles se descartan como ruido operativo.
- Hecho cuando el cierre de una corrida deja el árbol limpio sin intervención manual de rescate.
- Ejecutado cuando `protocol_cli hygiene --fix` limpia caches, __pycache__ y directorios vacíos heredados sin tocar el core.

### Sprint 23 — Validación sin efectos volátiles  ✅
- Hacer que `check`, los hooks y los validadores no reescriban metadatos con timestamps cambiantes ni encolen ruido innecesario.
- Separar evidencia real de estado derivado para que la validación no deje el árbol sucio al volver a ejecutarse.
- Mantener `REGISTRY.json`, `review_queue.json` y reportes generados estables salvo cambios funcionales explícitos.
- Hecho cuando una corrida completa de validación no deja modificaciones persistentes no funcionales.
- Ejecutado cuando el mantenimiento post-commit pasa a ser opt-in y `check` vuelve a salir limpio sin tocar metadatos volátiles.

## 📦 SPRINTS DE DEUDA ABSOLUTA CERO
- Todo lo pendiente fue absorbido por los Sprints 16-23.
- No queda backlog funcional fuera del modelo de sprints.
- No quedan items fuera del modelo de sprints.

## Métrica de éxito global
Remediado cuando **un vicio del catálogo introducido a propósito es bloqueado por el gate en
ruta activa** — catálogo = ejecución, sin brecha. Hoy: ~12% real → meta del Sprint 3.

## Secuencia
```
[Sprint 0,1 ✅] → Sprint 2 (cerrar) → Sprint 3 (cobertura real, CRÍTICO) → Sprint 4 (desconexión+higiene) → Sprints 16-21 (deuda absoluta cero)
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
| **5** | **Cero warnings tolerados** | A | Inventario de TODO warning/insight no-bloqueante (12D insights, ruff no-F, acciones WARN del GS, notas en `00 audit/results/`). Cada uno → BLOCK o fix. Test: warning conocido reintroducido → gate bloquea y el root queda limpio tras la corrida. |
| **6** | **Auditoría profunda de exclusiones** | G | Barrer whitelists/excludes/skips/`xfail`/`noqa`/`# type: ignore`/`pytest.skip`/`except…continue`. Cada exclusión: justificada-y-mínima o eliminada. Cero xfail-expected, cero stub/mock/placeholder. Test: exclusión injustificada nueva → detectada y convertida en fallo. |
| **7** | **Naming descriptivo total** | E | Barrer `scripts/`+`tools`+hooks por nombres rimbombantes → descriptivos. REPLACE=DELETE+CREATE (`git mv`), propagar refs, re-sync satélites si aplica, rollback test obligatorio. |
| **8** | **Aplanado estructural + KISS** | ✅ | Ejecutado: flatten de entrypoints operativos y veredicto KISS por subsistema. |
| **9** | **Golden Standard = conocimiento puro** | ✅ | Ejecutado: PI-015..PI-018 formalizan aprendizaje puro, batch-authorization, ratchet y ingestión canónica satélite. |
| **10** | **Repos externos + vigilancia en vivo** | ✅ | 36 repos auditados con fuentes oficiales; matriz INTEGRAR/COMPLEMENTAR/DESCARTAR/BACKLOG cerrada; deepdive selectivo en token-saving + arquitectura simple; vigilancia en tiempo real absorbida sin duplicar Golden Standard. |
| **11** | **Auditoría 12D completa + veredicto** | ✅ | Guías `00 audit/` refrescadas, auditoría adversarial ejecutada, reporte canónico emitido y stale root `implementation_plan.md` retirado. |

## Dependencias / secuencia
```
5,6 (endurecer+limpiar)  →  7,8 (reestructurar, destructivo, 1 sola ola de re-sync satélite)
10 (research, paralelo/background)  →  9 (GS absorbe aprendizajes)  →  11 (auditoría final + veredicto + limpieza)
```

## Higiene pendiente (detectada hoy)
- `implementation_plan.md` (plan viejo de Sprint 2) → retirado en Sprint 11.
- `00 audit/` guías 00-04: rangos históricos ya refrescados en 00 audit/03 para separar catálogo canónico `PI-*` del legado `VT/VC/TK`.
- `protocol_cli propagate` (alias de `global_sync_safe --apply`) → implementado como envoltura canónica; queda como entrada privilegiada, no como permiso base.
- **[Sprint 6 hallazgo resuelto]** `_get_audit_files` ahora incluye `protocol_engine/`, de modo que el motor de reglas recibe la D-suite y la brecha de cobertura quedó cerrada.

### Sprint 12 — Inventario canonico de deuda  ✅
- Crear y mantener [docs/DEBT_LEDGER.md](/D:/GoogleDrive/AI/Cerberus/docs/DEBT_LEDGER.md) como unica fuente de verdad para deuda viva, backlog, drift historico y deuda externa.
- Consolidar en ese ledger el estado de `TODO.md`, `STATUS.md`, `PLAN.md`, `HISTORIAL.md`, `docs/P5_coverage_ledger.md` y `.protocol/metadata/REGISTRY.json`.
- Hecho cuando cada item quede clasificado como `ACTIVE`, `DEFERRED`, `HISTORICAL` o `EXTERNAL`.

### Sprint 13 — Purga de drift historico visible  ✅
- Normalizar `STATUS.md` para que describa el presente sin contadores o relatos obsoletos.
- Normalizar `PLAN.md` para que las referencias históricas queden claramente separadas del backlog vivo.
- Hecho cuando el árbol activo deje de mezclar estado presente con narrativa ya cerrada.

### Sprint 6 — exclusiones (CERRADO ✅)
- `test_all_scripts.exclude_names`: podado a minimal & real (verificado por exit-codes); stale+redundantes fuera; `run_compliance_tests` re-incluido.
- `test_p1_dead_code`: `skipif(ruff)` portable + **hard test** `test_ruff_is_installed_in_governed_repo` (ausencia = RED, no skip mudo).
- Auto-exención D-suite de 4 core: documentada con rationale (string-pattern self-reference) + **`tests/test_core_self_audit.py`** re-arma pureza D5 → limpiados 11 `except` mudos (incl. `except Exception: pass` ancho l.1312) en `run_security_audit_12d.py`, `core_utils.py`, `rule_collector.py`. Gate APPROVED.
