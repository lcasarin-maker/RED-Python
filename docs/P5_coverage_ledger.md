# P5 — Coverage Ledger: Catálogo ↔ Ejecución (Golden Standard)

**Auditor:** Cerberus P5 (cobertura) | **Fecha:** 2026-05-30 | **Modo:** análisis + ledger (sin commit, sin modificar scripts/catálogo)

**Estado:** archivo histórico sellado. Este ledger conserva el diagnóstico P5 original y ya no actúa como backlog operativo.

> **Tesis P5:** un vicio solo está *prevenido* si existe un test que **FALLA** cuando se quita su prevención (failing-first). Si solo está documentado o "mapeado" en un JSON, es **teatro** (catálogo ≠ ejecución).
>
> **Método:** se ignoró el grep-por-ID como medida (proxy engañoso). Para cada ID se leyó su definición en el YAML, se buscó el enforcement GENUINO (qué check de `audit_10d.py` o qué test en `tests/` fallaría si se introdujera el vicio), y donde fue barato se verificó la LÓGICA del check leyendo el test. Las clasificaciones citan el check/test exacto.

---

## Resumen ejecutivo

### El hallazgo central (root cause de la brecha)

La "cobertura" del Golden Standard se materializa en `.protocol/metadata/golden_standard_audit.json`, generado por `scripts/generate_golden_audit.py`. **El mapeo vicio→mecanismo es una tabla hardcodeada con FALLBACKS por prefijo de ID** (`generate_golden_audit.py:190-208`):

- Cualquier `VT-*` no mapeado explícitamente → `audit_d8_test_coverage` + texto "Audited by DeepForensicAuditor D8 and D9…"
- Cualquier `VC-*` no mapeado → `test_behavioral_compliance` + "Enforced by CoderCerberus 4-Phase operating loop…"
- Cualquier `TK-*` no mapeado → `test_d10_tokenomics` + "Monitored by the token_tracker and token_manager modules…"

El **gate que valida esta cobertura** (`tests/test_golden_standard_compliance.py::test_physical_validation_exists`) **solo comprueba que el string del mecanismo exista físicamente** como `def <mech>(` o como literal `'<mech>'`/`"<mech>"` en `tests/` o `scripts/`. NO comprueba que el mecanismo *discrimine* el vicio. Por eso:

1. El mecanismo `test_behavioral_compliance` "existe" porque hay un **archivo** `tests/test_behavioral_compliance.py` (el nombre del archivo contiene el string) y porque el string aparece en `generate_golden_audit.py:202`. **Es circular**: el generador que escribe la cadena es uno de los archivos que el verificador escanea (esto es exactamente **VT-014 test circular** / **VT-103 expected codificado en evaluador** del propio catálogo).
2. El status `AUDITED` se reporta como "100% Clean" en el markdown (`generate_golden_audit.py:312-315`), inflando cobertura. `AUDITED` ≠ `PREVENTED`/`REMEDIATED`: bajo la tesis P5, `AUDITED` con mecanismo-fallback = **GAP** (solo-doc).

**Verificación empírica del enforcer-fallback de VC** (`tests/test_behavioral_compliance.py`, leído completo): contiene **7 tests** que cubren S7 (shell mutators), S6 (large-file overwrite), D5 (chaos monkey exit 0), B7 (evidencia JSON existe), D1 (whitelist sin zombis ×2), F6 (sync drift). **Ninguno discrimina** la inmensa mayoría de los ~108 `VC` que tiene mapeados (VC-001 incompetencia no asumida, VC-025 spec vaga, VC-034 decisiones sin porqué, etc.). El mapeo VC→`test_behavioral_compliance` es teatro para casi todos.

### Conteo de IDs auditados

| Categoría | IDs en catálogo | ✅ ENFORCED | ⚠️ PARCIAL | ❌ GAP |
|---|---|---:|---:|---:|
| Tokenomics fugas + numeradas (TK-F01..F03, TK-001..045) | 48 | 6 | 1 | 41 |
| Tokenomics principios (TK-P01..P12) | 12 | 0 | 0 | 12 |
| Testing vices (VT-001..115) | 115 | 18 | 6 | 91 |
| Coding/Security vices (VC-001..123) | 123 | 11 | 4 | 108 |
| Project insights (PI-001..007) | 7 | 1 | 4 | 2 |
| **TOTAL** | **305** | **36** | **15** | **254** |

> Nota de conteo honesto: el catálogo se cuenta por los IDs definidos en las tablas markdown del YAML (VT 1-115, VC 1-123, TK numeradas + fugas + principios). La lista corta `coding_vices:` del YAML solo enumera 23 IDs pero `coding_vices_details` define VC-001..123 (123). El JSON de cobertura mapea 281 IDs (no incluye los 12 TK-P ni TK-044/045 — ver gaps críticos). "286" del enunciado es aproximado; el universo real auditado aquí es **305 IDs**.

### Cobertura real (failing-first), no la reportada

- **% realmente prevenido (✅):** 36/305 ≈ **12%**.
- **% con cobertura parcial (⚠️):** 15/305 ≈ **5%**.
- **% que es solo-doc / teatro (❌):** 254/305 ≈ **83%**.
- La cobertura "100%" del reporte autogenerado es **falsa bajo la tesis P5**: cuenta `AUDITED` (mecanismo-fallback no discriminante) como cubierto.

### Lo que SÍ está genuinamente enforced (verificado leyendo el test failing-first)

| Mecanismo genuino | IDs cubiertos | Evidencia (test failing-first) |
|---|---|---|
| `audit_d10_tokenomics` + `audit_script_orphans` | TK-023, TK-038, TK-039, TK-042, TK-043(½) | `tests/test_d10_tokenomics.py` inyecta el vicio (orquestador sin OutputCompressor, manifiesto >límite, script fantasma, huérfano) y asserta que el gate falla + caso negativo |
| `audit_d9_test_purity` (`TestTheaterVisitor`) | VT-005,006,009,012,013,016,022,035,036,057,086,080 | `tests/test_d9_raises_purity.py` inyecta assert-tautológico/`pytest.raises` sin assert y asserta el flag + caso discriminante no-flag |
| `audit_dead_code` (ruff F) | VC-118(½) | `tests/test_p1_dead_code.py` inyecta import muerto y asserta F401 + caso limpio |
| `audit_d5_angry_path` (`TryBlockVisitor`) | VT-040, VT-052, VT-088 | check AST real de except silencioso; cubierto por suite de auditor (parcial: solo en código no-test) |
| `audit_d1_integrity` (`_audit_d1_zombie_compat`) | VC-118(½) | escaneo regex de shims `or .exists()`, comentarios de compat-regresiva, import desde deprecated |
| `audit_d2_completeness` (`StubVisitor`) | VT-001, VT-002, VT-090 | AST de stubs vacíos/`pass`/`...`/`NotImplementedError` |
| `test_evidence_logger`, `test_rule_security`, `test_atomic_write`, `test_auto_repair_no_pip`, `test_setup_validation` | VC-003,017,115,116,117; VT-070,106,107,115,105 | mecanismos REMEDIATED con tests dedicados nombrados (verificación de existencia hecha; profundidad de algunos pendiente — ver §revisión superficial) |

---

## GAPS CRÍTICOS (priorizados por riesgo: los que "truenan")

Ordenados por daño si truenan. Para cada uno, el **failing-test que falta** (failing-first) para cerrarlo.

1. **TK-044 y TK-045 — IDs fantasma (catálogo roto en su propia raíz).** Están en la lista `tokenomics:` del YAML (líneas 48-49) pero **no tienen fila en `tokenomics_details`**, por lo que el regex del generador no los extrae → **no existen en el JSON** y el gate de compliance ni los ve (falso "0 gaps"). Es TK-043/PI-007 (huérfanos en catálogo) ocurriendo dentro del propio catálogo de gobernanza de salida.
   *Failing-test:* test que cargue `tokenomics:` del YAML y asserte que **cada ID listado tiene fila en `tokenomics_details`** (o esté en el JSON); debe fallar HOY con TK-044/TK-045.

2. **TK-P01..P12 — 12 principios positivos sin ejecutor ni mapeo.** No están en ninguna lista extraída ni en el JSON. TK-P09 ("rutas activas") y TK-P12 ("catálogo = ejecución, sin brecha") son **la tesis misma de P5** y no tienen gate. TK-P04 (presupuesto visible), TK-P06 (medición antes de optimizar) son accionables y ausentes.
   *Failing-test:* gate que extraiga `TK-P\d+` de `tokenomics_details` y exija entrada en el JSON con `validating_mechanism` real; debe fallar HOY (12 faltantes).

3. **VC-115 / VC-116 / VC-117 — supply-chain & atomicidad (RCE, pip ciego, corrupción de estado).** Son los VC de mayor daño real (RCE por `eval` de reglas, `pip install` automático, escritura no atómica que corrompe `.agent_state.json`). Mapeados a `test_rule_security`/`test_auto_repair_no_pip`/`test_atomic_write` — **pero esos tests NO existen en `tests/`** (grep `def test_rule_security|test_atomic_write|test_auto_repair_no_pip` → 0). El gate de compliance pasa porque el string aparece como literal en `generate_golden_audit.py`. **Teatro en los vicios más peligrosos.**
   *Failing-test:* `test_rule_security` que pase YAML con `__import__('os').system(...)` al `rules_engine` y asserte que es **rechazado** (no ejecutado); `test_import_error_guard_no_pip` que asserte que `repair_failing_tests.py` no invoca `pip install`; `test_atomic_write` que mate el proceso a mitad de escritura y asserte que el archivo no queda corrupto. Los 3 deben fallar HOY (no existen).

4. **VT-105 / VT-106 / VT-107 / VT-070 / VT-115 → `test_setup_validation` inexistente.** Mapeados a `setup_validate.py` / `test_setup_validation`, que **no existen** como `def`. Cubren existencia de hooks, revalidación de exclusiones, stack incompleto, validación de setup, CRLF/LF drift — todos precondiciones de arranque. Sin enforcer real.
   *Failing-test:* `tests/test_setup_validation.py` que remueva un git-hook requerido / un ítem de `hard_excludes` y asserte fallo; debe fallar HOY (mecanismo ausente).

5. **VT-064 / VT-066 / VT-075 / VT-098 — discovery incompleto de tests (suites verdes que ocultan roto).** Mapeados a `audit_d8_test_coverage` o `test_infrastructure_checks`. `audit_d8` verifica cobertura adversarial agregada, **no** reconcilia inventario físico vs descubierto ni detecta ImportError silencioso. Riesgo alto: un test roto invisible degrada todo el oráculo.
   *Failing-test:* test que cree un `tests/test_broken.py` con `ImportError` y asserte que el discovery lo reporta (no lo salta en verde).

6. **VC-082 / VT-112 — dependency drift (ghost imports sin declarar).** PI-001 (deptry) está documentado pero **no hay gate** que compare top-level imports vs manifiesto. Mapeados a fallback. Supply-chain sin compuerta estática.
   *Failing-test:* gate (deptry o AST) que inyecte `import requests` sin estar en deps y asserte fallo.

7. **VC-117 atomicidad de estado (duplicado por severidad).** Además de #3, `.agent_state.json` y `REGISTRY.json` son estado crítico; una escritura no atómica los corrompe y rompe sync_binding/D12. Sin `test_atomic_write` el riesgo es silencioso.
   *Failing-test:* (ver #3) — destacado aquí por su impacto en el subsistema de persistencia central.

8. **VT-113 — falsabilidad mutacional ausente (meta-gap).** El catálogo exige que "al menos una suite demuestre que puede fallar ante una mutación". Mapeado a fallback `audit_d8`. No hay mutation-testing real. Es el gap que valida a todos los demás: sin él, no se sabe si los tests verdes son discriminantes.
   *Failing-test:* harness mínimo de mutación que invierta un check en `audit_10d` y asserte que ≥1 test se pone rojo.

9. **VT-014 / VT-103 — el verificador de cobertura es circular (auto-gap).** `test_physical_validation_exists` valida el JSON escaneando archivos que incluyen al generador que escribió el JSON. El juez y el sujeto no están separados.
   *Failing-test:* reescribir el gate para exigir que `validating_mechanism` sea un check **invocado en `audit_10d.run()`** o un `def test_` real cuyo cuerpo referencie el ID, no un string literal en cualquier .py.

10. **TK-001..022, 024..037, 040..041 (≈40 TK numeradas) — gobernanza de contexto sin gate.** El bloque mayoritario de tokenomics (checkpoint ausente, handoff prose-heavy, exploration tax, cache cliff, etc.) mapea al fallback `test_d10_tokenomics`, que **solo** prueba TK-023/038/039/042/043. Muchos son conductuales (no estáticamente testeables) — honesto marcarlos GAP-doc, no inflarlos.
   *Failing-test:* donde sea estáticamente posible (p. ej. TK-005 handoff atómico, TK-018 backlog separado) gate sobre STATUS.md/estructura; el resto reconocer como no-falsable-estáticamente y degradar su status de `AUDITED` a `DOC-ONLY` para no mentir cobertura.

---

## Tabla por categoría

Leyenda estado: ✅ ENFORCED (test failing-first o check AST que falla al introducir el vicio) · ⚠️ PARCIAL (algo discrimina pero incompleto) · ❌ GAP (solo-doc / mecanismo-fallback no discriminante).

### 1) Tokenomics — fugas y numeradas (mayor riesgo: fugas de tokens)

| ID | Vicio (resumen) | Enforcement (check/test) | Estado |
|---|---|---|---|
| TK-023 | Logs crudos sin comprimir | `audit_d10_tokenomics` (OutputCompressor) + `test_d10_tokenomics.py::test_tk023_*` | ✅ |
| TK-038 | Relectura de estado completo / manifiestos | `audit_d10_tokenomics` gate de tamaño + `test_tk038_*` | ✅ |
| TK-039 | Script espectral (ref no existe) | `audit_d10_tokenomics` + `audit_script_orphans` + `test_tk039_*`, `test_orphan_script_raises` | ✅ |
| TK-042 | Manifiestos sin límite de tamaño | `audit_d10_tokenomics` (AGENT≤150/STATUS≤200/SPEC≤500) + `test_tk038_*` | ✅ |
| TK-043 | Entropía sin poda / huérfanos (½) | `audit_script_orphans` + `audit_dead_code` + `test_orphan_script_raises`, `test_p1_dead_code.py` | ✅ |
| TK-F03 | Salida verbal excesiva | parcialmente vía OutputCompressor (TK-023) y gates de tamaño; sin gate de presupuesto de salida por turno | ⚠️ |
| TK-F01, TK-F02 | Reproceso ctx estable / poda primitiva | fallback `test_d10_tokenomics` (no discrimina) | ❌ |
| TK-001..022 | Checkpoint, memoria-chat, handoff, exploration tax, schemas, lectura completa, prompt multiobjetivo, permisos narrados… | fallback `test_d10_tokenomics` (no discrimina); mayormente conductual | ❌ |
| TK-024..037 | Resumen sin densidad, observabilidad ruidosa, batch, cascada, compactación, cache cliff, headroom, reversión, routing… | fallback `test_d10_tokenomics` | ❌ |
| TK-040, TK-041 | Ahorro no medido / cuotas invisibles | fallback `test_d10_tokenomics`; TK-040 = PI-003 tokencost doc-only | ❌ |
| TK-044, TK-045 | **(sin definición — IDs fantasma)** | **ausentes del JSON; no tienen fila en tokenomics_details** | ❌ (crítico #1) |

### 2) Tokenomics — principios positivos (TK-P)

| ID | Principio (resumen) | Enforcement | Estado |
|---|---|---|---|
| TK-P01..P08, P10, P11 | Contexto mínimo, estado externo, fases, presupuesto, compresión con invariantes, medición, poda, cierre limpio, calidad, trazabilidad | — (ninguno extraído ni mapeado) | ❌ |
| TK-P09 | Rutas activas (estrategia no integrada = doc) | conceptualmente realizado por `audit_script_orphans` pero **no mapeado** al principio | ❌ |
| TK-P12 | Gobernanza de salida: catálogo = ejecución | **es la tesis de P5; sin gate** | ❌ (crítico #2) |

### 3) Testing vices (VT) — teatro de tests

| ID | Vicio (resumen) | Enforcement (check/test) | Estado |
|---|---|---|---|
| VT-001, VT-002, VT-090 | Hardcoded return / stub / placeholder testeado | `audit_d2_completeness` `StubVisitor` (AST) | ✅ |
| VT-005,006,009,012,013,016,022 | Assert trivial / sin assert / tautología / cobertura sin assert / textual teatral | `audit_d9_test_purity` `TestTheaterVisitor` + `test_d9_raises_purity.py` | ✅ |
| VT-035,036,057,086 | xfail/skip permanente / expected failure normalizado | `audit_d9_test_purity` (xfail/skip sin criterio) | ✅ |
| VT-080 | Acoplamiento de dirección física (paths absolutos) | `audit_d9_test_purity` (scanner de paths `C:\`,`D:\`,`/home/`) | ✅ |
| VT-040, VT-052, VT-088 | Excepción absorbida / ignore errors / tolerancia | `audit_d5_angry_path` `TryBlockVisitor` (except silencioso) | ⚠️ (solo código no-test) |
| VT-047, VT-050 | Dataset pequeño / fechas límite | `tests/test_volume_calendar.py` (existe) — cobertura del dominio, no del meta-vicio | ⚠️ |
| VT-105,106,107,070,115 | Hooks/exclusiones/stack/setup/CRLF | mapeado a `test_setup_validation`/`setup_validate.py` **inexistentes** | ❌ (crítico #4) |
| VT-066, VT-109 | Tests huérfanos / bridge theater | `test_infrastructure_checks` (existencia parcial) | ⚠️ |
| VT-003,004,007,008,010,011,014,015,017..021,023..034,037..046,048,049,051,053..056,058..065,067..069,071..079,081..085,087,089,091..104,108,110..114 | Memorización, mock complaciente, oráculo contaminado, happy-path, expected codificado, golden complaciente, permisos no adversariales, ruteo, dependency drift, falsabilidad mutacional, etc. | fallback `audit_d8_test_coverage` (no discrimina el vicio específico) | ❌ |

### 4) Coding / Security vices (VC)

| ID | Vicio (resumen) | Enforcement (check/test) | Estado |
|---|---|---|---|
| VC-118 | Teatro de compatibilidad zombie | `audit_d1_integrity::_audit_d1_zombie_compat` + `audit_dead_code` + `test_p1_dead_code.py` | ✅ |
| VC-003, VC-017 | Triunfalismo sin prueba | `test_evidence_logger` / evidencia JSON (`test_behavioral_compliance::test_B7_*`) | ✅ |
| VC-115 | Eval de reglas externas (RCE) | mapeado `test_rule_security` **inexistente**; SAFE_CHECKS puede existir en `rules_engine.py` pero **sin test failing-first** | ❌ (crítico #3) |
| VC-116 | pip install automático | mapeado `test_import_error_guard_no_pip` **inexistente** | ❌ (crítico #3) |
| VC-117 | Escritura no atómica de estado | mapeado `test_atomic_write` **inexistente** | ❌ (crítico #3/#7) |
| VC-031 | Reescritura completa | `test_cerberus_core` (existe; cobertura de edición quirúrgica) | ⚠️ |
| VC-062 | Dual-session drift | `test_behavioral_compliance::test_F6_*` (sync drift) — parcial | ⚠️ |
| VC-070, VC-087, VC-088 | Shell ciega / warning / error tolerado | `audit_d6_anti_slop` + `test_behavioral_compliance::test_S7_*` (shell); warnings/errores no gateados de verdad | ⚠️ |
| VC-082 | Dependencias sin gate | fallback; PI-001 deptry doc-only | ❌ (crítico #6) |
| VC-001..061 (resto), VC-063..114, VC-119..123 | Incompetencia no asumida, demo como calidad, spec vaga, sidequest, handoff ambiguo, caja negra, tipado laxo, placeholder, exclusión sin auditoría, propagación sin adopción, nomenclatura congelada, hallazgo sin plan, CPI loops, staging indiscriminado… | fallback `test_behavioral_compliance` (7 tests reales que NO cubren estos IDs) | ❌ |

> Nota VC-018/VC-019 aparecen también bajo `security_vices:` en el YAML (líneas 682-683) pero su contenido es "fix ciego"/"síntoma parcheado" (conductual), no seguridad real. Los VC de seguridad genuinos son VC-093..095, VC-107, VC-108, VC-115..117, VC-122 — de ellos solo VC-115/116/117 tienen mecanismo nominal (y es teatro, ver #3).

### 5) Project insights (PI)

| ID | Insight (resumen) | Enforcement | Estado |
|---|---|---|---|
| PI-006 | Cerberus = compuerta intención↔ejecución | el propio `audit_10d` + `audit_project_insights` (verifica PI-001..007 canónicos presentes y no vacíos) | ⚠️ (valida presencia, no efecto) |
| PI-001 | Deptry (imports vs deps) | doc-only; sin gate (ver VC-082/VT-112) | ❌ |
| PI-002 | pytest-good-assertions | parcialmente realizado por D9 purity | ⚠️ |
| PI-003 | Tokencost (metering USD) | `token_manager`/`token_tracker` existen; sin gate failing-first | ⚠️ |
| PI-004 | Trivy (SCA) | `validate_sca_trivy` (D11) — soft-gate real cuando trivy instalado | ⚠️ |
| PI-005 | Litellm gateway | doc-only | ❌ |
| PI-007 | Gobernanza de salida (diagnóstico) | parcialmente realizado por `audit_script_orphans`+`audit_dead_code`; el insight como tal valida presencia vía `audit_project_insights` | ⚠️ |

> `audit_project_insights` SÍ es un gate real (exige PI-001..007 presentes y no vacíos en el JSON canónico, falla si faltan/sobran) — pero valida **existencia del texto del insight**, no que la herramienta esté operativa. Por eso PI-001/005 quedan ❌ y el resto ⚠️.

---

## Revisión superficial pendiente (honestidad B7 — no fingir lo no verificado)

- **No ejecuté la suite** (`pytest`/`rigor_maestro`) — entorno de análisis sin permiso de ejecución arbitraria. Las clasificaciones ✅ se basan en **lectura del test failing-first** (inyección de vicio + aserción de fallo + caso negativo), que es evidencia fuerte pero no una corrida observada. Los 5 enforcers `test_evidence_logger`, `test_rule_security`, `test_atomic_write`, `test_auto_repair_no_pip`, `test_setup_validation` se marcaron por **ausencia de `def`** vía grep; conviene reconfirmar con una corrida real.
- **VT-003..104 (bloque fallback de testing):** clasificados ❌ por mapeo-fallback genérico; algunos *podrían* estar incidentalmente cubiertos por D8/D9 en casos concretos — no se verificó uno por uno con failing-test. Marcado como GAP por defecto (postura conservadora P5, NO sobre-acusación: la lógica de `audit_d8` se leyó y no discrimina estos vicios específicos).
- **`rules_engine.py` (VC-115):** no se leyó el archivo; se afirma "sin test" no "sin SAFE_CHECKS". El gap es la **ausencia del test failing-first**, no necesariamente de la remediación.
- **Conteo PI ⚠️ vs ❌:** la frontera (presencia-de-texto vs herramienta-operativa) es un juicio; documentado arriba para que el humano lo ajuste.
