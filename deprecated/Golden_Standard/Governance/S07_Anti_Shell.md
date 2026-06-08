# S7: Anti-Shell — No Bash Hacks for File Operations

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_4/M1 (Prohibitions)
**Severity:** 🟠 HIGH

---

## Definition

**PROHIBITED:** `echo`, `sed`, `awk`, `Add-Content`, `Set-Content` for creating/modifying files.

Use Edit/Write tools instead. Shell operations hide changes from atomic VC tracking.

---

## Why

Shell operations are opaque. Use atomic file tools for auditability.

---

## Prohibited Patterns

```bash
# ❌ NO
echo "content" > file.txt
sed -i 's/old/new/g' file.txt
Add-Content file.txt "line"

# ✅ YES
# Use Edit or Write tool instead
```

---

## Exceptions

- `git` commands (version control)
- Package managers (`npm`, `pip`)
- Build commands
- Data pipelines (awk for ETL is fine)

---

## Related

- **S6:** Large File Safety (edits must be atomic)
- **S8:** Debt Tax (prevents accumulation)
