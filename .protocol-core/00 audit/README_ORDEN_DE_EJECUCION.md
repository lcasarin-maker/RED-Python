# README — ORDEN DE EJECUCIÓN DE PROMPTS CERBERUS

## Archivos generados

```text
00_CONSTITUCION_CERBERUS.md
01_AUDITORIA_LOCAL.md
02_AUDITORIA_REPOSITORIOS.md
03_EVOLUCION_GOLDEN_STANDARD.md
04_CONTEXTO_EJECUCION.md
```

## Orden de carga

Carga siempre en este orden:

```text
1. 00_CONSTITUCION_CERBERUS.md
2. 01_AUDITORIA_LOCAL.md
3. 02_AUDITORIA_REPOSITORIOS.md
4. 03_EVOLUCION_GOLDEN_STANDARD.md
5. 04_CONTEXTO_EJECUCION.md
```

## Lógica

- `00_CONSTITUCION_CERBERUS.md` contiene reglas permanentes.
- `01_AUDITORIA_LOCAL.md` audita el proyecto, su autonomía y su arquitectura.
- `02_AUDITORIA_REPOSITORIOS.md` audita repos externos y extrae capacidades agnósticas.
- `03_EVOLUCION_GOLDEN_STANDARD.md` valida y evoluciona el Golden Standard.
- `04_CONTEXTO_EJECUCION.md` contiene la ruta del proyecto, repositorios, objetivos y formato final.

## Regla operativa

Después de cargar los cinco archivos, ejecutar la auditoría completa sin pedir confirmación entre fases, salvo bloqueo técnico real.
