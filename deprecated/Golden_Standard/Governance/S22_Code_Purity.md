# S22: Code Purity — No Stubs in Production

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_1/M1 (INTEGRIDAD TOTAL)
**Severity:** 🔴 CRITICAL

---

## Definition

No production method can return `True`, `0`, `"success"`, or similar unconditionally without executing real logic.

A stub that reports success without verifying anything is a lie registered in the evidence trail.

---

## Why

Code integrity requires that every statement either:
1. Does real work, OR
2. Fails fast if conditions aren't met

Placeholder logic masquerading as real logic corrupts the evidence trail.

---

## Prohibited

```python
def process_file():
    return True  # ❌ NO

def validate_user():
    return "success"  # ❌ NO

def save_data():
    return 0  # ❌ NO (exit code 0 = success)
```

---

## Correct Pattern

```python
def process_file():
    # Real logic here
    if not file.exists():
        raise FileNotFoundError()
    # ... actual processing ...
    return True  # ✅ After real work

def validate_user():
    # Validation logic
    if not user.valid():
        raise ValueError("Invalid user")
    # ... actual validation ...
    return "success"  # ✅ After validation
```

---

## Enforcement

- **Code review:** Manual inspection (no automated check)
- **S1:** Audit catches if stub blocks validation

---

## Related

- **S23:** Test Purity (tests must also be real)
- **LEVEL_1/M1:** INTEGRIDAD TOTAL (code must be verifiable)
