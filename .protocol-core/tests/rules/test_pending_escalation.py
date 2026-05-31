"""Tests for the R-PENDING-ESCALATION rule."""
# tests/rules/test_pending_escalation.py
"""Tests for the R‑PENDING‑ESCALATION rule.

The rule fails when there are open tasks in ``pending_tasks``.
"""

from protocol_engine.rules_engine import validate

def test_no_pending_tasks_pass():
    """When there are no pending tasks the rule should not report an error."""
    context = {"pending_tasks": []}
    errors = validate(context)
    assert not any("R-PENDING-ESCALATION" in e for e in errors)

def test_pending_tasks_fail():
    """When an open task exists the rule must report an error."""
    context = {"pending_tasks": [{"id": "t1", "status": "open"}]}
    errors = validate(context)
    assert any("R-PENDING-ESCALATION" in e for e in errors)
