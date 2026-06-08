<<<<<<< HEAD
# RED-Python — Remove Empty Directories

A cross-platform Python tool for finding and removing empty (or effectively empty) directories.  
Combines the best of [hxseven/Remove-Empty-Directories](https://github.com/hxseven/Remove-Empty-Directories) (C#/Windows), the simplicity of a bottom-up Python approach, and additional features gathered from the broader ecosystem (Czkawka, VoidFinder, emptydir, etc.).

---

## Features

| Feature | Description |
|---|---|
| **Advanced grid** | New results table with Size (potential savings), Date, and status |
| **Windows Menu** | Context menu integration — right-click a folder to scan with RED-Python |
| **Portable Mode** | Automatic detection of local `settings.json` for USB drive use |
| **Audible Feedback**| Beep sound when long scans or deletions finish (configurable) |
| **Smart detection** | Finds folders that *would* become empty after cleanup — not just physically empty ones |
| **GUI + CLI** | Full tkinter GUI for desktop use; CLI mode for scripting and automation |
| **Simulation mode** | Preview exactly what would be deleted before touching anything |
| **Recycle Bin** | Safely moves folders to the Recycle Bin instead of permanent deletion |
| **Permanent delete** | Direct removal with confirmation dialog |
| **Multi-path scan** | Add multiple root directories to scan in a single pass |
| **Recent paths** | History of the last 10 used paths |
| **Ignore patterns** | Wildcard (`*.tmp`) and regex (`/pattern/`) for files and folder names |
| **Safe defaults** | Pre-configured to ignore `desktop.ini`, `Thumbs.db`, `.DS_Store`, `__pycache__`, `.venv`, etc. |
| **Protected dirs** | System32, SysWOW64, $RECYCLE.BIN and others are never touched |
| **Max depth** | Limit scan depth to avoid going too deep |
| **Age filter** | Skip directories modified less than N hours ago |
| **0-byte files** | Treat empty files as non-existent (configurable) |
| **Symlink detection** | Avoids infinite loops caused by symbolic links |
| **Permission handling** | Separates permission errors from other errors; continues gracefully |
| **Detailed log** | Timestamped log with all operations |
| **Export results** | Save scan results to CSV or TXT |
| **Post-action report** | Shows total folders processed and MB freed |
| **Persistent settings** | Configuration saved to `~/.red_python/settings.json` |
| **Long path support** | Handles Windows paths longer than 260 characters (`\\?\` prefix) |

---

## External Audit

The external audit instruction for this repo lives in [00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md](00%20audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md).
Use that document as the source of truth for any external audit run or review.

---

## Requirements

- Python 3.10+
- [`send2trash`](https://pypi.org/project/Send2Trash/) (for Recycle Bin support)

```bash
pip install -r requirements.txt
```

---

## Usage

### GUI

```bash
python red.py
```

### CLI

```bash
# Simulate (dry-run) — show what would be deleted
python red.py --scan "C:\Users\Me\Projects" --dry-run

# Send to Recycle Bin (default)
python red.py --scan "D:\Backup" "E:\Archive"

# Permanent delete with depth limit
python red.py --scan "C:\Temp" --permanent --max-depth 3

# Export results to CSV
python red.py --scan "C:\Data" --dry-run --export results.csv

# All options
python red.py --help
```

#### CLI Options

| Option | Description |
|---|---|
| `--scan PATH [PATH...]` | Root directories to scan (required) |
| `--dry-run` | Simulate — list what would be deleted |
| `--permanent` | Delete permanently (default: Recycle Bin) |
| `--max-depth N` | Max recursion depth (0 = unlimited) |
| `--min-age N` | Only delete dirs older than N hours |
| `--no-empty-files` | Do NOT treat 0-byte files as empty |
| `--scan-hidden` | Include hidden and system folders |
| `--follow-symlinks` | Follow symbolic links |
| `--export FILE` | Save results to FILE (.csv or .txt) |
| `--quiet` | Only show summary output |

---

## Build executable (Windows)

```bash
pip install pyinstaller
pyinstaller red.spec
```

Output: `dist/RED-Python.exe` — a standalone Windows executable, no Python required.

---

## How it works

RED-Python uses a **bottom-up walk** (`os.walk(topdown=False)`) and tracks a set of "would-be-empty" directories:

1. A directory is considered **effectively empty** if:
   - All files in it match an ignore pattern, are 0-byte (if configured), or are hidden/system files
   - All subdirectories are already in the `would_be_empty` set

2. This correctly handles **nested chains**: a folder containing only empty subfolders is also detected as empty.

3. Before permanent deletion, any remaining ignorable files (e.g. `Thumbs.db`) inside the directory are removed first so `os.rmdir` can succeed.

---

## Configuration

Settings are stored at `~/.red_python/settings.json` and editable via the GUI (⚙ Config button).

Default ignored files:
```
desktop.ini, Thumbs.db, .DS_Store, ._*, .gitkeep,
__pycache__, .venv, .ipynb_checkpoints, .jekyll-cache
```

Default protected directories (never deleted):
```
C:\Windows\System32, C:\Windows\SysWOW64, C:\Windows\WinSxS,
$RECYCLE.BIN, System Volume Information
=======
# 🛡️ Coder Cerberus v0.3 — Guardián de Calidad del Código

[![Version](https://img.shields.io/badge/version-v0.3-blueviolet.svg?style=flat-square)](PLAN.md)
[![Audit](https://img.shields.io/badge/audit--12d-APPROVED-success.svg?style=flat-square)](scripts/run_security_audit_12d.py)
[![Tests](https://img.shields.io/badge/tests-386%20PASSED-success.svg?style=flat-square)](#)
[![MCP](https://img.shields.io/badge/MCP-compatible-brightgreen.svg?style=flat-square)](#integraciones)
[![Python](https://img.shields.io/badge/python-3.13+-yellow.svg?style=flat-square)](#)

---

## ¿Qué es Cerberus?

**Cerberus es el blindaje defensivo del código** — no orquesta agentes (eso hacen LangGraph, CrewAI), sino que **valida y protege** todo lo que otros sistemas generan.

Funciona como un guardián automático que revisa todo el código antes de cada cambio. Piensa en él como un revisor que:

- ✅ **Valida que el código funciona correctamente** — detecta errores silenciosos y codigo abandonado
- ✅ **Garantiza documentación y claridad** — obliga a explicar qué hace cada cosa
- ✅ **Previene costumbres malas** — bloquea patrones que causan problemas después
- ✅ **Mantiene todo sincronizado** — los cambios se propagan automáticamente a todos los sub-proyectos
- ✅ **Controla el gasto** — vigila cuántos tokens de IA se gastan en cada operación

Cerberus funciona automáticamente: cada vez que intentas guardar cambios, ejecuta 12 tipos de verificación (llamados "dominios") que aseguran que todo esté bien antes de permitir que el cambio se guarde.

---

## Lo que Cerberus valida

| Validación | ¿Qué revisa? |
|------------|-------------|
| **Integridad** | Que no haya archivos "fantasma" sin declarar en el sistema |
| **Completitud** | Que el código esté terminado (no tenga placeholders vacíos) |
| **Claridad** | Que el código sea legible y esté documentado |
| **Lógica simple** | Que la lógica sea directa (no demasiado enredada) |
| **Manejo de errores** | Que cada error se maneje con registro y contexto |
| **Higiene** | Que no haya código viejo, imports innecesarios o malas prácticas |
| **Seguridad** | Que no haya contraseñas, secretos ni operaciones peligrosas |
| **Tests funcionales** | Que los tests existan y pasen |
| **Tests auténticos** | Que los tests realmente prueben el código (no sean falsos) |
| **Tokenomics** | Que se controle el gasto de recursos (tokens de IA) |
| **Seguridad externa** | Que no haya librerías con vulnerabilidades conocidas |
| **Sincronización** | Que todos los sub-proyectos estén alineados |

---

## 🔗 Integraciones (Complementario a otros sistemas)

| Sistema | ¿Qué hace? | ¿Cómo se complementan? |
|---------|-----------|----------------------|
| **LangGraph** | Orquesta flujos de agentes | Cerberus valida el código que LangGraph genera |
| **CrewAI** | Coordina equipos de agentes | Cerberus audita las decisiones y código del equipo |
| **MCP** | Protocolo estándar para herramientas | Cerberus protege las conexiones MCP contra errores silenciosos |
| **Tu código actual** | Lo que escribes tú | Cerberus lo verifica automáticamente |

**La clave:** Cerberus no compite con estos sistemas, los **protege**. Mientras ellos orquestan y coordinan, Cerberus es el sistema inmunológico que evita que algo malo llegue a producción.

---

## Cómo se usa

### Verificación automática (diaria)
```bash
python scripts/run_security_audit_12d.py .
```
Esto ejecuta todas las verificaciones y muestra:
- ✅ **APPROVED** — todo está bien, puedes guardar tus cambios
- ❌ **REJECTED** — hay problemas, y te muestra dónde están para que los arregles

### Sincronizar sub-proyectos
```bash
python scripts/protocol_cli propagate --apply
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
```
Asegura que 17 sub-proyectos tengan los mismos estándares que el core.

---

<<<<<<< HEAD
## Inspired by

- [hxseven/Remove-Empty-Directories](https://github.com/hxseven/Remove-Empty-Directories) — original RED (C#)
- [alexwlchan/emptydir](https://github.com/alexwlchan/emptydir) — opinionated safe defaults
- [qarmin/czkawka](https://github.com/qarmin/czkawka) — multi-purpose disk cleaner
- [sztaroszta/VoidFinder](https://github.com/sztaroszta/VoidFinder) — Python/tkinter approach

---

## License

MIT
=======
## Estado actual

- **Versión:** v0.3 (Sprint 5-11 completados)
- **Tests:** 386 pasando, 0 fallando
- **Auditoría:** APPROVED (todas las 12 verificaciones pasan)
- **Cobertura de problemas:** 278 tipos de errores detectados y bloqueados
- **Sprints cerrados:** 0-11 (arquitectura, naming, documentación, auditoría final)

---

## Aprendizajes integrados (Sprints 5-11)

| Sprint | Aprendizaje | Implementado |
|--------|-------------|--------------|
| **5** | No permitir hallazgos que no causen bloqueo (WARN→BLOCK) | ✅ Recomendaciones solo con FAILs |
| **7** | Nombres de script claros y descriptivos | ✅ 23 scripts renombrados (verb_noun) |
| **8** | Estructura simple, sin carpetas innecesarias | ✅ Aplanamiento ejecutado |
| **9** | Golden Standard como única fuente de verdad | ✅ PI-015..018 formalizadas |
| **10** | Vigilancia de costos en tiempo real | ✅ 36 repos externos auditados |
| **11** | Auditoría completa y veredicto final | ✅ Guides refrescadas, plan viejo retirado |

---

## Documentación importante

- **[PLAN.md](PLAN.md)** — Qué sprints están hechos y cuáles quedan (para supervisión)
- **[Golden Standard repo](https://github.com/lcasarin-maker/VibeCoding_GoldenStandard)** — Fuente normativa externa separada del core de Cerberus
- **[HISTORIAL.md](HISTORIAL.md)** — El registro de todo lo que se ha hecho (auditoría histórica)
- **[scripts/run_security_audit_12d.py](scripts/run_security_audit_12d.py)** — El guardián (aquí está la inteligencia)

---

## Para empezar

1. **Clona este repo** y entra en la carpeta
2. **Ejecuta la auditoría inicial:**
   ```bash
   python scripts/run_security_audit_12d.py .
   ```
3. **Si ves APPROVED**, todo está listo. Si ves REJECTED, lee los mensajes — te dicen exactamente qué arreglar.
4. **Cada vez que hagas cambios**, el sistema los verifica automáticamente (mediante Git hooks).

---

## Preguntas frecuentes

**¿Cerberus bloquea mi trabajo?**
No. Solo bloquea cosas que después van a causar problemas (código incompleto, errores silenciosos, etc.). Es una protección, no una restricción.

**¿Qué pasa si una verificación es muy estricta?**
Se puede documentar como una excepción válida en [REGLAS.md](docs/REGLAS.md), pero con causa clara.

**¿Puedo deshabilitar Cerberus?**
Técnicamente sí, pero no se recomienda. Está diseñado para proteger el proyecto. Si algo no tiene sentido, mejor abre un issue para discutirlo.

---

---

## 🌍 Ecosistema & Compatibilidad

- ✅ Compatible con **MCP** (Model Context Protocol) — el estándar emergente para herramientas de IA
- ✅ Funciona con **LangGraph**, **CrewAI** y otros orquestadores
- ✅ Multi-plataforma: Windows, Linux, macOS
- ✅ Python 3.13+

---

**Última actualización:** 2026-05-31 (Sprints 5-11 finalizados)
**Mantenedor:** Luis Casarin
**Repositorio:** [lcasarin-maker/protocolo-agentes](https://github.com/lcasarin-maker/protocolo-agentes)

>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
