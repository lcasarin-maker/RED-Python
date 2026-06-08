# SPEC_REFACTORS — Template para Code Refactors (5-10 minutos)

**Cómo usar:** Rellena este template con tu refactor, ejecuta:
```bash
python scripts/spec_executor.py SPEC_REFACTORS.md
```

---

## Refactor: [Nombre del refactor]

**Descripción (2-3 líneas):**
[Por qué refactorizar y qué mejora]

---

### Consolidación (qué mezclar)

**Files to merge/consolidate:**
```
Archivo 1: [archivo1.py] — [qué contiene]
Archivo 2: [archivo2.py] — [qué contiene]
Result: [archivo_consolidado.py] — [nueva estructura]
```

**Ejemplo (Config consolidation):**
```
Archivo 1: src/config/settings.py — Static settings (DB URL, API keys)
Archivo 2: src/config/environment.py — Environment-specific overrides
Archivo 3: src/utils/constants.py — Hardcoded constants (duplicates #1)
Result: src/config.py — Single source of truth for all config
```

---

### Cambios Qué hacemos

- [ ] Change 1: Description
- [ ] Change 2: Description
- [ ] Change 3: Description

**Ejemplo:**
- [ ] Merge settings.py + environment.py → single config.py
- [ ] Remove duplicate constants from utils/constants.py
- [ ] Update all imports (12 files affected)
- [ ] Maintain backward compatibility (re-export old names if needed)
- [ ] Add config validation (ensure all required keys present)
- [ ] Add config reload on SIGHUP (no server restart needed)

---

### Archivos afectados (impact analysis)

```
Files modified: [count]
Files deleted: [count]
Files created: [count]

Risk level: [LOW/MEDIUM/HIGH]
```

**Ejemplo:**
```
Files modified: 12 (all imports updated)
Files deleted: 2 (old config files removed)
Files created: 1 (new consolidated config.py)

Risk level: MEDIUM (import changes across codebase)
```

---

### Restricciones (qué respetar)

- [Constraint 1]
- [Constraint 2]

**Ejemplo:**
- Must maintain backward compatibility (old import paths still work via re-export)
- Cannot change public API signatures
- No new dependencies
- Must work with existing build pipeline

---

### Aceptación (Qué prueba que funciona)

- [x] Acceptance 1: Description
- [x] Acceptance 2: Description

**Ejemplo:**
- [x] All imports updated (no broken references)
- [x] All 18 existing tests pass (zero regressions)
- [x] New test: test_config_loading() covers edge cases
- [x] No duplicate code in codebase (verified by scan)
- [x] Build succeeds with new structure
- [x] Backward compatibility: old imports still work
- [x] Code coverage maintained (>85%)

---

### Migration Path (how to upgrade)

```
[Step-by-step for users to upgrade]
```

**Ejemplo:**
```
1. Update to new version: pip install --upgrade app==2.0
2. Old imports still work: from src.config.settings import DEBUG (re-exported)
3. Recommended: use new imports: from src.config import DEBUG
4. Deprecation warning if using old imports (2 major versions)
```

---

### Performance Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Import time | XXms | XXms | +/-X% |
| Memory usage | XXMb | XXMb | +/-X% |
| Startup time | XXms | XXms | +/-X% |

**Ejemplo:**
```
| Import time | 45ms | 22ms | -51% |
| Memory | 12Mb | 9Mb | -25% |
| Startup | 2300ms | 2100ms | -9% |
```

---

## NOTAS

- **Tiempo en SPEC:** 5-10 minutos
- **Tiempo AI ejecuta:** 10-15 minutos (refactor + tests + verify)
- **Total ahorro:** 60% (vs manual 30-60 min)

---

## Ejemplo Real: Settings Consolidation Refactor

```markdown
## Refactor: Consolidate configuration files

Descripción: We have 3 config files doing overlapping jobs. Need single source of truth for all settings to reduce duplication and fix sync issues.

### Consolidación
```
Archivo 1: src/config/settings.py (200 líneas)
  - DB_URL, API_KEY, DEBUG, ALLOWED_HOSTS

Archivo 2: src/config/environment.py (80 líneas)
  - ENV (production/development/test)
  - Environment-specific overrides (hard to maintain)

Archivo 3: src/utils/constants.py (60 líneas)
  - Duplicate definitions (TIMEOUT, MAX_RETRIES, etc)
  - Should be in config, not utils

Result: src/config.py (single file, ~200 líneas)
  - Single source of truth
  - Environment-aware defaults
  - Validation on load
```

### Cambios
- [ ] Create new src/config.py with consolidated schema
- [ ] Migrate all settings from settings.py + environment.py
- [ ] Remove duplicate constants from utils/constants.py
- [ ] Update 12 files to use new import path
- [ ] Add backward compatibility re-exports (from src.config import DEBUG)
- [ ] Add config validation: ensure REQUIRED keys present on startup
- [ ] Add config reload: SIGHUP signal handler

### Archivos afectados
```
Files modified: 12
  - auth/routes.py
  - auth/models.py
  - api/endpoints.py
  - utils/decorators.py
  - ... (8 more)

Files deleted: 2
  - src/config/settings.py
  - src/config/environment.py

Files created: 1
  - src/config.py

Risk: MEDIUM (widespread imports)
```

### Restricciones
- Maintain backward compatibility (old imports still work)
- Cannot add new dependencies
- Must not change public API signatures
- Production config must not leak into git

### Aceptación
- [x] All 18 existing tests pass
- [x] New test: test_config_validation() added
- [x] New test: test_config_reload() added
- [x] No duplicate code found (verified by tool)
- [x] Build succeeds with new imports
- [x] Linter passes (no issues)
- [x] Performance: same or faster
- [x] Backward compatibility verified

### Migration
```
1. Update code (done by refactor)
2. Old imports still work:
   from src.config.settings import DEBUG  # Still works!
3. Recommended:
   from src.config import DEBUG
4. Deprecation warning appears after 2 versions
```

### Performance
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Config load | 45ms | 12ms | -73% |
| Memory | 8Mb | 4Mb | -50% |
| Imports | 120ms | 80ms | -33% |
```

---

## Tips

1. **Specific files** → AI knows exactly what to touch
2. **Impact analysis** → no surprise side effects
3. **Migration path** → users know how to upgrade
4. **Performance metrics** → can measure improvement
