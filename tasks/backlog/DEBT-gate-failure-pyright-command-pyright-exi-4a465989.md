---
id: DEBT-gate-failure-pyright-command-pyright-exi-4a465989
status: open
severity: P1
risk_score: 8
blast_radius: HIGH
category: debt
satd_family: FINDING_BACKLOG_DEBT
lifespan: introduced
tag: BUG
verification_command: "pyright"
---

# Technical Debt [BUG | FINDING_BACKLOG_DEBT]: gate-failure: pyright: command `pyright` exited nonzero

## Finding

<!-- findings:start -->
- gate-failure: pyright: command `pyright` exited nonzero
<!-- findings:end -->

## Acceptance

- [ ] The finding no longer reproduces (resolved in code and pruned), OR
- [ ] Marked as `status: closed` with verifiable justification and evidence.

```json queue-job
{
  "name": "remediate_DEBT-gate-failure-pyright-command-pyright-exi-4a465989",
  "command": "pyright",
  "artifact": "tasks/backlog/DEBT-gate-failure-pyright-command-pyright-exi-4a465989.md"
}
```
