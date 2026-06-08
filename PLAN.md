# PLAN.md — RED-Python v0.5 (CoderCerberus)

**Versión:** 0.5
**Protocolo:** CoderCerberus v0.5
**Mandato:** B10 (Checkpointing)
**Escrito:** 2026-06-02

---

## OPERACIÓN PRINCIPAL

Escanear y eliminar directorios vacíos o efectivamente vacíos:
1. Detectar directorios con solo archivos ignorables (0-byte, ocultos, sistema)
2. Propagar "vacío" hacia arriba en cadenas de carpetas anidadas
3. Proteger directorios críticos (Windows, ProgramFiles, etc.)
4. Opcionalmente eliminar o mover a Recycle Bin

Dual interface: GUI (Tkinter) + CLI (argparse)

External audit instruction: see [00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md](00%20audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md).

---

## PASOS NUMERADOS

<<<<<<< HEAD
1. **Bootstrap:** Cargar config.yaml con Settings (S4: Modularidad)
2. **Scan:** Scanner.scan() en thread daemon (thread-safe callbacks):
   - on_found → emitir ScanResult por cada carpeta vacía
   - on_log → logging de eventos
   - on_progress → actualizar UI con % completado
3. **Cleanup:** Cleaner.delete() elimina con undo tracking
4. **Undo:** Leer logs y reversar movimientos en orden inverso

---

## ANGRY PATHS — 3 FORMAS DE ROMPER (B3)

### 🔴 Path 1: Permission Denied on Protected Directory
**Escenario:** Scanner intenta acceder a C:\System32 o C:\ProgramFiles; OSError "Access Denied".
**Impacto:** Scanner crash; aplicación cuelga sin logging del error.
**Mitigación:** Envolucaer os.walk() en try/except; verificar is_protected() ANTES; skip con logger.info().

```python
# En Scanner.scan():
try:
    for root, dirs, files in os.walk(path, topdown=False):
        if is_protected(root):
            logger.info(f"SKIP protected: {root}")
            dirs.clear()  # No descender
            continue
except OSError as e:
    logger.error(f"Permission denied: {root}: {e}")
    self.on_log(f"[ERROR] {root}: {e}")
=======
### Auditoria exterior — Control_Procesal Fase 1  ✅ COMPLETADA
1. Crear contrato declarado/inferido desde codigo vivo, sin asumir capacidades no probadas.
2. Completar README del repo auditado con proposito, ejecucion, pruebas, limites y no-objetivos.
3. Actualizar descripcion de GitHub y verificar que el repo siga privado.
4. Registrar evidencia en `00 audit/results/exterior/Control_Procesal/2026-06-05/`.
5. Correr pruebas locales y dejar commit trazable en repo auditado y en Cerberus.

### Auditoria exterior — Control_Procesal Fase 2  ✅ REMEDIADA Y VERIFICADA
1. Backend local verificado: `/ping`, `/storage/get`, `/expedientes` y 404 de PDF inexistente responden.
2. `/expedientes` timeout historico no se reprodujo: 28 expedientes en ~0.13s.
3. UI humano-like fallo inicialmente: despues de 8s mostraba `Conectando...` y `0` expedientes aunque backend tenia 86 registros y 28 expedientes unicos.
4. Causa raiz corregida: script inline roto por `const dualTable` dentro de concatenacion + bootstrap asincrono sin `await`.
5. Remediacion verificada: captura post-fix muestra `Sincronizado`, `28` expedientes y lista poblada; tests del repo auditado `5 passed`.

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
- `python -m pytest tests/test_infrastructure.py tests/test_cerberus_core.py tests/test_dead_defs.py tests/test_d3_dead_code.py tests/test_sprint3_cost_metering.py tests/test_regla_6_token_tracking.py -q` → verde.
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

### Sprint 16 — Cierre de deuda externa `Control_Procesal`  ✅ CERRADO
- `Control_Procesal` (satélite externo D:\GoogleDrive\AI\Control_Procesal) sincronizado y en APPROVED.
- Registrado en REGISTRY.json con status `active` y `adoption_verified`.
- **Estado:** Hecho. Satélite alineado sin bloqueantes.

### Sprint 17 — Purga de ruido en reportes generados  ✅ CERRADO
- `docs/golden_standard_audit_report.md` y `.protocol/metadata/golden_standard_audit.json` existen.
- Formulaciones viejas purgadas; esquema actual documentado.
- **Estado:** Hecho.

### Sprint 18 — Sellado del historial y drift narrativo  ✅ CERRADO
- `HISTORIAL.md` sellado (4318 líneas con trazabilidad completa).
- `STATUS.md` y `PLAN.md` sin ambiguedades de estado antiguo.
- **Estado:** Hecho.

### Sprint 19 — Cierre del ledger de cobertura  ✅ CERRADO
- `docs/P5_coverage_ledger.md` y `docs/DEBT_LEDGER.md` existen como referencia histórica.
- Ledger pasa de "deuda viva" a "referencia cerrada".
- **Estado:** Hecho.

### Sprint 20 — Eliminacion de placeholders documentales  ✅ CERRADO
- Cero `[TODO]` abiertos en `ESCALATION_PROTOCOL.md` y `docs/architecture/`.
- Placeholders históricos purgados.
- **Estado:** Hecho.

### Sprint 21 — Verificacion final de deuda absoluta cero  ✅ CERRADO
- Gate APPROVED. 386 tests pasando. Cero items `ACTIVE`, `DEFERRED`, `EXTERNAL`.
- Estado limpio congelado.
- **Estado:** Hecho.

### Sprint 22 — Higiene de workspace y cierre de ruido de hooks  ✅ CERRADO (2026-06-01 01:57)
- Removidos __pycache__ (5 dirs) y .pytest_cache.
- Git status limpio: sin artefactos automáticos no funcionales.
- Commit `d869674`: "workspace hygiene + validation stability"
- **Estado:** Hecho.

### Sprint 23 — Validación sin efectos volátiles  ✅ CERRADO (2026-06-01 01:57)
- REGISTRY.json timestamps estabilizados (cambios funcionales nulos tras re-run).
- Metadatos volátiles separados de estado real.
- Validación no deja el árbol sucio tras ejecutarse.
- **Estado:** Hecho.

---

## 🚀 SPRINT 24 — D13 Observable Behavior (Token Meter + Decision Logger + Divergence Detector)

**Objetivo:** Observabilidad en tiempo real de agentes (tokens, decisiones, divergencias).

**Complejidad:** 🟢 FÁCIL | **Duración:** 2 weeks | **Prioridad:** HIGH | **Blocker:** Ninguno

### 24.1: Token Meter
- Herramienta: tiktoken (OpenAI tokenizer)
- Archivo: `scripts/d13_token_meter.py` (39 líneas)
- Mide: tokens reales de SPEC.md, AGENT.md, PLAN.md, CLAUDE.md
- Métrica: tokens, costo USD por manifest

### 24.2: Decision Logger
- Archivo: `scripts/d13_decision_logger.py` (48 líneas)
- Formato: JSONL estructurado
- Campos: decision_id, agent, decision, reasoning, action, result, timestamp
- Output: `~/.cerberus/decision_logs/decisions_TIMESTAMP.jsonl`

### 24.3: Divergence Detector
- Archivo: `scripts/d13_divergence_detector.py` (56 líneas)
- Parse AGENT.md: extrae "PUEDE" y "NO PUEDE"
- Check: compara acción real vs permitidas
- Severidad: CRITICAL (prohibido) / WARNING (no permitido)

### 24.4: Observable Behavior Orchestrator + Dashboard
- Archivo: `scripts/d13_observable_behavior.py` (41 líneas)
- D13Report class con `generate()` method
- Dashboard: HTML/JSON histórico últimas 100 ejecuciones

**Tests:** 10 casos (token counting, decision logging, divergence detection)
**Status:** INFORMATIONAL (no bloquea gate)

---

## 🟢 SPRINT 25 — Vulture + Ruff Integration (D3 Dead Code)

**Objetivo:** Dead code coverage 60% → 95%

**Complejidad:** 🟢 FÁCIL | **Duración:** 1 week | **Prioridad:** HIGH | **Blocker:** Sprint 24

**Implementación:**
- Archivo: `scripts/d3_dead_code_enhanced.py` (120 líneas)
- Herramientas: Vulture + Ruff (dos pasadas: 50ms + 100ms = 150ms)
- Lógica: Ruff (rápido) → Vulture (profundo) → merge results
- FAIL si >5 unused en código crítico

**Tests:** 12 casos (unused vars, args, attrs, false positives, critical paths)

---

## 🟡 SPRINT 26 — D11 Enhanced (Dependency Validation + License + Deprecation)

**Objetivo:** Validación deps + licenses + deprecation tracking

**Complejidad:** 🟡 MEDIA | **Duración:** 2 weeks | **Prioridad:** MEDIUM | **Blocker:** Ninguno

### 26.1: Version Compatibility Check
- Herramienta: poetry check + pip-audit
- Detecta: versiones incompatibles entre dependencias
- Ejemplo: "Requests 2.25.0 incompatible con urllib3 <1.26"

### 26.2: License Scanning
- Herramienta: pip-licenses + SPDX validation
- Detecta: licencias problemáticas (GPL, AGPL en MIT project)
- Acción: WARN si incompatible, FAIL si explícitamente prohibido

### 26.3: CVE + Deprecation Tracking
- Herramienta: Trivy + PyPI API
- Detecta: CVEs actuales + deprecations anunciadas
- Acción: FAIL si CVE, WARN si deprecation próxima

### 26.4: Monthly Report
- Archivo: `scripts/d11_deprecation_report.py`
- Genera: JSON/HTML con histórico de cambios de deps

**Tests:** 16 casos (incompatible versions, GPL conflict, CVE detection, deprecated packages)

---

## 🟠 SPRINT 27 — Bandit + Semgrep + Trivy Integration (D7 Security)

**Objetivo:** Security coverage 70% → 98%

**Complejidad:** 🟠 MEDIA-ALTA | **Duración:** 2 weeks | **Prioridad:** HIGH | **Blocker:** Ninguno

**Herramientas:**
- Bandit: credenciales hardcoded, crypto débil (~30ms)
- Semgrep: patrones complejos, taint tracing (~150ms)
- Trivy: CVE scanning en dependencias (~200ms)

**Implementación:**
- Archivo: `scripts/d7_security_scan_enhanced.py` (180 líneas)
- Lógica: Bandit → Semgrep → Trivy → deduplicar → FAIL si any CRITICAL

**Tests:** 18 casos (hardcoded passwords, SQL injection, crypto, CVEs, false positives)

---

## 🔴 SPRINT 28 — D14 Discourse Rigor + Pre-Response Hook

**Objetivo:** Validar nitidez discursiva de respuestas antes de envío

**Complejidad:** 🔴 ALTA | **Duración:** 2 days | **Prioridad:** HIGH | **Blocker:** Ninguno | **Status:** ✅ CERRADO (absorbido por 28.5 — d14 migrada a `dimensions/d14_discourse_rigor.py` + cableada al Stop hook; ver línea 564)

### 28.1: D14 Discourse Validator Script
- Archivo: `scripts/d14_discourse_rigor.py` (140-160 líneas)
- Clase: `DiscourseValidator` con métricas de nitidez
  - `measure_clarity()`: análisis palabra-clave, capitalización, puntuación regular → score 0-1
  - `detect_ambiguity()`: contar frases vagas ("maybe", "perhaps", "could be")
  - `count_evidence()`: detectar citas y referencias "[1]", "cite:", "ref:"
  - `measure_chain_of_thought()`: profundidad causal ("because", "therefore", "leads to")
  - `validate()`: ejecutar métricas, determinar PASS/FAIL vs threshold
  - `report()`: JSON con métricas y veredicto
- Severity: CRITICAL (clarity<0.5), HIGH (0.5-0.65), MEDIUM (0.65-0.8), PASS (>=0.8)
- Fail threshold default: clarity_score >= 0.7

### 28.2: Tests D14
- Archivo: `tests/test_d14_discourse_rigor.py` (14 test cases)
  - TestDiscourseMetric: creation, status defaults
  - TestDiscourseValidator: init, thresholds
  - measure_clarity: high/medium/low clarity scoring
  - detect_ambiguity: count vague phrases
  - count_evidence: citations detection
  - chain_of_thought: causal marker depth
  - validate: PASS/FAIL logic
  - report: JSON format validation
  - integration: full response validation
- Expect: 14/14 passing

### 28.3: Register + Commit
- SPEC.md lines 141-143: register script + tests
- Commit: `Sprint 28: D14 Discourse Rigor (14/14 tests, S-SPRINT)`

---

## 🧊 SPRINT 29 — Agent-Agnostic ReviewBot Orchestration (FUTURE — NO acción inmediata)

> **Status: FUTURE / diferido (2026-06-01).** Sprint 28 (todo 27→29, incl. 28.5) cerrado; Sprint 29
> NO se inicia hasta resolver el bloqueo de diseño B1: definir el mecanismo real de invocación del
> agente (`ClaudeReviewAgent` "vía MCP" está sin definir — no hay cliente Anthropic/MCP en el repo).
> Riesgo de teatro: ~520 LOC mockeados que no revisan ningún PR real. Requiere decisión del usuario
> antes de promover a acción inmediata. Ver análisis en HISTORIAL.md.

**Objetivo:** Orquestación de revisión de PR via middleware + agentes intercambiables (Claude, Gemini, local, remote)

**Complejidad:** 🔴🔴 ALTA | **Duración:** 2 weeks | **Prioridad:** FUTURE (diferido) | **Blocker:** Diseño B1 (motor del agente sin definir)

**Principio:** Agent-agnostic (NO hardcoding de Claude API). Arquitectura síntesis de 3 repos:
- GrumPHP (middleware chain, max-based aggregation)
- JSLint (6-phase pipeline, exhibits, inline directives)
- reviewbot (verdict model, GitHub integration)

### Decisión registrada (2026-05-31)
**Opción elegida:** Agent-Agnostic ReviewBot Orchestrator (vs hardcoded Claude)
- Agent type configurable via env var: `REVIEW_AGENT_TYPE` (claude/subprocess/remote)
- Implementación inicial: ClaudeReviewAgent (via MCP, swappable later)

### 29.1: Middleware Stack (120-140 líneas)
**File:** `scripts/pr_middleware.py`

**Runner middleware (orchestración síncrona):**
- GateValidationMiddleware — D1-D12 audit
- AgentInvocationMiddleware — invoke review agent
- ResultAggregationMiddleware — max(gate_code, agent_code)
- EventDispatchingMiddleware — emit events
- ReportingMiddleware — post GitHub comment

**Handler middleware (per-agent, async):**
- AgentErrorHandlingMiddleware — catch exceptions, retry
- AgentResultCachingMiddleware — memoize responses
- DecisionLoggingMiddleware — log via D13

**Status codes (max-based, GrumPHP):**
```
GATE_PASSED = 0, AGENT_PASSED = 1, AGENT_WARNED = 5, GATE_FAILED = 10
overall = max(gate_code, agent_code)
```

### 29.2: Agent-Agnostic Review Interface (80-100 líneas)
**File:** `scripts/agent_review_adapter.py`

**Abstract ReviewAgent protocol:**
```python
class ReviewAgent(Protocol):
    def analyze_pr(self, pr_files: List[str], pr_context: dict) -> ReviewFindings:
        """Analyze PR and return findings (JSON-serializable)"""
```

**Implementations (pluggable):**
- ClaudeReviewAgent (MCP, in-process)
- SubprocessReviewAgent (local/ollama)
- RemoteReviewAgent (HTTP external)

**Agent registry (tag-based):**
```python
agents = {
    "claude": ClaudeReviewAgent,
    "subprocess": SubprocessReviewAgent,
    "remote": RemoteReviewAgent,
}
agent_type = os.getenv("REVIEW_AGENT_TYPE", "claude")
agent = agents[agent_type](config)
```

### 29.3: Feedback Loop Pattern Tracking (50-70 líneas)
**File:** `scripts/analyze_decision_patterns.py`
- Load decision logs (D13, past 7 days)
- Detect patterns: high rejection rate, low warning rate
- Suggest agent sensitivity adjustments (informational)

### 29.4: Testing (15+ cases)
**File:** `tests/test_cerberus_pr_gate.py` (220-250 líneas)
- 3 Agent interface tests (different agent types, mocked)
- 7 merge logic tests (gate scenarios, deterministic veto)
- 3 feedback loop tests (pattern detection)
- 2 integration tests (full flow with mock agent)
- All mocked (no real agent calls, no API keys)

### 29.5: 6-Phase Pipeline (JSLint-inspired)
```
PHASE 1: SPLIT   → normalize PR context
PHASE 2: LEX     → extract config + inline directives
PHASE 3: PARSE   → D1-D12 gate audit
PHASE 4: WALK    → agent review (middleware)
PHASE 5: FORMAT  → aggregate + build exhibits (A,B,C,D)
PHASE 6: REPORT  → post GitHub comment + update status
```

### 29.6: Finding Structure (JSLint exhibits)
```python
{
    "rule": "security_check_12",
    "severity": "HIGH",
    "message": "SQL injection risk",
    "file": "app.py",
    "line": 42,
    "exhibits": {
        "a": {...},  # Primary problem
        "b": {...},  # Secondary context
        "c": {...},  # Optional
        "d": {...}   # Optional
    }
}
```

### 29.7: Inline Directives (JSLint pattern)
```python
# In code: portable, no extra files
# reviewbot: disable=rule_12
# reviewbot: ignore-line

# In YAML config
directives:
  enabled: true
  scope: [file, block, line]
```

### 29.8: Register + Commit
- SPEC.md: register scripts + status codes
- PLAN.md: update Sprint 29 status
- HISTORIAL.md: add Sprint 29 completion entry
- `.github/workflows/protocol.yaml`: ReviewBot trigger on PR events
- Commit: `Sprint 29: Agent-Agnostic ReviewBot (6-phase, middleware, exhibits, S-SPRINT)`
- Use `--no-verify` (S-SPRINT exception)

**Tests:** 15+ casos (accept, reject, warn scenarios)

---

## 📦 SPRINTS DE DEUDA ABSOLUTA CERO
- Todo lo pendiente fue absorbido por los Sprints 16-23.
- No queda backlog funcional fuera del modelo de sprints.
- No quedan items fuera del modelo de sprints.
- **Sprint 12 (D13) es forward-planning, no deuda pendiente.**

## Métrica de éxito global
Remediado cuando **un vicio del catálogo introducido a propósito es bloqueado por el gate en
ruta activa** — catálogo = ejecución, sin brecha. Hoy: ~12% real → meta del Sprint 3.

## Secuencia
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
```

### 🔴 Path 2: Symbolic Link Loop (Infinite Recursion)
**Escenario:** Symlink points to parent dir; os.walk() descubre loop infinito sin --follow-symlinks.
**Impacto:** Stack overflow; OOM kill si memoria llena de calls recursivos.
**Mitigación:** Mantener conjunto de inodes visitados; detectar cycle con dev/ino; skip si ya visto.

```python
# En Scanner.__init__():
self._visited_inodes = set()

# En Scanner.scan():
try:
    stat_result = os.stat(root)
    inode = (stat_result.st_dev, stat_result.st_ino)
    if inode in self._visited_inodes:
        logger.warning(f"LOOP detected: {root}")
        dirs.clear()
        continue
    self._visited_inodes.add(inode)
except OSError as e:
    logger.error(f"Cannot stat {root}: {e}")
```

### 🔴 Path 3: Disk Full During Deletion
**Escenario:** Cleaner.delete() -> shutil.rmtree() falla mitad del camino; disco lleno.
**Impacto:** Árbol parcialmente eliminado; datos irrecuperables sin undo.
**Mitigación:** Verificar espacio ANTES de delete; usar undo log para rollback atomicity.

```python
# En Cleaner.delete():
import shutil
free_bytes = shutil.disk_usage(path).free
if free_bytes < 10 * 1024 * 1024:  # 10MB threshold
    logger.error(f"Insufficient disk space: {free_bytes / 1e9:.1f}GB free")
    raise IOError("Not enough space for safe deletion")

try:
    shutil.rmtree(path)
    logger.info(f"Deleted: {path}")
except Exception as e:
    logger.error(f"Deletion failed: {path}: {e}")
    # Trigger undo mechanism
    self._undo_last_deletion()
```

---

## VALIDACIÓN PRE-CAMBIO

- ✅ S4: Modularidad (Scanner, Cleaner, App separados)
- ✅ S5: Anti-Slop (tests validan importación sin error)
- ✅ S9: Logging (logger configurado en core.py)
- ✅ B10: Checkpointing (PLAN.md presente)
- ✅ B11: Validación Deps (test suite: CLI + GUI smoke tests)
- ✅ B3: Angry Paths (documentadas 3 formas de romper)

---

<<<<<<< HEAD
## PRÓXIMOS SPRINTS
=======
## Sprints
| # | Sprint | Item | Entregable / failing-first |
|---|--------|------|----------------------------|
| **5** | **Cero warnings tolerados** | ✅ | `[RECOMENDACIONES POR DOMINIO]` suprimida de gate APPROVED (PI-009 WARN→BLOCK). Solo aparece cuando hay FAILs activos. Refactor `_print_recommendations` (C901). Test: gate APPROVED → sin recomendaciones; zombie → recomendaciones visibles. Commit `feat(sprint5)`. |
| **6** | **Auditoría profunda de exclusiones** | ✅ | Barrer whitelists/excludes/skips/`xfail`/`noqa`/`# type: ignore`/`pytest.skip`/`except…continue`. Cada exclusión: justificada-y-mínima o eliminada. Cero xfail-expected, cero stub/mock/placeholder. Test: exclusión injustificada nueva → detectada y convertida en fallo. |
| **7** | **Naming descriptivo total** | ✅ | 23 renames verb_noun (git mv, historia preservada). `import_error_guard.py`→`scripts/repair_failing_tests.py` + CLI guard. 17/17 satélites re-sync. Commit `feat(sprint7)`. |
| **8** | **Aplanado estructural + KISS** | ✅ | Ejecutado: flatten de entrypoints operativos y veredicto KISS por subsistema. |
| **9** | **Golden Standard = conocimiento puro** | ✅ | Ejecutado: PI-015..PI-018 formalizan aprendizaje puro, batch-authorization, ratchet y ingestión canónica satélite. |
| **10** | **Repos externos + vigilancia en vivo** | ✅ | 36 repos auditados con fuentes oficiales; matriz INTEGRAR/COMPLEMENTAR/DESCARTAR/BACKLOG cerrada; deepdive selectivo en token-saving + arquitectura simple; vigilancia en tiempo real absorbida sin duplicar Golden Standard. |
| **11** | **Auditoría 12D completa + veredicto** | ✅ | Guías `00 audit/` refrescadas, auditoría adversarial ejecutada, reporte canónico emitido y stale root `implementation_plan.md` retirado. |
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b

1. **Sprint 1:** Implementar Path 1 (Permission Denied handling)
2. **Sprint 2:** Implementar Path 2 (Symlink loop detection)
3. **Sprint 3:** Implementar Path 3 (Disk full detection + rollback)
4. **Sprint 4:** Integración tests (end-to-end con directorios reales)

---

<<<<<<< HEAD
**Status:** ✅ PLAN APROBADO PARA EJECUCIÓN
**Auditor:** Claude (CoderCerberus v0.5)
**Fecha:** 2026-06-02
=======
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

---

## Sprint 28.5 — Refactor a paquete `dimensions/` + integración real (PRE-29, BLOQUEANTE)
**Principio rector (usuario, 2026-05-31):** las dimensiones nuevas deben *enforzar de verdad*. "N dimensiones" = N defensas ejercidas sobre I/O real, no verdes huérfanos. **Forma elegida:** refactor a paquete con contrato + registry (no parchar el monolito, que es la inextensibilidad que causó las enhanced).

### Hallazgos que disparan el sprint (auditoría 2026-05-31)
- **H1 — Arquitectura dual:** monolito `run_security_audit_12d.py` (D1–D12, cableado vía `run_compliance_tests.py:44`) vs `d3/d7/d11/d13/d14_*.py` (886 líneas, **sin caller** salvo sus tests). D7 y D11 implementados dos veces.
- **H2 — Teatro de gate:** tests enhanced son unitarios con mock/vacío; no auditan repo real. 96 `theater_risk_*.json` con `verified:false`.
- **H3 — Dos clases de dimensión:** A=auditan repo (D3/D7/D11 → canal gate). B=auditan al agente (D13 observable, D14 discourse `response`) → **canal hook runtime** (decisión usuario). B no puede entrar al auditor forense.
- **H4 — Fallo silencioso:** `d7_security_enhanced.py:54` `except: return []`. Binario ausente = PASS falso. **RESUELTO parcialmente:** bandit 1.9.4 / semgrep 1.164.0 / trivy 0.70.0 instalados y verificados (bandit ya halla B602 HIGH real en `scripts/`). Falta: ausencia de binario → `UNAVAILABLE` ruidoso, no `[]`.
- **H5 — Sin mapa confiable:** `codebase_map.json` (local, ruido) + `MAPA_FUNCIONAL.md` (prosa stale) no ahorran tokens → reviews re-derivan con grep.
- **H6 — Dos taxonomías de test:** `test_sprint*_tier*.py` (por sprint) vs `test_d*.py` (por dimensión). Mismo desorden dual en los tests.

### Arquitectura objetivo (S2 brain-first)
```
dimensions/
  __init__.py     # REGISTRY = [D1..D14]; auto-registro
  base.py         # Dimension(Protocol): audit(ctx) -> list[Finding]; Finding con status PASS/WARN/FAIL/UNAVAILABLE
  context.py      # AuditContext: file_list + ast_cache calculado UNA vez (conserva la pasada única del monolito)
  d1_integrity.py ... d14_*.py   # un módulo por dimensión, SIN main()
```
- `run_security_audit_12d.py::run()` se vuelve loop sobre `REGISTRY` con `AuditContext` compartido → un veredicto, una pasada. Conserva la virtud del monolito, elimina su inextensibilidad.
- **Canal gate:** D1–D12 + D3/D7/D11-enh absorbidas como módulos (S19/VC-118: reemplazan inline donde el concern es idéntico, sin puentes). **Trivy invocado una sola vez** (dedupe).
- **Canal hook runtime** (`pre_edit_guard.py`/Stop hook): D13/D14, WARN-only hasta calibrar.
- **`dimension_registry.json`** generado desde `REGISTRY`, committeado, fresh-gated por `run_compliance_tests.py` (falla si `git_sha ≠ HEAD`). Campos: `channel`, `wired`, `binary_available`, `test_audits_real_repo`. Reemplaza `MAPA_FUNCIONAL.md` (git rm), absorbe `codebase_map.json`.

### Angry Path (B3 — 3 formas de romperlo)
1. **Regresión de pasada única:** módulos que re-caminan el árbol/re-parsean AST → gate 12× más lento. Mitigación: `AuditContext` calcula file_list+AST una vez; test de perf antes/después.
2. **Refactor pierde cobertura:** mover 12 métodos a módulos rompe detección silenciosamente. Mitigación: migración dimensión-por-dimensión; cada módulo entra con su test falsable (fixture malo→FAIL, limpio→PASS) ANTES de borrar el método inline.
3. **Hook D14 bloquea respuestas legítimas:** umbral clarity mal calibrado. Mitigación: D13/D14 WARN-only en primer release; nunca BLOCK sin corpus de calibración.

### Pasos (failing-first, S8 ≤50 líneas/turno)
1. **Registry ledger (documenta verdad inerte):** `dimension_registry.json` + generador; test que refleja estado actual. Verificable hoy.
2. **`dimensions/base.py` + `context.py`:** contrato `Dimension` + `Finding(status=UNAVAILABLE)` + `AuditContext`. Tests del contrato.
3. **Migrar 1 dimensión piloto** (D7: tiene inline + enhanced + binario vivo) → módulo `d7_security.py`, test falsable real-repo, `run()` la consume vía REGISTRY, borrar inline (sin puente).
4. **Migrar resto Clase A** (D1–D6, D8–D12, D3/D11-enh) una por turno; dedupe trivy.
5. **Wire Clase B al hook** (D13 observable, D14 discourse), WARN-only.
6. **Consolidar tests:** reabsorber `test_sprint*_tier*.py` en `test_d*.py` (1 por dimensión, falsable).
7. **Purga:** `git rm MAPA_FUNCIONAL.md`; absorber codebase_map; `gate_output.txt` fuera de git; retención `.protocol/evidence/`.

### Hecho cuando
- Toda dimensión en `dimension_registry.json` con `channel`+`wired:true` (o `UNAVAILABLE` honesto), fresh-gated.
- Cero dimensión que reporte PASS sin auditar I/O real. 1 test falsable por dimensión.
- `run()` = loop sobre REGISTRY, pasada única. Recién entonces Sprint 29 (D15).

### Decisión 2026-06-01 (usuario: "volver todo real y cablearlo")
Los 3 huérfanos que rompen `test_all_scripts` se vuelven reales + cableados (no se borran, salvo el teatro que el real reemplaza). Orden por riesgo creciente:
1. **d3 piloto (offline, determinista)** — `dimensions/d3_dead_code.py` = ruff F (imports/locals) **+ vulture solo para funciones/métodos/clases/código-inalcanzable** (el hueco de symbol-table). Reemplaza inline `audit_dead_code()` (S19). `git rm` de `d3_dead_code_enhanced.py` (teatro: duración hardcodeada) + su test.
2. **d11** — requiere red (PyPI/OSV reales) + resolver colisión de etiqueta (inline D11 = SCA Trivy, otra cosa que el "enhanced" dependency-validator). Diseño antes de codear.
3. **d13/d14** — construir canal hook runtime, WARN-only. **d14 HECHA (2026-06-01):** migrada a `dimensions/d14_discourse_rigor.py` canal hook (audit_response), `git rm` del script standalone; falta el caller runtime real (fully_wired False honesto). Pendiente: d13 + canal hook.

**Diseño d3-real (decisión técnica, NO exclude-para-pasar):** vulture "unused variable" se excluye del gate porque (a) los locals reales ya los toma ruff F841, (b) el subconjunto de *parámetros* produce falsos positivos estructurales (firmas de callback obligatorias). Esto es scoping, no whitelist — los hallazgos de params se enrutan abajo, no se entierran.

**Hallazgos de params sin usar (vulture conf 80, 2026-06-01) — cleanup separado:**
- P-VC1 (BUG): `check_empirical_proof.py:32` `check_proof(claim)` **ignora `claim`** — valida evidencia sin mirar el claim. ¿Bug o intencional? Requiere decisión del usuario.
- P-VC2 (FALSO POSITIVO): `protocol_cli.py:97` `_onerror(func, path, exc_info)` — firma obligatoria de `shutil.rmtree(onerror=)`. NO tocar.
- P-VC3 (feature incompleto): `compress_memory_context.py:67` y `helpers.py:147` `compress_memory_block(max_tokens)` ×2 — presupuesto nunca aplicado.
- P-VC4 (opción muerta): `manage_tokens.py:44` `process_output(command_type)`; `repair_failing_tests.py:18` `run_tests(stop_on_fail)`.

### d11 recalibrado (hallazgo 2026-06-01: superficie de deps real ≈ 1)
**Causa raíz:** el repo NO tiene manifiesto. `cerberus-gatekeeper.yaml:27` tiene `if [-f requirements.txt]...else pip install pytest pyyaml` — el `else` es teatro porque el archivo nunca existió. El enhanced d11 leía ese `requirements.txt` inexistente → teatro doble (lógica fake + sin input). Deps third-party reales (derivadas de imports): **solo `PyYAML==6.0.3`** runtime + `pytest==9.0.3` test. `rich` se instala (install_cerberus.ps1) pero **NO se importa en ningún lado** → grasa.

**Decisión usuario (recalibrada):** d11 LEAN, sin cache/TTL (sobre-ingeniería para 1 dep; Trivy ya cubre CVEs). Pasos:
1. `requirements.txt` pinneado real (PyYAML, pytest) → mata el fallback-teatro del CI + da input a Trivy/d11. Registrar en SPEC.
2. `dimensions/d11_dependency.py` = Trivy SCA (consolida el inline `audit_d11_validate_sca_trivy`, S19) + check PyPI outdated/yanked SIMPLE (consulta directa, WARN si offline; sin estado/cache). Cablear vía REGISTRY, borrar inline, `git rm` teatro `d11_dependency_enhanced.py`+test.
3. Limpiar `rich` de install_cerberus.ps1; simplificar CI a `pip install -r requirements.txt` (quitar fallback).

**Hallazgos d11 (cleanup):** P-D11a `rich` dead-install; P-D11b CI else-fallback teatro; P-D11c install scripts no usan single-source-of-truth.

### d7 diseño (próxima migración, Clase A gate, dual-impl) — 2026-06-01
**Causa raíz:** inline `audit_d7_data_security` = escaneo regex de secretos/inyección (real, sin binario, cableado). Enhanced `d7_security_enhanced.py` = SAST merger bandit+semgrep+trivy con `except: return []` ×3 (fallo silencioso H4) + trivy DUPLICADO con d11.

**Diseño d7-real** `dimensions/d7_security.py` (gate): inline regex (preservar, superset) + bandit + semgrep. **SIN trivy** (d11 lo posee, dedupe). Binario ausente → UNAVAILABLE (no `[]`). Resolver bandit/semgrep en `~/.local/bin` (pipx) + `python -m bandit`, no solo PATH. Umbral **HIGH** (enforcement real).

**Blast-radius medido (B3):** bandit HIGH = 1 solo: B602 `shell=True` en `core_utils.py:69`. **Fix honesto SIN supresión:** `run_command` usa `shell=is_shell` (string→shell), pero TODOS los callers pasan listas → el modo shell es código muerto → `shell=False` siempre lo elimina. B310 (urlopen en d11) y B608 (track_tokens SQL) son MEDIUM, no bloquean en HIGH. semgrep p/security-audit: blast-radius NO medido aún (lento+red) — riesgo a verificar en implementación.

**Pasos d7:** 1) fix B602 (core_utils shell=False). 2) `dimensions/d7_security.py` regex+bandit+semgrep, UNAVAILABLE, umbral HIGH. 3) cablear REGISTRY, borrar inline `audit_d7_data_security` (S19), `git rm d7_security_enhanced.py`+test (migrar tests). 4) regen ledger (d7 dual→package). 5) verificar gate APPROVED + suite + commit.

**d7 HECHA (2026-06-01):** ✅ todos los pasos. Ajustes vs plan: semgrep DIFERIDO (red+latencia en gate por-commit; bandit cubre Python SAST). _SCAN_EXTS igualado al inline (.py/.html/.js/.css). Gate APPROVED, suite 444 pass. Follow-ups: semgrep en hook/CI; ampliar exts d7 a .yaml/.sh. **Restan: d13 (hook) + canal hook runtime real.**

### Cierre de Sprint 28.5 — d13 + canal hook runtime (decisión usuario 2026-06-01)
**Objetivo:** cumplir el "Hecho cuando" de 28.5 — toda dim cableada o UNAVAILABLE honesto; D13/D14 enforcando de verdad (no verdes huérfanos). Solo entonces Sprint 29.

**Parte A — d13 migración (chico, como d14):** `dimensions/d13_observable.py` canal hook. Los 4 scripts `d13_token_meter`/`d13_decision_logger`/`d13_divergence_detector`/`d13_observable_behavior` (D13Report orchestrator) → consolidar/envolver en una Dimension. d13 NO es pass/fail de una respuesta como d14: es OBSERVABILIDAD (tokens, decisiones, divergencia vs AGENT.md). Su entrada hook = observar/loguear, no bloquear. `git rm` de los scripts standalone (S19), repuntar tests, registrar en REGISTRY (channel hook, fully_wired tras tener caller).

**Parte B — canal hook runtime (la pieza novedosa):** base = `scripts/pre_edit_guard.py` (PreToolUse hook, stdin JSON, exit 0/2, enforce S6/S7/S19).
- **DISEÑO RESUELTO (2026-06-01):** el **Stop hook** de Claude Code recibe por stdin JSON `{session_id, transcript_path, stop_hook_active}`. El `transcript_path` es el JSONL de la sesión → leer el ÚLTIMO mensaje `role:assistant` y extraer su texto (la prosa de respuesta) = la fuente real de `audit_response`. Nuevo `scripts/discourse_hook.py`: lee stdin, parsea transcript, corre `D14.audit_response(text)` + observabilidad d13, imprime WARN, exit 0 (Stop no bloquea de forma dura; surface-only). Cablear en `.claude/settings.json` hooks.Stop. Guardas: `stop_hook_active` para no recursar; tolerar transcript ausente/parcial (no crashear el turno).
- **WARN-only primero** (decisión previa): nunca BLOCK sin corpus de calibración. El hook emite WARN visible, no exit 2.
- d13 observabilidad: correr en Stop (loguear tokens/decisiones de la sesión).
- Cablear en `.claude/settings.json`. Tras tener caller → `_package_impls` marca d13/d14 wired=True (actualizar la regla `channel=="gate"` a "tiene caller").

**Angry path:** (1) hook no puede ver la prosa → audit_response sin fuente real → quedaría teatro. Mitigación: confirmar capacidad ANTES de codear; si no hay fuente, d14 se queda como herramienta CLI/CI honesta (no fingir hook). (2) WARN ruidoso en cada respuesta → fatiga. Mitigación: umbral + WARN-only. (3) hook lento bloquea cada turno. Mitigación: rápido, sin red.

**Pasos failing-first:** A1 d13 módulo+test, A2 wire REGISTRY+regen+gate, A3 commit. B1 investigar capacidad de hooks (¿fuente de response?), B2 hook script + settings, B3 audit_response cableado WARN-only + test, B4 actualizar generador (wired=tiene-caller), B5 verificar + commit.

**✅ SPRINT 28.5 CERRADO (2026-06-01):** las 14 dimensiones fully-wired (gate vía REGISTRY o hook vía `discourse_hook.py`). d13 migrada a `dimensions/d13_observable.py` (consolida los 4 d13_*, tiktoken→requirements.txt); d14 + d13 cableadas al Stop hook (d14 audit_response, d13 observe_session). Generador `_hook_caller_exists`. count 14/14, gate APPROVED, suite 450 pass. El "Hecho cuando" se cumple. **Recién ahora desbloqueado Sprint 29 (ReviewBot).** Follow-ups menores: semgrep en hook/CI, d7 exts .yaml/.sh, generador escanee dimensions/ para huérfanos, calibrar umbral D14 antes de pasar de WARN a BLOCK, limpiar cirílicos "auditа".

### C3 — Grafo Capa 1 interno (Deuda #3, ancla VC-069) — 2026-06-06
**Causa raíz (B9):** el grafo actual (`generate_graph_report.py` → `.protocol/metadata/graph.json`) es **Capa 2** (ecosistema: 17 satélites del REGISTRY). NO modela el código interno de Cerberus (módulos .py, imports, huérfanos, god-nodes). Por eso la auditoría interior 2026-06-06 detectó huérfanos/consumidores con grep manual en vez de consulta al grafo.

**Decisión Luis (Fase A aprobada):** **Adoptar graphify** (motor externo `graphifyy`, NO construir desde cero). B11 OK: `graphifyy` v0.8.33, MIT, Safi Shamsi (`github.com/safishamsi/graphify`), tree-sitter AST, extracción code-only OFFLINE (sin API keys). Instalación aislada y reversible vía **pipx** (1.13.0).

**Angry Path (B3 — 3 formas de romper):**
1. **Colisión de artefactos:** graphify podría emitir `graph.json`/`GRAPH_REPORT.md` en CWD → clobbearía la Capa 2 (`.protocol/metadata/graph.json` + `GRAPH_REPORT.md` raíz). Mitigación: correr SIEMPRE con salida a dir aislado, JAMÁS en raíz; verificar antes de integrar.
2. **Mismatch de esquema:** la Capa 1 necesita orphans/god_nodes/entry_points/consumers_of; el output de graphify puede tener otro esquema → integrarlo a ciegas rompe consumidores. Mitigación: inspeccionar el JSON real ANTES de cablear; derivar, no asumir.
3. **Contaminación de entorno:** instalar en el venv del proyecto arrastra tree-sitter + N deps → infla superficie d11 (recalibrada a ≈1 dep). Mitigación: pipx aísla en su propio venv; graphifyy NO entra a requirements.txt; es herramienta de análisis, no dependencia runtime.

**Pasos failing-first:**
1. `pipx install graphifyy` (aislado). `graphify --help` → descubrir el CLI REAL (flags, code-only, output path).
2. Correr code-only sobre `scripts/`+`protocol_engine/` con salida a dir AISLADO. Inspeccionar output crudo.
3. Comparar esquema emitido vs necesidad Capa 1. Decidir: ¿usar directo, derivar, o envolver?
4. Integrar (wrapper que invoca graphify + normaliza) SIN tocar la Capa 2. Gate verde + test falsable.
5. Registrar en SPEC. Rollback: `pipx uninstall graphifyy` + borrar dir aislado.

---

## Sprint 3.6 — VC-140 Norma de Continuidad (Handoff agnóstico)

**Objetivo:** trabajo continuo entre agentes (Codex/Gemini/Claude) sin pérdida de
contexto. Cada commit deja un relevo claro para el siguiente agente. Diseño aprobado
por Luis: **bloqueante con escape** + **HANDOFF.md vivo**. Orden GS-first → Cerberus → satélites.

**Diseño:**
- Artefacto canónico `HANDOFF.md` (vivo, se sobrescribe por commit). Esquema fijo:
  ESTADO / SIGUIENTE / BLOQUEOS / VERIFICAR / NO HACER. Histórico en HISTORIAL.md.
  Plantilla `HANDOFF.template.md`.
- Mecanismo `scripts/check_handoff_freshness.py` → función pura
  `check_handoff_freshness(staged, handoff_text, msg) -> (ok, reason)`. Bloquea si hay
  cambio sustantivo staged y HANDOFF.md no está staged o le faltan secciones
  obligatorias (ESTADO/SIGUIENTE/VERIFICAR). Triviales que no exigen relevo: HANDOFF/HISTORIAL/STATUS.
- Enforcement agnóstico: hook git `commit-msg` (ve staged + mensaje). Plantilla versionada
  en `scripts/hooks/commit-msg`, instalada por install_hooks.sh/.ps1 → satélites heredan.
- Escape: `[skip-handoff]` en el mensaje o `CERBERUS_SKIP_HANDOFF=1`.

**Angry Path (B3):** (1) agente olvida `git add HANDOFF.md` → bloquea (deseado).
(2) HANDOFF.md vacío → el chequeo de esquema bloquea. (3) commit-msg sí ve staged vía
`git diff --cached` (el commit aún no existe) — validado con test.

**Pasos:** [x] GS VC-140 PREVENTED · [x] template+script+tests · [ ] wire commit-msg+installer
· [ ] regen GS audit DB→copiar→normalizar · [ ] SPEC+HISTORIAL+dogfood HANDOFF.md · [ ] sync+suite+gate+commit
· [ ] propagación satélites (go explícito).

---

## Sprint 3.7 — Blast Radius real (grafo de código) · PLAN para Gemini/Codex

**Origen:** propuesta de Codex (8 pasos) para que el grafo deje de ser solo de
conocimiento/navegación y responda "qué código rompe este cambio". **Diseño-first (S2):
NO codear hasta que Luis dé go.**

### Reconciliación con lo que YA existe (B1 — verificado en código, no asumido)
`scripts/internal_graph.py` (Capa 1, ya en repo) **ya cubre los pasos 2-3 de Codex**:
- Construye grafo AST vía **graphify** OFFLINE (relaciones `calls`/`imports`/`references`).
- `derive_internal_graph()` ya deriva: `node_count`, `edge_count`, `god_nodes` (grado≥umbral),
  `orphans` (código muerto), `entry_points` (raíces), y **`consumers_of`** = mapa inverso
  directo = **la semilla del blast radius (1 salto)**. Artefacto: `.protocol/metadata/internal_graph.json`.
- Capa 2 = `.protocol/metadata/graph.json` (ecosistema 17 satélites). **NO mezclar** (Codex paso 1 ✔ ya respetado).

→ Codex no sabía que esto existía. **No reconstruir el extractor AST. Extender lo que hay.**

### Gaps REALES (lo único que falta de los 8 pasos)
| Codex | Estado | Gap a implementar |
|------|--------|-------------------|
| 1 Dos capas separadas | ✅ hecho | — (internal_graph vs graph) |
| 2 Inventario AST | ✅ hecho | graphify ya extrae imports/calls/refs |
| 3 Grafo de código | ✅ hecho | nodos+aristas ya en internal_graph.json |
| 4 Blast radius | ⚠️ parcial | `consumers_of` es **1 salto**. Falta: **cierre transitivo inverso**, **ciclos**, **fan-in/fan-out explícito**, **clasificación local/medio/alto/sistémico** |
| 5 Preflight | ❌ falta | `preflight_compliance.py` debe imprimir impacto del archivo tocado antes de editar |
| 6 Tooling CLI | ❌ falta | comando `blast` en `protocol_cli.py` (dispatch dict l.552, patrón `_delegate`) |
| 7 GS puro | ✅ política | NO meter rutas/imports de Cerberus en GS; solo insight agnóstico (abajo) |
| 8 Validación | ❌ falta | tests falsables: ciclos, fan-in excesivo, blast subestimado |

### Pasos para el agente fresco (orden, S8 ≤50 líneas/turno)
1. **`scripts/blast_radius.py`** — función PURA `compute_blast(internal_graph, target) -> dict`
   con: `direct` (=consumers_of[target]), `transitive` (BFS sobre el inverso hasta fixpoint),
   `fan_in`/`fan_out`, `in_cycle` (bool), `severity` (umbral sobre |transitive|:
   local/medio/alto/sistémico). **Lee internal_graph.json existente, no re-parsea AST.**
2. **Tests** `tests/test_blast_radius.py` — path negativo obligatorio (D8): grafo con ciclo
   A→B→A detecta `in_cycle`; cambio en god-node clasifica `sistémico`; hoja = `local`;
   blast subestimado falla (assert sobre tamaño del cierre transitivo).
3. **CLI** `protocol_cli.py`: añadir `"blast": lambda: self._delegate("scripts/blast_radius.py", argv[1:])`
   al dispatch (l.552). Responde "qué depende de este archivo/módulo".
4. **Preflight** `preflight_compliance.py`: al detectar archivo staged, imprimir su `severity` +
   consumidores directos (advertencia, NO bloqueo en v1).
5. **GS (paso 7, GS-first si se toca doctrina):** importar SOLO el insight agnóstico —
   *"antes de editar, calcular el radio de impacto inverso (quién depende de esto), no solo
   el directo"*. Vía `Inbox/cerberus/` (no editar Wiki curada). Candidato a vicio tipo
   "edición sin blast radius inverso". **No meter rutas de Cerberus en GS.**

### Angry Path (B3 — 3 formas de romperlo)
1. **internal_graph.json desactualizado** → blast miente. Mitigación: `blast_radius.py` exige
   timestamp fresco o regenera vía `internal_graph.py` antes de calcular.
2. **Ciclos → BFS transitivo infinito**. Mitigación: set de visitados + fixpoint (test del ciclo A→B→A).
3. **graphify solo ve Python** (`_only_python`). Aristas hacia `.sh/.ps1/config` NO existen →
   blast hacia runners se subestima. Mitigación: documentar el límite; v1 = solo código Python.

### Definición de cierre
`protocol_cli blast scripts/foo.py` responde: archivos que rompe (transitivo), severidad,
si está en ciclo. Tests verdes + gate APPROVED. GS gana 1 insight agnóstico, sin fugas de rutas.

---

## Sprint 3.8 — Fase 2c: acotar "símbolo crítico" + gate align-check opt-in  🟢 EN CURSO (2026-06-07)

**Objetivo:** 0 deuda de alineación Código↔Docs en Cerberus SIN bloquear los 17 satélites no
documentados. Cierra el ADVISORY de Fase 2 (commit `f647e1e`).

**Evidencia empírica** (`internal_graph.json` Cerberus): `god_nodes=21`, `entry_points=140`, extraction=ok.
- 140 entry_points = todo `_main` → exigirles doc es ruido (no es criticidad).
- 21 god_nodes: **7 artefactos mecánicos** (`ast` import stdlib + 6 `*_py_path` constante
  `Path(__file__)`) + **14 hubs reales documentables** (protocol_engine init/knowledge_loader,
  core_utils run_command/setup_windows_utf8, protocol_cli ProtocolClient.run/.log_evidence,
  run_security_audit_12d DeepForensicAuditor.run, validate_external_audit_phases ×4).

**Diseño (3 sub-pasos, failing-first):**
1. **2c-a** `alignment_checker._is_documentable_symbol(sym, namespaces)` puro: excluye sufijo
   `_py_path` + símbolos cuyo 1er segmento no está en namespaces de código del repo (`ast`→externo).
   `detect_code_orphans`: critical = **god_nodes documentables** (NO entry_points).
2. **2c-b** Gate **opt-in**: bloquea SOLO si existe `.protocol/align_gate.enabled`. Ausente →
   FAIL se reporta como WARN, exit 0 (satélites quedan ADVISORY hasta documentar — anti-brick).
3. **2c-c** `docs/architecture/CODE_MAP.md` NEW: mapa real de los 5 módulos núcleo + 14 símbolos
   con `[[refs]]` (resueltos por alias 2b). Crear marcador en Cerberus. align-check → exit 0, 100%.

**Angry Path (B3):** (1) brick de 17 satélites al propagar pre-commit bloqueante → gate opt-in.
(2) verde ceremonial (prosa vacía) → PROHIBIDO; CODE_MAP describe función real de cada hub.
(3) filtro demasiado agresivo → exclusiones explícitas (`_py_path`+namespace), test símbolo-a-símbolo.

**Hecho cuando:** `align-check --repo-root .` → exit 0, FAIL=0, cobertura 100% · pytest verde ·
auditor APPROVED · árbol limpio. NO propagar a satélites (PASO 3, requiere go de Luis).
<<<<<<< HEAD
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
=======

---

## Sprint 3.9 — PASO 3: Reparar binding satélites (junction self-heal) + propagar

**Go de Luis:** "paso 3" → al descubrir sustrato roto, eligió **"Reparar modelo antes de propagar"**
y modelo **"Junction repointado + self-heal"**.

**Causa raíz (B9):** los 17 satélites referencian el protocolo vía junction `.protocol-core`
apuntando a `D:\AI\Cerberus\rules` — subdir que **NO existe** (el protocolo vive en la raíz
`D:\AI\Cerberus`). Cerberus se reorganizó (de `D:\GoogleDrive\AI\Cerberus` con layout `rules/`
→ `D:\AI\Cerberus` plano); los junctions quedaron colgando. **Enforcement muerto en los 17.**

**Evidencia:** `Get-Item .protocol-core` → `LinkType=Junction Target=D:\AI\Cerberus\rules`;
`ls rules/` → NO EXISTE; `ls .protocol-core/` → 0 items en Declutter/Quenza/Indices/RED-Python;
`git ls-files .protocol-core` → 0 (gitignoreado, `.gitignore:36`). 3 sin `.git` (Frankenstein,
Alesa Inc, Amparo Pensiones) → se saltan. Ningún satélite tiene `internal_graph.json`.

**Modelo objetivo:** `.protocol-core` = junction → `D:\AI\Cerberus` (raíz viva, derivada del
`__file__` del propio script de reparación = auto-localización robusta). Gitignoreado (ya lo está).

**Diseño (atómico, failing-first, canary antes de batch):**
1. **3-a** `scripts/repair_protocol_junction.py` NEW (~50L): `canonical_core_root()` (de `__file__`),
   `junction_status(sat, core) -> ok|missing|broken|wrong_target` (puro), `repair_junction(sat, core,
   dry_run)` (idempotente: ok→noop; si no, rmdir junction + `mklink /J`). main `--repo-root` | `--all`
   (de REGISTRY) | `--dry-run`. Gate: `test_repair_junction.py` con tmp dirs.
2. **3-b CANARY (RED-Python):** reparar junction → `install_hooks_in_satellite` → generar
   `internal_graph.json` local → commit de prueba que dogfood VC-140/VC-141/align-check ADVISORY.
   Verificar end-to-end ANTES de tocar los otros.
3. **3-c BATCH:** repetir en los 12 satélites con `.git` restantes. Los 3 sin git se reportan, no se
   fuerzan. align-check queda **ADVISORY** en todos (sin marcador `align_gate.enabled` → anti-brick).
4. **3-d** Reconciliar `global_sync_safe.py`/`migrate_to_subtree.py`: el modelo es junction, NO
   subtree-pull. Sin puentes zombie (S19) — la ruta de propagación canónica pasa a junction-repair.

**Angry Path (B3):** (1) `mklink /J` requiere que el target exista y el link NO exista → borro junction
colgante primero (rmdir, no del recursivo que seguiría el reparse). (2) batch ciego corrompe 12 repos
reales → CANARY verificado primero + commits acotados a hooks/grafo. (3) self-heal borra datos del
usuario si confunde un dir real con junction → `repair` SOLO actúa si `LinkType==Junction` o entrada
colgante, jamás sobre dir normal con contenido. (4) Cerberus se mueve otra vez → self-heal re-deriva
de `__file__` y repunta; documentar en SPEC que el junction es efímero/regenerable.

**Hecho cuando:** los 12 satélites con git tienen junction válido → `.protocol-core/scripts/protocol_cli.py`
resuelve · hooks instalados · `internal_graph.json` generado · commit de prueba pasa el hook · pytest
verde · auditor APPROVED. Los 3 sin git: reportados en HANDOFF. NO se propaga el marcador del gate.
>>>>>>> c3854ffde03996103a886749dc656aa35f6d8888
