# REFERENCIA_RAPIDA.md — Inicio de Sesion y Plantillas XML
**Fuente:** deprecated/docs/REFERENCIA_RAPIDA.md | **Rescatado:** 2026-05-24

---

## INICIO DE SESION (cada vez)

1. Modelo default: HAIKU (80% de tareas)
   `/model claude-haiku-4-5-20251001`

2. Prompt de retoma (copiar y pegar):

```xml
<instrucciones>
  Lee los archivos de contexto. No expliques lo que vas a hacer, hazlo.
</instrucciones>
<contexto>
  <archivo>AGENT.md</archivo>
  <archivo>STATUS.md</archivo>
</contexto>
<tarea>
  Explicame donde nos quedamos y cual es el siguiente paso exacto.
  Luego ejecutalo si es pequeno y seguro.
</tarea>
<formato_respuesta>
  ESTADO: [1 linea]
  SIGUIENTE_PASO: [1 linea]
  EJECUTADO: [max 3 lineas]
  STATUS_MD: [actualizado | pendiente]
</formato_respuesta>
```

---

## CUANDO EL CONTEXTO SE LLENA

Claude avisa con `[Ctx: 30+ msgs]`. Responder:
- `COMPACT` → limpia contexto, sigue en mismo chat
- `CLEAR` → cierra chat, abre nuevo

---

## MODELOS — CUANDO USAR CADA UNO

| Modelo | Cuando |
|--------|--------|
| HAIKU | Default (80% tareas: retoma, ediciones, lectura) |
| SONNET | Analisis, arquitectura, debugging complejo |
| OPUS | Cuando Sonnet falla en la misma tarea |

Comandos:
```
/model claude-haiku-4-5-20251001   — Haiku
/model claude-sonnet-4-6            — Sonnet
/model claude-opus-4-6              — Opus
```

---

## PLANTILLA: TAREA NUEVA CON ANGRY PATH

```xml
<instrucciones>
  Antes de implementar, lista 3 formas en que este plan puede fallar.
  Luego implementa con esas fallas en mente.
</instrucciones>
<contexto>
  <archivo>SPEC.md</archivo>
  <archivo>STATUS.md</archivo>
</contexto>
<tarea>
  [DESCRIBIR TAREA AQUI]
</tarea>
<restricciones>
  - Max 50 lineas de codigo por turno (S8)
  - Sin echo/sed/Add-Content: solo Edit/Write atomico (S7)
  - Logger obligatorio en todo codigo nuevo (S9)
  - No declarar exito sin terminal log (B7)
</restricciones>
```

---

## PLANTILLA: AUDITORIA DE PROYECTO EXTERNO

```xml
<instrucciones>
  Auditoria adversarial. Asume que el codigo esta roto hasta que se demuestre lo contrario.
  Sigue todos los archivos: HTML, scripts, configuracion, todo.
</instrucciones>
<contexto>
  <archivo>SPEC.md</archivo>
  <archivo>FALLOS_CONOCIDOS.md</archivo>
</contexto>
<tarea>
  Audita [NOMBRE_PROYECTO] contra los 6 dominios y reporta fallos concretos con ubicacion exacta (archivo:linea).
</tarea>
<formato_respuesta>
  D1: [PASS|FAIL] — [razon]
  D2: [PASS|FAIL] — [razon]
  D3: [PASS|FAIL] — [razon]
  D4: [PASS|FAIL] — [razon]
  D5: [PASS|FAIL] — [razon]
  D6: [PASS|FAIL] — [razon]
  FALLOS: [lista con archivo:linea]
  SIGUIENTE_PASO: [1 linea]
</formato_respuesta>
```

---

## REGLA #1 DE LECTURA DIRIGIDA

Nunca cargar un archivo completo de mas de 100 lineas. Usar siempre:
- Claude Code: `read archivo.py --lines 45:78`
- Gemini CLI: `@archivo.py:45-78`
- Codex: descripcion textual del rango
- ChatGPT Projects: `Read artifact id, lines 45-78`

Para tabla completa: ver `docs/SINTAXIS_MULTI_AGENT.md`.
