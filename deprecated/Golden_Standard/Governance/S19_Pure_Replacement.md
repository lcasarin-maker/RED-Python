# S19: Pure Replacement — Anti-Zombie-Compat

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_1/M1 (INTEGRIDAD TOTAL) + VC-118
**Severity:** 🔴 CRITICAL

---

## Definition

**REEMPLAZAR = ELIMINAR + CREAR (no bridges, no shims, no fallbacks)**

When replacing component X with Y:
- `git rm X` (delete from VCS)
- Y must NOT import from X
- Copy code if needed, don't reference
- Tests point ONLY to Y
- No backward-compat comments

---

## Why

Mixed paths (old + new) are unverifiable. Code integrity requires single source of truth.

---

## Prohibited

- `from OLD import X`
- `(new.exists() or old.exists())`
- Dual test sentinels
- Comments: "# deprecated", "# for now"

---

## Correct Pattern

```bash
git rm OLD
# Copy code from OLD to NEW if needed
git add NEW
git commit "Replace OLD with NEW (pure replacement)"
```

---

## Enforcement

- **PreCommit:** Detects import patterns, blocks
- **S21:** Double-key rule (ask first)

---

## Related

- **VC-118:** Zombie Compatibility Theater (anti-pattern definition)
- **LEVEL_1/M1:** INTEGRIDAD TOTAL (why purity matters)
- **LEVEL_4/M1:** Prohibitions (no shims allowed)
