"""
Tests for security and sandbox enforcement of Cerberus rules engine.
Verifies that Arbitrary Code Execution (ACE) vectors are successfully mitigated.

After P6.1: inline expression execution removed. Unknown check names → KeyError caught as
"exception during check" in validate(). Registered SAFE_CHECKS work normally.
"""

from cerberus.rules_engine import validate, _RULES


def test_dispatch_rejects_unknown_check_with_double_underscores():
    """P6.1: __import__ string not in SAFE_CHECKS → caught as 'exception during check'."""
    malicious_rule = {
        "id": "R-TEST-MALICIOUS-EXEC",
        "description": "Exploit attempt",
        "check": "__import__('os').system('whoami')",
    }
    _RULES.append(malicious_rule)
    try:
        errors = validate({})
        has_error = any(
            "R-TEST-MALICIOUS-EXEC" in err and "exception during check" in err
            for err in errors
        )
        assert has_error, f"Expected 'exception during check' error, got: {errors}"
    finally:
        _RULES.pop()


def test_dispatch_rejects_unauthorized_builtin_string():
    """P6.1: open('/etc/passwd') string not in SAFE_CHECKS → caught as 'exception during check'."""
    malicious_rule = {
        "id": "R-TEST-UNAUTHORIZED-BUILTIN",
        "description": "Access unauthorized builtin",
        "check": "open('/etc/passwd')",
    }
    _RULES.append(malicious_rule)
    try:
        errors = validate({})
        has_error = any(
            "R-TEST-UNAUTHORIZED-BUILTIN" in err and "exception during check" in err
            for err in errors
        )
        assert has_error, f"Expected 'exception during check' error, got: {errors}"
    finally:
        _RULES.pop()


def test_registered_safe_check_passes_and_fails_correctly():
    """P6.1: Registered SAFE_CHECKS function works as expected (replaces whitelisted-builtins test)."""
    safe_rule = {
        "id": "R-TEST-REGISTERED",
        "description": "pending tasks must be empty",
        "check": "pending_tasks_empty",
    }
    _RULES.append(safe_rule)
    try:
        # Case 1: check passes — no error for this rule
        errors = validate({"pending_tasks": []})
        assert not any("R-TEST-REGISTERED" in e for e in errors)
        # Case 2: check fails — error is reported
        errors = validate({"pending_tasks": ["blocked-task"]})
        assert any("R-TEST-REGISTERED" in e for e in errors)
    finally:
        _RULES.pop()
