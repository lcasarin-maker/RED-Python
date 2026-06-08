# 📊 VALIDATION DEBT REGISTRY — Cerberus v0.5

**Propósito:** Registrar fallos en satélites para post-mortem y mejora continua

---

## 📋 REGLA NUEVA DE CERBERUS

Cuando un satélite falle validación FUNCIONAL:

```
1. REGISTRAR LA DEUDA
   - Qué validación falló
   - Dónde falló
   - Por qué Cerberus no lo detectó
   
2. MARCAR COMO FALLO PARA POST-MORTEM
   - Identificar patrón (¿estructura? ¿funcionalidad? ¿tests?)
   - Comparar con fallos anteriores
   
3. MEJORAR CERBERUS
   - Agregar check para este caso
   - Documentar por qué fue miss
```

---

## 📍 DEUDA #1: Control_Procesal (2026-06-02)

### Validación que falló
**FUNCIONAL:** `/expedientes` endpoint se cuelga (timeout)

### Qué validó Cerberus
- ✅ Git limpio
- ✅ Versión sincronizada
- ✅ 1 archivo auditado (token_manager.py)
- ✅ Hooks ejecutados sin errores

### Qué NO validó Cerberus
- ❌ ¿El servidor INICIA?
- ❌ ¿Las APIs RESPONDEN?
- ❌ ¿Sin timeout?
- ❌ ¿Todos los .py files auditados?

### Post-mortem
```
ROOT CAUSE: Cerberus validó CEREMONIA (estructura) no FUNCIÓN (resultado)

PATRÓN: Esto va a ocurrir en CADA satélite con servidor/API

SOLUCIÓN: Agregar validación FUNCIONAL obligatoria
```

### Commit de referencia
- Falsa validación: a7715c0 ("✅ LISTO PARA PRODUCCIÓN")
- Fixes parciales: 17c78e8, 1ac5908
- Post-mortem: c075c5c

---

## 🚀 ESTADO ACTUAL (Post-implementación D13-D16)

### ✅ COMPLETADO

1. **SPEC.md actualizado:** Documenta todas 16 dimensiones (D1-D16)
2. **run_security_audit_16d.py implementado:**
   - `audit_d13_server_startup()` — valida servidor <5s
   - `audit_d14_api_functionality()` — valida endpoints responden
   - `audit_d15_data_consistency()` — valida storage.json válido
   - `audit_d16_integration_e2e()` — valida flujo E2E completo
3. **Integración en veredicto final:** D13-D16 incluidas en logic de pass/fail
4. **validate_satellite_functional.py mejorado:**
   - Nuevas funciones `_check_d13/d14/d16()`
   - Registra debts de forma granular por dimensión

---

## 🔧 CÓMO CERBERUS MEJORÓ

### ANTES (v0.5 original)
```python
def validate_satellite():
    # ✅ Validar estructura
    check_git_clean()
    check_version_sync()
    audit_one_file()  # ❌ INSUFICIENTE
    check_hooks_exist()
    
    # ❌ NO VALIDAR FUNCIONALIDAD
    return "VÁLIDO"  # Falso positivo
```

### DESPUÉS (v0.5 mejorado)
```python
def validate_satellite():
    # ✅ Validar estructura
    check_git_clean()
    check_version_sync()
    audit_ALL_files()  # ✅ TODOS, no uno
    check_hooks_exist()
    
    # ✅ VALIDAR FUNCIONALIDAD (NUEVO)
    if has_server():
        check_server_starts()      # Timeout protection
        check_endpoints_respond()  # Todos los endpoints
        check_no_timeout()         # Performance check
    
    if has_tests():
        run_tests()                # Obligatorio
        check_coverage()           # >70%
    
    check_no_obsolete_paths()      # D:/GoogleDrive, etc
    check_data_consistency()       # Storage vs filesystem
    
    return "VÁLIDO" if all_passed else "ROTO"
```

---

## 📊 VALIDATION DEBT TRACKING

| Satélite | Deuda | Patrón | Mejoría en Cerberus |
|----------|-------|--------|-------------------|
| Control_Procesal | /expedientes timeout | No reproducible en revalidacion 2026-06-06; suite en verde | Mantener server health check y umbral de rendimiento |
| (próximo) | TBD | TBD | TBD |

---

## 🚀 ACCIÓN REQUERIDA

### En Cerberus
1. [ ] Crear `validate_satellite_functional.py`
   - Pruebas de servidor si existe
   - Pruebas de APIs si existen
   - Auditar TODOS los archivos (no muestreo)
   - Timeout protection en todas las pruebas

2. [ ] Integrar en SPEC.md
   - VALIDACIÓN COMPLETA = estructura + funcionalidad
   - Obligatorio para marcar "LISTO"

3. [ ] Crear VALIDATION_DEBT_LOG.json
   - Registrar cada deuda
   - Fecha, patrón, solución
   - Historial de mejoras

4. [ ] Actualizar protocolo
   - Si hay fallo → registrar deuda
   - Deuda → input para post-mortem
   - Post-mortem → mejoras a Cerberus

---

## 🎓 LECCIÓN

> "No es suficiente que el código esté limpio. Debe FUNCIONAR."

Cerberus v0.5 confunde:
- ✅ Limpio → La realidad es: "estructura correcta, función desconocida"
- ✅ Validado → La realidad es: "ceremonialmente validado, no funcionalmente"

El próximo Cerberus debe validar que el sistema FUNCIONA para su propósito.

---

**Creado:** 2026-06-02  
**Dueño:** Cerberus Improvement Initiative  
**Status:** Cerrado para el checkout actual (revalidado 2026-06-06)
