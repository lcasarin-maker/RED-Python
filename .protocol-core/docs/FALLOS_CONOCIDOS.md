# FALLOS_CONOCIDOS.md — Bugs Confirmados en Scripts Core
**Estado:** ACTIVO | **Fuente:** Auditoría `deprecated/docs/Fallos Concretos.md` | **Fecha rescate:** 2026-05-24

Estos son fallos concretos, no teóricos. Cada uno tiene ubicación exacta en el código.

---

## FALLOS ACTIVOS (10 confirmados)

### F1 — D7 Code Completeness no implementado
- **Síntoma:** `rg D7` solo aparece en HISTORIAL.md, no en scripts.
- **Impacto:** El dominio D7 está documentado pero el auditor no lo ejecuta. Silently skipped.
- **Fix requerido:** Implementar validación D7 en `scripts/audit_6d.py` o `scripts/audit_8d.py`.

### F2 — audit_6d.py:88 valida sección, no cumplimiento
- **Síntoma:** `scripts/audit_6d.py` línea 88 verifica que `SPEC.md` contenga una sección, no que el proyecto cumpla esa especificación.
- **Impacto:** SPEC.md puede estar vacía o desactualizada y el auditor pasa.
- **Fix requerido:** Validar contenido mínimo por sección, no solo existencia de encabezado.

### F3 — audit_6d.py:102 valida docstrings por cantidad, no calidad
- **Síntoma:** Línea 102 cuenta docstrings, pero no verifica que las funciones estén conectadas, usadas o sean correctas.
- **Impacto:** Dead code con docstrings pasa el audit.
- **Fix requerido:** Cruzar funciones documentadas vs funciones llamadas/testadas.

### F4 — audit_6d.py:164 detecta "try" textual (falso positivo)
- **Síntoma:** Línea 164 busca el texto `"try"` para validar manejo de errores. Un `try` inútil (`try: pass`) pasa.
- **Impacto:** Error handling teatro (forma sin fondo).
- **Fix requerido:** Validar que el bloque `except` tenga logging real, no `pass`.

### F5 — audit_6d_expanded.py:89 usa tests del protocolo, no del proyecto
- **Síntoma:** Ejecuta tests del protocolo base pero no exige tests específicos del proyecto auditado ni prueba startup real.
- **Impacto:** Un proyecto sin tests pasa si el protocolo tiene tests.
- **Fix requerido:** Detectar y ejecutar `tests/` del proyecto auditado.

### F6 — audit_6d_expanded.py:125 omite validación humana si UI no cambió
- **Síntoma:** Línea 125 solo exige validación humana si hay archivos UI modificados en el commit actual.
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

### F10 — CLI bug: --project-path no soportado en audit_6d.py
- **Síntoma:** `python scripts/audit_6d.py --project-path .` falla porque el script interpreta `--project-path` como nombre de carpeta.
- **Impacto:** Agentes que usen la interfaz documentada obtendrán errores silenciosos o rutas incorrectas.
- **Fix requerido:** Agregar argparse con `--project-path` explícito.

---

## ESTADO DE CORRECCIONES

| Fallo | Prioridad | Estado |
|-------|-----------|--------|
| F9 (assertIn teatro) | CRÍTICA | PENDIENTE |
| F1 (D7 sin implementar) | ALTA | PENDIENTE |
| F4 (try textual) | ALTA | PENDIENTE |
| F10 (CLI bug) | ALTA | PENDIENTE |
| F2 (SPEC.md sección) | MEDIA | PENDIENTE |
| F5 (tests protocolo vs proyecto) | MEDIA | PENDIENTE |
| F6 (UI validación parcial) | MEDIA | PENDIENTE |
| F3 (docstrings cantidad) | BAJA | PENDIENTE |
| F7 (evidencia stale) | BAJA | PENDIENTE |
| F8 (archivos muertos) | BAJA | PENDIENTE |

---

**Regla:** Antes de marcar cualquier fallo como RESUELTO, se requiere terminal log que demuestre el fix.
**Antipatrón:** No cambiar el test para que pase — cambiar el código para que el test tenga razón.
