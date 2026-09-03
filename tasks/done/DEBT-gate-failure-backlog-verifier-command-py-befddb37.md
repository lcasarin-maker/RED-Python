---
id: DEBT-gate-failure-backlog-verifier-command-py-befddb37
status: open
severity: P1
risk_score: 8
blast_radius: HIGH
category: debt
satd_family: FINDING_BACKLOG_DEBT
lifespan: introduced
tag: BUG
verification_command: "python .simplecode/run.py simplecode.verification.backlog_verifier --root . --gate"
kind: debt
origin: asserted
close_check: {"cmd": "python .simplecode/run.py simplecode.verification.backlog_verifier --root . --gate", "expect": "exit_zero"}
prior_status: done
title: DEBT gate failure backlog verifier command py befddb37
created: 2026-08-28
---

# Technical Debt [BUG | FINDING_BACKLOG_DEBT]: gate-failure: backlog-verifier: command `python .simplecode/run.py simplecode.ve

## Finding

<!-- findings:start -->
- gate-failure: backlog-verifier: command `python .simplecode/run.py simplecode.verification.backlog_verifier --root . --gate` exited nonzero
<!-- findings:end -->

## Acceptance

- [x] The finding no longer reproduces (resolved in code and pruned).

```json queue-job
{
  "name": "remediate_DEBT-gate-failure-backlog-verifier-command-py-befddb37",
  "command": "python .simplecode/run.py simplecode.verification.backlog_verifier --root . --gate",
  "artifact": "tasks/done/DEBT-gate-failure-backlog-verifier-command-py-befddb37.md"
}
```

## Root Cause

`backlog_verifier` shares its task-contract validator
(`validate_task_contract` / `verify_tasks_contract_compliance`) with
`adversarial_judge` -- the same 26 contract breaches described in
`DEBT-gate-failure-adversarial-judge-command-p-8f65867f.md` (missing
mandatory frontmatter fields, missing findings/queue-job blocks on legacy
`tasks/done/*.md` files, 3 noise `CONV-DEBT-*` tasks) were the entire cause
of this gate's failure too. No separate defect was found once that shared
root cause was fixed.

## Regression Test

`python .simplecode/run.py simplecode.verification.backlog_verifier --root . --gate --no-revert`
is the regression test (run with `--no-revert` so a genuine fraud finding
during verification doesn't also revert working-tree changes mid-audit).

## Verification Evidence

Before (start of this remediation session, 2026-08-28): the same 26 contract
breaches reproduced here as in `adversarial_judge` (shared validator), giving
a nonzero exit.

After:

```
$ python .simplecode/run.py simplecode.verification.backlog_verifier --root . --gate --no-revert
[backlog-verifier] OK: all tasks verified (counts -> frauds: 0 · could_not_run: 0 · contract_breaches: 0).
```
(exit code 0)

Negative control: `contract_breaches` is a counted, printed field, not a
boolean the verifier could hide behind -- the same run against this
session's starting state would have reported `contract_breaches: 26`, and
introducing a single missing mandatory frontmatter field into any governed
task file reproduces a nonzero `contract_breaches` count again (verified
live while iterating fixes throughout this session: each partial fix
produced a smaller, printed leftover-violation count until it reached 0).
