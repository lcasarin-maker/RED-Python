# PLAN.md — RED-Python v0.5 (CoderCerberus)

**Versión:** 0.5
**Protocolo:** CoderCerberus v0.5
**Mandato:** B10 (Checkpointing)
**Escrito:** 2026-06-02

---

## OPERACIÓN PRINCIPAL

Escanear y eliminar directorios vacíos o efectivamente vacíos:
1. Detectar directorios con solo archivos ignorables (0-byte, ocultos, sistema)
2. Propagar "vacío" hacia arriba en cadenas de carpetas anidadas
3. Proteger directorios críticos (Windows, ProgramFiles, etc.)
4. Opcionalmente eliminar o mover a Recycle Bin

Dual interface: GUI (Tkinter) + CLI (argparse)

External audit instruction: see [00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md](00%20audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md).

---

## PASOS NUMERADOS

1. **Bootstrap:** Cargar config.yaml con Settings (S4: Modularidad)
2. **Scan:** Scanner.scan() en thread daemon (thread-safe callbacks):
   - on_found → emitir ScanResult por cada carpeta vacía
   - on_log → logging de eventos
   - on_progress → actualizar UI con % completado
3. **Cleanup:** Cleaner.delete() elimina con undo tracking
4. **Undo:** Leer logs y reversar movimientos en orden inverso

---

## ANGRY PATHS — 3 FORMAS DE ROMPER (B3)

### 🔴 Path 1: Permission Denied on Protected Directory
**Escenario:** Scanner intenta acceder a C:\System32 o C:\ProgramFiles; OSError "Access Denied".
**Impacto:** Scanner crash; aplicación cuelga sin logging del error.
**Mitigación:** Envolucaer os.walk() en try/except; verificar is_protected() ANTES; skip con logger.info().

```python
# En Scanner.scan():
try:
    for root, dirs, files in os.walk(path, topdown=False):
        if is_protected(root):
            logger.info(f"SKIP protected: {root}")
            dirs.clear()  # No descender
            continue
except OSError as e:
    logger.error(f"Permission denied: {root}: {e}")
    self.on_log(f"[ERROR] {root}: {e}")
```

### 🔴 Path 2: Symbolic Link Loop (Infinite Recursion)
**Escenario:** Symlink points to parent dir; os.walk() descubre loop infinito sin --follow-symlinks.
**Impacto:** Stack overflow; OOM kill si memoria llena de calls recursivos.
**Mitigación:** Mantener conjunto de inodes visitados; detectar cycle con dev/ino; skip si ya visto.

```python
# En Scanner.__init__():
self._visited_inodes = set()

# En Scanner.scan():
try:
    stat_result = os.stat(root)
    inode = (stat_result.st_dev, stat_result.st_ino)
    if inode in self._visited_inodes:
        logger.warning(f"LOOP detected: {root}")
        dirs.clear()
        continue
    self._visited_inodes.add(inode)
except OSError as e:
    logger.error(f"Cannot stat {root}: {e}")
```

### 🔴 Path 3: Disk Full During Deletion
**Escenario:** Cleaner.delete() -> shutil.rmtree() falla mitad del camino; disco lleno.
**Impacto:** Árbol parcialmente eliminado; datos irrecuperables sin undo.
**Mitigación:** Verificar espacio ANTES de delete; usar undo log para rollback atomicity.

```python
# En Cleaner.delete():
import shutil
free_bytes = shutil.disk_usage(path).free
if free_bytes < 10 * 1024 * 1024:  # 10MB threshold
    logger.error(f"Insufficient disk space: {free_bytes / 1e9:.1f}GB free")
    raise IOError("Not enough space for safe deletion")

try:
    shutil.rmtree(path)
    logger.info(f"Deleted: {path}")
except Exception as e:
    logger.error(f"Deletion failed: {path}: {e}")
    # Trigger undo mechanism
    self._undo_last_deletion()
```

---

## VALIDACIÓN PRE-CAMBIO

- ✅ S4: Modularidad (Scanner, Cleaner, App separados)
- ✅ S5: Anti-Slop (tests validan importación sin error)
- ✅ S9: Logging (logger configurado en core.py)
- ✅ B10: Checkpointing (PLAN.md presente)
- ✅ B11: Validación Deps (test suite: CLI + GUI smoke tests)
- ✅ B3: Angry Paths (documentadas 3 formas de romper)

---

## PRÓXIMOS SPRINTS

1. **Sprint 1:** Implementar Path 1 (Permission Denied handling)
2. **Sprint 2:** Implementar Path 2 (Symlink loop detection)
3. **Sprint 3:** Implementar Path 3 (Disk full detection + rollback)
4. **Sprint 4:** Integración tests (end-to-end con directorios reales)

---

**Status:** ✅ PLAN APROBADO PARA EJECUCIÓN
**Auditor:** Claude (CoderCerberus v0.5)
**Fecha:** 2026-06-02
