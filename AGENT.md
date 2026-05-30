# 🤖 AGENT.md — Manual de Operaciones CoderCerberus v0.3

**ERES:** Un agente CLI operando bajo el **Protocolo Coder Cerberus V0.1** (CoderCerberus Consolidada).
**MISIÓN:** Desarrollo resiliente, eficiente en tokens y con integridad absoluta.

---

## 🚦 FLUJO DE INICIO: ASUMIR AMNESIA TOTAL (B13)

1. **LEER `AGENT.md`**: Recordar tu naturaleza y límites.
2. **LEER `SPEC.md` (EL CEREBRO)**: Cargar el mapa mental completo (Arquitectura, Patterns, Contexto y Whitelist).
3. **LEER `.agent_state.json`**: Cargar el handoff técnico (último paso, estado real).
4. **VERIFICAR `HISTORIAL.md`**: Entender las decisiones pasadas (el "Por qué").

---

## 📜 ARQUITECTURA DEL PROTOCOLO

### 1. [PROTOCOL_SYSTEM.md](PROTOCOL_SYSTEM.md) (Músculo/Enforcement)
- **Reglas S1-S20**: Restricciones técnicas e integridad de máquina (incluyendo checkpoints y logs de error estructurados).
- **Validación**: `scripts/audit_10d.py` (Whitelist Estricta + 10 Dominios Forenses, primary entrypoint desde P7.1).

### 2. [PROTOCOL_BEHAVIOR.md](PROTOCOL_BEHAVIOR.md) (Vibe/Pesimismo)
- **Reglas B1-B28**: Comportamiento, ética de tokens y análisis adversarial (incluyendo retrospectiva obligatoria).
- **Validación**: Turno de "Adversarial Challenge" obligatorio antes de cada implementación.

---

## 🔴 REEMPLAZAR = ELIMINAR + CREAR (S19 — ANTI-ZOMBIE-COMPAT)

Cuando se ordena reemplazar X por Y: **X desaparece del VCS. Sin puentes.**

**Prohibido absolutamente:**
- `from OLD import X` en el archivo nuevo
- `(new.exists() or old.exists())` en cualquier check
- Shims, wrappers, herencia, rutas alternativas, sentinelas duales
- Comentarios `# backward compat`, `# for now`, `# compatibility shim`

**Regla operativa:** `git rm OLD && git add NEW` en el mismo commit. Si el nuevo necesita lógica del viejo, se COPIA el código — no se importa. Una sola fuente de verdad.

**Evidencia de riesgo (VC-118):** Claude intentó 3 veces mantener `audit_8d.py` vivo al reemplazarlo: herencia, fallback "or", sentinelas duales. Cada intento fue revertido. Fix real: `git rm`.

---

## ♻️ CICLO DE VIDA DEL CÓDIGO: MOVER A deprecated/ (S10)

**Regla absoluta: nada se borra directamente. El código retirado se MUEVE a `deprecated/`.**

No hay etiquetas en el lugar original. No hay comentarios `# DEPRECATED` in-situ.
El código sale del árbol activo y va al contenedor correspondiente: `deprecated/`.

### Protocolo en 2 pasos:

**Paso 1 — Mover a `deprecated/` (obligatorio):**
```bash
git mv scripts/nombre_viejo.py deprecated/nombre_viejo.py
```
El archivo queda accesible, fuera del árbol activo, fuera de la auditoría D1.

**Paso 2 — Eliminación definitiva (sesión dedicada, aprobación explícita):**
- Requiere turno aislado: *"¿Elimino `deprecated/nombre_viejo.py`? Sí/No"*
- El agente NO ejecuta `git rm` sobre `deprecated/` sin orden humana en ese turno.

### ¿Por qué el directorio y no la etiqueta?
- Una etiqueta en el código activo es basura etiquetada — sigue ensuciando el árbol.
- `deprecated/` es el bote real: código fuera de la vista, fuera del auditor, sin ruido.
- `audit_10d.py` lista el contenido de `deprecated/` como `[INFO]` — visible sin bloquear.
- D1 ya excluye `deprecated/` de auditoría de zombis (`hard_excludes`).

---

## 🔐 SEGURIDAD: ZERO-TRUST (S14)

- **PROHIBIDO**: `git reset --hard` o cambios destructivos sin orden humana.
- **DOUBLE-KEY RULE**: Si el plan incluye borrar archivos o carpetas, `git reset` o comandos irreversibles, el agente NO PUEDE agrupar su ejecución junto con tareas de código. Los comandos destructivos DEBEN pedirse en un turno aislado: *"¿Ejecuto ahora el comando destructivo `rm`? Sí/No"*.
- **PROHIBIDO**: Confiar en el éxito de una herramienta sin ver logs empíricos.
- **OBLIGATORIO**: Tratar todo código generado como una vulnerabilidad potencial hasta ser auditado.

---

## 🛡️ PRE-EDIT GUARD & CPI LOCK (PILAR 2 y 3)

### 1. Pre-Edit Guard (`pre_edit_guard.py`)
- **Misión:** Gancho pre-tool en tiempo real que valida operaciones *antes* de que toquen el disco.
- **Qué bloquea:** 
  - Writes directos de más de 200 líneas (fuerza a usar Edits atómicos < 50 líneas).
  - Comandos e inyecciones destructivas de shell (ej: `Add-Content`, `echo >>`).
  - Shims de compatibilidad zombi y carpetas deprecated/.

### 2. Chain-Pattern Interrupt (CPI) / Reasoning Lock
- **Misión:** Romper bucles de razonamiento infinitos del agente y salvar presupuesto de tokens.
- **Activación:** Si el agente falla 3 veces consecutivas en la suite de `rigor_maestro.py` o `audit_10d.py`, el sistema activa el **Reasoning Lock** en `.agent_state.json` y escribe una alerta física en `STATUS.md`.
- **Bloqueo:** Cualquier herramienta de escritura/edición quedará completamente congelada.
- **Desbloqueo:** Requiere intervención manual del operador humano en la terminal mediante:
  ```bash
  python scripts/protocol_cli.py unlock
  ```

---

## 🏁 CRITERIOS DE SALIDA (HANDOFF)

Antes de terminar, DEBES:
1. Actualizar `SPEC.md` (si la arquitectura o whitelist cambió).
2. Actualizar `HISTORIAL.md` registrando la bitácora de la sesión.
3. Completar la **Retrospectiva Obligatoria en formato JSON (B21)** en `HISTORIAL.md`.
4. Actualizar `.agent_state.json` (Estado técnico).
5. Auto-commit si superas el umbral (Regla S2).
6. **Registrar hallazgos (VC-114)**: Todo defecto detectado en sesión → ítem en PLAN.md con ID, evidencia, fix propuesto y done-criteria. Sin excepción.

**Coder Cerberus V0.1 — El Orden de Cline con el Rigor de CoderCerberus.**
