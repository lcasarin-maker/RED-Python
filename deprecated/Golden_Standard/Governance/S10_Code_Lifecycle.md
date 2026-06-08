# S10: Code Lifecycle — Deprecated/ as Archive

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_2/M1 (Fundamentals)
**Severity:** 🟡 MEDIUM

---

## Definition

Dead code moves to `deprecated/` with archival date and reason.

Never leave commented-out code or orphaned files in active directories.

---

## Why

Active code must be clean. Deprecated patterns must be discoverable for learning.

---

## Rules

1. **Dead code** → Move to `deprecated/YYYY-MM-DD_reason/`
2. **Keep structure** → Copy directory hierarchy
3. **Add README** → Why it was deprecated, when to revisit
4. **Link from active** → DEPRECATION_NOTICE.md pointing to archive

---

## Pattern

```
deprecated/
  2026-06-02_old_auth_v1/
    README.md (reason, date, alternative)
    old_auth.py
    tests/
```

Then in active code:
```python
# DEPRECATED: See deprecated/2026-06-02_old_auth_v1/README.md
# Use: new_auth.py instead
```

---

## Enforcement

- **Manual discipline:** Part of cleanup
- **S5:** Anti-Slop (dead code = warnings/bloat)

---

## Related

- **S5:** Anti-Slop (no warnings = no dead code)
- **S19:** Pure Replacement (no dual paths)
