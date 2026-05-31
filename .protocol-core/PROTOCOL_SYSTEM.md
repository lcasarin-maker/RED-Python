# 🛡️ PROTOCOL_SYSTEM — Código Penal de Coder Cerberus V0.1
**Estado:** 💀 ZERO-TRUST ENFORCED | **Nivel:** 1:1 Parity Mandatory
Version: v0.3


---

## 🛑 MANDATO S7: PROHIBICIÓN DE SHELL MODIFICATION (ANTI-BLIND WRITING)
- **Definición:** Queda terminantemente PROHIBIDO usar comandos de terminal (`echo`, `sed`, `Add-Content`, `Set-Content`, `>` o `>>`) para escribir, editar, inyectar o manipular de forma ciega el contenido de archivos del core o del workspace.
- **Razón:** El shell no tiene validación semántica ni de encoding y es propenso a corromper archivos. Toda edición DEBE pasar exclusivamente por las herramientas atómicas de edición y escritura del agente (`replace_file_content` o `write_to_file`).
- **Validación:** La suite de auditoría forense (`run_security_audit_12d.py`) busca activamente patrones de comandos mutadores peligrosos en los scripts del control plane, hooks de git y archivos del workspace. `pre_edit_guard.py` bloquea patrones S7 antes de que la edición ocurra (PreToolUse hook).
- **Excepción:** Solo se permite shell para lectura segura (`git diff`, `ls`), ejecución de tests o ejecución de scripts de validación autorizados.

## 📈 MANDATO S8: IMPUESTO DE DEUDA TÉCNICA (DEBT TAX)
- **Definición:** Prohibido generar o modificar más de 50 líneas de código real (excluyendo comentarios) en un solo turno.
- **Turno de Refactorización:** Tras cada bloque de 50 líneas, el agente está obligado a detenerse y realizar un "Simplicity Pass" para consolidar nombres y simplificar lógica antes de que el código decaiga.
- **Bloqueo:** No se puede proponer el siguiente bloque de lógica hasta que el humano certifique la legibilidad del anterior.

## 📄 MANDATO S6: SEGURIDAD DE ARCHIVOS GRANDES (ANTI-CORRUPTED-EDIT)
- **Definición:** Prohibido usar `write_to_file` o shell mutation para archivos >200 líneas. Máximo 50 líneas por operación de `replace_file_content`.
- **Razón:** Editar archivos masivos en una operación atómica corre el riesgo de corrupción parcial si falla la validación semántica.
- **Acción:** Para archivos grandes, usar múltiples ediciones pequeñas (<50 líneas cada una). Agrupar cambios lógicamente pero mantenerlos separados.
- **Validación:** `pre_edit_guard.py` (PreToolUse hook) bloquea `Write` >200 líneas antes de que ocurra. `run_security_audit_12d.py` lo detecta en auditoría post-hoc.

## 🔊 MANDATO S9: INSTRUMENTACIÓN VERBOSA OBLIGATORIA (ANTI-CAJA NEGRA)
- **Definición:** Queda terminantemente PROHIBIDO escribir funciones, clases o módulos "silenciosos".
- **Logging Mandatario:** Todo código generado por IA DEBE incluir puntos de entrada de logging estructurado (`logger.info` o equivalente) que describan los argumentos recibidos y el estado inicial.
- **Trazabilidad:** El manejo de errores (`try/except/catch`) debe loguear no solo el mensaje de error, sino el contexto de los datos que causaron el fallo. El código silencioso se considera deuda técnica letal.

---

## 🛑 MANDATO S1: RIGOR DE VALIDACIÓN (6D ANGRY PATH)
- **Definición:** Prohibido cerrar tareas sin score 100% en `scripts/run_security_audit_12d.py` (gatekeeper primario, 10 dominios). `pre_edit_guard.py` complementa con validación en tiempo real (PreToolUse hook).
- **Angry Path:** Si el código corre pero carece de `try/except` robustos o validación de tipos, la tarea es un fallo de seguridad.
- **Acción:** `Sin Tests, No Hay Código`. Cada bloque lógico debe tener un test de estrés que fuerce el error.
- **Nota:** La auditoría debe ejecutarse hasta alcanzar 100% de puntuación; el agente no debe detenerse prematuramente.

## 🧱 MANDATO S2: ARQUITECTURA E INTEGRIDAD (BRAIN-FIRST)
- **Definición:** El `SPEC.md` es el único "Cerebro". Prohibido mutar código sin actualizar primero el mapa mental.
- **Whitelist Strict:** Cualquier archivo no registrado en la Whitelist del `SPEC.md` es considerado una infección (Zombi) y bloquea el commit.
- **Dry-Runs:** Todo comando destructivo (git, rm, env) requiere un `dry-run` y explicación de riesgo previa.
- **Context Drift:** Divergencia gradual entre asunciones del agente y estado real del repo — el agente edita una copia obsoleta porque trabaja desde contexto cacheado. Síntoma: acciones que contradicen el plan reciente. Prevención: `sync_binding.py --check` + releer SPEC.md al inicio de sesión. Si se detecta drift, el bootstrap ritual es obligatorio antes de continuar cualquier tarea.

## 🔐 MANDATO S3: SEGURIDAD Y CONFINAMIENTO (BIO-CONTAINMENT)
- **Definición:** Asumir que toda IA es un "Pasante Incompetente" que inyectará vulnerabilidades.
- **Acción:** Auditoría de seguridad línea por línea obligatoria en fronteras de I/O.
- **Prohibición Estricta:** Cero variables no sanitizadas o stubs SQL/HTML sin tipado de seguridad estricto en fronteras de comunicación I/O.
- **Tipado Fuerte:** Prohibición absoluta del uso del tipo genérico `any` en funciones I/O o interfaces de datos. Todo dato debe ser tipado de manera determinista y estricta.
- **Contención Física:** Cero acceso directo a DB de producción sin capas middleware validadas. Cero placeholders e inyecciones en APIs. Cero lógica de seguridad ("fallbacks") relajada.
- **Bóveda de Secretos Global:** Está estrictamente prohibido hardcodear llaves (API keys, Tokens, DB Passwords) en archivos `.env` dispersos. Todo secreto debe migrarse y leerse desde una bóveda centralizada global fuera del control de versiones (por ejemplo, `D:\GoogleDrive\AI\.secrets\`), y los repositorios locales solo deben contener archivos `.example`.
- **Reject, Don't Coerce (REGLA #30):** Dato inválido en frontera = `raise ValueError` inmediato. PROHIBIDO asignar valor por defecto silencioso (`status = 'PENDING'`) para ocultar entrada inválida. Checklist mínimo en toda frontera externa: Presente / Tipo correcto / Longitud / Formato / Valores permitidos (whitelist) / Encoding UTF-8.
- **Trust Internal Code:** NO validar entre funciones del mismo módulo. La validación aplica SOLO en bordes del sistema (user input, APIs externas, webhooks, file uploads, DB legacy). Código interno que ya pasó la frontera se considera confiable.
- **4 Elementos Obligatorios en Error Handling:** Toda cláusula `try/except` o `try/catch` DEBE contener exactamente estos 4 elementos o el commit falla:
  1. **LOG** — Registrar el error con contexto: `logger.error(f"Failed to X: {args}, error={err}")`
  2. **USUARIO** — Mensaje legible en lenguaje natural (no "Error 500"). Ejemplo: "No se pudo leer el archivo. Verifica que existe y tengo permiso."
  3. **ESTADO** — Rollback o garantía de consistencia. ¿Se revierte parcialmente? ¿Se marca como corrupto? Documentar.
  4. **ACCIÓN** — ¿Reintentar automáticamente? ¿Fallar crítico? ¿Degradación elegante? Explicitar la decisión.

## 🚫 10 PROHIBICIONES OPERACIONALES (N4_M1 COMPLIANCE)
1. **LECTURA COMPLETA PROHIBIDA:** No leer archivos .md >100 líneas sin especificar rango (`--lines X:Y`). Ahorro −80% input tokens.
2. **VERBOSIDAD CRÍTICA:** Máximo 5 líneas de explicación. Prioridad: código > narrativa. Sin preámbulos ni conclusiones.
3. **OPTIMISMO PROHIBIDO:** No declarar "100% completado" si hay gaps conocidos. Documentar gaps en HISTORIAL.md.
4. **IGNORANCIA ACTIVA:** No ignorar compiler warnings. Toda advertencia = error fatal. Zero tolerance.
5. **REGENERACIÓN INJUSTIFICADA:** Prohibido reescribir archivo completo para 1 sección. Usar `replace_file_content` <50 líneas.
6. **FRAGILIDAD DE TESTS:** Obligatorio regression suite (no smoke tests). Cobertura angry path + flujos críticos.
7. **AUDITORÍA PEREZOSA:** No asumir estado sin leer. Obligatorio `git status`, `git log`, HISTORIAL.md ANTES.
8. **SECRETOS HARDCODEADOS:** Prohibido absoluto. Todo a `.secrets/` centralizado. Solo `.example` en repo.
9. **SILENCIO EN ERRORES:** Cubierto por S3 (4 elementos obligatorios: LOG, USUARIO, ESTADO, ACCIÓN).
10. **SCOPE CREEP:** Prohibido modificar fuera del scope. Hallazgos secundarios → HISTORIAL.md sin ejecutar.

## 📦 MANDATO S4: MODULARIDAD Y ESTADO (ANTI-SPAGHETTI)
- **Definición:** Forzar esquemas de estado centralizados (Zod/Pydantic). Prohibido el estado local disperso.
- **Aislamiento:** Los módulos generados por IA deben estar confinados tras interfaces rígidas. Si un módulo falla, el sistema debe sobrevivir (Bio-Containment).
- **Tipado:** Prohibición total del tipo `any`. Todo dato externo debe ser validado en la frontera.

## 🧹 MANDATO S5: CALIDAD TÉCNICA Y PODA (ANTI-SLOP)
- **Definición:** Toda advertencia (Warning) es un error fatal. Cero tolerancia al ruido.
- **Poda:** Premiamos la eliminación de líneas. El código muerto o redundante se mueve a `deprecated/` tras validación.
- **Anti-Gaslighting:** Prohibido afirmar éxito sin evidencia empírica (logs/terminal). "Funciona" es una trampa.

## 📏 MANDATO S17: SINCRONIZACIÓN UNIVERSAL DE VERSIÓN (ANTI-DRIFT)
- **Definición:** La versión del protocolo debe ser IDÉNTICA en todos los manifiestos (`SPEC.md`, `AGENT.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md` y `.agent_state.json`).
- **Paridad Obligatoria:** Un solo carácter de diferencia en la versión entre estos archivos dispara un **Fallo Crítico** y bloquea cualquier commit.
- **Acción:** El agente DEBE verificar la paridad al inicio y al final de cada sesión. Si detecta desincronización, su única tarea permitida es la resincronización total antes de proceder.

## 💾 MANDATO S19: REGISTRO DE CHECKPOINT DE ESTADO (STATE CHECKPOINT)
- **Definición:** Toda sesión de cambio significativo (>50 líneas o cambios estructurales/de diseño) DEBE registrar un `STATE CHECKPOINT` formal en `HISTORIAL.md` con los hashes SHA256 de los archivos alterados.
- **Formato:** Incluir Timestamp, Agente, Estatus, Files Modified y State Hash para prevenir deriva o forks en sesiones concurrentes.

## 📊 MANDATO S20: REPORTES DE ERROR ESTRUCTURADOS (STRUCTURED ERROR LOGS)
- **Definición:** Toda violación detectada, excepción en caliente o fallo de tests debe ser documentado de forma machine-parseable en `HISTORIAL.md` usando etiquetas estructuradas: `[ERROR] [REGLA_VIOLADA] [CONTEXT] [SEVERITY]`.
- **Campos:** Timestamp, Agent, Severity, Root Cause, Impact y Required Action. Quedan prohibidos los reportes de error informales o ambiguos.

## 🛑 MANDATO S21: VETO A GIT DESTRUCTIVO Y DUAL-SESSION AWARENESS (REGLA #0-PROHIBIDA)
- **Definición:** Queda terminantemente PROHIBIDO usar comandos destructivos de control de versiones (`git reset --hard`, `git revert` o `git clean`) de manera directa o en scripts automatizados sin autorización explícita previa del operador Luis.
- **Dual-Session Awareness:** Antes de tocar o editar archivos compartidos, el agente debe verificar el estado y los últimos commits mediante `git status` y `git log` de forma obligatoria. Si hay cambios de otros agentes, se debe analizar su impacto para evitar regresiones antes de realizar un commit.
- **Enforcement:** El módulo de validación de permisos bloqueará activamente cualquier intento de invocar estos comandos y levantará excepciones críticas inmediatas.

## 💰 MANDATO S18: OPTIMIZACIÓN DE TOKENS — 3 FUGAS CRÍTICAS
- **Fuga 1 — Prompt Caching (Static Instructions):** Cada mensaje paga por CLAUDE.md + STATUS.md completos (~1200 tokens). Solución: Caching de API (almacenar instrucciones estáticas, reutilizar −90% en siguientes mensajes).
- **Fuga 2 — RAG Pruning (Fragmentos):** Lectura de archivos >100 líneas para cambios de 1 línea. Solución: ChromaDB indexing de fragmentos (<50 líneas), no archivos completos. RTK (Rust Token Killer) para compresión CLI.
- **Fuga 3 — Output Constraining (Preámbulos/Conclusiones):** Respuestas verbosas con saludos, conclusiones innecesarias. Solución: Modo "Caveman" (XML hard-delimiters), máx 5 líneas de explicación, código > narrativa.
- **Mandato de Acción:** Antes de usar RTK o ChromaDB, verificar que están instalados. Fallback a compresión manual si no disponibles.

## MANDATO S22: PUREZA DE CODIGO — PROHIBICION ABSOLUTA DE CODIGO TEATRO

- **Stubs prohibidos:** Ningun metodo de produccion puede retornar `True`, `0`, `"success"` o similar de forma incondicional sin ejecutar logica real. Un stub que reporta exito sin verificar nada es una mentira registrada en el evidence trail.
- **Verificacion por exit code:** La verdad de un proceso externo es su `returncode`. Verificar por string (`"APPROVED" in stdout`, `"100%" in stdout`) es teatro y queda prohibido. Usar siempre `code == 0`.
- **Emojis prohibidos en scripts de produccion:** Los scripts en `scripts/` no usan emojis en `print()` ni `logging`. Los emojis en hooks de git o mensajes de CI son aceptables solo si el mandato del contexto lo permite.
- **xfail permanente prohibido:** Un test marcado `xfail` sin criterio de conversion a `pass` es cobertura falsa. Todo `xfail` debe tener una condicion de remocion documentada como comentario en el test.
- **Nombres honestos obligatorios:** El nombre de un modulo, clase o funcion debe describir exactamente lo que hace. Nombres como "self_improvement_loop" que implican comportamiento que no existe son violacion de este mandato.
- **Deprecated como cuarentena, no como basurero:** Mover a `deprecated/` es una medida temporal de cuarentena, no una forma de silenciar un error. Si el codigo en deprecated/ tiene una idea rescatable, se rescata. Si no, se documenta la razon del retiro en HISTORIAL.md.

## MANDATO S23: PUREZA DE TESTS EN VIBE CODING

- **Asercion negativa obligatoria:** Todo test debe incluir al menos una verificacion de que el codigo RECHAZA o FALLA ante input invalido, no solo que acepta input correcto. Un test que solo verifica el happy path es cobertura parcial, no cobertura.
- **Mocking interno prohibido:** Queda prohibido usar `unittest.mock.patch` o `monkeypatch` sobre modulos en `scripts/` del mismo repositorio. Solo se permite mock de servicios externos (APIs de terceros, bases de datos externas, filesystem de sistema operativo). El codigo propio se prueba ejecutandolo real.
- **xfail con criterio de remocion obligatorio:** Todo `@pytest.mark.xfail` debe tener en la linea anterior un comentario que incluya la razon tecnica y la condicion bajo la cual debe removerse. Formato: `# TODO:`, `# REMOVE_WHEN:`, o `# reason:`. Sin este comentario, el xfail es cobertura falsa detectada por D9.
- **Feature flags en tests prohibidos:** Ningun test puede tener logica condicional basada en variables de entorno (`os.getenv`, `os.environ`). El test siempre ejecuta la ruta real sin atajos de entorno.
- **Verificacion de ruptura antes de declarar completo:** En vibe coding, antes de marcar una feature como completa, el agente debe demostrar que al menos 1 test falla si se elimina la logica principal del feature. Esta es la prueba empirica de que el test mide algo real, no teatro.
- **Path absoluto en tests prohibido:** Ningun test puede hardcodear rutas absolutas (`C:\`, `D:\`, `/home/`, `/Users/`). Usar siempre `Path(__file__).parents[N]` o la constante `ROOT` relativa al repo. Detectado automaticamente por D9.
- **Auditoria de descubrimiento antes de APPROVED:** Antes de declarar APPROVED, el agente DEBE verificar que no hay archivos "fantasma" en `/tests`. Procedimiento: (1) listar todos los archivos en `/tests/`, (2) listar los tests efectivamente descubiertos por pytest, (3) comparar — cualquier archivo en `/tests/` no descubierto por pytest debe clasificarse como test activo, helper explícito, o moverse fuera de `/tests/`. Un archivo ambiguo en `/tests/` es deuda de cobertura invisible que permite falsos APPROVED.

---

## 🔧 REGLAS DETALLADAS — IMPLEMENTACIONES CRÍTICAS

### REGLA #18 — PRE-COMMIT SAFETY HOOK
- **Bloqueados:** `git reset --hard`, `git clean -f`, `rm -rf`, `git push --force origin main`
- **Permitidos:** `git reset --soft`, `git revert`, commits normales, push a ramas feature
- **Enforcement:** `.git/hooks/pre-commit` inspecciona mensajes de commit; detecta intención destructiva
- **Override:** Requiere mensaje con `[FORCE] [REGLA #18 DIRECTIVE] [razón específica]`

### REGLA #21 — POST-SESSION RETROSPECTIVE
- **Obligatoria:** Cada sesión DEBE tener retrospectiva antes de COMPACT/CLEAR
- **Formato:** JSON-parseable en HISTORIAL.md con 5 preguntas:
  1. ¿Qué aprendiste NO obvio?
  2. ¿Qué regla violaste (si acaso)?
  3. ¿Qué debería saber el próximo agente?
  4. ¿Qué falta en AGENT_SAFETY.md?
  5. ¿Token budget fue eficiente? `{efficient: bool, estimate: N, actual: N, note: "..."}` — **Umbral:** `efficient = true` si `actual/estimate < 1.1` (10% overhead aceptable). Si overhead > 10% o se requirió COMPACT anticipado → `efficient = false` + explicar causa.
- **Enforcement:** Pre-push hook verifica que la última sesión en HISTORIAL.md tiene sección RETROSPECTIVE

### REGLA #29 — ROLLBACK TESTING
- **Aplicabilidad:** Migraciones BD, cambios esquema API, rotación secretos, reorganización archivos, cambios CLAUDE.md/AGENT.md/REGLAS
- **Procedimiento:** 3 pasos — (1) Plan reversión, (2) Ejecutar operación + prueba rollback real en dev, (3) Documentar resultado en HISTORIAL.md
- **Enforcement:** Pre-push hook bloquea commits con cambios destructivos sin "✅ Estado: PASSED" documentado
- **Rollback SLA:** Debe completarse en <5 minutos idealmente

### REGLA #31 — STACK REQUIREMENTS & SETUP VALIDATION
- **Stack Ideal:** Python 3.9+, RTK (Rust Token Killer), git hooks, SQLite3, pathlib/json/re/subprocess (built-in)
- **Validación:** Ejecutar `python scripts/setup_validate.py --full` al inicio de cada proyecto
- **RTK Mandatorio:** Agente debe anteponer `rtk` a comandos de lectura sistema (`git status`, `ls -R`) automáticamente
- **Fallback:** RTK opcional en dev; REQUERIDO en producción. Sin RTK: −60-90% → −20-30% compresión

### S18 — TOKEN ESTIMATION OBLIGATORIO EN PLAN.md
- **Mandato:** Todo PLAN.md DEBE incluir estimación de costo de tokens ANTES de iniciar trabajo.
- **Formato:** `Estimación: ~N turnos | ~X tokens | headroom Y%`
- **Escalación:** Si estimado supera el 70% del headroom disponible → STOP, rediseñar scope.
- **Fuente:** Lección extraída de DIRECTIVAS_PART_1 (S11 sprint, 2026-05-26)

## 🚫 MANDATO S19: REEMPLAZAR = ELIMINAR + CREAR (ANTI-ZOMBIE-COMPAT)

**Definición:** Cuando se ordena reemplazar un archivo, módulo, clase o función por uno nuevo, el viejo SE ELIMINA. Sin excepciones.

**Prohibiciones absolutas:**
- `from OLD import X` en el archivo nuevo (herencia de compatibilidad)
- `(new.exists() or old.exists())` — rutas alternativas de adopción
- Shims que reenvían al nuevo (`sys.exit(subprocess.run([new]) )`)
- Tests con sentinelas para OLD y NEW simultáneamente
- Comentarios `# backward compat`, `# for now`, `# compatibility shim`
- Herencia de clase de un archivo marcado para eliminación

**Regla operativa:** Una sola fuente de verdad. El reemplazo es atómico: git rm old + crear new en el mismo commit. Si el nuevo necesita lógica del viejo, la lógica se COPIA, no se importa.

**Evidencia del riesgo:** Claude intentó 3 veces mantener `audit_8d.py` vivo al reemplazarlo (P7.1, 2026-05-27): herencia, fallback "or", sentinelas duales. Cada intento fue revertido manualmente. **VC-118.**

**Audit:** `run_security_audit_12d.py D1` verifica ausencia de patrones shim en scripts activos.

**🔍 RENAME SWEEP RULE (extensión S19 — lección VC-119, 2026-05-28):**

Después de eliminar o renombrar cualquier archivo, el agente DEBE ejecutar este paso antes de declarar el commit completo:

```bash
grep -r "nombre_viejo" . --include="*.py" --include="*.md" --include="*.json"
```

Cada hit debe clasificarse como: (a) actualizar, (b) eliminar, o (c) documentar como intencional (e.g. centinelas "does_not_exist"). **Zero referencias funcionales al nombre viejo antes de hacer commit.**

Omitir este paso es el error que produjo GF-3 y los 4 stale comments de audit_8d en P7.1.

---
**Rector:** La eficiencia de tokens es secundaria ante la integridad del sistema. No negocies el rigor.


