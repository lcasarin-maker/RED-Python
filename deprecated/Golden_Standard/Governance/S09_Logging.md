# S9: Structured Logging — Mandatory for All New Code

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_1/M2 (Usability)
**Severity:** 🔴 CRITICAL

---

## Definition

Every new code function MUST have structured logging: `logger.info(args, state)` at entry/exit and error points.

No `print()`, no debug messages without context.

---

## Why

Logs are the ONLY proof of execution. Unstructured logs are useless for debugging.

---

## Pattern

```python
logger.info(f"process_file START: {filename}, state={state}")
try:
    result = process(filename)
    logger.info(f"process_file SUCCESS: result={result}")
    return result
except Exception as e:
    logger.error(f"process_file FAIL: {e}, state={state}")
    raise
```

---

## Structured Format

- **Entry:** Function name + INPUT args
- **State:** Current system state
- **Exit:** Result or error + context
- **Errors:** Full traceback + recovery action

---

## Enforcement

- **Code review:** Manual inspection
- **S1:** Audit may catch missing logs

---

## Related

- **S20:** Structured Error Logs (4-element requirement)
- **LEVEL_1/M2:** Usability (logging = debuggability)
