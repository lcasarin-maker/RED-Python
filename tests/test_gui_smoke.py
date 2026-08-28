from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, call

import red


def test_run_gui_uses_app_mainloop(monkeypatch):
    fake_instance = MagicMock()
    fake_app_cls = MagicMock(return_value=fake_instance)
    fake_app_module = types.SimpleNamespace(App=fake_app_cls)
    monkeypatch.setitem(sys.modules, "app", fake_app_module)

    red._run_gui()

    assert fake_app_cls.call_args_list == [call()]
    assert fake_instance.mainloop.call_args_list == [call()]
