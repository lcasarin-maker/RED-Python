from __future__ import annotations

import sys
import types

import red


def test_run_gui_uses_app_mainloop(monkeypatch):
    calls = []

    class FakeApp:
        def mainloop(self):
            calls.append("mainloop")

    fake_app_module = types.SimpleNamespace(App=FakeApp)
    monkeypatch.setitem(sys.modules, "app", fake_app_module)

    red._run_gui()

    assert calls == ["mainloop"]

