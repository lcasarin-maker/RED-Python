# AGENT ONBOARDING — Entrenar Agentes sin Romper Nada

Para Claude, Gemini, Codex, ChatGPT, o cualquier agente IA nuevo en el proyecto.

---

## 📖 Onboarding (30 minutos)

### 1️⃣ Lee PRIMERO (5 min)
```
AGENT.md                 ← PROTOCOLO BASE (todos los agentes)
[AGENT_NAME].md          ← TU EXTENSIÓN ESPECÍFICA (CLAUDE.md, GEMINI.md, etc.)
AGENT_SAFETY.md          ← PROHIBICIONES críticas (⚠️ IMPORTANTE)
README.md                ← Router global
STATUS.md                ← Estado actual (7 CAMPOS)
```

**Explicación:**
- **AGENT.md:** Protocolo agnostic que aplica a TODOS los agentes
- **[AGENT_NAME].md:** Tu archivo específico (ej: CLAUDE.md si eres Claude, GEMINI.md si eres Gemini)
  - Extiende AGENT.md con instrucciones agent-específicas
  - Ej: CLAUDE.md agrega auto-inicialización, modelo selection, MCP filesystem
  - Ej: GEMINI.md agrega incident awareness, dual-session risks

### 2️⃣ Entiende la estructura (10 min)
```
NIVEL_1_INTEGRIDAD.md    ← Código (indice a N1_MODULOS/)
NIVEL_2_OPERACION.md     ← Operación (indice a N2_MODULOS/)
  └─ N2_MODULOS/N2_M5_*  ← REGLAS #0-17 aquí
NIVEL_3_VALIDACION.md    ← Checklist 6D
NIVEL_4_GUARDIAS.md      ← Prohibiciones/obligatorios
NIVEL_5_TOKEN_SAVING.md  ← Optimización tokens
```

### 3️⃣ Memoriza estas REGLAS (10 min)
```
#0:  Atomicidad (estado PREVIO)
#1:  Lectura dirigida
#2:  Modo cavernícola (no derives)
#3:  Memoria = archivos proyecto
#4:  Monitoreo con triggers
#5:  Honestidad brutal
#6:  Edición quirúrgica
#7:  Perfil usuario (Luis: abogado, no programmer)
#8:  Control scope estricto
#9:  Sigue plan, no derives
#10: Verifica antes de preguntar
#11: Decide y ejecuta
#12: Exploración vs auditoría
#13: Auto-commit (>3 archivos o >50 líneas)
#14: Reversión y backups
#15: Validación 6D OBLIGATORIA (antes de CLEAR)
#16: Ciclo de vida + limpieza
#17: Validación post-movimiento
#18: Pre-commit safety hook (bloquea destructivos)
#19: State checkpoint format (SHA256, reducer)
#20: Structured error reporting (JSON-parseable)
#21: Post-session retrospective (5 Q + JSON)
#22: Sources of Truth Index (SPEC vs POLICY)
```

### 4️⃣ ⚠️ LEE AGENT_SAFETY.md
```
PROHIBIDO: git reset / revert / clean sin directive
OBLIGATORIO: Leer HISTORIAL.md antes de cambios destructivos
OBLIGATORIO: Documentar cambios en HISTORIAL.md
```

### 5️⃣ Practica (5 min)
- Abre proyecto
- Lee STATUS.md
- Identifica CAMPO 3 "Trabajando en"
- Lee últimas 3 entradas HISTORIAL.md
- ✅ Listo

---

## 🚨 FAIL-SAFES (Evitar Romper Cosas)

### Fail-Safe #1: Antes de CUALQUIER `git` destructivo
```bash
# NUNCA ejecutes sin checking:
git reset / revert / clean / rm / checkout .

# SIEMPRE:
1. Leer HISTORIAL.md (últimos cambios)
2. git status (qué modificaste)
3. Pregunta a usuario: "¿Voy a [ACCIÓN]? ¿Confirmado?"
4. Documenta en HISTORIAL.md después
```

### Fail-Safe #2: Si otro agente hizo cambios
```
[1] Lee HISTORIAL.md PRIMERA
[2] Revisa últimas 3 sesiones
[3] Si hay cambios recientes: INTEGRA, no REVIERTAS
[4] Ejemplo: Gemini hizo v2.8.6, Claude hizo FASE 5
             → Solución: v2.9.0 (ambos preservados)
             → NO: git reset (perdería FASE 5)
```

### Fail-Safe #3: Dual-session conflicts
```
Si dos agentes trabajan en paralelo:
  [A] Claude: FASE 5 (README, CONTRIBUTING, .secrets)
  [B] Gemini: v2.8.6 (Módulos, REGLAS #0-17)
  
  ❌ MALO: Gemini ejecuta git reset → pierde FASE 5
  ✅ BUENO: Claude preserva v2.8.6 + restaura FASE 5 → v2.9.0
```

---

## 📋 TEMPLATE: Primeras 5 minutos de Sesión

```markdown
# Mi Primera Sesión en Coder Cerberus V0.1

## ✅ Checklist Pre-Trabajo
- [ ] Leí AGENT.md (protocolo base)
- [ ] Leí [MI_ARCHIVO].md (CLAUDE.md / GEMINI.md / mi extensión)
- [ ] Leí AGENT_SAFETY.md
- [ ] Leí STATUS.md (7 CAMPOS)
- [ ] Leí HISTORIAL.md (últimas 3 sesiones)
- [ ] git status (limpio o qué cambió?)
- [ ] Entiendo REGLA #0, #13, #15, #17

## 📝 Mi Tarea (qué me pidió usuario)
[Describe aquí]

## 🎯 Plan
1. [Paso 1]
2. [Paso 2]
3. Validar 6D
4. COMPACT si >40 msgs

## ⚠️ Si rompo algo
1. git log --oneline (ver qué pasó)
2. Documenta en HISTORIAL.md "Sesión X — Fallo detectado: [QUÉ]"
3. Informa a usuario INMEDIATAMENTE
4. NO ejecutes git reset sin confirmación
```

---

## 🔐 REGLAS DE ORO (Memorizar)

```
1. NUNCA git reset/revert sin directive explícita ← CRITICAL
2. SIEMPRE leer HISTORIAL.md antes de destructivos ← CRITICAL
3. SIEMPRE documentar qué hiciste en HISTORIAL.md ← CRITICAL
4. SIEMPRE validar 6D antes de CLEAR (REGLA #15) ← CRITICAL
5. SIEMPRE respetar scope (REGLA #8) ← IMPORTANT
6. NUNCA asumir (REGLA #12, auditoría) ← IMPORTANT
7. SIEMPRE auto-commit si >3 archivos (REGLA #13) ← IMPORTANT
8. SIEMPRE test post-movimiento (REGLA #17) ← IMPORTANT
```

---

## 📞 Si Necesitas Ayuda

**Pregunta fácil?** → REGLA #10 (Verifica antes de preguntar)
**Cambio grande?** → REGLA #11 (Decide y ejecuta) + REGLA #15 (Valida 6D)
**Duda de seguridad?** → Leer AGENT_SAFETY.md
**Histórico?** → HISTORIAL.md
**Estado actual?** → STATUS.md (7 CAMPOS)

---

## ✅ Eres Listo Cuando...

- [ ] Entiendes REGLA #0-17
- [ ] Sabes qué es AGENT_SAFETY.md y por qué existe
- [ ] Lees HISTORIAL.md antes de destructivos
- [ ] Documentas cambios automáticamente
- [ ] Validas 6D antes de CLEAR
- [ ] Haces COMPACT cuando contexto >40 msgs

**Bienvenido al protocolo.** No rompas nada. 🚀
