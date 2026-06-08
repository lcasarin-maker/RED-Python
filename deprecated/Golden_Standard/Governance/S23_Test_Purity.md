# S23: Test Purity — No Theater in Tests

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_1/M3 (Angry_Path) + LEVEL_3/M1 (Regression_Suite)
**Severity:** 🔴 CRITICAL

---

## Definition

Tests are not theater. An assertion that always passes is a lie.

Every test must be able to FAIL on real breaks. No tautologies, no mocks that verify themselves, no hardcoded expectations.

---

## Why

Tests are the ONLY proof that code works. Fake tests give false confidence and hide regressions.

---

## Prohibited

```python
# ❌ Tautology — assertion is meaningless
assert True

# ❌ Stub oracle — mock returns what test expects
mock.process.return_value = expected_result
assert process() == expected_result

# ❌ Always passes — no real condition tested
if 1 == 1:
    assert "success" == "success"
```

---

## Correct Pattern

```python
# ✅ Real assertion — can fail
result = process(test_data)
assert result.status == "COMPLETE"
assert result.count > 0

# ✅ Real oracle — external validation
expected = compute_expected(test_data)
actual = process(test_data)
assert actual == expected

# ✅ Angry path — test failure modes
with pytest.raises(ValueError):
    process(invalid_data)
```

---

## Angry Path Requirement

For every code path, test:
1. **Happy path:** Normal input → success
2. **Null/empty:** No input → error
3. **Type mismatch:** Wrong type → error
4. **Boundary:** Edge values → correct behavior
5. **Failure modes:** When dependencies fail → graceful degradation

---

## Enforcement

- **Code review:** Manual inspection
- **S1:** Audit catches if tests don't provide real validation

---

## Related

- **S22:** Code Purity (code must be real)
- **LEVEL_1/M3:** Angry Path (adversarial testing)
- **LEVEL_3/M2:** Angry Path Testing (structured)
