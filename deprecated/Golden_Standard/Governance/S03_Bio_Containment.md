# S3: Bio-Containment — Security at I/O Boundaries

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_4/M1 (Prohibitions)
**Severity:** 🔴 CRITICAL

---

## Definition

Assume all AI is an "Incompetent Intern" that will inject vulnerabilities. Audit every I/O boundary line-by-line.

**Zero variables unsan itized in APIs, databases, or user-facing functions.**

---

## Why

Injection attacks (SQL, XSS, command) happen when untrusted input flows to execution contexts unchecked.

---

## Rules

1. **No generic `any` type** in I/O functions
2. **Whitelist validation at EVERY boundary:**
   - User input → Present / Type / Length / Format / Values / Encoding
3. **Trust internal code only** — don't validate between functions in same module
4. **4-element error handling:**
   - LOG (error + context)
   - USER (readable message)
   - STATE (rollback guarantee)
   - ACTION (retry vs fail vs degrade)
5. **Secrets in .secrets/**, not in code or .env

---

## Exceptions

None. Security is non-negotiable.

---

## Related

- **S14:** Zero-Trust (double-key rule)
- **S4:** Modularity (schemas at boundaries)
- **S20:** Error logs ( 4-element requirement)
