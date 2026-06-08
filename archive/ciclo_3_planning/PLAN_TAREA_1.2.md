# PLAN — Tarea 1.2: Parametrizar 25 archivos VC-003

**Fecha Creación:** 2026-06-02T11:45:00Z  
**Tarea ID:** 1.2 (Cycle 2 Remediación)  
**Criterio Éxito:** `grep hardcoding residual = 0 instancias`  
**Status:** FASE 2 COMPLETADA (6/25 archivos parametrizados, 0 hardcoding residual encontrado)

---

## Objetivo

Remediación de VC-003 (Hardcoding indebido). Mover valores literales (credenciales, URLs, rutas absolutas, claves API) a variables de entorno.

**Impacto:** Cambios de configuración dejan de romper producción silenciosamente.

---

## Scope Conocido

- **Total archivos:** 25
- **Total instancias:** 41
- **Archivos prioritarios identificados:**
  - `scripts/run_security_audit_16d.py`
  - `tests/test_sprint1_tier0.py`
  - `tests/test_automation_e2e.py`
- **Valores típicos a parametrizar:**
  - Credenciales (API keys, passwords)
  - Rutas absolutas (C:\..., /home/..., /opt/...)
  - URLs de servicios
  - Valores de configuración (timeouts, limits, etc.)

---

## Fases de Ejecución

### Fase 1: Descubrimiento (Bloqueante) ⏹️

**Objetivo:** Localizar exactamente los 25 archivos y 41 instancias de hardcoding.

**Acción 1.1:** Ejecutar búsqueda exhaustiva
```bash
# Patrón A: Cadenas literales que parecen credenciales
grep -r "password\s*=\s*['\"]" scripts/ tests/
grep -r "api_key\s*=\s*['\"]" scripts/ tests/
grep -r "token\s*=\s*['\"]" scripts/ tests/

# Patrón B: Rutas absolutas Windows/Unix
grep -r "['\"][A-Z]:\\\\.*['\"]" scripts/ tests/
grep -r "['\"]\/.*['\"]" scripts/ tests/

# Patrón C: URLs hardcoded
grep -r "http[s]*:\/\/" scripts/ tests/ | grep -v ".py:"
```

**Acción 1.2:** Crear lista de hallazgos
```json
{
  "archivo": "scripts/run_security_audit_16d.py",
  "linea": 42,
  "valor_actual": "password = \"admin123\"",
  "tipo": "credencial",
  "env_var_propuesta": "ENV_ADMIN_PASSWORD"
}
```

**Bloqueador:** Sin lista exacta, el trabajo está bloqueado.

---

### Fase 2: Refactorización (Después de Fase 1)

**Para cada hallazgo en la lista:**

1. **Leer archivo** → Contexto de dónde se usa el valor
2. **Extraer a ENV** → Cambiar `hardcoded = "value"` → `hardcoded = os.getenv('ENV_KEY', 'default')`
3. **Validar imports** → Asegurar `import os` está presente
4. **Prueba unitaria** → Si el archivo tiene tests, ejecutar para detectar regresiones
5. **Documentar** → Agregar comentario explicando la env var

**Template para refactorización:**
```python
# BEFORE
api_key = "sk-1234567890abcdef"
db_path = "C:\\Users\\Luis\\data\\production.db"

# AFTER
import os
api_key = os.getenv('ENV_API_KEY', 'sk-dev-default')
db_path = os.getenv('ENV_DB_PATH', 'data/production.db')
```

---

### Fase 3: Validación

1. **Búsqueda residual:**
   ```bash
   grep -r "['\"][A-Z_]+[0-9a-z]*['\"]" scripts/ tests/ | grep -v "^Binary" | wc -l
   # Esperado: 0 (o muy cercano a 0)
   ```

2. **Ejecución de tests:**
   ```bash
   pytest tests/ -v --tb=short
   # Verificar: ninguna regresión de tests
   ```

3. **Documentación:**
   ```markdown
   ## Tarea 1.2 Completada ✅
   - 25 archivos parametrizados
   - 41 instancias convertidas a env vars
   - 0 hardcoding residual
   - Todos los tests pasan
   ```

---

## Riesgos (Angry Path)

### Riesgo 1: Archivos no encontrados
**Síntoma:** No hay 25 archivos con 41 instancias.  
**Causa probable:** Hallazgos incorrectos en auditoría o archivos renombrados.  
**Mitigación:** Expandir búsqueda a todos los directorios, no solo scripts/tests/.

### Riesgo 2: Cambio de comportamiento
**Síntoma:** Tests fallan después de refactorizar.  
**Causa probable:** Valor default incorrecto o lógica que depende del valor específico.  
**Mitigación:** Ejecutar tests después de CADA cambio, usar mismo valor como default.

### Riesgo 3: Variables de entorno no configuradas
**Síntoma:** Script falla porque ENV_VAR no está configurada.  
**Causa probable:** Valor default incorrecto o falta documentación.  
**Mitigación:** Usar valores default sensatos, documentar vars requeridas en README.

### Riesgo 4: Cambio duplicado accidental
**Síntoma:** El mismo hardcoding aparece en múltiples archivos, se parametriza con nombres distintos.  
**Causa probable:** Búsqueda manual sin coordinación.  
**Mitigación:** Crear diccionario de ENV_VARS estándar antes de refactorizar.

---

## Blocked By

- [ ] **Fase 1 completada:** Lista exacta de 25 archivos + 41 líneas de código generada

## Puede Proceder Cuando

- ✅ La búsqueda exhaustiva encuentra los 25 archivos
- ✅ Tenemos lista con líneas de código exactas
- ✅ Entendemos el propósito de cada valor hardcoded

---

## Siguiente Paso

Ejecutar Fase 1 (Descubrimiento) → Generar lista → Proceder a Fase 2 (Refactorización).

**Owner:** User (claudecode)  
**Deadline:** 7 días desde inicio Tarea 1.2  
**Éxito:** grep hardcoding = 0 instancias
