# HANDOFF

> Relevo entre agentes (VC-140). Lo PRIMERO que lee el siguiente agente.
> Copia esta plantilla a `HANDOFF.md`, complétala y haz `git add HANDOFF.md` en el mismo
> commit. Secciones obligatorias: ESTADO, SIGUIENTE, VERIFICAR.

**Agente saliente:** <Codex | Gemini | Claude> · **Fecha:** <AAAA-MM-DD> · **Commit:** <hash o "este">

## ESTADO
<1–3 líneas: qué se acaba de terminar y por qué. Sin triunfalismo (B7): solo lo verificado.>

## SIGUIENTE
1. <paso accionable + archivo(s) exacto(s)>
2. <...>

## BLOQUEOS
<qué falla y por qué, o "Ninguno">

## VERIFICAR
<comandos exactos para confirmar verde, p.ej.:>
- `python -m pytest -q`
- `python scripts/run_security_audit_12d.py`  → APPROVED

## NO HACER
<restricciones específicas de esta tarea, o "—">
