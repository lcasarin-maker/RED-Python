---
id: DEBT-gate-failure-pyright-command-pyright-exi-4a465989
kind: debt
title: DEBT gate failure pyright command pyright exi 4a465989
status: open
prior_status: done
severity: P1
origin: asserted
satd_family: FINDING_BACKLOG_DEBT
close_check: {"cmd": "pyright", "expect": "exit_zero"}
created: 2026-08-28
---

<!-- Prosa: ningun gate la lee. Migrada de tasks/done/DEBT-gate-failure-pyright-command-pyright-exi-4a465989.md el 2026-09-01. -->

> **REABIERTA POR EL CONTRATO DE CIERRE, no por un defecto nuevo.** Estaba
> `status: closed`. Lo que no trae es `evidence.fail`: la corrida con el
> veredicto contrario. Sin ella no se demostro que su comprobacion pudiera salir
> negativa, y una verificacion que no puede salir negativa no es una verificacion.
> Luis voto el 2026-09-01, con el costo delante, la opcion SIN amnistia. No se
> pierde nada: la evidencia de abajo se conserva verbatim.

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

## Root Cause

`pyright` started at 48 errors. No `pyrightconfig.json` existed, so pyright
defaulted `pythonPlatform` to the host OS (Linux) even though red_python is
a Windows desktop app (`winreg`, `os.startfile`, Explorer shell integration).
Three distinct causes, all confirmed by isolating them one at a time rather
than assumed:

1. **Wrong target platform (29 errors gone with one config line).** With
   `pythonPlatform` unset, pyright's typeshed stub for `winreg` resolves to
   nothing on Linux (`"CreateKey" is not a known attribute of module
   "winreg"`), and `os.name == "nt"`-guarded attribute assignments in
   `app.py` (`self._btn_reg`, `self._btn_unreg`) were consequently
   unreachable from pyright's point of view. Setting
   `"pythonPlatform": "Windows"` in a new `pyrightconfig.json` (the honest
   fix: this app targets Windows, so its type-checker should analyze it as
   it will actually run) cleared these outright: 48 -> 29 errors.
2. **An untyped `dict` swallowing `None` through `Settings.get()` (10 more
   errors gone).** `config.py`'s `Settings.data` had no type annotation and
   `Settings.get(self, key, default=None)` had no return annotation, so
   pyright inferred a `None`-including return type that then broke every
   caller doing `"\n".join(settings.get(...))` or `IntVar.set(settings.get
   (...))` in `app.py`. `Settings.data` and JSON-loaded settings values are
   genuinely dynamically typed (loaded from freeform JSON), so `Any` is the
   accurate type here, not a narrower one. Annotated both: 29 -> 18 errors.
3. **A real bug pyright caught: a method that was called but never
   defined.** `app.py`'s `_on_delete_done` called `self._play_done_sound()`
   -- grep confirms no such method existed anywhere in the file. Every
   completed deletion has been raising `AttributeError` inside a tkinter
   callback, silently swallowed by Tk's default
   `report_callback_exception` (logs to stderr, does not crash the app), so
   the "Play a sound when long tasks finish" checkbox (`play_sound` setting,
   `DEFAULT_SETTINGS["play_sound"] = True`) has never actually worked.
   Implemented the method for real (`winsound.MessageBeep`, guarded by both
   the setting and `os.name == "nt"`): 18 -> 17 errors.
4. **One real bug in a test.** `tests/test_red_core_behaviour.py` called
   `scanner._thread.join(...)` where `_thread: Thread | None` -- added an
   `assert scanner._thread is not None` before the join, both fixing the
   pyright finding and documenting the actual invariant (`scan()` always
   starts the thread before this point). 17 -> 16 errors.
5. **The remaining 16 errors were all in `tests/test_shell_and_app.py`,
   and are not bugs: they are deliberate test-double monkeypatching**
   (`instance._path_entry = FakeEntry(...)` assigned in place of a real
   `tkinter.Entry`, etc.) -- exactly what a test double is for. Suppressed
   with targeted `# pyright: ignore[reportAttributeAccessIssue]` comments on
   each assignment, with a comment at the top of the block explaining why:
   16 -> 0 errors.

## Regression Test

- `config.py`: `Settings.data: dict[str, Any]`, `Settings.get(self, key,
  default: Any = None) -> Any`.
- `app.py`: added `App._play_done_sound`, wired from the already-existing
  `_on_delete_done` call site and the already-existing `play_sound`
  setting/checkbox.
- `tests/test_red_core_behaviour.py`: `assert scanner._thread is not None`
  before `.join()`.
- `pyrightconfig.json` (new): `{"pythonPlatform": "Windows",
  "reportMissingModuleSource": "warning"}`.
- Full unit suite still green after all of the above (`pytest -q`, 33
  passed) -- none of these were behavior changes to the tested paths except
  `_play_done_sound`, which had no test coverage before (it could not have:
  the method did not exist) and still runs as a no-op off-Windows, so
  existing tests are unaffected.

Negative control (pyright CAN still fail — this repo is not exempted, the
finding was actually fixed): reverting just the `_play_done_sound`
definition (commenting it out) reproduces a `reportAttributeAccessIssue` at
the exact original call site, confirmed by temporarily removing the method
and re-running pyright:

```
$ cp app.py /tmp/app.py.bak
$ python3 -c "
import pathlib
p = pathlib.Path('app.py')
src = p.read_text()
p.write_text(src.replace('    def _play_done_sound(self):', '    def _play_done_sound_DISABLED(self):', 1))
"
$ pyright 2>&1 | tail -6
  /home/lcasarin/projects/red_python/app.py:868:18 - error: Cannot access attribute "_play_done_sound" for class "App*"
    Attribute "_play_done_sound" is unknown (reportAttributeAccessIssue)
  ...
1 error, 1 warning, 0 informations
$ cp /tmp/app.py.bak app.py   # restored
```

## Verification Evidence

```
$ pyright; echo "EXIT:$?"
/home/lcasarin/projects/red_python/core.py
  /home/lcasarin/projects/red_python/core.py:245:24 - warning: Import "send2trash" could not be resolved from source (reportMissingModuleSource)
0 errors, 1 warning, 0 informations
EXIT:0
```

The one remaining warning is pre-existing and unrelated to this finding:
`send2trash` ships without inline type stubs (a third-party packaging
detail, not a type error in this repo's code) and pyright's own gate
threshold is errors, not warnings.
