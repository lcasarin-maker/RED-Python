# S8: Debt Tax — 50-Line Per Turn Maximum

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_4/M1 (Prohibitions)
**Severity:** 🟠 HIGH

---

## Definition

Max 50 lines of new/modified code per turn. After turn, run Simplicity Pass (refactor, remove redundancy, verify).

Prevents debt accumulation. Forces clarity.

---

## Why

Long turns hide bugs. 50 lines is the limit for human + AI code review capacity.

---

## Rules

1. **Count:** All new + modified lines (not just new files)
2. **Limit:** 50 lines per turn MAXIMUM
3. **After:** Simplicity Pass required (clean, dedupe, verify)
4. **Exception:** Justified + approved

---

## Simplicity Pass Checklist

- [ ] Dead code removed?
- [ ] Redundancy eliminated?
- [ ] Variable names clear?
- [ ] Comments justify WHY, not WHAT?
- [ ] All tests passing?

---

## Enforcement

- **PreCommit:** Blocks >50 lines without justification
- **S5:** Anti-Slop (debt manifests as warnings)

---

## Related

- **S6:** Large File Safety (atomic edits)
- **S5:** Anti-Slop (debt = warnings)
