# 🛡️ PROTOCOL_SYSTEM — Código Penal de Coder Cerberus V0.1
**Estado:** 💀 ZERO-TRUST ENFORCED | **Nivel:** 1:1 Parity Mandatory
Version: v0.02


---

## 🛑 MANDATO S7: PROHIBICIÓN DE SHELL MODIFICATION (ANTI-BLIND WRITING)
- **Definición:** Queda terminantemente PROHIBIDO usar comandos de terminal (`echo`, `sed`, `Add-Content`, `Set-Content`, `>` o `>>`) para escribir, editar, inyectar o manipular de forma ciega el contenido de archivos del core o del workspace.
- **Razón:** El shell no tiene validación semántica ni de encoding y es propenso a corromper archivos. Toda edición DEBE pasar exclusivamente por las herramientas atómicas de edición y escritura del agente (`replace_file_content` o `write_to_file`).
- **Validación:** La suite de auditoría estática (`audit_6d.py`) buscará activamente patrones de comandos mutadores peligrosos en los scripts del control plane, hooks de git y archivos del workspace, disparando fallos inmediatos si se detecta su uso.
- **Excepción:** Solo se permite shell para lectura segura (`git diff`, `ls`), ejecución de tests o ejecución de scripts de validación autorizados.

## 📈 MANDATO S8: IMPUESTO DE DEUDA TÉCNICA (DEBT TAX)
- **Definición:** Prohibido generar o modificar más de 50 líneas de código real (excluyendo comentarios) en un solo turno.
- **Turno de Refactorización:** Tras cada bloque de 50 líneas, el agente está obligado a detenerse y realizar un "Simplicity Pass" para consolidar nombres y simplificar lógica antes de que el código decaiga.
- **Bloqueo:** No se puede proponer el siguiente bloque de lógica hasta que el humano certifique la legibilidad del anterior.

## 🔊 MANDATO S9: INSTRUMENTACIÓN VERBOSA OBLIGATORIA (ANTI-CAJA NEGRA)
- **Definición:** Queda terminantemente PROHIBIDO escribir funciones, clases o módulos "silenciosos".
- **Logging Mandatario:** Todo código generado por IA DEBE incluir puntos de entrada de logging estructurado (`logger.info` o equivalente) que describan los argumentos recibidos y el estado inicial.
- **Trazabilidad:** El manejo de errores (`try/except/catch`) debe loguear no solo el mensaje de error, sino el contexto de los datos que causaron el fallo. El código silencioso se considera deuda técnica letal.

---

## 🛑 MANDATO S1: RIGOR DE VALIDACIÓN (6D ANGRY PATH)
- **Definición:** Prohibido cerrar tareas sin score 100% en `scripts/audit_6d.py`.
- **Angry Path:** Si el código corre pero carece de `try/except` robustos o validación de tipos, la tarea es un fallo de seguridad.
- **Acción:** `Sin Tests, No Hay Código`. Cada bloque lógico debe tener un test de estrés que fuerce el error.
- **Nota:** La auditoría debe ejecutarse hasta alcanzar 100% de puntuación; el agente no debe detenerse prematuramente.

## 🧱 MANDATO S2: ARQUITECTURA E INTEGRIDAD (BRAIN-FIRST)
- **Definición:** El `SPEC.md` es el único "Cerebro". Prohibido mutar código sin actualizar primero el mapa mental.
- **Whitelist Strict:** Cualquier archivo no registrado en la Whitelist del `SPEC.md` es considerado una infección (Zombi) y bloquea el commit.
- **Dry-Runs:** Todo comando destructivo (git, rm, env) requiere un `dry-run` y explicación de riesgo previa.

## 🔐 MANDATO S3: SEGURIDAD Y CONFINAMIENTO (BIO-CONTAINMENT)
- **Definición:** Asumir que toda IA es un "Pasante Incompetente" que inyectará vulnerabilidades.
- **Acción:** Auditoría de seguridad línea por línea obligatoria en fronteras de I/O.
- **Prohibición Estricta:** Cero variables no sanitizadas o stubs SQL/HTML sin tipado de seguridad estricto en fronteras de comunicación I/O.
- **Tipado Fuerte:** Prohibición absoluta del uso del tipo genérico `any` en funciones I/O o interfaces de datos. Todo dato debe ser tipado de manera determinista y estricta.
- **Contención Física:** Cero acceso directo a DB de producción sin capas middleware validadas. Cero placeholders e inyecciones en APIs. Cero lógica de seguridad ("fallbacks") relajada.
- **Bóveda de Secretos Global:** Está estrictamente prohibido hardcodear llaves (API keys, Tokens, DB Passwords) en archivos `.env` dispersos. Todo secreto debe migrarse y leerse desde una bóveda centralizada global fuera del control de versiones (por ejemplo, `D:\GoogleDrive\AI\.secrets\`), y los repositorios locales solo deben contener archivos `.example`.

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

---
**Rector:** La eficiencia de tokens es secundaria ante la integridad del sistema. No negocies el rigor.


