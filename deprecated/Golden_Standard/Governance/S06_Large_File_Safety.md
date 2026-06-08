# S6: Large File Safety — Edit Guards

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_4/M1 (Prohibitions)
**Severity:** 🟠 HIGH

---

## Definition

Edit tool: MAX 50 lines per operation. Write tool: PROHIBITED for >200 lines.

Large changes require multiple atomic edits or justification + approval.

---

## Why

Large edits hide mistakes. Atomic changes enable review and rollback.

---

## Rules

1. **Edit tool:** <50 lines per call
2. **Write tool:** Only for new files or complete rewrites
3. **If >200 lines:** Ask before proceeding
4. **Multiple edits:** Preferred for large changes

---

## Enforcement

- **PreCommit:** Blocks large atomic changes
- **Agent discipline:** S8 (Debt Tax enforces smaller changes)

---

## Related

- **S8:** Debt Tax (50-line limit philosophy)
- **S7:** Anti-Shell (prevents large shell operations)
