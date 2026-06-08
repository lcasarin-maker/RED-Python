# Worktree Change Review — 2026-06-05

## Objetivo

Revisar cambios ajenos/preexistentes en el worktree y decidir si se conservan, se depuran o se retiran del codigo vivo.

## Decision general

Se conservan los cambios que endurecen Cerberus v0.5, separan GS como repo externo, eliminan referencias legacy de `audit_6d`, hacen pruebas mas falsables o sincronizan metadata generada con el estado real.

No se conserva como autoridad viva el `AGENTS.md` raiz v0.3: fue archivado en `deprecated/docs_archive_legacy/HISTORICO_PROTOCOLO/AGENTS_Codex_v0.3_20260520.md`.

## Se quedan

| Grupo | Decision | Causa |
|---|---|---|
| GS externo | KEEP | `protocol_engine`, `split_golden_standard_catalogs.py`, `.gitmodules` eliminado y docs apuntan a `D:\AI\VibeCoding_GoldenStandard`, evitando copia local o submodulo zombie. |
| Auditoria `00 audit/` | KEEP | Los cambios separan auditoria local, repos externos, GS y auditoria exterior contract-first. |
| `golden_standard_audit.json` | KEEP | Resincronizado con GS actual e incluye `VC-135` a `VC-139`; normalizado para no aceptar mecanismos circulares. |
| `normalize_golden_audit_consumer_contract.py` | KEEP | Evita teatro de validacion: convierte mecanismos no verificables fisicamente en `DOC_ONLY` honesto con `downstream_verification`. |
| Tests GS/project insights/pre-edit | KEEP | Eliminan conteos hardcodeados, preservan `downstream_verification`, y aislan el sentinel de compactacion. |
| Pruebas anti-teatro | KEEP | `test_portability`, `test_rescate_utility`, `test_cerberus_silent_failure`, `test_sprint*` sustituyen checks simbolicos por comportamiento observable. |
| Evidencia fresca | KEEP | `check_empirical_proof.py` y `log_evidence.py` rechazan evidencia obsoleta o no vinculada al claim. |
| Limpieza legacy `audit_6d` | KEEP | `.claude/settings.template.json`, permisos y rollback dejan de apuntar a auditores viejos. |
| Compact/token hooks | KEEP | `discourse_hook.py`, `compact_automation_helper.py`, `compress_historial.py` y `pre_compact_evaluator.py` estan referenciados en SPEC y pasan 12D. |
| Graph/adopcion | KEEP | `GRAPH_REPORT.md`, `.protocol/metadata/graph.json` y `REGISTRY.json` reflejan estado real de satelites: adopcion parcial, no aprobacion cosmetica. |

## Se depuro

| Cambio | Decision | Accion |
|---|---|---|
| `AGENTS.md` raiz v0.3 | RETIRAR DE RAIZ | Movido a `deprecated/docs_archive_legacy/HISTORICO_PROTOCOLO/AGENTS_Codex_v0.3_20260520.md`. |
| `.codex/` | NO VERSIONAR | Agregado a `.gitignore`; queda como configuracion local. |
| `PROTOCOL_SYSTEM.md` S24 | CORREGIR | `VC-120` -> `VC-124`, alineado con GS. |
| `PROTOCOL_BEHAVIOR.md` | CORREGIR | `Escalation Path` renumerado a `B16`; `Integridad Etica ante Presion` renumerado a `B29` para eliminar IDs duplicados. |

## Se elimina del arbol activo

| Archivo | Decision | Evidencia |
|---|---|---|
| `00 audit/results/external_repositories_audit.md` | KEEP deletion | El contenido esta preservado en `deprecated/audits_legacy/2026-06-05/external_repos_audit_archive/2026-06-05/external_repositories_audit.md`; `00 audit/results/` no debe ser fuente de verdad historica. |

## Riesgos residuales

- `REGISTRY.json` y `GRAPH_REPORT.md` son artefactos generados con timestamps; se conservan porque expresan drift real de adopcion, pero deben regenerarse deliberadamente si cambia el inventario de satelites.
- `golden_standard_audit.json` es grande; se conserva porque los tests y 12D lo usan como contrato normalizado, no como copia doctrinal del GS.
- `.codex/hooks.json` queda local e ignorado; si se quiere estandarizar hooks de Codex, debe hacerse como adapter documentado, no como config local accidental.

## Validacion esperada

1. `python scripts/sync_binding.py --check`
2. `python -m pytest -q`
3. `python scripts/run_security_audit_12d.py --project-path .`
