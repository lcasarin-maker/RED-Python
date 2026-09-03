---
id: DEBT-ANGRY-PATH-DEGRADATION
status: done
severity: P1
risk_score: 6
blast_radius: MEDIUM
category: debt
satd_family: TECHNICAL_DEBT
lifespan: introduced
tag: BUG
verification_command: "pytest tests/test_filters.py"
kind: debt
origin: asserted
close_check: {"cmd": "pytest tests/test_filters.py", "expect": "exit_zero"}
prior_status: done
title: DEBT ANGRY PATH DEGRADATION
created: 2026-08-22
---

# Silent Error Swallowing & Dummy Fallbacks (Rule B3)

Empty catch blocks, blind except handlers or dummy returns detected:

<!-- findings:start -->
- /home/lcasarin/projects/red_python/filters.py:157: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/filters.py:248: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/shell_integration.py:33: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/shell_integration.py:54: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/shell_integration.py:66: blind except returns dummy fallback without logging/re-raise
<!-- findings:end -->

```json queue-job
{
  "name": "remediate_DEBT-ANGRY-PATH-DEGRADATION",
  "command": "pytest tests/test_filters.py",
  "artifact": "tasks/done/DEBT-ANGRY-PATH-DEGRADATION.md"
}
```



## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Cierre — 2026-08-24
Reabierta por el sync de flota (10 hallazgos nuevos, ver mensaje de simplecode-15):
app.py:468 (loop swallow), filters.py:157/187/197/206/248/256, shell_integration.py:33/54/66.
Todas resueltas agregando `logging.debug`/`logger.exception` en cada handler ciego
en vez de `print(..., file=sys.stderr)` (que el guard no reconoce como logging) o
sin ninguna traza. Verificado:

```
python .simplecode/run.py simplecode.guards.angry_path --gate
[angry-path] OK: all 169 scanned files adhere to Angry Path Dominance (Rule B3).
```

`pytest`: 33 passed.

## Root Cause

Several `except` blocks in `filters.py`, `shell_integration.py`, and `app.py`
caught exceptions and either returned a dummy fallback or fell through silently,
with no `logging`/`logger.exception` call and no re-raise -- violating Rule B3
(Angry Path Dominance). A first pass missed some of these because it used
`print(..., file=sys.stderr)`, which the `angry_path` guard does not recognize
as logging.

## Regression Test

`python .simplecode/run.py simplecode.guards.angry_path --gate` is the
regression test: it fails again the moment a bare/broad `except` without
`logging`/`logger.exception` or re-raise is reintroduced.

## Verification Evidence

Command run 2026-08-28 in this repo:

```
$ python .simplecode/run.py simplecode.guards.angry_path --gate
[angry-path] OK: all 179 scanned files adhere to Angry Path Dominance (Rule B3).
```

Negative control, run 2026-08-28 (git-add a tracked scratch file with a blind
`except Exception: return None`, confirm the gate fails, then revert):

```
$ git add neg_control_scratch.py
$ python .simplecode/run.py simplecode.guards.angry_path --gate
[angry-path] FAIL: 1 silent error handling finding(s):
  - /home/lcasarin/projects/red_python/neg_control_scratch.py:4: blind except returns dummy fallback without logging/re-raise
$ git reset neg_control_scratch.py && rm neg_control_scratch.py
```