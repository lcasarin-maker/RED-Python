# cerberus/rules_engine.py
"""Central rule engine for Cerberus.
Loads all YAML rule definitions from ``cerberus/rules/`` and provides a simple
validation API used by ``scripts/run_audit_loop.py``.

P6.1 — eval() REMOVED. Rule checks must use named functions from SAFE_CHECKS.
YAML files use: check: "function_name"  (not inline expressions).
To add a new check: add to SAFE_CHECKS below, then reference by name in YAML.
"""
import pathlib
import yaml
from typing import List, Dict, Any, Callable

RULES_DIR = pathlib.Path(__file__).parent / "rules"

# ── Safe check registry — the ONLY allowed string-based checks ────────────────
# Each function receives the validation context dict and returns bool.
# Adding a check here is the approved change process (P6.1 / VC-111 equivalent).
SAFE_CHECKS: Dict[str, Callable[[Dict[str, Any]], bool]] = {
    "pending_tasks_empty": lambda ctx: len(ctx.get("pending_tasks", [])) == 0,
    "all_rules_have_severity": lambda ctx: all(
        "severity" in rule for rule in ctx.get("rules", [])
    ),
    "all_rules_have_tests": lambda ctx: all(
        rule.get("id") in ctx.get("test_rule_ids", [])
        for rule in ctx.get("rules", [])
    ),
}


def _load_rules() -> List[Dict[str, Any]]:
    rules = []
    for file in RULES_DIR.glob("*.yaml"):
        with open(file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                rules.extend(data)
            else:
                rules.append(data)
    # Validate at load time: reject unknown string checks immediately.
    for rule in rules:
        check = rule.get("check")
        if isinstance(check, str) and check not in SAFE_CHECKS:
            raise ValueError(
                f"Rule '{rule.get('id', 'unknown')}' uses unknown check '{check}'. "
                "Add a named function to SAFE_CHECKS in rules_engine.py — "
                "inline expressions are forbidden (P6.1 / ASI-02)."
            )
    return rules


_RULES = _load_rules()


def validate(context: Dict[str, Any]) -> List[str]:
    """Validate the given *context* against all loaded rules.
    Returns a list of error messages (empty if all pass)."""
    errors = []
    for rule in _RULES:
        try:
            check = rule.get("check")
            if callable(check):
                passed = check(context)
            elif isinstance(check, str):
                passed = SAFE_CHECKS[check](context)
            else:
                errors.append(f"{rule.get('id','unknown')}: invalid check type {type(check)}")
                continue
            if not passed:
                errors.append(rule.get("id", "unknown") + ": " + rule.get("description", ""))
        except Exception as e:
            errors.append(f"{rule.get('id','unknown')}: exception during check – {e}")
    return errors


__all__ = ["validate"]
