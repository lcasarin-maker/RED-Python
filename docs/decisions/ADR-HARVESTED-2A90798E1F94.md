---
id: ADR-2A90798E1F94
status: accepted
tag: MAD
---

# ADR-2A90798E1F94: Decisiones_Arquitect_nicas_y_Post-Mortem (MADR 3.0)

## 1. Context and Problem Statement
> "Decisiones Arquitectónicas y Post-Mortems (`ADRs`):** Mensajes de commit detallados que explican por qué se revirtió una función, por qué se descartó una librería o cómo se resolvió un race condition"

## 2. Decision Drivers (Fuerzas y Limitaciones)
- Proveniencia: `/home/lcasarin/.gemini/antigravity/brain/82720f90-dcdc-42e4-a431-6ef51b7dd1c9/.system_generated/logs/transcript_full.jsonl`
- Clasificación técnica: `MAD`

## 3. Considered Options & Rationale
```text
### Cosecha Profunda de Git History y Archive Completada

Se expandió el **Universal Harvester** con el módulo de extracción de **historial de commits de Git** ([`scan_git_history`](file:///home/lcasarin/projects/simplecode/src/simplecode/verification/universal_harvester.py#L254-L270)) e ingesta de volcados históricos de `archive/`.

---

### 1. ¿Qué se Rescató del Historial de Git y Archive?

Al escanear los miles de commits en los repositorios de la flota y los volcados de `archive/`, se recuperaron:
1. **Decisiones Arquitectónicas y Post-Mortems (`ADRs`):** Mensajes de commit detallados que
```

## 4. Decision Outcome & Validation
- Opción elegida clasificada como `MAD`.
- Obligatoria para futuros refactors en `red_python`.
