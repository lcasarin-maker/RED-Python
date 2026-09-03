---
id: DEBT-gate-failure-adversarial-judge-command-p-8f65867f
status: open
severity: P1
risk_score: 8
blast_radius: HIGH
category: debt
satd_family: FINDING_BACKLOG_DEBT
lifespan: introduced
tag: BUG
verification_command: "python .simplecode/run.py simplecode.verification.adversarial_judge --root . --gate"
kind: debt
origin: asserted
close_check: {"cmd": "python .simplecode/run.py simplecode.verification.adversarial_judge --root . --gate", "expect": "exit_zero"}
prior_status: done
title: DEBT gate failure adversarial judge command p 8f65867f
created: 2026-08-28
---

# Technical Debt [BUG | FINDING_BACKLOG_DEBT]: gate-failure: adversarial-judge: command `python .simplecode/run.py simplecode.v

## Finding

<!-- findings:start -->
- gate-failure: adversarial-judge: command `python .simplecode/run.py simplecode.verification.adversarial_judge --root . --gate` exited nonzero
<!-- findings:end -->

## Acceptance

- [x] The finding no longer reproduces (resolved in code and pruned).

```json queue-job
{
  "name": "remediate_DEBT-gate-failure-adversarial-judge-command-p-8f65867f",
  "command": "python .simplecode/run.py simplecode.verification.adversarial_judge --root . --gate",
  "artifact": "tasks/done/DEBT-gate-failure-adversarial-judge-command-p-8f65867f.md"
}
```

## Root Cause

`adversarial_judge --gate` was failing with 37 distinct violations, none of
them in `red_python`'s application code -- all in the task backlog's own
contract compliance and two documentation cross-reference sets:

1. **26 backlog contract breaches** across `tasks/done/*.md`: legacy closed
   tasks (most predating the current GS2-214 mandatory-frontmatter contract:
   `severity`, `risk_score`, `blast_radius`, `category`, `satd_family`,
   `lifespan`, `tag`, plus a `queue-job` block and a structured findings
   block) that were correctly resolved historically but never migrated to
   the newer schema, and 3 closed tasks (`CONV-DEBT-*`) auto-harvested from
   an external AI assistant's transcript log that described the fleet's own
   harvesting tool rather than a red_python defect. Fixed per-file: missing
   frontmatter fields added (backfilled truthfully from each task's own
   existing narrative, not fabricated), missing findings/queue-job blocks
   added, and the 3 `CONV-DEBT-*` noise tasks closed with justification
   (no code defect existed to fix -- see each file's own Root Cause
   section).
2. **9 broken evidence pins**: `README.md` linked `00 audit/...` with a
   URL-encoded space (`00%20audit/...`) that didn't match the real directory
   name (`00 audit/`, literal space) -- fixed by using the literal space.
   `Wiki/*.md` (4 files) linked `docs/...` paths that only resolve correctly
   from the repo root, but the evidence-pin checker resolves links relative
   to the FILE'S OWN directory (`Wiki/`) -- fixed by prefixing each link
   with `../` so it actually reaches `docs/...` from `Wiki/`.

Full per-file detail lives in each fixed task's own Root Cause /
Verification Evidence sections under `tasks/done/`.

## Regression Test

`python .simplecode/run.py simplecode.verification.adversarial_judge --root . --gate`
itself is the regression test: it re-audits every governed task file's
contract AND every tracked markdown file's evidence links on every run.

## Verification Evidence

Before (start of this remediation session, 2026-08-28):

```
$ python .simplecode/run.py simplecode.verification.adversarial_judge --root . --gate
[judge-zero] FAIL: Detected 37 technical frauds or mock-theater violations:
  ... (26 Backlog Contract Breach + 9 Broken Evidence Pin entries)
```

After:

```
$ python .simplecode/run.py simplecode.verification.adversarial_judge --root . --gate
=== ADVERSARIAL RED-TEAM JUDGE (JUDGE-ZERO) ===
[judge-zero] OK: Configured source audits and task contracts passed.
```
(exit code 0)

Negative control: this same gate, run against the state at the start of
this session (before the 26+9 fixes above), demonstrably printed 37 real
violations with specific file/line detail -- not an instrument that reports
green unconditionally. Re-introducing any single one of the fixed contract
breaches or broken links would reproduce a FAIL again, since the checks are
per-file/per-line, not aggregate.
