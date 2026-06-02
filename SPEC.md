# SPEC.md — RED-Python v0.5

**Versión:** 0.5  
**Protocolo:** CoderCerberus v0.5  
**Escrito:** 2026-06-02  
**Dueño:** RED-Python Development Team  
**Status:** 🟢 OPERATIVO

---

## 1. DESCRIPCIÓN OPERACIONAL

RED-Python (Remove Empty Directories) es una herramienta multiplataforma que encuentra y elimina directorios vacíos o efectivamente vacíos. 

**Modos de Operación:**
- GUI tkinter completa (desktop)
- CLI para scripting y automatización
- Integración con menú contextual Windows
- Modo portátil (USB drive ready)

**Core Functions:**
- Detección inteligente de directorios efectivamente vacíos
- Simulación previa (preview sin tocar datos)
- Traslado a Papelera Recicle Bin
- Eliminación permanente con confirmación
- Filtros por edad, patrón, profundidad
- Exportación de resultados (CSV/TXT)

---

## 2. INTERFAZ PÚBLICA

### Modo GUI
```
Ventana principal:
- Selección de raíces (multi-path)
- Tabla de resultados (tamaño, fecha, estado)
- Historial de últimas 10 rutas
- Botones: Scan | Preview | Delete | Export

Configuración:
- Patrones a ignorar (wildcard + regex)
- Max depth
- Age filter (horas)
- Sonido de finalización (configurable)
```

### Modo CLI
```
red-python --scan /path/to/scan
red-python --scan /path --simulate
red-python --scan /path --delete --ignore "*.tmp"
red-python --export results.csv
```

### Binarios Requeridos
- Python 3.10+
- send2trash (pip install)

---

## 3. RESTRICCIONES

**Hard Limits:**
- Nunca tocar System32, SysWOW64, $RECYCLE.BIN (protected)
- Máximo profundidad configurable (evita recursiones infinitas)
- Simlink detection para evitar loops

**Forbidden Patterns:**
- ❌ Eliminar sin preview o confirmación
- ❌ Acceder a directorios sin permisos (skip gracefully)
- ❌ Ignorar symlinks (pueden causar loops)
- ❌ Procesar paths >260 caracteres sin prefix \\?\

**Known Limitations:**
- En Windows, requiere se2trash para Recycle Bin
- Algunos directorios del sistema siempre protegidos
- Permission errors se loguean pero no frenan el scan

---

## 4. ARQUITECTURA

### Estructura Principal
```
RED-Python/
├── main.py              → Entrypoint (GUI/CLI)
├── gui/
│   ├── window.py        → Tkinter window
│   ├── results_table.py  → Tabla de resultados
│   └── settings.py      → Panel de configuración
├── core/
│   ├── scanner.py       → Lógica principal de scan
│   ├── validator.py     → Validación de directorios
│   └── cleaner.py       → Eliminación/traslado
├── cli/
│   └── commands.py      → Parseo de argumentos CLI
├── config/
│   ├── defaults.json    → Configuración por defecto
│   └── protected_dirs.json
├── tests/
│   └── test_scanner.py
├── requirements.txt     → Dependencias (send2trash)
├── scripts/
└── AGENT.md + SPEC.md
```

### Módulos Críticos
- `scanner.py`: Punto de entrada para análisis
- `cleaner.py`: Único owner de eliminación
- `protected_dirs.json`: Never modify

---

## 5. MANDATOS APLICABLES

| Mandato | Status | Notas |
|---------|--------|-------|
| S2 | ✅ CUMPLE | SPEC.md presente (este archivo) |
| S4 | ✅ CUMPLE | Schemas de configuración validados |
| S5 | ✅ CUMPLE | Tests validando comportamiento |
| B2 | ✅ CUMPLE | Documentación de propósito clara |

---

## 6. Próximos Sprints

| Sprint | Objetivo | Fecha |
|--------|----------|-------|
| Sprint 1 | Beta release con GUI completa | Jul 2026 |
| Sprint 2 | Integración con menú Windows (opcional) | Aug 2026 |
| Sprint 3 | Soporte para Linux/Mac testing | Sep 2026 |

---

## 7. Regla de Cierre

Proyecto se marca como **PRODUCTION READY** cuando:
1. ✅ GUI tkinter funcional y responsive
2. ✅ CLI con todos los flags documentados
3. ✅ Tests de scanner/cleaner >95% coverage
4. ✅ Protected dirs nunca modificados (audit trail)

---

## 8. Contacto

**Dueño:** RED-Python Development Team  
**Repositorio:** /d/AI/RED-Python  
**Última revisión:** 2026-06-02  
**Próxima revisión:** 2026-06-16
