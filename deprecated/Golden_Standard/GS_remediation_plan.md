# GS Remediation Plan — Golden Standard

Este plan de remediación aborda de manera exclusiva la migración, consolidación y endurecimiento de la base de datos de conocimiento del **Golden Standard** (GS) de CoderCerberus v0.5.

---

## 1. Diagnóstico del Estado Actual

1. **Estructura Híbrida Frágil**: Los archivos YAML actuales (`golden_standard_coding_vices.yaml`, `golden_standard_testing_vices.yaml` y `golden_standard_tokenomics.yaml`) almacenan sus contenidos de vicios dentro de un string Markdown monolítico que representa una tabla.
2. **Deuda de Hardcoding en Auditoría**: La información sobre el estado de cumplimiento (`status`), la acción tomada (`action`) y el test validador (`validating_mechanism`) de cada uno de los 284 vicios está hardcodeada en el script Python `generate_golden_audit.py`.
3. **Drift de Datos**: Cambiar la descripción o el ID de un vicio requiere actualizar manualmente el YAML de conocimiento, el parser de expresiones regulares y la lista de mappings hardcodeados en el script de auditoría, aumentando el riesgo de inconsistencias.

---

## 2. Acciones de Remediación Propuestas

### Fase 1: Migración al Esquema de YAML Estructurado Puro
Transformar los catálogos en listas estructuradas con los siguientes campos tipados para cada vicio/patrón:
- `id` (str) — Identificador único (ej: `VC-001`, `VT-001`, `TK-001`)
  - `title` (str) — Nombre del vicio/patrón
  - `symptom` (str) — Síntoma operativo observable
  - `cause` (str) — Causa raíz teórica
  - `solution` (str) — Principio de solución agnóstica
  - `status` (str) — Nivel de cumplimiento (`PREVENTED`, `REMEDIATED`, `AUDITED`, `DOC_ONLY`)
  - `action` (str) — Acción tomada o barrera preventiva implementada
  - `validating_mechanism` (str) — Nombre del test o guard de validación asociado (o `DOC_ONLY`)

### Fase 2: Script de Migración Automatizado
- Desarrollar un script temporal `scripts/migrate_catalogs.py` para automatizar la transformación:
  1. Leer los archivos YAML actuales.
  2. Parsee el Markdown usando el regex de `generate_golden_audit.py`.
  3. Resolver el estado de mitigación (`status`, `action`, `validating_mechanism`) buscando el ID del vicio en la función `determine_mapping` de `generate_golden_audit.py`.
  4. Generar y sobreescribir los archivos YAML consolidados y endurecidos en la estructura de YAML puro.

### Fase 3: Refactorización de Componentes de Lectura y Compilación
- **Modificación en [knowledge_loader.py](file:///d:/AI/Cerberus/protocol_engine/knowledge_loader.py)**:
  - Adaptar la carga para deserializar directamente la lista de diccionarios de YAML puro.
- **Refactorización de [generate_golden_audit.py](file:///d:/AI/Cerberus/scripts/generate_golden_audit.py)**:
  - Cambiar el compilador para leer los YAMLs estructurados directos.
  - **Eliminar por completo** el regex de parseo de tablas Markdown y el mapping hardcodeado `determine_mapping`.
  - Exportar el reporte Markdown (`docs/golden_standard_audit_report.md`) y el JSON estático (`.protocol/metadata/golden_standard_audit.json`) a partir de la información de origen de los YAMLs estructurados.

### Fase 4: Endurecimiento de la Suite de Pruebas
- **Actualización de [test_golden_standard_compliance.py](file:///d:/AI/Cerberus/tests/test_golden_standard_compliance.py)**:
  - Configurar aserciones para validar que los catálogos YAML estructurados cumplan con el esquema tipado (campos no nulos, IDs únicos, formatos válidos) e impedir cualquier regresión o drift.

---

## 3. Plan de Verificación

1. **Ejecutar Migración**: Correr `python scripts/migrate_catalogs.py`.
2. **Validar Estructura**: Inspeccionar visualmente que los nuevos archivos YAML contengan toda la información integrada.
3. **Correr Compilador**: Ejecutar `python scripts/generate_golden_audit.py` para regenerar el reporte Markdown y el JSON estático.
4. **Verificar Tests Unitarios**: Ejecutar `pytest tests/test_golden_standard_compliance.py`.
5. **Ejecutar Auditor de Seguridad**: Correr `python scripts/run_security_audit_12d.py` para asegurar que el veredicto del repositorio sea **APPROVED** al 100%.
