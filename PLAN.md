# PLAN — Post-Auditoría Adversarial 4 Fases
**Cerberus V0.02 | 2026-05-28 | 329/329 tests passing**

Orden de ejecución: mayor valor y trascendencia primero.
Cada ítem tiene: evidencia, impacto, fix concreto, criterio de done.

---

## ESTADO ACTUAL
- Suite: 329 passing / 0 failing
- audit_10d: APPROVED (10/10 dominios D1-D10)
- Adopción satélites: 16/16 (100%) — Test_Fantasma eliminado del registry
- Deuda activa: ninguna (P8.0 + P8.1 cerrados 2026-05-28)
- Rama: master

---

## P1–P3 — SPRINTS COMPLETADOS ✅

| Sprint | Fixes | Commit |
|---|---|---|
| P1 (infraestructura) | sys.path bootstrap en protocol_cli + rigor_maestro; cache_protocol_rules repurposed a PROTOCOL_*.md; TOKEN_BUDGET centralizado en core_utils | Sprints 1-2 |
| P2 (gobernanza) | PROTOCOL_SYSTEM.md → audit_8d primario; test_resilience: assertIn→assertEqual; auto_export: regex case-insensitive | Sprint 3 |
| P3 (deuda AST) | 10 scripts, profundidad 8/6/5 → ≤4; empirical_proof_checker, protocol_cli, helpers, memory_compression_reme, auto_export, global_sync_safe, review_queue, state_checkpoint, sync_binding, token_manager | `6245d78` |

---

---

## P4 — HALLAZGOS AUDITORÍA DIRECTA vs GOLDEN STANDARD (2026-05-27)

Auditoría directa bidimensional: TIENE el vicio / PREVIENE el vicio.
214 vicios auditados (110 VC + 104 VT). Score: 82% limpio.
**Regla operativa:** Todo hallazgo encontrado durante cualquier sesión se registra aquí.

---

### P4.1 — `helpers.py` 3 stubs permanentes en producción ❌ CRÍTICO
**Vicios:** VC-061 (Stub como arquitectura), VC-078 (Placeholder permanente), VT-002 (Stub permanente), VT-090 (Placeholder testeado)
**Evidencia:**
- `_collect_tokens()` l.224: retorna `list(token_source)` sin lógica real — docstring dice "placeholder"
- `_compact_tokens()` l.232: retorna `tokens` sin modificar — docstring dice "Real implementation would apply compression heuristics"
- `_process_queue_item()` l.250: siempre retorna `True` — docstring dice "Placeholder — real validation logic should be inserted here"

**Impacto:** Cualquier sistema que llame a estas funciones recibe comportamiento trivial sin error visible. D8 detecta el marcador "placeholder" en docstrings pero no bloquea merge porque helpers.py está en SPEC.md whitelist.

**Fix:** Decidir entre dos opciones antes de implementar:
- **A (recomendada):** Implementar lógica real de compresión de tokens y validación de queue items
- **B:** Eliminar las 3 funciones si no tienen callers reales (verificar con D3 dead code)

**Done cuando:** `grep -n "Placeholder\|placeholder" scripts/helpers.py` devuelve vacío.

---

### P4.2 — `audit_8d.py:21` sys.path frágil ❌ CRÍTICO
**Vicios:** VC-109 (Ruta literal ambiental), VT-080 (Acoplamiento de Dirección Física)
**Evidencia:** `sys.path.append(os.getcwd())` — el auditor usa el anti-patrón que prohíbe. Falla si se invoca desde CWD distinto al proyecto.

**Fix:** Reemplazar línea 21:
```python
# audit_8d.py:21 — reemplazar:
sys.path.append(os.getcwd())
# por:
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

**Done cuando:** `cd C:\ && python D:\GoogleDrive\AI\Cerberus\scripts\audit_8d.py` produce APPROVED sin ImportError.

---

### P4.3 — `audit_8d.py` 2 silent `except Exception: pass` reales ⚠️ MEDIO
**Vicios:** VC-014 (Falso positivo de auditoría), VT-040 (Excepción absorbida)
**Evidencia:**
- `l.626` (D7): `except Exception: pass` en lectura de archivo — un archivo ilegible pasa D7 silenciosamente
- `l.911` (D9 CI yml): `except Exception: pass` — error leyendo workflow YAML pasa D9 silenciosamente

Los 6 `except SyntaxError: pass` son defensivos (archivos no-Python que no parsean); los 2 `except Exception: pass` son swallowers reales.

**Fix:** Cambiar a logging en vez de silencio:
```python
except Exception as e:
    logging.debug("D7: skipped %s — %s", f.name, e)
```

**Done cuando:** Errores de lectura de archivo y de CI yml se logean en DEBUG en vez de desaparecer.

---

### P4.4 — `SPEC.md:124` descripción obsoleta de cache_protocol_rules ⚠️ MEDIO
**Vicios:** VC-063 (Documentación mentirosa), VT-091 (Dominio documentado no implementado)
**Evidencia:** `SPEC.md:124` dice "generates .claude/cache/protocol_rules.json from REGLAS/". REGLAS/ ya no existe. El script fue repurposado en P1.3 para leer PROTOCOL_SYSTEM.md + PROTOCOL_BEHAVIOR.md.

**Fix:** Actualizar línea 124 de SPEC.md:
```
scripts/cache_protocol_rules.py (v2.0, FASE 5: Token-saving — indexes PROTOCOL_SYSTEM.md + PROTOCOL_BEHAVIOR.md into .claude/cache/protocol_rules.json. 39 mandates cached for fast load.)
```

**Done cuando:** `grep "REGLAS" SPEC.md` devuelve vacío (excepto referencias históricas en deprecated/).

---

### P4.5 — Sin gate de prevención para tests de volumen y calendario ❌ GAP PREVENCIÓN
**Vicios:** VT-047 (Dataset pequeño), VT-050 (No fechas límite)
**Evidencia:** audit_8d no tiene dominio que verifique tests con datos de volumen o fronteras de calendario. Ningún proyecto gobernado está obligado a probar estos casos.

**Fix (governance):** Agregar a CHECKLIST.md una sección "Tests de frontera no funcional":
- [ ] ¿Hay al menos un test con dataset >1000 items para funciones de procesamiento?
- [ ] ¿Hay al menos un test con fechas límite (31 dic, 29 feb, cambio de hora)?

**Done cuando:** Los checks aparecen en CHECKLIST.md y audit_8d los reporta en el auto-checklist.

---

### P4.6 — `CHECKLIST.md` sin gate humano real ⚠️ MENOR
**Vicios:** VC-007 (Auditoría no humana del core)
**Evidencia:** CHECKLIST.md dice explícitamente "Este archivo es informativo — la evaluación es automática." La revisión humana de tests críticos nunca ocurre como gate obligatorio.

**Impacto:** VT-081 (Autor prueba su implementación) queda sin mitigación real — IA escribe código Y tests sin revisión externa.

**Fix:** Agregar al menos 1 check humano bloqueante en el flujo de PR:
- Opción A: GitHub PR template con checkbox manual "Revisé al menos 3 tests adversariales"
- Opción B: `review_queue.py` agrega automáticamente commits de IA a la cola de revisión

**Done cuando:** Existe al menos un gate humano en el flujo que no puede ser auto-aprobado.

---

### P4.7 — Sin dominio de performance en audit_8d ⚠️ GAP PREVENCIÓN
**Vicios:** VC-100 (No funcional ignorado)
**Evidencia:** audit_8d tiene D1-D9 pero ningún dominio mide latencia, throughput ni consumo de memoria. Proyectos gobernados pueden tener regresiones de performance sin detección.

**Fix (governance):** No necesariamente un dominio D10 completo — pero sí un check mínimo:
- Verificar que funciones críticas tienen benchmark de referencia en tests
- O agregar nota en PROTOCOL_SYSTEM.md como mandato S-performance

**Done cuando:** Al menos 1 check de performance existe en el pipeline de validación.

---

## ORDEN DE EJECUCIÓN P4

```
Sprint 5 (integridad del auditor — COMPLETADO):
  [x] P4.2 — audit_8d.py:21 sys.path fix (_ROOT bootstrap)
  [x] P4.3 — audit_8d.py 2 silent Exception → logging.debug
  [x] P4.4 — SPEC.md:124 descripción actualizada a v2.0
  [x] P4.1 — helpers.py 3 stubs eliminados (0 callers, opción B)

Sprint 8 (deuda residual) ✅ COMPLETO:
  [x] global_sync_safe.py --apply: adopción 2/17 → 14/17 (82%).
  [x] P4.5 — tests/test_volume_calendar.py: 12 tests Vol-1/Vol-2 + Cal-1/Cal-2/Cal-3
  [x] P4.7 — tests/test_performance.py: budget <120s/3s/15s para audit_8d/setup_validate/adoption
  [x] P4.6 — Gate humano en PR: .github/pull_request_template.md + CI verifica [x] en body + --enqueue en push
  [x] P4.8 — Bootstrap manual Alesa Inc + Referencias: hook + tests/test_protocol_adoption.py + rm audit_8d.py zombie. Adopción: 16/17 (94%). (2026-05-28)
```

---

*Segunda auditoría: Golden Standard bidimensional (TIENE/PREVIENE) | 2026-05-27*
*Score: 82% limpio en 214 vicios (110 VC + 104 VT). 4 ❌ críticos, ~20 ⚠️ parciales.*

---

## P5 — HALLAZGOS SESIÓN 2026-05-27 (expansión de protocolo, gobierno de exclusiones, nomenclatura)

**Regla operativa:** Todo hallazgo encontrado durante cualquier sesión se registra aquí.

---

### P5.1 — Expansión de protocolo a proyectos hijo: solo se copian archivos, no se verifica adopción real ❌ CRÍTICO (mayor impacto)
**Vicios:** VC-112 (Propagación sin verificación de adopción), VT-095 (Tests del protocolo, no del sujeto)
**Evidencia:** `global_sync_safe.py` copia 7 archivos (AGENT.md, SPEC.md, etc.) a 16 proyectos satélite en cada commit. Pero no verifica: que el proyecto tiene git hooks instalados, que `audit_8d.py` es ejecutable, que el proyecto tiene su propia suite de tests, ni que las dependencias Python están instaladas. Un proyecto puede recibir `SPEC.md` actualizado pero seguir sin hooks y sin auditor activo.
**Impacto:** El protocolo aparece "propagado" en los reportes pero puede estar completamente inoperante en los proyectos hijo. Divergencia entre sincronización formal y adopción real.
**Fix:**
- Agregar a `global_sync_safe.py` un check post-copia: verificar que el proyecto destino tiene `.git/hooks/pre-commit`, `scripts/audit_8d.py`, y `tests/` con al menos un archivo.
- Crear `scripts/verify_protocol_adoption.py`: audita cada proyecto del REGISTRY.json y reporta % de adopción real (hooks + auditor + tests).
- El REGISTRY.json debe tener campo `adoption_verified: true/false` con fecha.

**Done cuando:** `verify_protocol_adoption.py` reporta que todos los proyectos activos del registry tienen hooks instalados, auditor presente y al menos un test ejecutable.

---

### P5.2 — Regla "hallazgo → PLAN.md" existe solo en memoria, no en el protocolo formal ⚠️ MEDIO
**Vicios:** VC-114 (Hallazgo sin plan de remediación), VC-010 (Fallo no convertido en doctrina)
**Evidencia:** La regla operativa "todo hallazgo encontrado durante cualquier sesión se registra en PLAN.md y en memoria" existe únicamente en `memory/feedback_register_findings.md`. No está en AGENT.md, PROTOCOL_BEHAVIOR.md ni CHECKLIST.md. Un agente que no carga memoria no aplica la regla.
**Fix:** Agregar a AGENT.md (sección de mandatos operativos) y a CHECKLIST.md como ítem de cierre de sesión obligatorio:
```
[ ] Todo hallazgo detectado en esta sesión está en PLAN.md con ID, evidencia, fix y done-criteria.
```

**Done cuando:** `grep -n "hallazgo.*PLAN\|PLAN.*hallazgo" AGENT.md CHECKLIST.md` devuelve al menos 1 resultado en cada archivo.

---

### P5.3 — No hay regla que exija auditar el contenido antes de mandarlo a hard_excludes ⚠️ MEDIO
**Vicios:** VC-111 (Exclusión sin auditoría previa), VT-106 (Exclusión no revalidada)
**Evidencia:** El histórico de `audit_8d.py` muestra que se añadieron 28 entradas a `hard_excludes` a lo largo del tiempo, incluyendo 15 que no existían en disco y varias que ocultaban zombis reales (docs/archive/, scratch/). Nunca hubo un step de "audita antes de excluir".
**Regla requerida:** Antes de añadir cualquier entrada a `hard_excludes`:
1. Ejecutar `audit_8d` CON ese directorio incluido y registrar los hallazgos.
2. Si tiene vicios: corregirlos O mover a `deprecated/` (única exención de negocio).
3. Solo si está limpio O va a deprecated: añadir a la lista.
4. Agregar comentario en el código con fecha y justificación.

**Test requerido:** Un test que verifica que cada entrada en `hard_excludes` tiene un comentario explicativo (o que el nombre del directorio es un tooling artifact conocido).
**Done cuando:** Existe test `test_hard_excludes_justificado` que falla si se añade una entrada sin comentario.

---

### P5.4 — Sin test de existencia de git hooks: si no hay githook = fail ❌ CRÍTICO
**Vicios:** VT-105 (Sin test de existencia de hooks), VC-108 (Frontera de seguridad por convención)
**Evidencia:** La suite de 295 tests no incluye ningún test que verifique que `.git/hooks/pre-commit` existe y es ejecutable. El protocolo de 3 capas (Prose + Hooks + Tests) puede estar roto en la capa de Hooks sin que ningún test lo detecte. Hay una única verificación en `protocol_cli.py` pero no es parte de la suite pytest.
**Fix:** Agregar a `tests/test_cerberus_core.py` (o nuevo `tests/test_infrastructure.py`):
```python
def test_pre_commit_hook_exists_and_executable(self):
    hook = Path(".git/hooks/pre-commit")
    self.assertTrue(hook.exists(), "pre-commit hook faltante")
    self.assertTrue(os.access(hook, os.X_OK), "pre-commit hook no ejecutable")
```

**Done cuando:** `pytest tests/ -k "hook"` pasa y falla cuando se elimina `.git/hooks/pre-commit`.

---

### P5.5 — `audit_8d.py` audita 9 dominios pero su nombre dice "8d" ⚠️ MEDIO
**Vicios:** VC-113 (Nomenclatura congelada), VC-063 (Documentación mentirosa), VT-108 (Nombre desconectado del dominio)
**Evidencia:** El script fue creado como "audit_8d" (8 dominios: D1-D8). Posteriormente se añadió D9 (Pureza de Tests). El nombre quedó congelado en el estado histórico. Todos los tests, hooks, SPEC.md, AGENT.md, CHECKLIST.md y HISTORIAL.md referencian "8d" sin actualización. No existe ningún test centinela que verifique que el número en el nombre corresponde al número de dominios en el código.
**Fix (dos opciones antes de implementar):**
- **A (recomendada):** Renombrar a `audit_9d.py` con migración completa de todas las referencias (grep: 40+ archivos)
- **B:** Agregar comentario explícito en el código: `# Nombre histórico: 8d. Dominios reales: 9 (D1-D9). No renombrar por compatibilidad.` + test centinela que valida la discrepancia conocida.

**Test centinela requerido:**
```python
def test_audit_8d_domain_count_documented(self):
    """Si se añade un dominio nuevo, el nombre o el comentario debe actualizarse."""
    content = Path("scripts/audit_8d.py").read_text()
    domain_count = len(re.findall(r'def audit_d\d+_', content))
    # Exactamente 9 dominios — si cambia, este test fuerza documentar el cambio
    self.assertEqual(domain_count, 9, f"Dominios detectados: {domain_count} (esperados: 9). Actualizar nombre o comentario.")
```

**Done cuando:** Existe test centinela que falla si se añade dominio D10 sin actualizar la documentación.

---

### P5.6 — Sin test de stack completo del usuario ⚠️ MEDIO
**Vicios:** VT-107 (Stack incompleto silencioso), VC-106 (Setup fantasma)
**Evidencia:** `setup_validate.py` existe (v2.0, REGLA #31) pero se desconoce si cubre: Python 3.10+, git instalado, hooks instalados, todas las dependencias de scripts (pathlib, json, re, etc.), permisos de escritura en disco, encoding UTF-8 del sistema. Si el usuario tiene el stack incompleto, Cerberus falla silenciosamente en algún subcomponente sin diagnóstico claro.
**Fix:** Auditar `setup_validate.py` y extender para cubrir:
- [ ] Python >= 3.10
- [ ] git disponible en PATH
- [ ] `.git/hooks/pre-commit` existe y es ejecutable
- [ ] Todos los imports de `scripts/` resuelven sin error
- [ ] Escritura a disco en `.protocol/` funciona
- [ ] Encoding del terminal es UTF-8
- [ ] `.protocol/metadata/REGISTRY.json` parseable

**Done cuando:** `python scripts/setup_validate.py` produce checklist verde/rojo para cada precondición y retorna exit 1 si alguna falla.

---

### P5.7 — hard_excludes puede derivar silenciosamente: lo que se ignoró puede dejar de ser inofensivo ⚠️ MEDIO
**Vicios:** VT-106 (Exclusión no revalidada), VC-009 (Autoauditoría contaminada)
**Evidencia:** En la sesión actual se descubrió que `docs/archive/`, `scratch/`, `Golden_Standard/` estaban en hard_excludes pero contenían zombis reales o archivos legítimos sin whitelistear. No hubo ningún test ni alerta que detectara esta deriva. El hard_excludes podría silenciar problemas reales en el futuro sin que nadie lo note.
**Regla requerida:** Todo ítem en `hard_excludes` es un contrato activo. Cada ítem debe:
1. Tener justificación en comentario de código (ya implementado en commit 5e3ed7b)
2. Ser verificado contra un test que lo valida como tooling artifact puro o deprecated (no project code)

**Test requerido:**
```python
ALLOWED_HARD_EXCLUDES = {'.git', '__pycache__', '.pytest_cache', '.ruff_cache',
    'venv', 'env', '.venv', 'node_modules', 'evidence', 'backups', 'exports', '.secrets', 'deprecated'}

def test_hard_excludes_no_derive(self):
    content = Path("scripts/audit_8d.py").read_text()
    # Extrae lista actual y verifica contra conjunto aprobado
    ...
```

**Done cuando:** Existe test que falla si se añade una entrada no aprobada a hard_excludes sin actualizar el test mismo.

---

## ORDEN DE EJECUCIÓN P5

```
Sprint 5 (ya activo — integridad del auditor):
  Ver P4 orden de ejecución

Sprint 6 (governance gaps + infrastructure) ✅ COMPLETO:
  [x] P5.4 — tests/test_infrastructure.py: 3 tests hook existence+executable+content
  [x] P5.5 — tests/test_infrastructure.py: centinela domain count + docstring
  [x] P5.3 — tests/test_infrastructure.py: hard_excludes whitelist sentinel
  [x] P5.7 — tests/test_infrastructure.py: hard_excludes floor sentinel
  [x] P5.2 — AGENT.md item 6 + CHECKLIST.md cierre + P4.5 gaps volumen/calendario
  [x] P5.6 — setup_validate.py: 6 checks (git, hook, registry, write access)

Sprint 7 (expansión real del protocolo — mayor impacto) ✅ COMPLETO:
  [x] P5.1 — scripts/verify_protocol_adoption.py: audit H/A/T por proyecto, adoption_verified en REGISTRY.json
       Estado actual: 2/17 adoptados (12%). Pendiente: siguiente sync propagará audit_8d.py a los 15 restantes.
       Propagación: scripts/audit_8d.py + scripts/verify_protocol_adoption.py añadidos a PROTOCOL_FILES en global_sync_safe.py.
```

---

### P4.8 — `audit_8d.py` hard_excludes silenciaba 600+ zombis legítimos ✅ CORREGIDO
**Vicios:** VC-009 (Auto-exclusión del auditor), VC-063 (Whitelist mentirosa)
**Evidencia:** hard_excludes incluía `docs/archive/`, `scratch/`, `_ORIGINALES_GRANDES/`, `Golden_Standard/`, `.CoderCerberus/`, `.protocol/`, `exports/` — 28 entradas incluyendo 15 directorios que no existían (ruido). Con esta configuración, D1 nunca podía detectar zombis reales en esas rutas.
**Fix aplicado:** `commit 5e3ed7b` — hard_excludes reducido a solo tooling puro + evidence + backups + exports + .secrets + deprecated. docs/archive/ → deprecated/docs_archive_legacy/, scratch/ → deprecated/scratch_legacy/. Golden_Standard/*.md y .CoderCerberus/REGISTRY.json agregados a SPEC.md whitelist. 295/295 tests verdes.
**Fecha:** 2026-05-27

---

## P6 — AUDITORÍA ADVERSARIAL GEMINI (4 Fases, 2026-05-27)

Auditoría externa adversarial realizada por Gemini. 9 findings validados empíricamente leyendo archivos reales.
Gemini también propuso 3 ítems rechazados: "destruir hooks suaves" (invierte 3-tier governance), "eliminar review_queue" (invierte P4.6), "desmantelar total" (hiperbólico).

---

### P6.1 — `cerberus/rules_engine.py`: eval() RCE ✅ CORREGIDO
**Vicios:** VC-ASI-01 (Ejecución arbitraria de código), supply chain RCE
**Evidencia confirmada:** `eval(rule['check'], {"__builtins__": {}}, context)` — cualquier YAML malicioso = ejecución arbitraria en proceso.
**Fix aplicado:** Reemplazado eval() con SAFE_CHECKS dispatch table. 3 YAML files actualizados (`pending_tasks_empty`, `all_rules_have_severity`, `all_rules_have_tests`). Load-time validation rechaza nombres desconocidos.
**Done cuando:** `grep -n "eval(" cerberus/rules_engine.py` devuelve vacío. ✅ VERIFICADO.

---

### P6.2 — `auto_repair.py`: pip install silencioso ✅ CORREGIDO
**Vicios:** VC-ASI-02 (Supply chain injection), VC-P6.2 (Instalación automática de paquetes)
**Evidencia confirmada:** `handle_import_error()` ejecutaba `subprocess.run([..., "pip", "install", module])`. `main()` tenía `commit_each=True` por defecto.
**Fix aplicado:** `handle_import_error()` imprime guía y retorna False. `main()` default `commit_each=False`.
**Done cuando:** `grep -n "pip install" auto_repair.py` devuelve vacío. ✅ VERIFICADO.

---

### P6.3 — `TOKEN_BUDGET.md`: referencias a script eliminado ✅ CORREGIDO
**Vicios:** VC-063 (Documentación mentirosa), VT-091 (Dominio documentado no implementado)
**Evidencia confirmada:** 2 ocurrencias de `python scripts/rtk_auto_compress.py --aggressive` → script no existe.
**Fix aplicado:** Ambas referencias → `python scripts/memory_compression_reme.py`. `tail -20` → `python scripts/auto_export_retrospective.py --list`.
**Done cuando:** `grep "rtk_auto_compress" TOKEN_BUDGET.md` devuelve vacío. ✅ VERIFICADO.

---

### P6.4 — Sin script de instalación de hooks para Windows ✅ CORREGIDO
**Vicios:** VC-P6.4 (Portabilidad Windows), VT-095 (Setup fantasma en Windows)
**Evidencia confirmada:** `scripts/install_hooks.sh` era bash-only; imposible ejecutar en Windows sin WSL.
**Fix aplicado:** Creado `scripts/install_hooks.ps1` — detecta .git, crea hooks dir, copia pre-commit, valida Python+pytest.
**Done cuando:** `Test-Path scripts\install_hooks.ps1` devuelve True. ✅ VERIFICADO.

---

### P6.5 — Tres límites de tokens con nombres iguales, unidades distintas ✅ CORREGIDO
**Vicios:** VC-063 (Documentación ambigua), VC-P6.5 (Confusión de unidades)
**Evidencia confirmada:**
- `TOKEN_BUDGET.md`: 200,000 = ventana de contexto total (tokens)
- `core_utils.py:20`: `TOKEN_BUDGET = 150_000` = presupuesto de sesión (tokens)
- `protocol_cli.py:57`: `max_bytes = 100_000` = proxy de tamaño de archivo (bytes, NO tokens)
**Fix aplicado:** Comentarios aclaratorios en los 3 archivos distinguiendo las 3 métricas.
**Done cuando:** Los 3 archivos tienen comentarios que distinguen las 3 métricas. ✅ VERIFICADO.

---

### P6.6 — `scripts/rigor_maestro.py`: TEST_SUITE hardcodeado rompe portabilidad ✅ CORREGIDO
**Vicios:** VC-109 (Ruta literal ambiental), VT-080 (Acoplamiento de Dirección Física)
**Evidencia confirmada:** 4 entradas con rutas hardcodeadas `tests/test_cerberus_mandates.py`, `tests/test_cerberus_core.py`, etc. — inexistentes en proyectos satélite.
**Fix aplicado:** 7 entradas → 3 entradas. Eliminados los 4 archivos individuales; `pytest tests/` ya los descubre dinámicamente. Comentario P6.6 añadido.
**Done cuando:** `grep "test_cerberus_mandates\|test_cerberus_core\|test_cerberus_resilience\|test_behavioral_compliance" scripts/rigor_maestro.py` devuelve vacío. ✅ VERIFICADO.

---

### P6.7 — `cerberus/close_pending.py`: escritura no atómica ✅ CORREGIDO
**Vicios:** VC-P6.7 (Corrupción de datos en crash), VT-044 (No transaccional)
**Evidencia confirmada:** `pending_path.write_text(...)` directamente — si el proceso es killed durante write, el JSON queda corrupto.
**Fix aplicado:** Write-to-tempfile (`tempfile.mkstemp`) + `Path.replace()` atómico. Limpieza de .tmp en caso de error.
**Done cuando:** `grep "write_text" cerberus/close_pending.py` devuelve vacío. ✅ VERIFICADO.

---

### P6.8 — `scripts/protocol_cli.py`: lógica tokenómica duplicada de token_optimizer.py ✅ COMPLETO
**Vicios:** VC-067 (Código duplicado), VT-069 (Test de duplicado)
**Evidencia confirmada:** `_check_and_compact_needed()` y `_calculate_compact_threshold()` son copias de lógica de `token_optimizer.py`.
**Fix propuesto:** Extraer ambas funciones a `core_utils.py` o importar desde `token_manager.TokenOptimizer`. Eliminar las copias de protocol_cli.py.
**Done cuando:** `diff <(grep -n "def _check\|def _calculate" scripts/protocol_cli.py) <(grep -n "def check_and_compact\|def _calculate" scripts/token_manager.py)` muestra que ambas están consolidadas.

---

### P6.9 — Tests VT-007/VT-016: assertions textuales, no de comportamiento ✅ COMPLETO
**Vicios:** VT-007 (Test textual), VT-016 (Assertion frágil)
**Evidencia confirmada:** `test_S1_audit_8d_has_forensic_auditor` usa `assertIn("forensic", content.lower())` — pasa aunque la función sea un stub sin lógica.
**Fix propuesto:** Reemplazar assertions textuales por pruebas funcionales: invocar la función y verificar que devuelve resultado real con datos de entrada reales.
**Done cuando:** Los tests VT-007/VT-016 fallan si se convierte la función a stub vacío.

---

## ORDEN DE EJECUCIÓN P6

```
P6 Sprint (seguridad adversarial Gemini) — ESTADO:
  [x] P6.1 — eval() RCE → SAFE_CHECKS dispatch
  [x] P6.2 — pip install silencioso → guía manual + commit_each=False
  [x] P6.3 — TOKEN_BUDGET.md refs rotas → memory_compression_reme.py
  [x] P6.4 — install_hooks.ps1 Windows
  [x] P6.5 — comentarios 3 límites de tokens
  [x] P6.6 — rigor_maestro TEST_SUITE hardcodeado → pytest dinámico
  [x] P6.7 — close_pending write atómico
  [x] P6.8 — check_compact_sessions/threshold extraídas a core_utils.py; protocol_cli importa desde ahí (2026-05-28)
  [x] P6.9 — test_core_mandates_functional: 3 subtests invocan D1/D5/D8 reales (VT-007/VT-016) (2026-05-28)
```

*Auditoría adversarial Gemini 4 fases: 2026-05-27. 7/9 findings cerrados.*

---

## P7 — D10 TOKENOMICS + D6 NAME-CONGRUENCY + RENAME audit_10d (2026-05-27)

**Origen:** Auditoría Gemini (2 rondas) + decisión de usuario. Cuatro objetivos coordinados:
0. **Prerequisito:** Cerrar 5 bugs lógicos validados empíricamente (P7.0)
1. Incorporar D10 al auditor central (tokenomics como compuerta física)
2. Agregar sub-check D6: nombre de script congruente con número de dominios
3. Renombrar audit_8d.py → audit_10d.py (cierre de VC-113 Nomenclatura congelada)

---

### P7.0 — 5 Bugs Lógicos (Gemini adversarial, validados empíricamente) ✅ COMPLETO

**Fuente:** Auditoría adversarial Gemini ronda 2. Todos confirmados leyendo código real y ejecutando prueba.

---

#### GF-1 — `token_manager.py:ContextExtractor` RAG completamente inactivo ❌ BUG
**Vicios:** VC-063 (Documentación mentirosa), VC-085 (Observabilidad ornamental)
**Evidencia confirmada:**
- `parse_status_md()` busca `line.startswith('## CAMPO')` (MAYÚSCULAS)
- STATUS.md real usa `## Campo 1: Estado actual` (mixto)
- Resultado empírico: `ContextExtractor().parse_status_md(content)` retorna `{}` en producción
- `smart_context_extraction()` reporta 0 tokens ahorrados, nunca ha funcionado

**Fix:**
```python
# token_manager.py:88 — reemplazar:
if line.startswith('## CAMPO'):
    m = re.search(r'CAMPO (\d+)', line)
# por:
if re.match(r'^## campo\s+\d+', line, re.IGNORECASE):
    m = re.search(r'campo\s+(\d+)', line, re.IGNORECASE)
```
**Done cuando:** `ContextExtractor().parse_status_md(Path("STATUS.md").read_text())` retorna dict no vacío.

---

#### GF-2 — `scripts/install_hooks.ps1` crash cuando Python no está en PATH ❌ BUG
**Vicios:** VC-106 (Setup fantasma), VC-088 (Error tolerado por política)
**Evidencia confirmada:**
- Línea 5: `$ErrorActionPreference = "Stop"` — cualquier error termina el script
- Línea 39: `Get-Command python -ErrorAction SilentlyContinue` → safe, asigna null si no existe
- Línea 46: `$pytest = & python -m pytest --version 2>&1` — se ejecuta incondicionalmente
- Si Python no está en PATH, línea 46 lanza `CommandNotFoundException` → terminating error → crash antes del mensaje de aviso

**Fix:** Wrap pytest check en `if ($python)`:
```powershell
# Reemplazar líneas 46-51 por:
if ($python) {
    $pytest = & python -m pytest --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "AVISO: pytest no disponible — instalar con: pip install pytest" -ForegroundColor Yellow
    } else {
        Write-Host "OK  $pytest" -ForegroundColor Green
    }
}
```
**Done cuando:** Ejecutar el script en entorno sin Python en PATH muestra AVISO en lugar de crash.

---

#### GF-3 — `auto_repair.py:handle_missing_whitelist` apunta a archivo eliminado ❌ BUG CRÍTICO
**Vicios:** TK-039 (Script espectral), VC-063 (Documentación mentirosa)
**Evidencia confirmada:**
- `audit_path = REPO_ROOT / "scripts/audit_6d.py"` — este archivo no existe (verificado con `Glob`)
- Cuando el handler se activa, lanza `FileNotFoundError` inmediatamente, crasheando el repair-loop
- El handler es disparado por cualquier mensaje de error que contenga 'missing' — muy frecuente

**Fix:** Actualizar ruta al archivo activo:
```python
# auto_repair.py:114 — reemplazar:
audit_path = REPO_ROOT / "scripts/audit_6d.py"
# por:
audit_path = REPO_ROOT / "scripts/audit_8d.py"
# Nota: P7.1 actualizará esto a audit_10d.py en el sprint de rename
```
**Done cuando:** `(REPO_ROOT / "scripts/audit_8d.py").exists()` es True desde el handler.

---

#### GF-4 — `protocol_cli.py:run()` IndexError sin valor para `--last-n` / `--port` ❌ BUG
**Vicios:** VC-074 (I/O sin validación), VC-076 (Tipado laxo)
**Evidencia confirmada:**
- Línea 161: `next((argv[i+1] for i, a in enumerate(argv) if a == "--last-n"), "5")` — sin guarda de límite
- Si `--last-n` es el último argumento: `argv[i+1]` → `IndexError: list index out of range`
- Mismo bug en `_command_dashboard` línea 147 con `--port`

**Fix — añadir guarda de índice:**
```python
# protocol_cli.py:161 — reemplazar:
last_n = int(next((argv[i+1] for i, a in enumerate(argv) if a == "--last-n"), "5"))
# por:
last_n = int(next((argv[i+1] for i, a in enumerate(argv) if a == "--last-n" and i+1 < len(argv)), "5"))
# Y en _command_dashboard:
port = int(next((argv[i+1] for i, a in enumerate(argv) if a == "--port" and i+1 < len(argv)), "5000"))
```
**Done cuando:** `python scripts/protocol_cli.py evidence --last-n` no lanza IndexError.

---

#### GF-5 — `token_manager.py:TokenOptimizer._log()` falla silenciosamente (tabla sin schema) ⚠️ BUG
**Vicios:** VC-061 (Stub como arquitectura), VC-085 (Observabilidad ornamental)
**Evidencia confirmada:**
- `token_manager.py:178`: `INSERT INTO token_optimizations (...)` — tabla usada para logging
- `token_manager.py:282`: `SELECT ... FROM token_optimizations` — tabla usada para reporte
- `grep "CREATE TABLE.*token_optim"` en todo el repo: **0 resultados**
- Toda llamada a `_log()` falla con `OperationalError: no such table: token_optimizations`, swallowed por `except Exception`
- `generate_report()` también falla silenciosamente — el reporte de optimizaciones nunca tiene datos reales
- NOTA: `setup_alerts_db` y `setup_token_events_db` SÍ están conectados (deadlock_resolver + token_tracker los usan). `setup_sessions_db` sí es deuda declarada — marcar como tal.

**Fix — agregar inicialización de la tabla en TokenOptimizer.__init__:**
```python
def _ensure_token_optimizations_table(self) -> None:
    """Create token_optimizations table if the DB exists (P7 / GF-5)."""
    if not self.db_path.exists():
        return
    try:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS token_optimizations "
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, "
                "action TEXT, tokens_saved INTEGER, method TEXT)"
            )
    except Exception as e:
        print(f"[WARN] token_optimizations init: {e}")
```
Llamar `self._ensure_token_optimizations_table()` al final de `__init__`.
Para `setup_sessions_db`: agregar comentario `# Infrastructure declared — not yet wired to runtime (VC-039 debt)`.
**Done cuando:** `TokenOptimizer().generate_report()` imprime datos reales en lugar de fallar silenciosamente.

**Angry Path (B3) — 3 formas de romper esto antes de implementar:**
- **Riesgo 1 (shim hell):** audit_8d.py como compatibility shim funciona en Cerberus, pero satélites recibieron audit_8d.py en sus scripts/ y tienen hooks que lo llaman. Si el shim falla silenciosamente en satélite, el hook pasa sin auditoría real → shim debe imprimir advertencia clara y hacer forward explícito.
- **Riesgo 2 (D10 TK-039 falsos positivos):** HISTORIAL.md contiene referencias históricas a scripts eliminados (rtk_auto_compress.py etc.) → D10 debe escanear SOLO secciones activas de TOKEN_BUDGET.md y AGENT.md, no todo el árbol de docs.
- **Riesgo 3 (D6 double-count):** si alguien nombra `def audit_d1_helper_internal()`, el regex lo cuenta como dominio → restringir a `def audit_d\d+_\w+\(self\)` (solo métodos con self, no helpers estáticos).

---

### P7.1 — Rename audit_8d.py → audit_10d.py ✅ DONE (2026-05-27)
**Vicios:** VC-113 (Nomenclatura congelada)
**Evidencia:** `audit_8d.py` audita 9 dominios (D1-D9) actualmente; con D10 serán 10. El nombre "8d" es un artefacto histórico. 29 archivos lo referencian.
**Fix original (SUPERSEDIDO — ver nota S19):**
~~1. Crear `scripts/audit_10d.py` (copia de audit_8d.py + D10 agregado).~~
~~2. Mantener `scripts/audit_8d.py` como **compatibility shim**~~ ← **PROHIBIDO por S19 + VC-118**

**Fix real implementado (S19 compliant):**
1. Creado `scripts/audit_10d.py` con D1-D10 completo (sin herencia de audit_8d).
2. `scripts/audit_8d.py` **ELIMINADO** — no existe en disco (test centinela lo verifica).
3. 26 archivos redirigidos a audit_10d vía VC-119 rename sweep.
4. Test: `test_audit_8d_does_not_exist` — falla si el archivo reaparece.

> **NOTA HISTÓRICA:** El plan original (pasos 1-5 arriba) recomendaba un shim. Eso fue
> descartado y reemplazado por la implementación real (S19 Anti-Zombie-Compat, VC-118).
> El texto del shim queda sólo como evidencia de la decisión — NO ejecutar.

**Archivos a actualizar (scripts y docs vivos):**
`rigor_maestro.py`, `protocol_cli.py`, `verify_protocol_adoption.py`, `global_sync_safe.py`, `chaos_monkey.py`, `self_improvement_loop.py`, `auto_audit_loop.py`, `review_reminder.py`, `audit_6d_expanded.py`, `SPEC.md`, `AGENT.md`, `CHECKLIST.md`, `STATUS.md`, `SOURCES_OF_TRUTH.md`, `PROTOCOL_SYSTEM.md`, `.github/pull_request_template.md`, y todos los tests que referencian el nombre del script.

**Done cuando (criterio real — S19):**
- `python scripts/audit_10d.py` produce `APPROVED`.
- `scripts/audit_8d.py` no existe en disco (`test_audit_8d_does_not_exist` verde).
- `grep -rn "audit_8d" scripts/ .github/ tests/*.py` devuelve sólo referencias en tests de verificación negativa.

---

### P7.2 — D10: Tokenomics & Eficiencia de Contexto ✅ DONE (2026-05-27)
**Vicios:** VC-100 (No funcional ignorado), TK-023 (Logs crudos), TK-038 (manifiestos sin límite), TK-039 (Script espectral)
**Evidencia:** TOKEN_BUDGET.md documenta políticas de ahorro de tokens, pero ninguna compuerta física en audit_10d.py las valida. Los vicios TK-023/TK-038/TK-039 de la Biblioteca existen solo como teoría.

**Tres checks de D10:**

**TK-023 — Log compression enforcement:**
- Objetivo: el orquestador principal de tests (rigor_maestro.py) y los auto-loops (self_improvement_loop.py, auto_audit_loop.py) DEBEN importar OutputCompressor para comprimir salida de subprocesos.
- Check: para cada archivo en `["scripts/rigor_maestro.py", "scripts/self_improvement_loop.py", "scripts/auto_audit_loop.py"]`: verificar que contiene `OutputCompressor` en el texto.
- Fail: si falta en cualquiera de los tres → D10: TK-023: `{archivo}` sin OutputCompressor.

**TK-038 — Manifest size gate (Trinity de la Memoria):**
- Objetivo: manifiestos core no deben saturar el contexto en cada sesión.
- Thresholds (Golden Standard Anexo A Trinity): `AGENT.md` ≤ 150 líneas, `STATUS.md` ≤ 200 líneas, `SPEC.md` ≤ 500 líneas.
- Check: `len(path.read_text().splitlines())` para cada manifiesto vs umbral.
- Fail: `D10: TK-038: AGENT.md tiene 187 líneas (límite: 150). Riesgo: saturación de contexto.`

**TK-039 — Active script references (no vaporware):**
- Objetivo: toda referencia `python scripts/X.py` en TOKEN_BUDGET.md y AGENT.md debe apuntar a un archivo que existe en disco.
- Check: regex `python (?:scripts/)?(\S+\.py)` en ambos archivos → `Path(match).exists()`.
- Fail: `D10: TK-039: TOKEN_BUDGET.md referencia 'scripts/rtk_auto_compress.py' pero no existe.`

**Implementación:** una función `audit_d10_tokenomics(self)` en audit_10d.py.

**Done cuando:**
- `python scripts/audit_10d.py` reporta `[PASS] D10 TOKENOMICS` con los tres sub-checks.
- Insertar referencia espectral en TOKEN_BUDGET.md → D10 la detecta y produce REJECTED.
- Superar 150 líneas en AGENT.md → D10 lo detecta.

---

### P7.3 — D6 sub-check: nombre de script congruente con número de dominios ✅ DONE (2026-05-27)
**Vicios:** VC-113 (Nomenclatura congelada), VC-063 (Documentación mentirosa)
**Evidencia:** VC-113 está en el Golden Standard pero audit_8d.py no tenía compuerta que lo previniera automáticamente. Si alguien agrega un D11 en el futuro sin renombrar el script, vuelve a ocurrir el mismo problema.
**Fix:** Agregar sub-check a `audit_d6_anti_slop()` en audit_10d.py:
```python
# D6 name-congruency: audit_Nd.py must declare exactly N audit_dN_(self) methods
m = re.match(r'audit_(\d+)d\.py', Path(self.project_path / "scripts" / "audit_10d.py").name)
if m:
    declared = int(m.group(1))
    content = (self.project_path / "scripts" / "audit_10d.py").read_text(encoding='utf-8')
    actual = len(re.findall(r'def audit_d\d+_\w+\(self\)', content))
    if actual != declared:
        issues.append(f"D6: audit_10d.py declara {declared} dominios en el nombre pero tiene {actual} métodos audit_dN_.")
```
**Test:** test_infrastructure.py centinela — si se agrega `def audit_d11_foo(self)` sin renombrar, el test falla.
**Done cuando:** `test_d6_name_congruency` falla si se rompe la congruencia nombre-dominio.

---

### P7.4 — Tests ✅ DONE (2026-05-27)
- `tests/test_d10_tokenomics.py`: 6 tests
  - D10 pasa cuando los 3 archivos de orquestación tienen OutputCompressor
  - D10 falla cuando falta OutputCompressor en rigor_maestro
  - D10 pasa cuando manifiestos están bajo umbral
  - D10 falla cuando AGENT.md supera 150 líneas
  - D10 pasa cuando todas las refs de scripts en TOKEN_BUDGET son reales
  - D10 falla cuando TOKEN_BUDGET referencia script espectral
- `tests/test_infrastructure.py` (ACTUALIZAR): agregar test D6 name-congruency sentinel

---

### P7.5 — Golden Standard: registrar nuevos vicios ✅ COMPLETO
**Agregar a BIBLIOTECA_VICIOS_VIBE_CODING.md (Categoría VII: Seguridad de Cadena de Suministro):**

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| VC-115 | Ejecución dinámica de expresiones externas | Motor de reglas ejecuta strings de YAML como código Python (eval/exec) | La fuente de reglas se trata como código confiable | Reemplazar eval con dispatch table de funciones registradas; validar nombres en tiempo de carga |
| VC-116 | Instalación automática de dependencias no verificadas | Un error de importación desencadena pip install sin revisión humana | Supply chain delegada al error handler | Prohibir pip install automático; reportar dependencia faltante y detener; el humano instala |
| VC-117 | Escritura destructiva no atómica de estado crítico | Crash durante write_text() corrompe JSON de estado | Atomicidad de escritura no modelada | Escribir a archivo temporal y renombrar atómicamente (tmp → final); limpiar tmp en caso de error |

**Agregar a BIBLIOTECA_TOKENOMICS_CONTEXTO.md (Categoría IV):**

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| TK-042 | Manifiestos sin restricción de tamaño | Archivos de gobernanza crecen sin control, saturando contexto en cada sesión | Ausencia de umbrales físicos para documentos core | Definir y hacer cumplir límites de líneas/bytes en AGENT.md, STATUS.md y SPEC.md; auditarlos como gate de commit |

---

## ORDEN DE EJECUCIÓN P7

```
P7 Sprint (bugs + D10 + nomenclatura):

  FASE A — Bug fixes (P7.0, prerequisito todo lo demás):
    [GF-1] token_manager.py: parse_status_md case-insensitive
    [GF-2] install_hooks.ps1: wrap pytest check en if ($python)
    [GF-3] auto_repair.py: audit_6d.py → audit_8d.py
    [GF-4] protocol_cli.py: guarda i+1 < len(argv) en ambos --last-n y --port
    [GF-5] token_manager.py: _ensure_token_optimizations_table() en __init__
    → run suite → 318+ green → commit GF fixes

  FASE B — D10 + D6 (P7.2 + P7.3):
    [P7.2] audit_10d.py: crear con D1-D9 + D10 (TK-023/TK-038/TK-039)
    [P7.3] D6 sub-check: name-congruency audit_Nd.py en audit_10d.py
    [P7.4] tests/test_d10_tokenomics.py (6 tests) + centinela D6 en test_infrastructure.py
    → run suite → audit_10d APPROVED → commit D10

  FASE C — Rename (P7.1) ✅ DONE (2026-05-27):
    [P7.1] audit_8d.py ELIMINADO; audit_10d.py contiene D1-D10 completo sin herencia
           26 archivos redirigidos (scripts, tests, docs)
           TK-023 cumplido: OutputCompressor en self_improvement_loop + auto_audit_loop
           → 326/326 passed → commit + PLAN actualizado

  NOTAS:
  - P7.5 (Golden Standard VC-115/116/117, TK-042) ya está hecho ✅
  - Los 5 GF findings se registran en GS con sus IDs de VC existentes (no hay nuevas entradas)
```

*Diseñado: 2026-05-27. Implementación aprobada por usuario.*

---

## P8 — DEUDA DETECTADA SESIÓN 2026-05-28

### P8.0 — Evidencia B7 invalida generada por conftest ✅ DONE (2026-05-28)
**IDs:** VT-017, VT-042, VT-043, VC-085, VC-117.
**Evidencia:** `python scripts/rigor_maestro.py` falla en `tests/test_cerberus_mandates.py::test_B7_evidence_directory_has_valid_records` porque `tests/conftest.py` escribe `.protocol/evidence/theater_risk_*.json` con `ts` en vez de `timestamp`.
**Riesgo:** El sistema produce evidencia documental invalida y luego se bloquea a si mismo; esto rompe gobernanza desatendida.
**Fix quirurgico:**
1. Cambiar `tests/conftest.py` para emitir schema B7 completo (`timestamp`, `operation`, `outcome`, `details`).
2. Reparar los artefactos contaminados existentes en `.protocol/evidence/theater_risk_*.json`.
3. Corregir import root en `scripts/self_improvement_loop.py` para evitar fallback/mojibake de `token_manager`.
**Done cuando:** `python scripts/rigor_maestro.py` llega al siguiente gate sin el fallo B7 de evidencia.

### P8.1 — Renombrar `.CoderCerberus/` → `.protocol/metadata/` ✅ DONE (2026-05-28)
**ID:** VC-120
**Vicios:** VC-113 (Nomenclatura congelada) — `.CoderCerberus/` es nombre zombie del sistema anterior "CoderCerberus". El sistema ahora se llama "CoderCerberus". El directorio está en raíz y es visible en todo `ls`.
**Evidencia:** `REGISTRY.json` y `backups/` viven en `.CoderCerberus/`. 7 scripts lo referencian directamente (audit_10d, core_utils, dashboard/server, global_sync_safe, hygiene_auditor, setup_validate, verify_protocol_adoption).
**Fix:**
1. Crear `.protocol/metadata/` (`.protocol/` ya existe con `evidence/`)
2. Mover `.CoderCerberus/REGISTRY.json` → `.protocol/metadata/REGISTRY.json`
3. Rename Sweep VC-119: grep -r "CoderCerberus" . — actualizar los 7 scripts
4. Actualizar `.gitignore` si tiene entradas de `.CoderCerberus/`
5. Verificar `global_sync_safe.py` no rompe sincronización satélites
6. Confirmar `audit_10d.py D1` whitelist actualizada
**Done cuando:** `grep -r "CoderCerberus" .` retorna cero hits funcionales; suite 328+ verde; `audit_10d APPROVED`.
**Sprint estimado:** propio, aislado. No mezclar con otros cambios.
