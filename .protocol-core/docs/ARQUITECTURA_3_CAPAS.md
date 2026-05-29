# ARQUITECTURA_3_CAPAS.md — Sistema Determinista con Orquestacion IA
**Fuente:** deprecated/docs/trabajo.md | **Rescatado:** 2026-05-24

Este documento define la arquitectura que separa LLMs probabilisticos de logica de negocio determinista. Es el patron estructural que debe seguir cualquier proyecto bajo el protocolo.

---

## EL PROBLEMA

Los LLMs son probabilisticos. La logica de negocio requiere consistencia determinista. Si el agente hace todo el trabajo directamente, los errores se componen: **90% de precision por paso = 59% de exito en 5 pasos.** La solucion es empujar la complejidad hacia codigo determinista.

---

## LAS 3 CAPAS

### Capa 1: Directiva (Que hacer)
- Archivos: `directives/` — SOPs escritos en Markdown
- Definen: objetivos, inputs, herramientas/scripts a usar, outputs, casos borde
- Idioma: lenguaje natural, como instrucciones a un empleado de nivel medio
- Regla: el agente NO crea ni sobreescribe directivas sin preguntar. Son el set de instrucciones y deben preservarse y mejorarse, no usarse y descartarse

### Capa 2: Orquestacion (Toma de decisiones)
- Actor: el agente IA (Claude, Gemini, etc.)
- Rol: routing inteligente — leer directivas, llamar scripts en orden correcto, manejar errores, pedir aclaraciones, actualizar directivas con aprendizajes
- NO hace el trabajo directamente — lee `directives/scrape_website.md` y ejecuta `execution/scrape_single_site.py`
- Es el pegamento entre intencion y ejecucion

### Capa 3: Ejecucion (Hacer el trabajo)
- Archivos: `execution/` — scripts Python deterministas
- Variables de entorno, API tokens en `.env`
- Manejan: llamadas API, procesamiento de datos, operaciones de archivos, interacciones con BD
- Caracteristicas: confiables, testeables, rapidos, bien comentados

---

## PRINCIPIOS OPERACIONALES

**1. Revisar herramientas antes de crear**
Antes de escribir un script, verificar si ya existe en `execution/` per la directiva activa. Crear nuevo solo si no existe equivalente.

**2. Self-annealing loop**
Cuando algo se rompe:
1. Leer mensaje de error y stack trace
2. Arreglar el script y volver a testearlo (salvo que use tokens pagados — en ese caso consultar primero)
3. Actualizar la directiva con lo aprendido (limites de API, timing, edge cases)
4. Sistema queda mas fuerte despues de cada fallo

**3. Actualizar directivas al aprender**
Las directivas son documentos vivos. Cuando se descubren restricciones de API, mejores enfoques, errores comunes o expectativas de timing — actualizar la directiva. Ejemplo: hit rate limit → buscar batch endpoint → reescribir script → testear → actualizar directiva.

---

## SELF-ANNEALING LOOP (Detalle)

```
Error ocurre
    ↓
1. Fix (arreglar el tool)
2. Test tool (verificar que funciona)
3. Update directive (incorporar nuevo flujo)
    ↓
Sistema mas fuerte
```

---

## ORGANIZACION DE ARCHIVOS

**Entregables vs Intermedios:**
- Entregables: Google Sheets, Google Slides, otros outputs cloud que el usuario puede acceder
- Intermedios: archivos temporales necesarios durante el procesamiento

**Estructura de directorio:**
```
.tmp/           — archivos intermedios (dossiers, datos scrapeados, exports temp) — nunca commitear
execution/      — scripts Python (los tools deterministas)
directives/     — SOPs en Markdown (el set de instrucciones)
.env            — variables de entorno y API keys
credentials.json, token.json — credenciales OAuth (en .gitignore)
```

**Principio clave:** Archivos locales son solo para procesamiento. Los entregables viven en servicios cloud. Todo en `.tmp/` puede borrarse y regenerarse.

---

## RELACION CON CERBERUS

| Capa Cerberus | Equivalente 3 Capas |
|---------------|---------------------|
| `directives/` | Capa 1 — Directivas (SOPs) |
| Claude/Gemini/Codex | Capa 2 — Orquestacion |
| `scripts/` + `cerberus/` | Capa 3 — Ejecucion determinista |
| `.agent_state.json` | Estado de orquestacion entre sesiones |

---

**Principio final:** Sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system. Be pragmatic. Be reliable. Self-anneal.
