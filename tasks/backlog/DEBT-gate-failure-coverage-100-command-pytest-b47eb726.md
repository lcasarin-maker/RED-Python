---
id: DEBT-gate-failure-coverage-100-command-pytest-b47eb726
status: open
severity: P1
risk_score: 8
blast_radius: HIGH
category: debt
satd_family: FINDING_BACKLOG_DEBT
lifespan: introduced
tag: BUG
verification_command: "pytest --cov=red --cov=app --cov=core --cov=config --cov=filters --cov=shell_integration --cov-fail-under=100 -q"
---

# Technical Debt [BUG | FINDING_BACKLOG_DEBT]: gate-failure: coverage-100: command `pytest --cov=red --cov=app --cov=core --cov

## Finding

<!-- findings:start -->
- gate-failure: coverage-100: command `pytest --cov=red --cov=app --cov=core --cov=config --cov=filters --cov=shell_integration --cov-fail-under=100 -q` exited nonzero
<!-- findings:end -->

## Acceptance

- [ ] The finding no longer reproduces (resolved in code and pruned), OR
- [ ] Marked as `status: closed` with verifiable justification and evidence.

```json queue-job
{
  "name": "remediate_DEBT-gate-failure-coverage-100-command-pytest-b47eb726",
  "command": "pytest --cov=red --cov=app --cov=core --cov=config --cov=filters --cov=shell_integration --cov-fail-under=100 -q",
  "artifact": "tasks/backlog/DEBT-gate-failure-coverage-100-command-pytest-b47eb726.md"
}
```
