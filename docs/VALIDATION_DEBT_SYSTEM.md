# Validation Debt System — CoderCerberus v0.5+

**Efectivo desde:** 2026-06-05  
**Propósito:** Eliminar falsos positivos de auditoría mediante registro formal de deudas.

## 🎯 Componentes (4 items)

1. **satellite_validation_debt.py** — Registro formal de deudas
2. **validate_satellite_functional.py** — Valida endpoints, no solo archivos
3. **postmortem_validation_analysis.py** — Análisis de patrones sistémicos
4. **audit_d13_validation_debt.py** — Exige deudas documentadas y remediadas

## Control_Procesal — Caso de Uso

**Problema:** Auditor marcó APPROVED (FASE 1) pero validación era ceremonial (solo archivos).  
**Resultado:** Servidor no respondía, UI colgaba (descubierto en FASE 2/3).  
**Solución:** Async bootstrap + 26 tests funcionales (remediado FASE 3).  

**Deuda registrada:** `validation_debt.json` con ID, severity=CRITICAL, remediation_date=2026-06-05

## Reglas D13 (Auditor Mejorado)

- **D13-1:** Sin deuda registrada = WARNING (recomendar validación)
- **D13-2:** Inconsistencia registry↔validation_debt = WARNING
- **D13-3:** CRITICAL sin remediar = ERROR (bloquea approval)
- **D13-4:** Sin tests funcionales = WARNING

## Archivos Clave

- `.protocol/validation_debt.json` — Base de debts
- `REGISTRY.json[Control_Procesal].validation_debt` — Metadatos por satélite
- `scripts/satellite_validation_debt.py` — API de registro
- `scripts/postmortem_validation_analysis.py` — Análisis automático

**Status:** ACTIVE | **V0.5+**
