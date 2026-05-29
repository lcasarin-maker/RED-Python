# CHECKLIST PRE-ENTREGA — Agent Self-Validation
**Completar ANTES de decir "Terminado" en cualquier tarea**

> **NOTA:** Este checklist es para que el agente (Claude/Gemini/GPT-4) lo use ANTES de decir "hecho". Si el agente lo salta → Luis puede rechazar la entrega hasta que pase.

---

## ✅ SECCIÓN 1: VALIDACIÓN DE LÍNEAS (Eficiencia)

```
Archivos críticos deben ser <100 líneas

Archivo                           Líneas   Límite   Status
───────────────────────────────────────────────────────────
AGENT.md                          ___      100      [ ]
CLAUDE.md                         ___      100      [ ]
GEMINI.md                         ___      100      [ ]
GPT4.md                           ___      100      [ ]
Cualquier archivo nuevo           ___      150      [ ]
```

**Si ALGUNO > límite:**
- [ ] Refactor: Eliminar líneas innecesarias
- [ ] Mover detalles a archivo ADVANCED o docs/
- [ ] Revalidar

---

## ✅ SECCIÓN 2: VALIDACIÓN DE AGNÓSTICISMO (Integridad)

**AGENT.md debe estar 100% limpio (0 keywords de agentes específicos)**

```
¿AGENT.md menciona CLAUDE-specific keywords?
  - haiku, sonnet, opus, /model, mcp, prompt caching
  Resultado: [ ] SÍ (❌ FALLA) [ ] NO (✅ PASA)

¿AGENT.md menciona GEMINI-specific keywords?
  - flash, pro, 1.5-pro, gemini, multi-modal, 2m tokens
  Resultado: [ ] SÍ (❌ FALLA) [ ] NO (✅ PASA)

¿AGENT.md menciona GPT-4-specific keywords?
  - gpt-4, gpt4, mini, vision, turbo, 4o-mini
  Resultado: [ ] SÍ (❌ FALLA) [ ] NO (✅ PASA)
```

**Cada extensión tiene SOLO sus keywords:**

```
¿CLAUDE.md tiene keywords de Claude?
  Resultado: [ ] SÍ (✅ PASA) [ ] NO (❌ FALLA)

¿CLAUDE.md menciona Gemini o GPT-4?
  Resultado: [ ] SÍ (❌ FALLA) [ ] NO (✅ PASA)

¿GEMINI.md tiene keywords de Gemini?
  Resultado: [ ] SÍ (✅ PASA) [ ] NO (❌ FALLA)

¿GEMINI.md menciona Claude o GPT-4?
  Resultado: [ ] SÍ (❌ FALLA) [ ] NO (✅ PASA)

¿GPT4.md tiene keywords de GPT-4?
  Resultado: [ ] SÍ (✅ PASA) [ ] NO (❌ FALLA)

¿GPT4.md menciona Claude o Gemini?
  Resultado: [ ] SÍ (❌ FALLA) [ ] NO (✅ PASA)
```

**Si ALGUNO FALLA:**
- [ ] Editar: Remover keywords fuera de lugar
- [ ] Verificar: Contenido duplicado entre extensiones
- [ ] Revalidar

---

## ✅ SECCIÓN 3: VALIDACIÓN 6D (Manual)

**Responde s/n para CADA dimensión:**

### Practicidad
- ¿Funciona en Windows 11 sin setup manual?
- ¿Todos los paths están correctos? (no hardcoded a tu máquina)
- ¿Usuarios pueden ejecutar sin problemas?

Resultado: [ ] PASS [ ] FAIL

---

### Completitud
- ¿Tiene TODO lo crítico?
- ¿Nada importante está faltando?
- ¿Se puede usar sin versión 2.0?

Resultado: [ ] PASS [ ] FAIL

---

### Integridad
- ¿Cero riesgo de corrupción de datos?
- ¿Agnósticismo validado (SECCIÓN 2)?
- ¿Validación de paths, permisos?
- ¿No hay race conditions?

Resultado: [ ] PASS [ ] FAIL

---

### Claridad
- ¿Código es legible?
- ¿Nombres de variables son claros?
- ¿Sin docstrings largos?
- ¿Comentarios solo si NO-obvio?

Resultado: [ ] PASS [ ] FAIL

---

### Usabilidad
- ¿Usuario puede usarlo sin problemas?
- ¿Mensajes de error son claros?
- ¿Fácil navegar la estructura?
- ¿Documentación existe dónde se necesita?

Resultado: [ ] PASS [ ] FAIL

---

### Limpieza
- ¿Cero logs de debug?
- ¿Cero secrets expuestos?
- ¿Cero temp files?
- ¿Archivos <100 líneas (SECCIÓN 1)?
- ¿Estructura lógica de carpetas (ver STRUCTURE.md)?
- ¿Sin commented-out code?

Resultado: [ ] PASS [ ] FAIL

---

## ✅ SECCIÓN 4: VALIDACIÓN DE ORGANIZACIÓN (Limpieza)

**Ver STRUCTURE.md para referencia. Checklist rápido:**

```
ESTRUCTURA DE CARPETAS:
- [ ] Python scripts están en scripts/ (no en raíz)
- [ ] Git hooks están en scripts/hooks/ (no en .git/)
- [ ] Tests están en tests/test_*.py (no esparcidos)
- [ ] REGLAS están en REGLAS/REGLA_XX.md (no en archivos grandes)
- [ ] Docs no-críticas están en docs/ADVANCED/ (no inflando AGENT.md)

NOMBRES CONSISTENTES:
- [ ] Specs: SPEC_BUGS.md, SPEC_FEATURES.md, SPEC_REFACTORS.md
- [ ] Tests: test_*.py (pytest standard)
- [ ] REGLAS: REGLA_00.md, REGLA_01.md, etc.
- [ ] Archivos: nombres describen contenido

GITIGNORE:
- [ ] .claude/ está en .gitignore (local config)
- [ ] .secrets/ está en .gitignore (sensitive data)
- [ ] .env, *.pyc, __pycache__/ están en .gitignore

SINCRONIZACIÓN:
- [ ] AGENT.md en raíz = AGENT.md en .claude/ (lógica idéntica)
- [ ] Extensiones (CLAUDE.md, etc) están en .claude/
- [ ] STATUS.md existe y tiene 7 Campos
```

**Si ALGUNO FALLA:**
- [ ] Reorganizar archivos a carpetas correctas
- [ ] Renombrar para consistencia
- [ ] Actualizar .gitignore
- [ ] Revalidar

---

## 🚀 RESULTADO FINAL

```
        Sección 1: Líneas       [ ] PASS / [ ] FAIL
        Sección 2: Agnósticismo [ ] PASS / [ ] FAIL
        Sección 3: 6D           [ ] PASS / [ ] FAIL
        Sección 4: Organización [ ] PASS / [ ] FAIL
        ───────────────────────────────────────────
        RESULTADO:              [ ] ✅ APROBADO / [ ] ❌ BLOQUEADO
```

**SI ALGUNA SECCIÓN FALLA:** Refactor y reintenta.
**SI TODAS PASAN:** OK para entregar.

---

## 📝 CÓMO USAR ESTE CHECKLIST

**Paso 1:** Completa tu tarea
**Paso 2:** Corre validación automática:
```bash
python scripts/validate_my_delivery.py
```

**Paso 3:** Completa ESTE checklist manualmente (6D es manual, el script hace el resto)
**Paso 4:** Si TODO está [ ] PASS → Entrega
**Paso 5:** Si ALGO está [ ] FAIL → Refactor y Paso 2

---

## 🎯 PRINCIPIO

**No entregar hasta que pase ESTE checklist + `validate_my_delivery.py`.**

Si lo saltas → entregas sin validar → fallas → tienes que refactor después.

Mejor: validar ANTES (5 min) que refactor DESPUÉS (30 min).
