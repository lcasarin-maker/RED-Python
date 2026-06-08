# PLAN — Semana 2: Configuración Exterior

**Fecha Inicio:** 2026-06-02T13:00:00Z  
**Semana:** 2 (Cycle 2 Remediación)  
**Duración Estimada:** 3 días  
**Status:** PENDIENTE EJECUCIÓN

---

## Tareas Semana 2

### Tarea 2.1 — Crear AGENT.md en 11 proyectos ⭐ CRÍTICA

**Objetivo:** Replicar template de protocolo (Quenza/AGENT.md) a 11 proyectos externos.

**Criterio Éxito:** 13+ proyectos con AGENT.md (11 externos + 2 activos = 13)

**Proyectos Target (11):**
1. Aequitas_OS
2. Agente_Inmobiliario
3. Blog_Ciudadano_X
4. Calculadora de sueldos
5. Calculadora_Plazos
6. Control_Procesal
7. Declutter
8. Frankenstein
9. Imagen_Corporativa_Aequitas
10. Indices_Financieros
11. Maletin Homeopatia

**Dependencias:**
- [ ] Template existe: `Quenza/AGENT.md`
- [ ] Quenza es un proyecto que pueda servir como referencia
- [ ] Acceso a los 11 proyectos (carpetas o repositorios)

**Riesgos (Angry Path):**

1. **RIESGO: Template no existe**
   - Síntoma: No hay Quenza/AGENT.md
   - Impacto: No hay base para copiar
   - Mitigación: Crear template desde PROTOCOL_SYSTEM.md + AGENT.md existente (Cerberus)

2. **RIESGO: Proyectos no accesibles**
   - Síntoma: Directorio no existe o permisos insuficientes
   - Impacto: No se pueden escribir archivos
   - Mitigación: Verificar ubicación de cada proyecto antes de proceder

3. **RIESGO: Personalización incorrecta**
   - Síntoma: AGENT.md copiado sin cambiar nombre del proyecto/usuario
   - Impacto: Documentación inútil (refiere a "CoderCerberus" en lugar del proyecto)
   - Mitigación: Template debe tener placeholders {PROJECT_NAME}, {OWNER}, {REPO}, etc.

---

## Fases de Ejecución

### Fase 1: Validación (Bloqueante) ⏹️

1. **Verificar template:**
   ```bash
   ls -la Quenza/AGENT.md
   wc -l Quenza/AGENT.md
   ```

2. **Verificar acceso a proyectos:**
   - Enumerar los 11 directorios
   - Verificar permisos de escritura en cada uno
   - Documentar ubicación exacta

3. **Diseñar template parametrizado:**
   - Identificar placeholders (PROJECT_NAME, OWNER, REPO_PATH, etc.)
   - Crear versión con placeholders
   - Validar sintaxis

### Fase 2: Replicación (Después de Fase 1)

Para cada proyecto:
1. Leer Quenza/AGENT.md
2. Reemplazar placeholders con datos del proyecto
3. Escribir a `{proyecto}/AGENT.md`
4. Validar: archivo existe + tamaño > 100 bytes
5. Verificar: contiene nombre del proyecto (no "CoderCerberus")

### Fase 3: Validación Final

```bash
# Contar AGENT.md en todos los proyectos
find . -name "AGENT.md" -type f | wc -l
# Esperado: 13+ (11 nuevos + actuales)

# Verificar que contenido es distinto (no copia idéntica)
find . -name "AGENT.md" -type f -exec grep "PROJECT_NAME\|CoderCerberus" {} +
# Esperado: reemplazados, no placeholders
```

---

## Template Esperado

Estructura de Quenza/AGENT.md (asumir):
```markdown
# AGENT.md — {PROJECT_NAME}

Binding: {PROJECT_BINDING}
Owner: {OWNER}
Repo: {REPO_PATH}

## Mandatos Activos
[Mandatos específicos al proyecto]

## Startup Obligatorio
[Procedimiento de inicio]
```

---

## Blocked By

- [ ] **Validación Fase 1:** Confirmar que Quenza/AGENT.md existe y es un template válido
- [ ] **Acceso a proyectos:** Localizar y confirmar acceso a los 11 directorios

---

## Próximos Pasos

1. Ejecutar Fase 1 (Validación)
2. Si bloqueadores resueltos → Proceder Fase 2 (Replicación)
3. Validar Fase 3 (Confirmación)

---

**Responsable:** User  
**Prioridad:** HIGH  
**Impacto:** Todos los 11 proyectos tendrán documentación de protocolo alineada a CoderCerberus
