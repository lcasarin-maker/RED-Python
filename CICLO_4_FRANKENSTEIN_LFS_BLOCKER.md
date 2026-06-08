# Ciclo 4 — Frankenstein LFS Blocker (P1-2)

**Status:** ⚠️ BLOQUEADO — Requiere acción manual avanzada  
**Fecha:** 2026-06-02  
**Root Cause:** Archivo 129.57MB en historial git previo a LFS setup

---

## Problema

**Archivo:**
```
implementacion/fase-g/portal/node_modules/@next/swc-win32-x64-msvc/next-swc.win32-x64-msvc.node
Tamaño: 129.57 MB
Límite GitHub: 100.00 MB
```

**Razón del Bloqueo:**
- El archivo se commiteó ANTES de agregar .gitignore
- Está en el historial de commits previos
- Git LFS setup posterior no lo retractua automáticamente
- Cada push intenta enviar el archivo completo (rechazado por GitHub)

**Error:**
```
remote: error: GH001: Large files detected.
  File ... exceeds GitHub's file size limit of 100 MB
error: failed to push some refs
```

---

## Soluciones Disponibles

### ✅ Opción 1: BFG Repo-Cleaner (RECOMENDADA)

**Ventaja:** Rápida, preserva histórico relativo  
**Desventaja:** Destructiva (reescribe commits)

```bash
# Instalar BFG
brew install bfg  # o descargar de https://rtyley.github.io/bfg-repo-cleaner/

# Limpiar repositorio
cd /d/AI/Frankenstein
git reflog expire --expire=now --all && git gc --prune=now
bfg --strip-blobs-bigger-than 100M
git reflog expire --expire=now --all && git gc --prune=now

# Force push
git push -u origin master --force --no-verify
```

### ⚠️ Opción 2: git filter-branch (Manual)

```bash
git filter-branch --tree-filter 'rm -rf implementacion/fase-g/portal/node_modules/@next/swc-win32-x64-msvc/next-swc.win32-x64-msvc.node' -- --all
git push -u origin master --force --no-verify
```

### ❌ Opción 3: Pagar el coste (No hacer nada)

- Mantener Frankenstein como local-only (sin push a GitHub)
- O crear fork privado con GitHub Enterprise LFS
- No recomendado

---

## Implementación para Ciclo 4.5

**Timeline:**
```
Ciclo 4.5 — DT-F1 (Future Sprint):
1. Backup remoto (fork/archive)
2. Ejecutar BFG cleanup
3. Force push
4. Verificar integridad
5. Documentar post-mortem
```

**Effort:** 30 minutos (con validación)  
**Risk:** MEDIA (force push, reescritura histórica)

---

## Decision Point

**¿Qué hacer ahora?**

- **A** Ignorar por ahora (Frankenstein queda local-only) — Proceder Ciclo 4
- **B** Ejecutar BFG ahora (destructivo, requiere coordinación)
- **C** Agendar para Ciclo 4.5 con owner de Frankenstein

---

**Recomendación:** Opción A (Ciclo 4) → Opción C (Ciclo 4.5)

*Blocker Analysis: 2026-06-02 | CoderCerberus v0.5*
