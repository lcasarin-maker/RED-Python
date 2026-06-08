# README — ORDEN DE EJECUCIÓN DE PROMPTS CERBERUS
**Versión protocolo activa: v0.5 | Actualizado: 2026-06-06**

## Alcance de este paquete

`00 audit/` contiene **solo doctrina viva**, en tres pilares:

1. Qué es Cerberus (definición permanente).
2. Cómo auditar hacia adentro (el propio Cerberus, local).
3. Cómo auditar proyectos satélite (hacia afuera, contract-first).

## Archivos vivos

```text
00_CONSTITUCION_CERBERUS.md
01_AUDITORIA_LOCAL.md
05_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md
```

## Orden de carga

Carga siempre en este orden:

```text
1. 00_CONSTITUCION_CERBERUS.md
2. 01_AUDITORIA_LOCAL.md
3. 05_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md
```

## Lógica

- `00_CONSTITUCION_CERBERUS.md` contiene las reglas permanentes (definición de Cerberus).
- `01_AUDITORIA_LOCAL.md` audita el propio Cerberus: su autonomía, su arquitectura y su control plane.
- `05_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md` define la metodología para auditar proyectos propios hacia afuera, empezando por contrato declarado o inferido, validación humano-like, mapeo GS y veredicto con plan de remediación.

## Lo que NO vive aquí (movido o externalizado)

- **Doctrina del Golden Standard:** GS es un repo separado. La interfaz Cerberus↔GS y la evolución del GS viven en `D:\AI\VibeCoding_GoldenStandard\CERBERUS_CONTRACT.md` e `INGESTION_PROTOCOL.md`, no en este paquete.
- **Minado de repositorios externos:** la cosecha de capacidades agnósticas se ingiere al GS por su canal `Inbox/external/`. La corrida histórica ya se digirió en el Wiki del GS. Doctrina deprecada en `deprecated/audit_doctrine_legacy/2026-06-06/` (`02`, `03`, `04`).
- **Resultados de corridas:** las salidas no son doctrina. Archivadas en `deprecated/audits_legacy/<fecha>/`.

## Regla operativa

Después de cargar los tres archivos, ejecutar la auditoría completa sin pedir confirmación entre fases, salvo bloqueo técnico real.

Si surge una duda previsible antes de una corrida larga, agrúpala con las demás en la misma pasada para evitar interrupciones innecesarias.

- Si la topología de `00 audit/` cambia, actualiza `scripts/run_security_audit_12d.py` (whitelist) en el mismo change set; no difieras la alineación del runner a una sugerencia posterior.

## Regla de arranque limpio

- No consultar resultados antiguos salvo que el usuario pida una comparación histórica.
- Las corridas escriben su salida fuera de este paquete; al reiniciar, la auditoría se comporta como primera ejecución lógica.
