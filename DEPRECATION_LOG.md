# DEPRECATION LOG — Coder Cerberus
**Mandato:** S21 Anti-Deprecación-Precipitada | **Vigente desde:** 2026-06-04

## PROTOCOLO OBLIGATORIO ANTES DE DEPRECAR

Todo archivo movido a `deprecated/` debe tener entrada aquí ANTES del `git mv`.

```
1. Leer el archivo completo
2. Buscar referencias activas: grep -r "nombre_archivo" . --include="*.py" --include="*.md"
3. Verificar si la funcionalidad existe en otro lugar
4. Documentar en este log
5. ENTONCES hacer git mv
```

**Sin entrada en este log → pre-commit hook bloquea el commit.**

---

## FORMATO DE ENTRADA

```markdown
### [YYYY-MM-DD] nombre_archivo.ext → deprecated/ruta/nombre.ext
**Razón:** [por qué se depreca]
**Referencias activas verificadas:** [ninguna / lista de archivos que la referenciaban]
**Funcionalidad cubierta por:** [archivo/sistema que lo reemplaza, o N/A]
**Análisis previo:** [qué se leyó y qué se encontró]
**Aprobado por:** [humano/agente + sesión]
```

---

## ENTRADAS

### [2026-06-04] tests/test_project_insights_integration.py → deprecated/tests_legacy/test_project_insights_integration_legacy2.py
**Razón:** Importaba `scripts.generate_golden_audit` que migró al repo VibeCoding_GoldenStandard
**Referencias activas verificadas:** Ninguna referencia externa al test
**Funcionalidad cubierta por:** Test restaurado a `tests/test_project_insights_integration.py` con 2 tests eliminados y 7 activos
**Análisis previo:** Archivo leído — 5 de 7 tests eran válidos. Error inicial: deprecado sin análisis. Corregido en la misma sesión.
**Aprobado por:** Agente (Claude) — sesión 2026-06-04. NOTA: esta entrada es retroactiva; el archivo fue restaurado, no permanece en deprecated.

### [2026-06-04] deprecated/tests_legacy/test_project_insights_integration.py (pre-existente)
**Razón:** Versión legacy del test de project insights — reemplazado por la versión activa
**Referencias activas verificadas:** Ninguna
**Funcionalidad cubierta por:** tests/test_project_insights_integration.py
**Análisis previo:** Archivo legacy, la versión activa cubre el mismo scope
**Aprobado por:** Agente (Claude) — sesión 2026-06-04

### [2026-06-05] 00 audit/results/external_repositories_audit.md → deprecated/audits_legacy/2026-06-05/
**Razón:** Resultado de corrida anterior — usuario solicita corrida limpia sin contaminación de resultados previos
**Referencias activas verificadas:** run_security_audit_12d.py whitelist (línea 568) — referencia eliminada
**Funcionalidad cubierta por:** Próxima corrida limpia en 00 audit/results/
**Análisis previo:** Auditoría de 36 repos externos con formato 12D. Válido como historial pero no debe influir en la próxima corrida.
**Aprobado por:** Luis Casarin — sesión 2026-06-05

### [2026-06-05] AGENTS.md → deprecated/docs_archive_legacy/HISTORICO_PROTOCOLO/AGENTS_Codex_v0.3_20260520.md
**Razón:** Binding Codex v0.3 obsoleto en raíz viva; contradice Cerberus v0.5, apunta a ruta antigua `D:\GoogleDrive\AI\Cerberus` y duplica autoridad con `AGENT.md`.
**Referencias activas verificadas:** `rg "AGENTS.md|CoderCerberus v0.3|Codex"`; no hay dependencia operativa sobre el archivo raíz. Las referencias restantes son documentación genérica o histórica.
**Funcionalidad cubierta por:** `AGENT.md` v0.5, `SPEC.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md` y `adapters/codex/README.md`.
**Análisis previo:** Archivo leído completo; contiene reglas útiles de VC-118 pero ya cubiertas por el protocolo vivo y 12D. Se conserva como referencia histórica, no como autoridad activa.
**Aprobado por:** Luis Casarin + Codex — sesión 2026-06-05

### [2026-06-06] record_validation_debt_historical.py → deprecated/bootstrap_v0.5/
**Razón:** Bootstrap script ejecutable una sola vez (seeding histórico de Control_Procesal debt). No forma parte del flujo operativo diario.
**Referencias activas verificadas:** No hay referencias en scripts activos; invocable solo en inicialización D13 system
**Funcionalidad cubierta por:** API `register_validation_debt()` en `satellite_validation_debt.py` (aún en activo)
**Análisis previo:** Script que registra deuda histórica de Control_Procesal. Ya ejecutado. Movido a bootstrap para clarificar que es init-only, no operational.
**Aprobado por:** Claude (Haiku 4.5) — sesión 2026-06-06

### [2026-06-06] validate_satellite_functional.py → deprecated/bootstrap_v0.5/
**Razón:** Validador funcional de satélites (endpoints, respuestas). Invocable manualmente para verificación empirical. No parte del flujo automated daily.
**Referencias activas verificadas:** No hay imports en scripts activos; invocable manualmente como `python deprecated/bootstrap_v0.5/validate_satellite_functional.py`
**Funcionalidad cubierta por:** D13 auditor (`audit_d13_validation_debt.py`) que verifica existence de functional tests, no ejecuta validación en tiempo real
**Análisis previo:** Utility para pruebas funcionales empíricas (HTTP requests a endpoints). Mantiene el código pero clarifica que es manual/bootstrap, no automatic.
**Aprobado por:** Claude (Haiku 4.5) — sesión 2026-06-06

### [2026-06-06] 00 audit/02_AUDITORIA_REPOSITORIOS.md → deprecated/audit_doctrine_legacy/2026-06-06/
**Razón:** Doctrina de minado de repos externos. La corrida ya se ejecutó y su cosecha (PI-001..PI-034) está digerida en el Wiki del GS. El canal vivo de cosecha externa es `Inbox/external/` del repo GS, no este paquete.
**Referencias activas verificadas:** `rg "02_AUDITORIA_REPOSITORIOS"` — whitelist de `run_security_audit_12d.py` (línea ~572, eliminada en este change set), README de `00 audit/` (reescrito), SPEC.md línea 207 (actualizada).
**Funcionalidad cubierta por:** Repo GS — `INGESTION_PROTOCOL.md` (promoción de conocimiento en 7 pasos) + `Inbox/templates/external_contribution.md`.
**Análisis previo:** Archivo leído completo. Su salida ya fue cosechada; mantener la doctrina aquí duplicaría autoridad con el GS. `00 audit/` debe contener solo doctrina viva: definición + auditar-adentro + auditar-satélites.
**Aprobado por:** Luis Casarin ("loye completo") + Claude — sesión 2026-06-06

### [2026-06-06] 00 audit/03_EVOLUCION_GOLDEN_STANDARD.md → deprecated/audit_doctrine_legacy/2026-06-06/
**Razón:** Doctrina de cómo auditar/evolucionar el Golden Standard. GS es repo separado desde 899b0cc; su evolución pertenece al repo GS, no a Cerberus ("si 03 es como auditar gs eso debería estar allá no aquí").
**Referencias activas verificadas:** `rg "03_EVOLUCION_GOLDEN_STANDARD|fase 3"` — whitelist del runner (eliminada), 01_AUDITORIA_LOCAL.md líneas 24/74 (reapuntadas a `VibeCoding_GoldenStandard\CERBERUS_CONTRACT.md`), README (reescrito), SPEC.md (actualizada).
**Funcionalidad cubierta por:** Repo GS — `CERBERUS_CONTRACT.md` (interfaz bidireccional Cerberus↔GS) + `INGESTION_PROTOCOL.md`.
**Análisis previo:** Archivo leído. La interfaz y la doctrina de evolución del GS ya existen en el repo GS. Conservar aquí contradice la separación GS/Cerberus.
**Aprobado por:** Luis Casarin ("loye completo") + Claude — sesión 2026-06-06

### [2026-06-06] 00 audit/04_CONTEXTO_EJECUCION.md → deprecated/audit_doctrine_legacy/2026-06-06/
**Razón:** Contexto de corrida obsoleto (Sprint 5, 37 repos, "v0.5 cierre vivo"). La política de arranque limpio y separación GS/Cerberus ya vive en el README; la plantilla de reporte vive en `01 §10`.
**Referencias activas verificadas:** `rg "04_CONTEXTO_EJECUCION"` — whitelist del runner (eliminada), README (reescrito), SPEC.md (actualizada). Sin imports ni dependencias operativas.
**Funcionalidad cubierta por:** `00_CONSTITUCION_CERBERUS.md §5` (política de arranque/separación, fusionada desde el README) + 01_AUDITORIA_LOCAL.md §10 (plantilla de reporte).
**Análisis previo:** Archivo leído. Mayormente estado de corrida caduco; lo vigente ya está duplicado en README y 01. No queda contenido único que rescatar.
**Aprobado por:** Luis Casarin ("loye completo") + Claude — sesión 2026-06-06

### [2026-06-06] 00 audit/results/ → deprecated/audits_legacy/2026-06-06/results_archive/
**Razón:** Resultados de corridas (Control_Procesal exterior 2026-06-05/06, worktree review) no son doctrina. El usuario pidió sacar `results/` por completo de `00 audit/` ("Fuera por completo"); el falso positivo asociado ya se resolvió por separado.
**Referencias activas verificadas:** `rg "00 audit/results"` — README (reescrito para apuntar salidas a `deprecated/audits_legacy/<fecha>/`). Sin referencias en código activo.
**Funcionalidad cubierta por:** N/A — son artefactos de corrida; se archivan como historial, no se reemplazan. Futuras corridas escriben fuera del paquete de doctrina.
**Análisis previo:** Directorio archivado íntegro (claims/logs/screenshots/recheck). Conservado como evidencia histórica de la auditoría Control_Procesal, fuera de la doctrina viva.
**Aprobado por:** Luis Casarin ("Fuera por completo") + Claude — sesión 2026-06-06

### [2026-06-06] 00 audit/README_ORDEN_DE_EJECUCION.md → deprecated/audit_doctrine_legacy/2026-06-06/
**Razón:** Con `00 audit/` reducido a tres pilares de doctrina viva, el README dejó de aportar contenido único. Su valor (alcance, orden de carga, "qué NO vive aquí", regla operativa y de arranque limpio) se fusionó en `00_CONSTITUCION_CERBERUS.md §5`, que ya es el primer archivo de carga. Mantener un índice separado duplicaría autoridad con la Constitución.
**Referencias activas verificadas:** `rg "README_ORDEN_DE_EJECUCION"` — whitelist de `run_security_audit_12d.py` (eliminada en este change set), SPEC.md línea 207 (actualizada), DEPRECATION_LOG entrada de `04_CONTEXTO_EJECUCION` (reapuntada a §5). Sin imports ni dependencias operativas.
**Funcionalidad cubierta por:** `00_CONSTITUCION_CERBERUS.md §5` ("Uso del paquete de auditoría" — alcance, orden de carga 00→01→02, qué NO vive aquí, regla operativa, regla de arranque limpio).
**Análisis previo:** Archivo leído completo. Todo su contenido se trasladó verbatim/condensado a §5 de la Constitución. No queda contenido único que rescatar.
**Aprobado por:** Luis Casarin ("fusiona lo que proceda en 00") + Claude — sesión 2026-06-06

---

*Este archivo es fuente de verdad de todas las deprecaciones. Actualizar antes de cualquier `git mv X deprecated/`.*
### [2026-06-07] ANALISIS_SPEC_COMPARATIVO.md → deprecated/root_legacy/2026-06-07/ANALISIS_SPEC_COMPARATIVO.md
**Razón:** Análisis comparativo puntual de SPEC.md para tres proyectos; valor histórico, no forma parte del runtime ni del protocolo activo.
**Referencias activas verificadas:** Ninguna referencia activa encontrada en búsqueda local.
**Funcionalidad cubierta por:** N/A — documento histórico.
**Análisis previo:** Archivo leído; contiene evaluación comparativa y propuesta de template, sin dependencias de código ni del runner.
**Aprobado por:** Luis Casarin + Codex — sesión 2026-06-07
### [2026-06-07] FASE3_FINAL_REPORT.md → deprecated/root_legacy/2026-06-07/FASE3_FINAL_REPORT.md
**Razón:** Reporte final de una fase ya cerrada; conserva evidencia histórica pero no gobierna el flujo vivo.
**Referencias activas verificadas:** Ninguna referencia activa encontrada en búsqueda local.
**Funcionalidad cubierta por:** N/A — documento histórico.
**Análisis previo:** Archivo leído; resume fases completadas y métricas de una corrida pasada, sin dependencias operativas actuales.
**Aprobado por:** Luis Casarin + Codex — sesión 2026-06-07
