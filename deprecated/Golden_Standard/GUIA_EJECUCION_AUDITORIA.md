# GUÍA DE EJECUCIÓN — AUDITORÍA CODERCERBERUS
## Step-by-step para ejecutar el plan de auditoría del Marco Conceptual

**Versión:** 1.0  
**Duración estimada:** 14-21 horas de auditoría sistemática  
**Herramientas:** Python, Bash, grep, jq, git  
**Salida:** REPORTE_AUDITORIA_[FECHA].md + hallazgos en CSV  

---

## FASE 1: PREPARACIÓN (30 MIN)

### Paso 1.1: Crear estructura de trabajo

```bash
cd D:\AI\Cerberus
mkdir -p auditorias/[FECHA]
cd auditorias/[FECHA]

# Crear directorios para artefactos
mkdir -p {matriz, evidencia, hallazgos, pruebas}

# Copiar plantillas
cp ../../Golden_Standard/PLAN_AUDITORIA_MARCO_CONCEPTUAL.md ./plan.md
```

### Paso 1.2: Verificar archivos base

```bash
# Verificar que existen
ls -la ../../Golden_Standard/CODERCERBERUS_MARCO_CONCEPTUAL.md
ls -la ../../rules/
ls -la ../../learnings/

# Contar líneas del Marco
wc -l ../../Golden_Standard/CODERCERBERUS_MARCO_CONCEPTUAL.md
# Esperado: ~1046 líneas

# Contar archivos en Cerberus
find ../../rules -type f | wc -l
find ../../learnings -type f | wc -l
```

### Paso 1.3: Crear log de auditoría

```bash
cat > auditoria.log << 'EOF'
AUDITORÍA CODERCERBERUS v0.5
Fecha inicio: $(date)
Auditor: [TU_NOMBRE]

Fase 1: Preparación ............... [PENDIENTE]
Fase 2: Escaneo de cobertura ...... [PENDIENTE]
Fase 3: Mapeo de implementación .. [PENDIENTE]
Fase 4: Prueba de operatividad ... [PENDIENTE]
Fase 5: Análisis de correspondencia [PENDIENTE]
Fase 6: Detección de teatro ....... [PENDIENTE]
Fase 7: Generación de reporte ..... [PENDIENTE]

EOF
```

---

## FASE 2: ESCANEO DE COBERTURA (2-3 HORAS)

### Paso 2.1: Mapear antipatrones de vibe coding

**Entrada:** CODERCERBERUS_MARCO_CONCEPTUAL.md sección 4.1  
**Salida:** matriz/cobertura_vibe_coding.csv

```bash
cat > matriz/cobertura_vibe_coding.csv << 'EOF'
ID,Antipatrón,En_GS,Regla_Interna,Prueba_Interna,Evidencia,Consecuencia,Estado
VC-001,Código improvisado,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-002,Soluciones parciales,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-003,Hardcoding indebido,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-004,Rutas absolutas,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-005,Archivos fantasma,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-006,Documentación ficticia,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-007,Tests cosméticos,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-008,Funcionalidades inaccesibles,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-009,Falta de reversibilidad,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-010,Falta de trazabilidad,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-011,Falta de arquitectura,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-012,Acumulación deuda técnica,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-013,Soluciones solo entorno,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-014,Parches no integrados,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-015,Pérdida sincronía módulos,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VC-016,Prompts sin control,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
EOF
```

### Paso 2.2: Mapear vicios de testing

**Entrada:** Sección 4.2  
**Salida:** matriz/cobertura_testing.csv

```bash
cat > matriz/cobertura_testing.csv << 'EOF'
ID,Vicio,En_GS,Regla_Interna,Prueba_Interna,Evidencia,Consecuencia,Estado
VT-001,Tests validan existencia,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-002,Tests sin flujos reales,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-003,Tests omitidos por nombrado,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-004,Tests desconectados comportamiento,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-005,Tests pasan pero función inaccesible,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-006,Falta cobertura backend/frontend,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-007,Pruebas sin regresión,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-008,Pruebas con mocks irrelevantes,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-009,Tests validan apariencia,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
VT-010,Pruebas desconectadas riesgos,SÍ,[Buscar],[Buscar],[Buscar],[Buscar],TBD
EOF
```

### Paso 2.3: Mapear principios transversales

**Entrada:** Secciones 3.5, 15, 16, 17, 18, 19, 20, 11, 12  
**Salida:** matriz/cobertura_principios.csv

```bash
cat > matriz/cobertura_principios.csv << 'EOF'
ID,Principio,Sección,En_GS,Regla,Prueba,Evidencia,Consecuencia,Estado
P-001,Cadena de operatividad,3.5,SÍ,[],[],[],[],TBD
P-002,Matriz de correspondencia,15,SÍ,[],[],[],[],TBD
P-003,Anti-teatro de seguridad,16,SÍ,[],[],[],[],TBD
P-004,Consecuencia operativa,17,SÍ,[],[],[],[],TBD
P-005,Reversibilidad,18,SÍ,[],[],[],[],TBD
P-006,Trazabilidad,19,SÍ,[],[],[],[],TBD
P-007,Automatización no-programador,20,SÍ,[],[],[],[],TBD
P-008,Repositorio limpio,11,SÍ,[],[],[],[],TBD
P-009,Validación funcional real,12,SÍ,[],[],[],[],TBD
EOF
```

### Paso 2.4: Buscar implementaciones en Cerberus Interior

**Script:** search_interior.py

```python
#!/usr/bin/env python3
import os
import re
import json

CERBERUS_RULES = "../../rules"
CERBERUS_TESTS = "../../cerberus_tests"

def search_for_pattern(pattern, directory, file_extension=".py"):
    """Buscar patrón en archivos"""
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extension):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if re.search(pattern, content, re.IGNORECASE):
                            results.append({
                                'archivo': filepath.replace(CERBERUS_RULES, '.'),
                                'líneas': len(content.split('\n')),
                                'match': True
                            })
                except:
                    pass
    return results

# Buscar implementaciones
antipatterns = {
    'VC-001': 'improvised|improvisado|adhoc',
    'VC-002': 'partial|parcial|incomplete',
    'VC-003': 'hardcode|hardcoded',
    'VC-004': 'absolute.*path|ruta.*absoluta',
    # ... continuar con todos
}

output = {}
for pattern_id, regex in antipatterns.items():
    results = search_for_pattern(regex, CERBERUS_RULES)
    results.extend(search_for_pattern(regex, CERBERUS_TESTS))
    output[pattern_id] = results

with open('hallazgos_raw.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Búsqueda completada. {sum(len(v) for v in output.values())} coincidencias encontradas.")
```

**Ejecutar:**
```bash
python3 search_interior.py
# Salida: hallazgos_raw.json
```

### Paso 2.5: Compilar matriz de cobertura

```bash
# Actualizar CSVs con hallazgos de búsqueda
python3 << 'EOPYTHON'
import json
import csv

with open('hallazgos_raw.json') as f:
    hallazgos = json.load(f)

# Actualizar cobertura basada en búsqueda
for pattern_id, matches in hallazgos.items():
    if matches:
        print(f"{pattern_id}: ENCONTRADO - {len(matches)} archivos")
    else:
        print(f"{pattern_id}: NO ENCONTRADO")
EOPYTHON
```

---

## FASE 3: MAPEO DE IMPLEMENTACIÓN (4-6 HORAS)

### Paso 3.1: Para cada antipatrón encontrado, verificar la cadena completa

**Template:**

```bash
# Para cada VC-XXX encontrado:

echo "=== VC-001: Código improvisado ==="

# 1. ¿Existe regla ejecutable?
echo "Buscando regla..."
find ../../rules -name "*improvised*" -o -name "*vibe*" | head -5

# 2. ¿Existe prueba?
echo "Buscando prueba..."
find ../../cerberus_tests -name "*improvised*" -o -name "*vibe*" | head -5

# 3. ¿Qué evidencia genera?
echo "Buscando evidencia..."
grep -r "logger.info\|evidence\|report" ../../rules --include="*.py" | grep -i improvised

# 4. ¿Tiene consecuencia?
echo "Buscando consecuencia..."
grep -r "raise.*Error\|sys.exit\|block\|fail" ../../rules --include="*.py" | grep -i improvised
```

### Paso 3.2: Completar matriz de operatividad

**Plantilla para cada mandato:**

```bash
# Mandato S1: Rigor 12D

echo "=== S1: RIGOR 12D ==="

# 1. ¿Archivo existe?
test -f ../../rules/security_audit_12d.py && echo "✓ run_security_audit_12d.py existe" || echo "✗ No encontrado"

# 2. ¿Se ejecuta automáticamente?
grep -r "pre-commit\|pre-push\|github.*action" ../../rules --include="*.yaml" --include="*.yml"

# 3. ¿Prueba valida operatividad real?
grep -A 10 "def test_security_audit" ../../cerberus_tests/*.py

# 4. ¿Genera evidencia?
grep -r "logger.info\|json.dump" ../../rules/security_audit_12d.py | head -3

# 5. ¿Consecuencia?
grep -r "sys.exit\|raise\|block\|fail" ../../rules/security_audit_12d.py | head -3
```

### Paso 3.3: Crear tabla de operatividad

```bash
cat > matriz/operatividad_interior.csv << 'EOF'
Mandato,Archivo,Automático,Prueba_Real,Evidencia,Consecuencia,Última_Ejecución,Estado
S1,rules/security_audit_12d.py,[],[],[],[],DESCONOCIDA,PENDIENTE
S2,rules/spec_first.py,[],[],[],[],DESCONOCIDA,PENDIENTE
S3,rules/bio_containment.py,[],[],[],[],DESCONOCIDA,PENDIENTE
[...]
EOF
```

---

## FASE 4: PRUEBA DE OPERATIVIDAD (3-4 HORAS)

### Paso 4.1: Script de prueba intencional

**pruebas_operatividad.py**

```python
#!/usr/bin/env python3
"""
Crear violaciones intencionales y verificar detección
"""
import os
import sys
import tempfile
import subprocess
import json
from datetime import datetime

RESULTADOS = {}

def test_regla(regla_id, violacion_tipo, archivo_viola):
    """
    Crear violación y ejecutar regla
    """
    print(f"\n[TEST] {regla_id}: {violacion_tipo}")
    
    # 1. Crear violación temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(archivo_viola)
        temp_file = f.name
    
    try:
        # 2. Ejecutar regla correspondiente
        resultado = subprocess.run(
            ['python3', f'../../rules/{regla_id.lower()}_check.py', temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # 3. Registrar resultado
        detectada = resultado.returncode != 0
        bloqueada = 'ERROR' in resultado.stdout or resultado.returncode > 1
        
        RESULTADOS[regla_id] = {
            'detectada': detectada,
            'bloqueada': bloqueada,
            'stdout': resultado.stdout[:200],
            'stderr': resultado.stderr[:200],
            'estado': 'OPERATIVO' if detectada and bloqueada else 'TEATRO'
        }
        
        print(f"  Detectada: {'✓' if detectada else '✗'}")
        print(f"  Bloqueada: {'✓' if bloqueada else '✗'}")
        print(f"  Estado: {RESULTADOS[regla_id]['estado']}")
        
    finally:
        os.unlink(temp_file)

# Test 1: Código improvisado (sin funciones, sin estructura)
test_regla('VC-001', 'Código improvisado', '''
x = 1
y = 2
z = x + y
print(z)
''')

# Test 2: Hardcoding
test_regla('VC-003', 'Hardcoding absoluto', '''
db_path = "C:\\\\Users\\\\Luis\\\\data\\\\production.db"
api_key = "sk-1234567890abcdef"
password = "admin123"
''')

# Test 3: Rutas absolutas
test_regla('VC-004', 'Rutas absolutas', '''
config_file = "D:\\\\AI\\\\config\\\\settings.json"
log_file = "/home/user/app/logs/debug.log"
''')

# [Continuar con más pruebas...]

# Generar reporte
with open('resultados_operatividad.json', 'w') as f:
    json.dump(RESULTADOS, f, indent=2)

teatro_count = sum(1 for v in RESULTADOS.values() if v['estado'] == 'TEATRO')
operativo_count = sum(1 for v in RESULTADOS.values() if v['estado'] == 'OPERATIVO')

print(f"\n\nRESUMEN:")
print(f"Operativos: {operativo_count}")
print(f"Teatro: {teatro_count}")
print(f"Tasa de operatividad: {operativo_count/(operativo_count+teatro_count)*100:.1f}%")

sys.exit(0 if teatro_count == 0 else 1)
```

**Ejecutar:**
```bash
python3 pruebas_operatividad.py
```

### Paso 4.2: Registrar resultados

```bash
# Actualizar matriz con resultados
python3 << 'EOF'
import json
import csv

with open('resultados_operatividad.json') as f:
    resultados = json.load(f)

# Exportar a CSV
with open('matriz/operatividad_verificada.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['Regla', 'Detecta', 'Bloquea', 'Estado'])
    writer.writeheader()
    for regla, res in resultados.items():
        writer.writerow({
            'Regla': regla,
            'Detecta': res['detectada'],
            'Bloquea': res['bloqueada'],
            'Estado': res['estado']
        })
EOF
```

---

## FASE 5: ANÁLISIS DE CORRESPONDENCIA (2-3 HORAS)

### Paso 5.1: Crear matriz GS ↔ Interior ↔ Exterior

```bash
cat > matriz/correspondencia.csv << 'EOF'
ID_GS,Principio,Regla_Interna,Prueba_Interna,Regla_Externa,Prueba_Externa,Estado
P-001,Cadena operatividad,[],[],[],[],ORFANO
VC-001,Código improvisado,[],[],[],[],ORFANO
[...]
EOF
```

### Paso 5.2: Buscar orfandades

```bash
python3 << 'EOF'
import os
import re

# Todos los principios de GS
gs_principles = [
    'VC-001', 'VC-002', # ... todo el listado
]

# Encontrar referencias en Cerberus Interior
interior_files = set()
for root, dirs, files in os.walk('../../rules'):
    for f in files:
        if f.endswith('.py'):
            interior_files.add(f)

# Encontrar referencias en proyectos vigilados
exterior_files = set()
# Buscar en repos de ejemplo
for root, dirs, files in os.walk('../..'):
    for f in files:
        if 'gatekeeper' in f or 'hook' in f:
            exterior_files.add(f)

# Identificar orfandades
for principle in gs_principles:
    has_interior = any(principle.lower() in f for f in interior_files)
    has_exterior = any(principle.lower() in f for f in exterior_files)
    
    if not has_interior:
        print(f"ORFANO INTERIOR: {principle}")
    if not has_exterior:
        print(f"ORFANO EXTERIOR: {principle}")
EOF
```

---

## FASE 6: DETECCIÓN DE TEATRO (2-3 HORAS)

### Paso 6.1: Script de detección

```bash
python3 << 'EOF'
import os
import re

TEATRO_INDICATORS = [
    ('test.*exist', 'Tests que validan existencia'),
    ('file.*open', 'Tests que abren archivos sin verificar funcionalidad'),
    ('mock.*assert', 'Tests con mocks sin comportamiento real'),
    ('pass', 'Tests vacíos que solo pasan'),
    (r'if.*True:', 'Condiciones siempre verdaderas'),
]

hallazgos_teatro = []

for root, dirs, files in os.walk('../../cerberus_tests'):
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            with open(filepath) as test_file:
                content = test_file.read()
                for pattern, desc in TEATRO_INDICATORS:
                    if re.search(pattern, content):
                        hallazgos_teatro.append({
                            'archivo': filepath,
                            'patrón': desc,
                            'severidad': 'MEDIA'
                        })

print(f"\n=== HALLAZGOS DE TEATRO ===")
for h in hallazgos_teatro:
    print(f"{h['archivo']}: {h['patrón']}")

print(f"\nTotal: {len(hallazgos_teatro)} potenciales falsos positivos")
EOF
```

---

## FASE 7: GENERACIÓN DE REPORTE (1-2 HORAS)

### Paso 7.1: Compilar hallazgos

```bash
python3 << 'EOF'
import csv
import json
from datetime import datetime

# Leer todas las matrices
cobertura = {}
operatividad = {}
correspondencia = {}
teatro = {}

# Compilar estadísticas
stats = {
    'fecha_auditoria': datetime.now().isoformat(),
    'elementos_gs': 0,
    'con_regla': 0,
    'con_prueba': 0,
    'con_evidencia': 0,
    'con_consecuencia': 0,
    'operativos': 0,
    'teatro': 0,
    'orfandades': 0,
}

# Generar REPORTE_AUDITORIA.md
with open('REPORTE_AUDITORIA.md', 'w') as f:
    f.write(f"""# REPORTE DE AUDITORÍA CODERCERBERUS v0.5

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Alcance:** Marco Conceptual, Cerberus Interior, Cerberus Exterior

## RESUMEN EJECUTIVO

- **Cobertura:** __% (elementos con 4 pilares)
- **Operatividad:** __% (reglas que funcionan de verdad)
- **Correspondencia:** __% (sin orfandades)
- **Teatro:** __% (falsos positivos)

## HALLAZGOS CRÍTICOS

[Listar hallazgos de Severidad Crítica]

## MATRIZ DE COBERTURA

[Insertar tabla...]

## MATRIZ DE OPERATIVIDAD

[Insertar tabla...]

## PLAN DE REMEDIACIÓN

[Insertar acciones...]
""")

print("Reporte generado: REPORTE_AUDITORIA.md")
EOF
```

### Paso 7.2: Crear resumen ejecutivo

```bash
cat > RESUMEN_EJECUTIVO.txt << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║        AUDITORÍA CODERCERBERUS v0.5 - RESUMEN EJECUTIVO        ║
╚════════════════════════════════════════════════════════════════╝

Cobertura de Implementación:
  • Elementos con regla ejecutable: __/%
  • Elementos con prueba asociada: __/%
  • Elementos con evidencia verificable: __/%
  • Elementos con consecuencia definida: __/%

Operatividad Real:
  • Reglas que funcionan de verdad: __/%
  • Reglas que son teatro: __/%

Correspondencia:
  • GS ↔ Interior conectado: __/%
  • GS ↔ Exterior conectado: __/%
  • Orfandades críticas: __

VEREDICTO:
  ✓ OPERATIVO
  ✗ CRÍTICO - REQUIERE ACCIÓN INMEDIATA
  ⚠ REQUIERE REMEDIACIÓN

Próximos Pasos:
  1. [Acción 1]
  2. [Acción 2]
  3. [Acción 3]

Auditor: __________
Aprobación: __________
Fecha: __________
EOF
```

---

## CHECKLIST FINAL

```bash
cat > CHECKLIST_EJECUCION.md << 'EOF'
# CHECKLIST DE EJECUCIÓN

## Fase 1: Preparación
- [ ] Estructura de directorios creada
- [ ] Archivos base verificados
- [ ] Log de auditoría inicializado

## Fase 2: Escaneo de Cobertura (2-3h)
- [ ] Mapeadas 16 antip atrones de vibe coding
- [ ] Mapeados 10 vicios de testing
- [ ] Mapeados 9 principios transversales
- [ ] Búsqueda exhaustiva en Cerberus Interior completada
- [ ] CSV de cobertura actualizado

## Fase 3: Mapeo de Implementación (4-6h)
- [ ] Cada antipatrón verificado en 3+ ubicaciones
- [ ] Cadena completa (regla→prueba→evidencia→consecuencia) trazada
- [ ] Matriz de operatividad completada
- [ ] Últimas ejecuciones verificadas

## Fase 4: Prueba de Operatividad (3-4h)
- [ ] 20+ pruebas intencionales ejecutadas
- [ ] Cada regla probada con violación real
- [ ] Resultados documentados en JSON
- [ ] Tasa de operatividad calculada

## Fase 5: Análisis de Correspondencia (2-3h)
- [ ] Matriz GS ↔ Interior ↔ Exterior creada
- [ ] Orfandades identificadas
- [ ] Drift de principios detectado

## Fase 6: Detección de Teatro (2-3h)
- [ ] Tests examinados línea por línea
- [ ] Falsos positivos identificados
- [ ] Reglas sin efecto real detectadas

## Fase 7: Generación de Reporte (1-2h)
- [ ] Reporte completo generado
- [ ] Hallazgos clasificados por severidad
- [ ] Plan de remediación definido
- [ ] Resumen ejecutivo creado

## Validaciones Finales
- [ ] ¿Hallazgos verificables (no asunciones)?
- [ ] ¿Evidencia real (logs, no testimonios)?
- [ ] ¿Severidades justificadas?
- [ ] ¿Plan de remediación accionable?
- [ ] ¿Sin falsas alarmas?

## Aprobación
- [ ] Auditor verifica checklist
- [ ] Responsable técnico revisa reporte
- [ ] Acciones prioritarias identificadas

Fecha completado: __________
Auditor: __________
Aprobación: __________
EOF
```

---

## NOTAS OPERATIVAS

### Anti-Triunfalismo (Mandato B7)

**Prohibido:**
- "CoderCerberus implementa correctamente el Marco"
- "La auditoría confirma que todo funciona"
- "Operatividad verificada" (sin adjuntar pruebas)

**Permitido:**
- "Se ejecutó prueba X en [fecha] con resultado Y; ver evidencia en [ruta]"
- "Grep muestra N instancias de [patrón] en [archivos]"
- "Script generó salida [adjuntar log]"

### Si encuentras teatro

No descartes el hallazgo como "falso positivo".

**Documento con severidad MEDIA:**
```
HALLAZGO: Test cosméticno en [archivo]
Descripción: assert file.exists() sin verificar contenido
Severidad: MEDIA
Remediación: Reescribir test para validar funcionalidad real
Responsable: [Quien mantiene el test]
Plazo: [Próxima sesión]
```

### Si encuentras orfandad

**No improvises implementación.**

**Marca como:**
```
HALLAZGO: Principio P-005 sin regla externa
Descripción: Reversibilidad está en GS pero no se valida en repos vigilados
Severidad: ALTA
Causa: Cerberus Exterior incompleto
Acción: Crear `hooks/check_reversibility.py`
Responsable: [Nombre]
Plazo: 1 semana
```

---

**FIN DE GUÍA DE EJECUCIÓN**

Tiempo estimado total: **14-21 horas de auditoría disciplinada**

Si necesitas interrumpir, guarda estado en `auditoria.log` y continúa desde última fase completada.
