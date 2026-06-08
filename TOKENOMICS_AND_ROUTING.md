# 💰 TOKENOMICS_AND_ROUTING.md — Conservación de Ventana de Contexto
**Estado:** 📜 BINDING POLICY | **Rigor:** Caveman Mode Enforced

---

## 1. Conservación Extrema de la Ventana de Contexto
El historial de la conversación **nunca** se utilizará como fuente de verdad del proyecto. El conocimiento se almacena en una estructura física de archivos independientes (`SPEC.md` + `AGENT.md` + `STATUS.md`).

### Reglas de Lectura Selectiva (RAG Pruning manual)
1. **No leas archivos completos** que superen las 100 líneas si no es estrictamente necesario.
2. Emplea búsquedas selectivas mediante comandos `grep_search` o lee **rangos delimitados** de líneas.
3. Si el contexto excede su capacidad útil, extrae solo la sección relevante para la tarea en curso y descarta el resto.

---

## 2. Restricción de Salida y Compactación (Context Compaction)
* **Caveman Mode (Modo Cavernícola):** Toda justificación o prosa en lenguaje natural se limitará a un **máximo estricto de 5 líneas de texto**. El output constraining es mandatario.
* **Compactación Forzada:** La conversación se interrumpirá cada 20 o 30 turnos para forzar una compactación del estado en un archivo físico (`STATUS.md`), seguido del inicio de un hilo limpio. Se debe sugerir `/compact` al usuario explícitamente.
* **Micro-resúmenes:** Genera micro-resúmenes de estado breves cada 10 mensajes.

---

## 3. Matriz de Enrutamiento y Niveles de Autoridad (Model Cascading)
Las tareas rutinarias se delegan en modelos rápidos y económicos (Haiku / Flash). Los requerimientos complejos se asignan a modelos de razonamiento profundo (Opus / Pro).

### Access Tiers:
* **Tier 1 (Write + VCS Control):** Agente principal en curso con plena autorización de escritura y control de versiones local.
* **Tier 2 (Local Isolation):** Subagentes confinados en entornos de ejecución locales aislados, limitados a variantes con flags `--dry-run`.
* **Tier 3 (Audit Read-Only):** Agentes de validación (como el `codebase_investigator`) con permisos de solo lectura para investigación.

---

## 4. Filosofía "TokenSaver Universal" (Nivel Prompt)
1. **Un objetivo claro por hilo:** No mezclar temas distintos en el mismo chat.
2. **XML Hard-Delimiters:** Cuando escribas prompts o plantillas para subagentes, usa delimitadores XML estrictos (`<instrucciones>`, `<contexto>`, `<tarea>`) para evitar "confusión de fronteras".
3. **Output Constraining:** Exige siempre a los subagentes un formato de respuesta rígido sin preámbulos.
4. **Pide Plan antes de Ejecución:** Si la tarea modifica el ecosistema central, exige siempre generar un `implementation_plan.md` antes de escribir una sola línea de código.

---
**Coder Cerberus V0.1 — Ecosistema Inmutable.**
