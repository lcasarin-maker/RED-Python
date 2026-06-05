# 🛡️ CoderCerberus V0.5 — Protocolo Único

**Binding Real | Agent-Agnostic | CoderCerberus v0.5**

**Verdad Única:** `D:\AI\Cerberus\`

---

## 🔗 VINCULACIÓN EXPLÍCITA

Este archivo es un **pointer** a la verdad única. Todos los proyectos bajo `D:\AI\` usan:

```
Proyecto/
├── .protocol-core/    ← symlink → D:\AI\Cerberus\rules\
├── .protocol-eval/    ← symlink → D:\AI\Cerberus\learnings\
└── [código normal]
```

**No dupliques Cerberus localmente.** Usa symlinks.

---

## 📋 MANDATOS ACTIVOS (CoderCerberus v0.5)

### SYSTEM-TIER (S1-S9, S17)
| Mandato | Capacidad | Acción |
|---------|-----------|--------|
| **S1: Rigor 12D** | ✅ FULL | Ejecuto `run_security_audit_12d.py` antes de commit |
| **S2: Brain-First** | ✅ FULL | Actualizo SPEC.md antes de código |
| **S3: Bio-Containment** | ✅ FULL | Auditoría línea por línea en fronteras I/O |
| **S4: Modularidad** | ✅ FULL | Esquemas Pydantic/Zod en datos externos |
| **S5: Anti-Slop** | ✅ FULL | Zero warnings; prueba = fallo; evidence-based |
| **S6: Large File Safety** | ✅ FULL | `Edit` <50 líneas; PROHIBIDO `Write` >200 líneas |
| **S7: Anti-Shell** | ✅ FULL | Nunca `echo`, `sed`, `Add-Content`; solo Edit/Write atómicas |
| **S8: Debt Tax** | ✅ FULL | Max 50 líneas código/turno; Simplicity Pass después |
| **S9: Logging Mandatorio** | ✅ FULL | Todo código nuevo: `logger.info(args, state)` |
| **S17: Paridad Versión** | ✅ FULL | Validar `.version` en .agent_state.json = v0.5 |

### BEHAVIOR-TIER (B1-B12)
| Mandato | Capacidad | Acción |
|---------|-----------|--------|
| **B1: Doctrina Fallo** | ✅ FULL | Asumo que fallo; verifi empírica antes de declarar éxito |
| **B3: Angry Path** | ✅ FULL | Listar 3 formas de romper el plan ANTES de implementar |
| **B7: Anti-Triunfalismo** | ✅ FULL | PROHIBIDO "éxito" sin logs de terminal o confirmación humana |
| **B8: Anti-Deriva** | ✅ FULL | Enfoco 100% en tarea actual; secundarios → HISTORIAL.md |
| **B9: Root Cause** | ✅ FULL | Explicar causa técnica en lenguaje natural ANTES de código |
| **B10: Checkpointing** | ✅ FULL | PLAN.md con pasos numerados ANTES de tocar código |
| **B11: Validación Deps** | ✅ FULL | Búsqueda/verificación de paquetes antes de `npm install` |
| **B12: Anti-Auto-Docs** | ✅ FULL | PROHIBIDO generar .md/.json/.yaml sin solicitud explícita (TK-049) |

---

## 📍 LOCALIZACIONES (Única Fuente de Verdad)

**Cerberus Maestro:** `D:\AI\Cerberus\`

**Cada Proyecto:** symlinks a Cerberus, nunca copia local.

---

## 🚀 STARTUP OBLIGATORIO (Cada Sesión)

1. **`git status`** — Verificar rama y limpieza
2. **Leer `AGENT.md`** (líneas 1-46, 2 min)
3. **Leer `SPEC.md`** (líneas 1-50, 3 min)
4. **Verificar symlinks OK:**
   ```bash
   ls -la .protocol-core
   # Debe mostrar: lrwxrwxrwx ... .protocol-core -> D:\AI\Cerberus\rules
   ```
5. **Proceder solo si no hay conflictos**

---

## 🔄 ARQUITECTURA: Hub-and-Spoke V0.5

**Cambio desde v0.3:**
- ❌ NO más copias locales de Cerberus
- ✅ Symlinks a reglas maestras
- ✅ Aprendizaje centralizado
- ✅ Repos independientes
- ✅ Evolución desacoplada

---

**Versión:** CoderCerberus v0.5 | **Binding válido desde:** 2026-06-01 | **Próxima revisión:** 2026-07-01
