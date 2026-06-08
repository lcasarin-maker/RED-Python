# S15: Localization — Single Source of Truth Location

**Source:** GLOBAL_LEARNING.md (2026-05-20 Gemini incident)
**Authority:** LEVEL_2/M1 (Fundamentals)
**Severity:** 🔴 CRITICAL

---

## Definition

**The ONLY authoritative location for CoderCerberus protocol is:**
```
D:\AI\Cerberus\
```

No `.protocolo/` folders, no alternate shadow directories, no "copies" elsewhere.

Any other location is a ZOMBIE infection and must be deleted immediately.

---

## Why

2026-05-20 incident: Gemini created `.protocolo/` folder, worked on obsolete v4.0 rules, created redundant bindings, lost location awareness.

Single location = single source of truth = no version drift.

---

## Rules

1. **Verify at session start:** Are we in `D:\AI\Cerberus/`?
2. **If not:** STOP. Delete shadow directory. Report.
3. **Only location:** Protocol lives here, nowhere else
4. **No copies:** Symlinks to rules/ are OK (v0.5 design); copies are not

---

## Exceptions

None. Location is non-negotiable.

---

## Related

- **S17:** Version Sync (version = location-specific)
- **LEVEL_2/M1:** Startup ritual (verify location first)

