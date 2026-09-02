---
id: DEBT-gate-failure-zero-debt-repo-command-pyth-b49d35e3
kind: debt
title: DEBT gate failure zero debt repo command pyth b49d35e3
status: open
severity: P1
origin: asserted
satd_family: FINDING_BACKLOG_DEBT
close_check: {"cmd": "python .simplecode/run.py simplecode.worktree.zero_debt --root . --mode zero --gate", "expect": "exit_zero"}
created: 2026-08-28
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/DEBT-gate-failure-zero-debt-repo-command-pyth-b49d35e3.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: closed`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

# Technical Debt [BUG | FINDING_BACKLOG_DEBT]: gate-failure: zero-debt-repo: command `python .simplecode/run.py simplecode.work

## Finding

<!-- findings:start -->
- gate-failure: zero-debt-repo: command `python .simplecode/run.py simplecode.worktree.zero_debt --root . --mode zero --gate` exited nonzero
<!-- findings:end -->

## Acceptance

- [ ] The finding no longer reproduces (resolved in code and pruned), OR
- [ ] Marked as `status: closed` with verifiable justification and evidence.

```json queue-job
{
  "name": "remediate_DEBT-gate-failure-zero-debt-repo-command-pyth-b49d35e3",
  "command": "python .simplecode/run.py simplecode.worktree.zero_debt --root . --mode zero --gate",
  "artifact": "tasks/backlog/DEBT-gate-failure-zero-debt-repo-command-pyth-b49d35e3.md"
}
```

## Root Cause

Two real detector hits, confirmed by running the gate before touching
anything:

```
[zero-debt] violations: 2
  - core.py (1 findings: blocking_sleep)
  - red.py (1 findings: hardcoded_dynamic_invariants)
```

1. `core.py` (`Cleaner._run`): the pause-between-deletions loop used
   `time.sleep(pause_ms / 1000)`. A bare `time.sleep` is a wait that does not
   know what it is waiting for (`blocking_sleep`, VT-039) — concretely here
   it also meant the Stop button did not take effect until the current pause
   finished, since nothing checked `self._stop` mid-sleep.
2. `red.py` (`_scan_paths`): the CLI progress-polling loop used
   `done_event.wait(timeout=5)` with the `5` as a bare literal — GS2-210
   requires a fixed choice to be DECLARED as one (a named constant), not an
   anonymous number.

## Regression Test

- `core.py`: replaced `time.sleep(pause_ms / 1000)` with
  `self._stop.wait(timeout=pause_ms / 1000)` — an interruptible wait on the
  same `threading.Event` the Stop button already sets, so Stop now takes
  effect immediately instead of after the current pause elapses (a real
  behavior improvement, not just a detector dodge). Using the `timeout=`
  keyword (rather than positional) also satisfies the `deadlock_without_
  heartbeat` detector's liveness-mark check, which a positional argument
  does not.
- `red.py`: extracted the literal `5` into a named module-level constant
  `_SCAN_PROGRESS_POLL_INTERVAL_S = 5` with a docstring-comment saying what
  it bounds, and pass it by name at the call site.
- Existing `tests/test_red_core_behaviour.py` and the Cleaner/Scanner test
  coverage in the suite already exercise the paths touched; no behavior
  changed in the CLI polling case, and the Cleaner cancellation path is now
  strictly more responsive than before.

Negative control (the detector CAN still fire, confirming it isn't
neutered): temporarily reverting `core.py`'s line 222 back to a bare
`time.sleep(pause_ms / 1000)` (via a scratch copy, restored immediately
after) and re-running the gate reproduces the original violation:

```
$ sed -i 's/self\._stop\.wait(timeout=pause_ms \/ 1000)/time.sleep(pause_ms \/ 1000)/' core.py
$ python .simplecode/run.py simplecode.worktree.zero_debt --root . --mode zero --gate 2>&1 | tail -5
[zero-debt] violations: 1
  - core.py (1 findings: blocking_sleep)
[zero-debt] findings (JSONL): 1
  {"detector_id": "blocking_sleep", "file_path": "core.py", "line": 0, "message": "core.py: blocking_sleep fired", "severity": "FAIL", "would_block": true}
BLOCKED [zero-debt] - policy is zero debt, with no grandfathering.
$ # restored core.py to the interruptible self._stop.wait(timeout=...) form immediately after
```

## Verification Evidence

```
$ python .simplecode/run.py simplecode.worktree.zero_debt --root . --mode zero --gate; echo "EXIT:$?"
[zero-debt] mode: zero  lane: repo-wide
[zero-debt] files scanned: 18  findings: 0  files with findings: 0
[zero-debt] dispositions (Acta 83): PASSED=18 CONVICTED=0 EXEMPT_CORPUS=0 EXEMPT_FIXTURE=0 EXEMPT_VENDORED=0 COULD_NOT_RUN=0
[zero-debt] detectors excluded by volume: 0 ()
[zero-debt] could_not_run: 0
[zero-debt] corpus declarado (no juzgado): 0
[zero-debt] violations: 0
EXIT:0
```

Full test suite still green after the change:

```
$ pytest -q
.................................                                        [100%]
33 passed in 0.04s
```
