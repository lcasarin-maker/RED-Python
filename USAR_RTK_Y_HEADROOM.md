# Usar RTK y Headroom — Guía Rápida

## RTK (Rust Token Killer)

**Qué hace:** Comprime output de comandos CLI (−60% a −90%)

### Uso básico

En PowerShell, **antepón `rtk`** a cualquier comando:

```powershell
# SIN RTK (mucho ruido, muchos tokens)
git log --oneline

# CON RTK (limpio, pocos tokens)
rtk git log --oneline
```

### Comandos comunes con RTK

```powershell
rtk git status          # Ver cambios comprimidos
rtk git log --oneline   # Historial comprimido
rtk npm list            # Dependencias comprimidas
rtk ls -la              # Listado comprimido
rtk cargo test          # Tests comprimidos
```

**Ahorro típico:** 200 tokens → 20 tokens (−90%)

---

## Headroom (Contexto)

**Qué hace:** Comprime logs y contexto automáticamente

### Cuándo se activa

- Cuando subas logs a Claude Code
- Cuando uses RAG intensivo
- Automáticamente si detecta contexto > 1000 tokens

### Cómo usarlo

**Opción 1: Manual (desde PowerShell)**

```powershell
headroom compress "tu_archivo_log.txt"
```

**Opción 2: Automático (en Claude Code)**

Si pasas un log grande a Claude Code, Headroom lo comprime automáticamente.

---

## Combinación Óptima

**El flujo ideal:**

1. **En Terminal:** Usa `rtk` para comandos
   ```powershell
   rtk git status
   rtk npm list
   ```

2. **En Claude Code:** Pega output comprimido
   - Claude Code detecta y comprime más si es necesario

3. **Resultado:** −50% a −70% tokens total

---

## Ejemplos reales

### Antes (sin RTK)
```
$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   src/file1.py
        modified:   src/file2.py
        deleted:    src/old_file.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .DS_Store
        __pycache__/

=== 180+ tokens ===
```

### Después (con RTK)
```
$ rtk git status
✓ main (up to date)
Modified: src/file1.py, src/file2.py (−1: src/old_file.py)
Untracked: .DS_Store, __pycache__/

=== 20 tokens ===
```

---

## Resumen

| Herramienta | Comando | Ahorro | Cuándo |
|---|---|---|---|
| **RTK** | `rtk [comando]` | −60-90% | Siempre en Terminal |
| **Headroom** | Automático | −40-87% | Logs grandes, RAG |
| **PROMPTS_RAPIDOS_v3** | Copiar/pegar | −25% | Cada sesión |
| **TOTAL** | Todo junto | **−50-70%** | Ahora |

---

**Comienza ahora: usa `rtk` en la próxima sesión de PowerShell**
