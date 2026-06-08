# S20: Structured Error Logs — 4-Element Mandate

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_4/M3 (Risk_Models)
**Severity:** 🟠 HIGH

---

## Definition

Every error handler MUST include 4 elements:

1. **LOG** — Error + context (logger.error)
2. **USER** — Readable message (what user sees)
3. **STATE** — Rollback guarantee (what state is safe)
4. **ACTION** — Recovery (retry, fail, degrade)

---

## Why

Errors without these 4 elements are impossible to debug and dangerous to recover from.

---

## Pattern

```python
try:
    result = process(data)
except FileNotFoundError as e:
    # 1. LOG
    logger.error(f"File missing: {e}, data={data}")
    
    # 2. USER
    user_message = "File not found. Please check path and retry."
    
    # 3. STATE
    # Database rolled back automatically, state is clean
    
    # 4. ACTION
    raise FileNotFoundError(user_message) from e
```

---

## Checklist per Error Handler

- [ ] logger.error called with error + context?
- [ ] User-facing message clear and actionable?
- [ ] State rollback guaranteed?
- [ ] Recovery action specified (retry, fail, degrade)?

---

## Enforcement

- **Code review:** Manual inspection
- **S1:** Audit checks completeness
- **S3:** Bio-Containment (validation at I/O)

---

## Related

- **S3:** Bio-Containment (where validation fails)
- **S9:** Logging (how to log structured)
- **LEVEL_4/M3:** Risk Models (error handling strategy)
