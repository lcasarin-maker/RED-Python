# PLAN — Tarea 2.2: Completar SPEC.md en 3 proyectos

**Fecha Inicio:** 2026-06-02T13:45:00Z  
**Tarea ID:** 2.2 (Semana 2 — Configuración Exterior)  
**Criterio Éxito:** 3 proyectos con SPEC.md (contenido mínimo)  
**Status:** FASE 1 EN EJECUCIÓN

---

## Objetivo

Crear o completar SPEC.md en 3 proyectos con contenido mínimo (estructura base).

**¿Por qué?** SPEC.md es el "cerebro" del protocolo CoderCerberus. Sin él, el proyecto no tiene memoria de sus intenciones, restricciones o arquitectura.

---

## Proyectos Target (3)

De REMEDIACION_STATE.json:
- No especificó cuáles 3 → **BLOQUEADOR 1**

Opciones posibles:
- Los 3 proyectos sin AGENT.md todavía (si hay)
- Los 3 más críticos del negocio
- Los primeros 3 de la lista de 11
- Proyectos específicos que el usuario indique

---

## Fase 1: Validación (COMPLETADA ✅)

### Acción 1.1: Localizar proyectos target
```bash
# ¿Cuáles 3 proyectos necesitan SPEC.md?
# Opciones:
#   a) Los primeros 3: Aequitas_OS, Agente_Inmobiliario, Blog_Ciudadano_X
#   b) Proyectos específicos indicados por usuario
#   c) Proyectos sin SPEC.md actualmente
```

**BLOQUEADOR 1:** Definir cuáles son los 3 proyectos → **REQUIERE DECISIÓN DEL USUARIO**

### Acción 1.2: Verificar SPEC.md existentes
```bash
# Para cada uno de los 3:
find proyecto -name "SPEC.md" -type f
```

### Acción 1.3: Analizar contenido existente (si existe)
```bash
# ¿Qué hay adentro?
# ¿Qué falta?
```

---

## Fase 2: Diseño de template SPEC.md mínimo

**Contenido mínimo esperado:**
```markdown
# SPEC.md — {PROJECT_NAME}

## Propósito
[1 párrafo describiendo qué hace este proyecto]

## Mandatos Activos
[Qué reglas CoderCerberus se aplican aquí]

## Estructura
[Áreas principales del código]

## Restricciones
[Qué NO se debe hacer]

## Versión
[Versión del protocolo: CoderCerberus v0.5]
```

---

## Fase 3: Replicación (Similar a Tarea 2.1)

Para cada proyecto:
1. Crear SPEC.md si no existe
2. Completar si existe pero está vacío
3. Personalizar con nombre del proyecto
4. Validar: archivo > 100 bytes + contiene nombre del proyecto

---

## Riesgos (Angry Path)

1. **Falta definición de 3 proyectos**
   - Síntoma: No sé cuáles rellenar
   - Impacto: No puedo empezar
   - Mitigación: Preguntar al usuario

2. **SPEC.md tiene contenido que no debo sobrescribir**
   - Síntoma: Archivo existe pero vacío vs. incompleto vs. con contenido viejo
   - Impacto: Perder información existente
   - Mitigación: Leer primero, solo agregar secciones faltantes

3. **No hay suficiente contexto para completar**
   - Síntoma: No sé el propósito del proyecto
   - Impacto: SPEC.md genérico/incorrecto
   - Mitigación: Leer README.md o estructura del código

---

## Blocked By

- [ ] **DECISIÓN DEL USUARIO:** ¿Cuáles son los 3 proyectos?
  - Opción A: Aequitas_OS, Agente_Inmobiliario, Blog_Ciudadano_X (primeros 3)
  - Opción B: Otros 3 específicos
  - Opción C: Los que ya existan parcialmente

---

## Siguientes Pasos

1. Usuario indica cuáles 3 proyectos
2. Ejecutar Fase 1 (Validación)
3. Diseñar template
4. Ejecutar Fase 3 (Replicación)
5. Validar

**Responsable:** User  
**Plazo:** 3 días  
**Impacto:** 3 proyectos con "cerebro" de protocolo documentado
