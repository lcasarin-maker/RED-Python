# 🤖 MATRIZ COMPLETA: AUTOMATIZACIÓN Y FILTROS POR AGENTE
**Configuración detallada | Mejores prácticas | Software externo | Integración**

---

## TABLA DE CONTENIDOS

1. **CLAUDE CODE** — Desktop Windows + Terminal
2. **CODEX** — Desktop Windows + Terminal
3. **GEMINI CLI** — Terminal Linux/Windows
4. **ANTIGRAVITY** — Desktop Windows
5. **Matriz comparativa de mejores prácticas**
6. **Software externo recomendado**
7. **Configuración por proyecto**

---

## 1. CLAUDE CODE (Desktop + Terminal)

### 1.1 AUTOMATIZACIÓN NIVEL A (SIN CÓDIGO)

| Tarea | Acción | Ahorro |
|---|---|---|
| **Mejorar prompts** | Usar PROMPTS_RAPIDOS_v2.md | −25% output |
| **Reducir contexto** | Usar view archivo.py --lines X:Y | −50% input |
| **Ahorrar preámbulos** | Agregar <formato_respuesta> | −20% output |
| **Auto-detección cambio** | Ya implementado en PROTOCOLO_FINAL | −10% fricción |

**Costo:** 0 horas (ya funciona)
**Beneficio:** −25% a −50% tokens

---

### 1.2 AUTOMATIZACIÓN NIVEL B (SPRINT 2 - Prompt Caching)

#### **Instalación (2 horas, una sola vez):**

```powershell
# Paso 1: Verificar Python 3.11+
python --version

# Paso 2: Instalar Sprint 2
cd D:\GoogleDrive\AI\Proyectos\Tokensaver_V1\referencias\sprint2
powershell -ExecutionPolicy Bypass -File INSTALAR_SPRINT2.ps1

# El script:
#   - Verifica Python
#   - Instala pip install anthropic
#   - Pide ANTHROPIC_API_KEY (entra como variable de entorno)
#   - Prueba conexión
```

#### **Uso diario (Desktop → Terminal):**

```powershell
# ANTES (Desktop - sin caching):
# Abres Claude Code Desktop
# Cada mensaje reprocesa CLAUDE.md completo
# −85% ahorro de tokens NO sucede

# DESPUÉS (Terminal - con caching):
cd D:\ruta\a\tu\proyecto
powershell -ExecutionPolicy Bypass -File D:\....\sprint2\SESION_API.ps1

# Aparece sesión interactiva:
# Session iniciada con Prompt Caching activo
# Cada mensaje reutiliza caché de CLAUDE.md + STATUS.md
# Resultado: −85% input tokens automáticamente
```

#### **Qué ves en pantalla:**

```
[HAIKU] input: 45 tokens | output: 120 tokens | cache_hit: 890 (95% ahorrado)
         ↑                                        ↑
    Lo que pagas                          Lo que se reutiliza
```

#### **Mejores prácticas SPRINT 2:**

| Práctica | Cómo | Impacto |
|---|---|---|
| **Reusar sesión** | Mantén sesión abierta para tareas del mismo proyecto | Cache hit máximo |
| **Cerrar limpio** | Escribe "exit" antes de cambiar proyecto | STATUS.md guarda automático |
| **Override modelo** | `/sonnet mi pregunta` dentro sesión | Control sin salir |
| **Checkpoints frecuentes** | Cada 5-10 mensajes, dile "actualiza STATUS.md" | Continuidad |

---

### 1.3 AUTOMATIZACIÓN NIVEL C (SPRINT 3 - Auto-Compaction)

#### **Instalación (1.5 horas):**

```powershell
cd D:\GoogleDrive\AI\Proyectos\Tokensaver_V1\referencias\sprint3
powershell -ExecutionPolicy Bypass -File INSTALAR_SPRINT3.ps1

# El script agrega:
#   - auto_compact.py (compresión automática cada 20 turnos)
#   - batch_processor.py (para tareas batch diferidas)
#   - tokensaver_session_v2.py (motor completo)
#   - BATCH_TAREAS.ps1 (menú visual)
```

#### **Uso diario:**

```powershell
# OPCIÓN A: Sesión normal (mejor para mayor parte del tiempo)
cd tu_proyecto
powershell -ExecutionPolicy Bypass -File D:\....\sprint3\BATCH_TAREAS.ps1
# Selecciona Opción 1 → "Sesión normal con auto-compact"

# OPCIÓN B: Procesar batch de documentos (rápido, paralelo)
# Selecciona Opción 2 → "Procesar carpeta de documentos"
# Resultado: −50% costo, latencia diferida
```

#### **Auto-Compaction en acción:**

```
Turno 1-19:     Conversación normal
                [Contexto: 19/50 | NORMAL]

Turno 20:       🔵 AUTO-COMPACT ACTIVADO
                Sistema resume automáticamente:
                  - Mensajes 1-14 → 200 palabras de resumen
                  - Últimos 6 mensajes → intactos
                [Contexto: 7 msgs de resumen + 6 originales = limpio]

Turno 21-39:    Conversación continúa normalmente
                [Contexto: 14/50 | NORMAL]

Turno 40:       🔵 AUTO-COMPACT ACTIVADO (2da vez)
                Same process
```

**Beneficio:** −70% a −80% input tokens en sesiones largas, AUTOMÁTICO.

---

### 1.4 AUTOMATIZACIÓN NIVEL D (SPRINT 4 - RAG Pruning)

#### **Instalación (3 horas):**

```powershell
cd D:\GoogleDrive\AI\Proyectos\Tokensaver_V1\referencias\sprint4

# Si tienes PDFs legales:
python pdf_extractor.py --input "D:\tu_carpeta_sentencias" --output "rag_docs"
# Convierte PDFs a .txt (OCR si es necesario)

# Indexar en ChromaDB:
python rag_indexer.py --folder rag_docs
# Resultado: Base de datos vectorial en C:\Users\Luis\.tokensaver\rag_db\

# Usar sesión v3 con RAG:
powershell -ExecutionPolicy Bypass -File SPRINT4.ps1
# Selecciona Opción 1 → "Sesión con RAG Pruning"
```

#### **RAG Pruning en acción:**

```
TÚ: "¿Hay algo sobre litisconsorcio necesario?"

ANTES (sin RAG):
  Sistema manda TODA la carpeta rag_docs/ (~15,000 tokens)

DESPUÉS (con RAG):
  1. Convierte pregunta a vector
  2. Busca fragmentos más cercanos
  3. Recupera 4-5 chunks relevantes (~500 tokens)
  4. Manda solo esos a Claude

RESULTADO: Misma respuesta, −97% contexto

Ganancia: −40% a −60% input tokens base
```

---

### 1.5 CONFIGURACIÓN FINAL CLAUDE CODE

#### **CLAUDE.md óptimo para Claude Code:**

```markdown
# CLAUDE.md — Claude Code Tokensaver v4.0

## Perfil del usuario
- Abogado, no programador
- Necesita pasos pequeños y verificables
- Prefiere español simple

## Reglas de respuesta
- CORTAS por default (máx 5 líneas)
- DETALLADAS solo si es explicación nova
- NUNCA preámbulos ("Claro, con gusto...")
- NUNCA postámbulos ("Espero haber ayudado...")

## Reglas técnicas
- NUNCA cargas archivo completo
- SIEMPRE: view archivo.py --lines 45:78
- Lee STATUS.md como fuente de verdad
- Monitorea contador X/50 automáticamente

## Archivos clave
- AGENTS.md: reglas permanentes
- STATUS.md: estado actual + siguiente paso
- PROMPTS_RAPIDOS.md: templates listos

## Protocolo
- Detecto cambios de tarea automáticamente
- Sugiero CLEAR cuando sea necesario
- Actualizo STATUS.md después de cada tarea
- Monitoreo contexto cada respuesta

## Restricciones
- No analices "todo el proyecto"
- Pide permiso antes de cambios grandes
- Si riesgo: avisa primero, ejecuta después
```

#### **.claudeignore agresivo:**

```
# Carpetas a excluir COMPLETAMENTE
node_modules/
__pycache__/
.git/
.venv/
venv/
dist/
build/
*.pyc
*.log
.DS_Store
Thumbs.db

# Archivos gigantes
*.pdf
*.mp4
*.mov
*.zip
*.tar.gz

# Ruido típico
.idea/
.vscode/
*.swp
.env (except si necesitas)
```

#### **STATUS.md template:**

```markdown
# STATUS.md — [Nombre Proyecto]
**Última actualización:** 2026-04-25

## Logrado en esta sesión
- ✅ Hiciste X
- ✅ Hiciste Y
- ❌ No lograste Z (bloqueador: razón)

## Estado actual
- ESTADO: [en_progreso | bloqueado | completado]
- ÚLTIMA_TAREA: [descripción de lo que acabas de hacer]
- PRÓXIMO_PASO: [exacto, no vago]

## Bloqueadores
- Ninguno / [si hay alguno]

## Información importante
- [Lo que durará más allá de esta sesión]
```

---

## 2. CODEX DE OPENAI (Desktop + Terminal)

### 2.1 REGLA DE ORO PARA CODEX

```
CODEX = Ejecución, NO pensamiento

✅ Úsalo para:      ❌ NO lo uses para:
- Tocar archivos    - Entender conceptos
- Corregir código   - Comparar opciones
- Implementar algo  - Redactar documentos
- Actualizar config - Pensar estrategia
```

### 2.2 AUTOMATIZACIÓN NIVEL A (Prompts optimizados)

#### **PROMPTS_RAPIDOS_v3_CODEX.md:**

```markdown
## PROMPT 1 — Tarea de código (el 90% de casos)

```xml
<instrucciones>
  Lee AGENTS.md and STATUS.md.
  Ejecuta EXACTAMENTE una cosa.
  Si no queda claro, haz la opción más segura y avísame.
</instrucciones>

<contexto>
  <archivo>AGENTS.md</archivo>
  <archivo>STATUS.md</archivo>
</context>

<tarea>
  [Tu tarea en máximo 2 líneas]
</tarea>

<restricciones>
  - SOLO este archivo: [archivo específico]
  - Máximo 200 palabras en tu respuesta
  - Si hay riesgo: **avísame ANTES de ejecutar**
  - Actualiza STATUS.md con resultado
</restricciones>

<formato_respuesta>
ACCIÓN: [lo que hiciste en 1 línea]
RESULTADO: [resultado en máx 3 líneas]
PRÓXIMO: [siguiente paso]
```
```

#### **Mejores prácticas CODEX Desktop:**

| Hacer | No hacer |
|---|---|
| ✅ "Corrige auth.py líneas 45-78" | ❌ "Analiza todo el backend" |
| ✅ "Sube AGENTS.md y STATUS.md, luego ayuda" | ❌ "Lee todo el proyecto" |
| ✅ Copiar/pega prompt de PROMPTS_RAPIDOS | ❌ Improvisar prompts |
| ✅ "Si hay riesgo, avísame primero" | ❌ "Ejecuta sin confirmar" |

### 2.3 AUTOMATIZACIÓN NIVEL B (Terminal - RAG manual)

#### **CODEX_OPTIMIZADO.ps1** (crear en Semana 4):

```powershell
# Script que automatiza:
# 1. Lee AGENTS.md / STATUS.md
# 2. Extrae SOLO secciones relevantes (RAG manual)
# 3. Manda a Codex con contexto mínimo
# 4. Captura respuesta
# 5. Actualiza STATUS.md

# Ahorro: −40% input tokens vs. mandar archivos completos

# Pseudocódigo:
function Invoke-CodexOptimized {
    param([string]$task)

    # 1. Detecta qué archivo/sección necesita la tarea
    $relevant_section = Extract-RelevantSection -AGENTS_MD $agents -task $task

    # 2. Crea contexto mínimo
    $minimal_context = @{
        instructions = $relevant_section.instructions
        restrictions = $relevant_section.restrictions
        files = @($task.primary_file)
    }

    # 3. Manda a Codex
    $response = Invoke-Codex -context $minimal_context -task $task

    # 4. Actualiza STATUS.md
    Update-StatusMD -response $response
}
```

**Esfuerzo:** 2-3 horas (crear script)
**Ahorro:** −40% input tokens

---

## 3. GEMINI CLI (Terminal)

### 3.1 REGLA DE ORO PARA GEMINI

```
GEMINI = Pensamiento, NO ejecución

✅ Úsalo para:       ❌ NO lo uses para:
- Pensar opciones    - Tocar archivos
- Entender conceptos - Ejecutar cambios
- Comparar           - Actualizar código
- Redactar mejores - Crear scripts
  prompts
```

### 3.2 AUTOMATIZACIÓN NIVEL A (Fragmentos, no archivos)

#### **GEMINI_OPTIMIZADO.ps1:**

```powershell
function Start-GeminiSession {
    param([string]$task)

    # NUNCA esto:
    # gcloud ai gemini upload AGENTS.md

    # SIEMPRE esto:
    # 1. Extrae fragmento relevante
    $fragment = Extract-Fragment -AGENTS_MD $agents -lines 50

    # 2. Abre Gemini con fragmento
    # 3. Usuario hace pregunta
    # 4. Copia resultado a STATUS.md

    Write-Host "Fragmento preparado. Abre Gemini y pega:"
    Write-Host $fragment
}
```

#### **Mejores prácticas GEMINI CLI:**

| Hacer | No hacer |
|---|---|
| ✅ Sube 200-300 palabras de contexto | ❌ Sube AGENTS.md completo (150 líneas) |
| ✅ Pregunta específica ("¿cuál es el riesgo?") | ❌ Exploración abierta ("cuéntame sobre...") |
| ✅ Copia resultado a STATUS.md tú | ❌ Espera que Gemini lo haga |
| ✅ Una sesión = una pregunta | ❌ Múltiples temas en sesión |

### 3.3 AUTOMATIZACIÓN NIVEL B (Integración con Claude)

**Flujo óptimo:**

```
1. TÚ: Quiero entender si hay riesgo en...
2. GEMINI: [análisis, opción A/B/C]
3. TÚ: Copias respuesta a STATUS.md
4. TÚ: Abre Claude Code
5. CLAUDE: Lee STATUS.md. Ejecuta opción A.
```

**Beneficio:** −60% tokens en GEMINI (solo fragmentos) + −85% en CLAUDE (Prompt Caching)

---

## 4. ANTIGRAVITY (Desktop Windows)

### 4.1 REGLA DE ORO PARA ANTIGRAVITY

```
ANTIGRAVITY = Revisión visual ÚNICAMENTE

✅ Usa para:           ❌ NO uses para:
- Revisar sentencias  - Pensar estrategia
- Análisis visual     - Análisis de código
- Comparar docs       - Generar prompts
- Brainstorm jurídico - Ejecutar cambios
```

### 4.2 AUTOMATIZACIÓN (Límites de fragmentos)

#### **Cómo usar sin fugas:**

```
ANTES (fuga masiva):
  └─ Abres Antigravity Desktop
  └─ Subes AGENTS.md completo (150 líneas)
  └─ Subes STATUS.md completo (80 líneas)
  └─ = 5,000+ tokens por sesión

DESPUÉS (optimizado):
  1. Abre un editor (Notepad)
  2. Copia FRAGMENTO de STATUS.md (5 líneas)
  3. Abre Antigravity
  4. Pega fragmento SOLAMENTE
  5. Pregunta específica
  6. Copia resultado a STATUS.md tú
  7. Cierra
  = 500 tokens por sesión (−90%)
```

#### **Template: "Uso Optimizado de Antigravity"**

```markdown
## Caso 1: Revisar sentencia

1. En Notepad: copia FRAGMENTO de sentencia (2-3 párrafos)
2. Abre Antigravity, pega
3. Pregunta: "¿Cuáles son los 5 puntos jurídicos clave?"
4. Copia respuesta a PROMPTS_RAPIDOS.md
5. Cierra

Costo: ~300 tokens
Beneficio: 5 puntos clave documentados

## Caso 2: Comparar dos contratos

1. Extrae FRAGMENTOS de ambos (3-4 párrafos cada)
2. Abre Antigravity
3. Pega ambos fragmentos
4. Pregunta: "¿Cuál es la diferencia crítica en indemnización?"
5. Copia a análisis
6. Cierra

Costo: ~400 tokens
Beneficio: Análisis específico vs. genérico
```

---

## 5. MATRIZ COMPARATIVA: MEJORES PRÁCTICAS

```markdown
| Práctica | Claude Code | Codex | Gemini | Antigravity |
|---|---|---|---|---|
| **Prompt Caching** | ✅ Sprint 2 | ❌ N/A | ❌ N/A | ❌ N/A |
| **RAG Pruning** | ✅ Sprint 4 | 🟡 Manual | 🟡 Manual | ✅ Fragmentos |
| **Output Constraining** | ✅ PROMPTS_v2 | ✅ PROMPTS_v3 | 🟡 Parcial | ✅ Directo |
| **Auto-Compaction** | ✅ Sprint 3 | ❌ Manual | ❌ Manual | ❌ N/A |
| **Model Cascading** | ✅ Sprint 2 | ❌ Manual | ❌ Manual | ❌ N/A |
| **Checkpoint automático** | ✅ Sprint 2/3 | 🟡 Manual | 🟡 Manual | ❌ Manual |
| **Ideal para** | Todo | Ejecución | Pensamiento | Revisión visual |
| **Ahorro máximo** | −85% input | −60% input | −60% input | −90% input |
```

---

## 6. SOFTWARE EXTERNO RECOMENDADO

### **OBLIGATORIO (ya tienes):**

```
✅ Python 3.11+
✅ PowerShell 7 (Windows)
✅ Git (para backup)
```

### **NECESARIO PARA SPRINTS 2+:**

```
✅ pip install anthropic
   └─ Para Prompt Caching y Batch API

✅ pip install chromadb
   └─ Para RAG Pruning (Sprint 4)
```

### **OPCIONAL (mejora velocidad):**

```
🟡 pip install python-dotenv
   └─ Para gestionar variables de entorno (API keys)

🟡 VSCode extension "PowerShell"
   └─ Para ejecutar scripts PS1 directamente desde editor

🟡 Notepad++ o VSCode
   └─ Para editar AGENTS.md / STATUS.md con sintaxis
```

### **PARA PDFs ESCANEADOS (solo si usas Sprint 4):**

```
🟡 Adobe Acrobat Reader DC
   └─ Verifica si PDF tiene OCR

🟡 PyMuPDF + ocr
   └─ pip install pymupdf
   └─ Extrae texto de PDFs escaneados
   └─ Incluido en pdf_extractor.py del Sprint 4
```

---

## 7. CONFIGURACIÓN POR PROYECTO

### **Configuración Template Proyecto Nuevo:**

```
mi_proyecto/
├── .claude/
│   └── system.md          ← Protocolo v4.0 (no editar)
├── .claudeignore          ← Lista de exclusión agresiva
├── CLAUDE.md              ← Identidad + reglas (CRÍTICO)
├── AGENTS.md              ← Información permanente
├── STATUS.md              ← Estado actual + siguiente paso
├── PROMPTS_RAPIDOS.md     ← Templates listos
├── PROMPTS_RAPIDOS_v3.md  ← Versión optimizada (nuevo)
├── justfile               ← Comandos de Windows
├── SESION_API.ps1         ← Lanzador Sprint 2 (nuevo)
│
├── src/                   ← Tu código
├── tests/                 ← Tests
├── docs/                  ← Documentación
└── README.md
```

### **Configuración por tipo de proyecto:**

#### **A. Proyecto de CÓDIGO (Python/Node):**

```markdown
## Configuración específica:

### CLAUDE.md: agregar
```
## Stack técnico
- Lenguaje: Python 3.11
- Framework: [Django/FastAPI/etc]
- DB: [PostgreSQL/SQLite/etc]

## Estructura clave
src/
├── api/
├── models/
├── utils/
└── main.py

## Errores conocidos
- [Si hay, documenta aquí]
```

### AGENTES_BASE.md para código:
```
## Herramienta principal
Claude Code (Desktop + Terminal con Sprint 2)

## Restricción clave
NUNCA cargas más de 100 líneas a la vez.
Usa: view archivo.py --lines 45:78

## Protocolo
- Prompt Caching activado (Sprint 2)
- Auto-Compaction cada 20 turnos (Sprint 3)
- RAG Pruning si {documentación, scripts} > 5MB (Sprint 4)
```
```

#### **B. Proyecto JURÍDICO (Sentencias, contratos):**

```markdown
## Configuración específica:

### CLAUDE.md: agregar
```
## Documentos principales
- Sentencias: carpeta /sentencias_PDF
- Contratos: carpeta /contratos_signed
- Análisis: carpeta /analisis_md

## Estructura
docs/
├── sentencias/          ← Indexadas con Sprint 4
├── contratos/
├── jurisprudencia/
└── resúmenes.md
```

### AGENTS_BASE.md para jurídico:
```
## Herramienta principal
PENSAMIENTO: Gemini CLI (fragmentos) + Claude para profundidad
EJECUCIÓN: Claude Code (análisis + docs)
VISUAL: Antigravity (revisar sentencias)

## Protocolo
- Gemini: NUNCA archivo completo, SIEMPRE fragmento
- Claude: RAG Pruning (Sprint 4) para sentencias
- Antigravity: Solo revisión visual (no análisis)
```
```

#### **C. Proyecto MIXTO (Código + Docs):**

```markdown
## Configuración específica:

### Usa TODOS los agentes pero SEGREGADOS:
- CÓDIGO: Claude Code (Sprint 2+3+4)
- DOCS: Gemini CLI (fragmentos)
- PENSAMIENTO: Claude Desktop si necesita reflexión
- EJECUCIÓN: Codex (si cambios pequeños confirmados)
```

---

## RESUMEN: QUÉ INSTALAR CUÁNDO

```
HOY (2 horas):
  └─ PROMPTS_RAPIDOS_v2.md mejorado
  └─ PROMPTS_RAPIDOS_v3.md creado

SEMANA 1 (3 horas):
  └─ Sprint 2 (Prompt Caching)
  └─ SESION_API.ps1 en cada proyecto

SEMANA 2 (2 horas):
  └─ Sprint 3 (Auto-Compaction)
  └─ BATCH_TAREAS.ps1 en proyectos

SEMANA 3-4 (3 horas):
  └─ Sprint 4 (RAG Pruning)
  └─ pdf_extractor.py si usas PDFs
  └─ rag_indexer.py para vectorización

MANTENIMIENTO (30 min/mes):
  └─ Actualizar CLAUDE.md con nuevos aprendizajes
  └─ Limpiar .claudeignore si crece repo
  └─ Documentar nuevos bloqueadores en STATUS.md
```

---

*Matriz generada: 2026-04-25 | Cobertura: 6 plataformas | Profundidad: Configuración + Mejores prácticas + Software*
