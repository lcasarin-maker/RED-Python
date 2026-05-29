# SINTAXIS_MULTI_AGENT.md — Lectura Dirigida por Agente
**Fuente:** deprecated/docs/TEMPLATE_SINTAXIS_LOCAL.md | **Rescatado:** 2026-05-24

Regla universal: NUNCA cargar un archivo completo de mas de 100 lineas. Siempre usar fragmentos con sintaxis nativa del agente activo.

---

## TABLA MAESTRA

| Agente | Sintaxis de Rango | Ejemplo |
|--------|-------------------|---------|
| **Claude Code** | `read archivo.py --lines X:Y` | `--lines 45:78` |
| **Gemini CLI** | `@archivo.py:X-Y` | `@archivo.py:45-78` |
| **Codex / OpenAI** | Descripcion textual | "Ver archivo.py, lineas 45-78 (funcion calcular_score)" |
| **ChatGPT Projects** | `Read artifact id, lines X-Y` | `lines 45-78` |

---

## IMPLEMENTACION POR AGENTE

### Claude Code
```
Para leer archivo.py lineas 45-78:
  read archivo.py --lines 45:78

Para leer archivo.py lineas 120-200:
  read archivo.py --lines 120:200

PRINCIPIO: Nunca leas completo >100 lineas. Siempre usa --lines X:Y
```

### Gemini CLI
```
Para leer archivo.py lineas 45-78:
  @archivo.py:45-78

Para leer archivo.py lineas 120-200:
  @archivo.py:120-200

PRINCIPIO: Nunca leas completo >100 lineas. Usa @archivo:X-Y
```

### Codex / OpenAI Operator
```
Para leer archivo.py lineas 45-78:
  [Ver archivo.py, lineas 45 a 78 (funcion calcular_score)]

PRINCIPIO: Describe el rango en lenguaje natural (no tiene sintaxis de rango nativa)
```

### ChatGPT Projects
```
Para leer archivo.py lineas 45-78:
  Read artifact artifact_id, lines 45-78

PRINCIPIO: Si tienes herramienta de rango, usala. Si no, describe en texto.
```

---

## INTEGRACION CON REGLA #1

**REGLA #1 (agnostica):**
> "El agente NUNCA carga un archivo completo >100 lineas. Carga SOLO el fragmento usando su sintaxis nativa."

**Tu implementacion:**
1. Elige tu fila en la tabla
2. Usa ESA sintaxis para toda lectura dirigida
3. Sin excepciones (salvo que justifiques con token count)
4. Si tu sintaxis cambia: actualiza este archivo + notifica a Luis

---

**Ahorro tipico:** -80% a -90% input tokens vs lectura completa de archivos.
