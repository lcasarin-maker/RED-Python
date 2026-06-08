# FALLOS_CONOCIDOS.md — Bugs Confirmados en Scripts Core
**Estado:** ACTIVO | **Fuente:** Auditoría `deprecated/docs/Fallos Concretos.md` | **Fecha rescate:** 2026-05-24

Estos son fallos concretos, no teóricos. Cada uno tiene ubicación exacta en el código.

---

## FALLOS ACTIVOS (10 confirmados)

> Nota de alcance: F1, F4 y F10 son referencias históricas al auditor previo y al auditor expandido previo.
> Esos ejecutables no existen en el árbol activo de Cerberus; se conservan aquí solo para trazabilidad.

### F1 — D7 Code Completeness no implementado
- **Estado:** Histórico. El auditor previo ya no existe en el árbol activo.
- **Síntoma:** `rg D7` solo aparece en HISTORIAL.md, no en scripts legacy activos.
- **Impacto:** Era un hueco real en la versión vieja; hoy solo queda como referencia documental.
- **Fix requerido:** Ninguno en el árbol activo. Mantener solo trazabilidad histórica.

### F2 — Auditor histórico: 88 valida sección, no cumplimiento
- **Síntoma:** El auditor histórico verificaba que `SPEC.md` contenga una sección, no que el proyecto cumpla esa especificación.
- **Impacto:** SPEC.md puede estar vacía o desactualizada y el auditor pasa.
- **Fix requerido:** Validar contenido mínimo por sección, no solo existencia de encabezado.

### F3 — Auditor histórico: 102 valida docstrings por cantidad, no calidad
- **Síntoma:** La implementación histórica contaba docstrings, pero no verificaba que las funciones estén conectadas, usadas o sean correctas.
- **Impacto:** Dead code con docstrings pasa el audit.
- **Fix requerido:** Cruzar funciones documentadas vs funciones llamadas/testadas.

### F4 — Auditor histórico: 164 detecta "try" textual (falso positivo)
- **Estado:** Histórico. La implementación referida ya no existe en el árbol activo.
- **Síntoma:** El detector textual buscaba `"try"` para validar manejo de errores. Un `try` inútil (`try: pass`) pasaba.
- **Impacto:** Era un falso positivo real en la versión vieja.
- **Fix requerido:** Ninguno en el árbol activo.

### F5 — Auditor expandido histórico: 89 usa tests del protocolo, no del proyecto
- **Síntoma:** Ejecutaba tests del protocolo base pero no exigía tests específicos del proyecto auditado ni prueba startup real.
- **Impacto:** Un proyecto sin tests pasa si el protocolo tiene tests.
- **Fix requerido:** Detectar y ejecutar `tests/` del proyecto auditado.

### F6 — Auditor expandido histórico: 125 omite validación humana si UI no cambió
- **Síntoma:** Solo exigía validación humana si hay archivos UI modificados en el commit actual.
- **Impacto:** Una UI ya rota que no cambió en este commit pasa sin revisión.
- **Fix requerido:** Validación humana periódica (no solo delta), o al menos primera vez por sprint.

### F7 — check_empirical_proof.py:98 acepta JSON sin verificar screenshot
- **Síntoma:** Línea 98 acepta evidencia JSON reciente, pero no valida que el screenshot/log corresponda al código actual ni pruebe el flujo completo.
- **Impacto:** Evidencia de sesión anterior pasa como prueba de sesión actual.
- **Fix requerido:** Validar timestamp del screenshot vs timestamp del último commit.

### F8 — validate_chunking.py:67 no detecta archivos "llenos pero muertos"
- **Síntoma:** Línea 67 protege contra truncamiento, pero no contra archivos completos que no ejecutan nada funcional.
- **Impacto:** Archivo con 200 líneas de placeholders pasa.
- **Fix requerido:** Verificar que funciones principales sean llamadas (no solo definidas).

### F9 — Tests usan assertIn sobre texto, no ejecución real
- **Síntoma:** Los tests en `tests/` validan que existan cadenas como `"MANDATO S1"`, no que esos mandatos se ejecuten efectivamente.
- **Impacto:** Forma auditada, fondo ignorado. Teatro de seguridad.
- **Fix requerido:** Tests deben invocar la función y verificar el efecto, no buscar texto.

### F10 — CLI bug: --project-path no soportado en auditor histórico
- **Estado:** Histórico. El entrypoint viejo ya no existe; el auditor activo es `scripts/run_security_audit_12d.py`.
- **Síntoma:** El CLI histórico fallaba porque interpretaba `--project-path` como nombre de carpeta.
- **Impacto:** Era un bug real en el CLI antiguo.
- **Fix requerido:** Ninguno en el árbol activo.

---

## ESTADO DE CORRECCIONES

| Fallo | Prioridad | Estado |
|-------|-----------|--------|
| F9 (assertIn teatro) | CRÍTICA | PENDIENTE |
| F1 (D7 sin implementar) | ALTA | HISTÓRICO |
| F4 (try textual) | ALTA | HISTÓRICO |
| F10 (CLI bug) | ALTA | HISTÓRICO |
| F2 (SPEC.md sección) | MEDIA | PENDIENTE |
| F5 (tests protocolo vs proyecto) | MEDIA | PENDIENTE |
| F6 (UI validación parcial) | MEDIA | PENDIENTE |
| F3 (docstrings cantidad) | BAJA | PENDIENTE |
| F7 (evidencia stale) | BAJA | PENDIENTE |
| F8 (archivos muertos) | BAJA | PENDIENTE |

---

**Regla:** Antes de marcar cualquier fallo como RESUELTO, se requiere terminal log que demuestre el fix.
**Antipatrón:** No cambiar el test para que pase — cambiar el código para que el test tenga razón.
