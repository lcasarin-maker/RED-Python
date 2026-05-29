### Problema

El proyecto contenía tests activos dentro de `/tests`, pero no eran ejecutados por la suite estándar porque usaban nombres fuera del patrón de descubrimiento de Pytest:

- `automation_test_regla_21_retrospective.py`
- `automation_test_regla_22_sources_index.py`
- `automation_test_fase8_automation.py`

Al mismo tiempo, esos archivos contenían rutas absolutas hardcodeadas al path anterior:

```text
D:\GoogleDrive\AI\Coder Cerberus V0.1\
````

Resultado: `rigor_maestro.py` reportaba `100% PASS`, pero existían tests latentes que fallaban instantáneamente si se ejecutaban de forma directa o si Pytest cambiaba su configuración de discovery.

### Causa raíz

El sistema confundió “tests existentes” con “tests efectivamente descubiertos y ejecutados”.

El fallo no estaba solo en el código, sino en la capa de validación:

1. archivos de test fuera del patrón estándar;
2. rutas absolutas hardcodeadas;
3. suite parcial reportando éxito global;
4. ausencia de auditoría sobre tests no descubiertos;
5. ausencia de verificación cruzada entre archivos en `/tests` y tests ejecutados realmente.

### Riesgo

Este error genera una falsa sensación de rigor.

Permite que el sistema declare `100% PASS` mientras conserva:

1. código de test roto;
2. dependencias de paths históricos;
3. deuda técnica invisible;
4. regresiones latentes;
5. incompatibilidad de entorno;
6. fragilidad ante migración de carpeta, máquina o CI.

### Regla nueva

Todo archivo ubicado en `/tests` debe ser una de tres cosas:

1. test descubierto y ejecutado automáticamente;
2. helper explícitamente marcado como no-test;
3. archivo deprecated movido fuera de `/tests`.

No puede existir un archivo ambiguo dentro de `/tests`.

### Control obligatorio

Antes de declarar `APPROVED`, el agente debe ejecutar una auditoría de descubrimiento de tests:

1. listar todos los archivos en `/tests`;
2. listar todos los tests efectivamente descubiertos por Pytest;
3. comparar ambos listados;
4. reportar archivos no descubiertos;
5. clasificar cada archivo no descubierto;
6. corregir naming, mover archivo o documentar exclusión;
7. buscar rutas absolutas hardcodeadas;
8. reemplazarlas por paths relativos, fixtures o variables de entorno.

### Prohibición

Prohibido reportar `100% PASS` si existen archivos de test no descubiertos, no clasificados o dependientes de rutas absolutas locales.

### Patrón de detección

Buscar:

```text
/tests/**/*
automation_test_*.py
*_test.py
D:\
C:\
/Users/
/home/
GoogleDrive
OneDrive
Coder Cerberus V0.1
```

### Validación mínima

La auditoría debe producir evidencia de:

```bash
pytest --collect-only
pytest
```

Y además una comparación contra el inventario físico:

```bash
find tests -type f
```

En Windows, equivalente:

```powershell
Get-ChildItem .\tests -Recurse -File
```

### Integración a la taxonomía general

Ubicación sugerida:

# VIII. Testing, Validación y Auditoría

Agregar como sección:

## 8.X Falsa Cobertura por Discovery Incompleto

Principio:

> Un test que existe pero no se ejecuta no es cobertura. Es deuda técnica disfrazada de rigor.

Regla:

> Todo archivo dentro de `/tests` debe ser ejecutado, excluido explícitamente o removido.

Candado:

> `APPROVED` queda prohibido si `pytest --collect-only` no coincide con el inventario esperado de tests.

```

También lo conectaría con estas reglas existentes:

- “Sin Tests, No Hay Código”
- “Auditoría Anti-Slop”
- “Asumir que Funciona es una Trampa”
- “Scripts Huérfanos”
- “Dependencia de paths históricos”
- “Fuente de verdad = ejecución real, no reporte parcial”
```
