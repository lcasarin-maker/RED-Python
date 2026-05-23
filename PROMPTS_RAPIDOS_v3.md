# PROMPTS_RAPIDOS v3.0 — Sprint 0 (Optimizados)
## Dónde copiar/pegar para cada agente

---

## PARA CLAUDE CODE (Desktop + Terminal)

### Template 1: Retomar sesión
```xml
<instrucciones>
Lee los documentos de contexto. No expliques lo que vas a hacer, hazlo.
</instrucciones>

<contexto>
  <archivo>CLAUDE.md</archivo>
  <archivo>STATUS.md</archivo>
</contexto>

<tarea>
Explícame en español simple: dónde estamos y cuál es el siguiente paso exacto.
Luego ejecuta ese paso SOLO si es pequeño y seguro.
</tarea>

<formato_respuesta>
ESTADO: [1 línea]
SIGUIENTE: [1 línea]
ACCIÓN: [qué hiciste, máx 3 líneas]
STATUS_ACTUALIZADO: [sí/no]
</formato_respuesta>
```

### Template 2: Tarea específica
```xml
<instrucciones>
Lee CLAUDE.md y STATUS.md. Ejecuta EXACTAMENTE una cosa.
Si no queda claro, haz la opción más segura.
</instrucciones>

<contexto>
  <archivo>CLAUDE.md</archivo>
  <archivo>STATUS.md</archivo>
</contexto>

<tarea>
[ESCRIBE TU TAREA AQUÍ EN 1-2 LÍNEAS]
</tarea>

<restricciones>
- SOLO este archivo: [ARCHIVO ESPECÍFICO]
- Máximo 200 palabras en tu respuesta
- Si hay riesgo: AVÍSAME ANTES de ejecutar
</restricciones>

<formato_respuesta>
ACCIÓN: [1 línea]
RESULTADO: [máx 3 líneas]
PRÓXIMO: [siguiente paso]
STATUS_ACTUALIZADO: [sí/no]
</formato_respuesta>
```

---

## PARA CODEX (Desktop)

### Template: Ejecución
```xml
<instrucciones>
Lee AGENTS.md y STATUS.md. Ejecuta UNA cosa exactamente.
No analices, no expliques, hazlo. Si ambiguo, opción segura.
</instrucciones>

<contexto>
AGENTS.md
STATUS.md
</contexto>

<tarea>
[Tu tarea en máximo 2 líneas]
</tarea>

<restricciones>
- SOLO archivo: [ARCHIVO]
- Máximo 100 palabras en respuesta
- Avísame si hay riesgo ANTES
</restricciones>

<formato>
ACCIÓN: [1 línea]
RESULTADO: [3 líneas máx]
</formato>
```

---

## PARA GEMINI CLI (Terminal)

### Regla: NUNCA archivos completos, SIEMPRE fragmentos

**Paso 1:** Abre Notepad
**Paso 2:** Copia 5-10 líneas relevantes de STATUS.md
**Paso 3:** Abre Gemini CLI, pega fragmento
**Paso 4:** Pregunta específica: "¿Cuál es el riesgo en...?"
**Paso 5:** Copia respuesta a STATUS.md
**Paso 6:** Cierra

Costo: ~300 tokens (vs. 3000 si subes archivo completo)

---

## PARA ANTIGRAVITY (Desktop)

### Regla: SOLO revisión visual de fragmentos

**Caso 1 — Revisar sentencia:**
1. Copia 2-3 párrafos de sentencia → Notepad
2. Abre Antigravity, pega
3. Pregunta: "¿5 puntos jurídicos clave?"
4. Copia respuesta a PROMPTS_RAPIDOS.md
5. Cierra

Costo: ~300 tokens

**Caso 2 — Comparar contratos:**
1. Extrae párrafo 1 de contrato A → Notepad
2. Extrae párrafo 1 de contrato B → Notepad
3. Abre Antigravity, pega ambos
4. Pregunta: "¿Diferencia crítica en indemnización?"
5. Copia a análisis
6. Cierra

Costo: ~400 tokens

---

**ESTADO:** ✅ Sprint 0 plantillas completadas | Ahorro: −25% output tokens inmediato
**Próximo paso:** Copiar a 6 proyectos principales
