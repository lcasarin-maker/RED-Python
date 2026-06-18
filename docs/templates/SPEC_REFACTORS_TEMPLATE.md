# SPEC_REFACTORS — Code Refactor Template (5-10 minutes)

**How to use:** Fill in this template with your refactor, then run:
```bash
python scripts/spec_executor.py SPEC_REFACTORS.md
```

---

## Refactor: [Refactor name]

**Description (2-3 lines):**
[Why the refactor is needed and what it improves]

---

### Consolidation (what to merge)

**Files to merge/consolidate:**
```
File 1: [file1.py] - [what it contains]
File 2: [file2.py] - [what it contains]
Result: [consolidated_file.py] - [new structure]
```

**Example (Config consolidation):**
```
Archivo 1: src/config/settings.py — Static settings (DB URL, API keys)
Archivo 2: src/config/environment.py — Environment-specific overrides
Archivo 3: src/utils/constants.py — Hardcoded constants (duplicates #1)
Result: src/config.py — Single source of truth for all config
```

---

### Changes to make

- [ ] Change 1: Description
- [ ] Change 2: Description
- [ ] Change 3: Description

**Example:**
- [ ] Merge settings.py + environment.py → single config.py
- [ ] Remove duplicate constants from utils/constants.py
- [ ] Update all imports (12 files affected)
- [ ] Maintain backward compatibility (re-export old names if needed)
- [ ] Add config validation (ensure all required keys present)
- [ ] Add config reload on SIGHUP (no server restart needed)

---

### Affected files (impact analysis)

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

### Constraints (what to respect)

- [Constraint 1]
- [Constraint 2]

**Ejemplo:**
- Must maintain backward compatibility (old import paths still work via re-export)
- Cannot change public API signatures
- No new dependencies
- Must work with existing build pipeline

---

### Acceptance (what proves it works)

- [x] Acceptance 1: Description
- [x] Acceptance 2: Description

**Example:**
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

## Notes

- **Time in SPEC:** 5-10 minutes
- **AI execution time:** 10-15 minutes (refactor + tests + verify)
- **Total savings:** 60% (vs manual 30-60 min)

---

## Real Example: Settings Consolidation Refactor

```markdown
## Refactor: Consolidate configuration files

Description: We have 3 config files doing overlapping jobs. Need a single source of truth for all settings to reduce duplication and fix sync issues.

### Consolidation
```
File 1: src/config/settings.py (200 lines)
  - DB_URL, API_KEY, DEBUG, ALLOWED_HOSTS

File 2: src/config/environment.py (80 lines)
  - ENV (production/development/test)
  - Environment-specific overrides (hard to maintain)

File 3: src/utils/constants.py (60 lines)
  - Duplicate definitions (TIMEOUT, MAX_RETRIES, etc)
  - Should be in config, not utils

Result: src/config.py (single file, ~200 lines)
  - Single source of truth
  - Environment-aware defaults
  - Validation on load
```

### Changes
- [ ] Create new src/config.py with consolidated schema
- [ ] Migrate all settings from settings.py + environment.py
- [ ] Remove duplicate constants from utils/constants.py
- [ ] Update 12 files to use new import path
- [ ] Add backward compatibility re-exports (from src.config import DEBUG)
- [ ] Add config validation: ensure REQUIRED keys present on startup
- [ ] Add config reload: SIGHUP signal handler

### Affected files
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

### Constraints
- Maintain backward compatibility (old imports still work)
- Cannot add new dependencies
- Must not change public API signatures
- Production config must not leak into git

### Acceptance
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
