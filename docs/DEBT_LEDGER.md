# Debt Ledger Canonico

Este documento es la fuente unica de verdad para la deuda del ecosistema Cerberus.
Clasifica deuda viva, backlog declarado, drift documental, ruido historico y deuda externa.

## Estado actual

- Gate operativo del root de Cerberus: `APPROVED`
- Deuda bloqueante viva en el root: ninguna
- Deuda bloqueante externa: ninguna
- Deuda declarada: cero en `TODO.md`
- Drift documental: presente en `PLAN.md`, `STATUS.md`, reportes generados y bitacoras historicas
- Ruido historico: presente por diseno en `HISTORIAL.md` y artefactos de auditoria

## Clasificacion

- `ACTIVE`: bloquea trabajo actual o requiere remediacion directa.
- `DEFERRED`: backlog explicitamente reconocido con siguiente accion.
- `HISTORICAL`: se conserva por trazabilidad, no bloquea.
- `EXTERNAL`: vive fuera del root de Cerberus, pero afecta el workspace.

## Inventario canonico

| ID | Estado | Tipo | Fuente | Deuda | Siguiente accion |
| --- | --- | --- | --- | --- | --- |
| DEBT-001 | HISTORICAL | Proyecto satelite resuelto | [`.protocol/metadata/REGISTRY.json`](/D:/GoogleDrive/AI/Cerberus/.protocol/metadata/REGISTRY.json) | `Control_Procesal` salio de `pending_sync` y quedo en `APPROVED` tras la sincronizacion frontend/backend. | Sprint 16 resuelto: conservar solo trazabilidad del cierre. |
| DEBT-002 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | El ajuste del pre-commit hook para VERSION.txt ya quedó validado en el árbol activo. | Mantener solo el historial de cierre. |
| DEBT-003 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | `pre-commit install` y la validación de hooks quedaron verificados con evidencia. | Mantener solo el historial de cierre. |
| DEBT-004 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | `scripts/bump_version.py` ya está documentado en `README.md`. | Mantener solo el historial de cierre. |
| DEBT-005 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | Las pruebas unitarias de `scripts/bump_version.py` ya existen y pasan. | Mantener solo el historial de cierre. |
| DEBT-006 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | `AGENT.md`, `PROTOCOL_SYSTEM.md` y `PROTOCOL_BEHAVIOR.md` ya reflejan la versión vigente. | Mantener solo el historial de cierre. |
| DEBT-007 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | `docs/rules.md` ya se genera y se consume como referencia activa. | Mantener solo el historial de cierre. |
| DEBT-008 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | El workflow de GitHub Actions ya está configurado para pruebas, lint y auditoría. | Mantener solo el historial de cierre. |
| DEBT-009 | HISTORICAL | Backlog cerrado | [`TODO.md`](/D:/GoogleDrive/AI/Cerberus/TODO.md) | `pending_tasks.json` quedó vacío y la cola no tiene pendientes. | Mantener solo el historial de cierre. |
| DEBT-010 | HISTORICAL | Decisión cerrada | [`PLAN.md`](/D:/GoogleDrive/AI/Cerberus/PLAN.md) | `P2.2` quedó resuelta: el auto-refresh de hash permanece targeted. | Mantener solo el criterio acordado. |
| DEBT-011 | HISTORICAL | Drift de estado | [`STATUS.md`](/D:/GoogleDrive/AI/Cerberus/STATUS.md) | El conteo historico de la auditoria fue normalizado; este item queda como referencia del drift ya corregido. | Mantener el resumen operativo sin contadores obsoletos. |
| DEBT-012 | HISTORICAL | Drift de estado | [`STATUS.md`](/D:/GoogleDrive/AI/Cerberus/STATUS.md) | La narrativa de sprints y logros fue compactada para describir el presente sin mezclar historia viva. | Mantener el resumen operativo sin mezclar historia viva. |
| DEBT-013 | HISTORICAL | Drift de plan | [`PLAN.md`](/D:/GoogleDrive/AI/Cerberus/PLAN.md) | El plan ya separa mejor la historia del backlog real; las referencias residuales se tratan como archivo. | Seguir compactando solo si reaparece narrativa obsoleta. |
| DEBT-014 | HISTORICAL | Ruido de reporte generado | [`docs/golden_standard_audit_report.md`](/D:/GoogleDrive/AI/Cerberus/docs/golden_standard_audit_report.md) y [`.protocol/metadata/golden_standard_audit.json`](/D:/GoogleDrive/AI/Cerberus/.protocol/metadata/golden_standard_audit.json) | Persistian textos generados con formulacion vieja y referencias historicas; se corrigio en Sprint 17. | Resuelto en Sprint 17: reportes regenerados con version y fecha vivas. |
| DEBT-015 | HISTORICAL | Archivo historico | [`HISTORIAL.md`](/D:/GoogleDrive/AI/Cerberus/HISTORIAL.md) | El historico conserva sesiones, rutas y estados ya superados; eso es trazabilidad, no estado vivo. | Resuelto en Sprint 18: historial sellado con resumen operativo compacto. |
| DEBT-016 | HISTORICAL | Ledger de cobertura | [`docs/P5_coverage_ledger.md`](/D:/GoogleDrive/AI/Cerberus/docs/P5_coverage_ledger.md) | Quedaba como diagnóstico P5 histórico con gaps documentados. | Resuelto en Sprint 19: ledger archivado como referencia cerrada. |
| DEBT-017 | HISTORICAL | Cobertura del auditor | [`PLAN.md`](/D:/GoogleDrive/AI/Cerberus/PLAN.md) | La brecha declarada de escaneo fue resuelta al ampliar `_get_audit_files` para incluir `protocol_engine/`. | Mantener el cambio como cobertura historica. |
| DEBT-018 | HISTORICAL | Placeholder documental | [`ESCALATION_PROTOCOL.md`](/D:/GoogleDrive/AI/Cerberus/ESCALATION_PROTOCOL.md) | La referencia de placeholder se normalizó y ya no funciona como deuda viva. | Resuelto en Sprint 20: nota histórica clara y sin TODO operativo. |
| DEBT-019 | HISTORICAL | Placeholder documental | [`docs/architecture/N6_REGLA_24_SECURITY_BOUNDARIES.md`](/D:/GoogleDrive/AI/Cerberus/docs/architecture/N6_REGLA_24_SECURITY_BOUNDARIES.md) | La tabla de tests ya no contiene `TODO: FASE 5`. | Resuelto en Sprint 20: placeholder eliminado. |

## Lectura practica

- Si el item es `ACTIVE` o `EXTERNAL`, bloquea una linea de trabajo real.
- Si el item es `DEFERRED`, debe salir de `TODO.md` y entrar a un sprint con done-criteria.
- Si el item es `HISTORICAL`, no bloquea, pero si contamina el relato operativo.
- Si el item es `OPEN`, sigue siendo una decision tecnica viva y debe cerrarse antes de declarar deuda cero global.

## Resultado

- Deuda viva bloqueante dentro del root: cero.
- Deuda externa bloqueante: 0 items.
- Deuda declarada: 0 items.
- Deuda abierta: 0 items.
- Deuda documental/historica: sellada en Sprints 17-20; queda solo trazabilidad archivada.

## Sprint 13

- Remediado: `STATUS.md` ya no expone contadores obsoletos ni narrativa de estado desalineada.
- Remediado: `PLAN.md` ya no presenta el cierre de Sprint 2 como deuda viva.
- Sellado: Sprints 18-20 cerraron el historial compacto, archivaron el ledger P5 y retiraron placeholders documentales.
