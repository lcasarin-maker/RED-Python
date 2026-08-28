from __future__ import annotations

import csv
import sys
from unittest.mock import MagicMock, call

import pytest

import app
import shell_integration
from core import ScanResult
from config import DEFAULT_FILTER_RULES


class FakeVar:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeEntry:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def delete(self, *_args):
        self.value = ""

    def insert(self, _index, value):
        self.value = value


class FakeListbox:
    def __init__(self, items=None):
        self.items = list(items or [])
        self.selected = []

    def get(self, *_args):
        return tuple(self.items)

    def insert(self, _index, value):
        self.items.append(value)

    def delete(self, index):
        self.items.pop(index)

    def curselection(self):
        return tuple(self.selected)

    def selection_set(self, *items):
        self.selected = list(range(len(self.items))) if not items else list(items)

    def selection_remove(self, *_args):
        self.selected = []


class FakeTree:
    def __init__(self):
        self.items = {}
        self.selection_value = ()

    def get_children(self):
        return tuple(self.items)

    def selection(self):
        return self.selection_value

    def selection_set(self, items):
        if isinstance(items, (list, tuple, set)):
            self.selection_value = tuple(items)
        else:
            self.selection_value = (items,)

    def selection_remove(self, items):
        blocked = set(items)
        self.selection_value = tuple(
            item for item in self.selection_value if item not in blocked
        )

    def selection_add(self, item):
        if item not in self.selection_value:
            self.selection_value = self.selection_value + (item,)

    def insert(self, parent, index, iid=None, **kwargs):
        text = kwargs.get("text", "")
        values = kwargs.get("values", ())
        tags = kwargs.get("tags", ())
        self.items[iid or text] = {"text": text, "values": values, "tags": tags}

    def item(self, iid, option=None, **kwargs):
        if kwargs:
            self.items.setdefault(iid, {}).update(kwargs)
        item = self.items.get(iid, {})
        if option is None:
            return item
        return item.get(option)

    def delete(self, item):
        self.items.pop(item, None)


class FakeText:
    def __init__(self, initial=""):
        self.text = initial
        self.state = None

    def delete(self, *_args):
        self.text = ""

    def insert(self, _index, value):
        self.text += value

    def get(self, *_args):
        return self.text

    def config(self, **kwargs):
        self.state = kwargs.get("state", self.state)


class FakeButton:
    def __init__(self):
        self.state = None

    def config(self, **kwargs):
        self.state = kwargs.get("state", self.state)


class FakeProgress:
    def __init__(self):
        self.started = 0
        self.stopped = 0

    def start(self, _interval):
        self.started += 1

    def stop(self):
        self.stopped += 1


class FakeStatus:
    def __init__(self, value=""):
        self.value = value

    def set(self, value):
        self.value = value


class FakeSettings:
    def __init__(self):
        self.data = {
            "recent_paths": [],
            "delete_mode": "simulate",
            "filter_rules": [dict(rule) for rule in DEFAULT_FILTER_RULES],
            "protected_dirs": [],
            "max_depth": 0,
            "min_age_hours": 0,
            "ignore_empty_files": True,
            "scan_hidden": False,
            "follow_symlinks": False,
            "pause_ms": 0,
            "max_warnings": 10,
            "play_sound": True,
        }
        self.saved = False

    def load(self):
        return self

    def save(self):
        self.saved = True

    def add_recent_path(self, path):
        recent = self.data.setdefault("recent_paths", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.data["recent_paths"] = recent[:10]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value


class FakeWinReg:
    HKEY_CLASSES_ROOT = object()
    REG_SZ = object()

    def __init__(self, fail_delete_command=False):
        self.created = []
        self.values = []
        self.deleted = []
        self.opened = []
        self.fail_delete_command = fail_delete_command

    class _Key:
        def __init__(self, registry, path):
            self.registry = registry
            self.path = path

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def CreateKey(self, root, path):
        self.created.append(path)
        return self._Key(self, path)

    def SetValue(self, key, name, regtype, value):
        self.values.append((key.path, value))

    def DeleteKey(self, root, path):
        self.deleted.append(path)
        if self.fail_delete_command and path.endswith("\\command"):
            raise FileNotFoundError(path)

    def OpenKey(self, root, path):
        self.opened.append(path)
        if path == "missing":
            raise FileNotFoundError(path)
        return self._Key(self, path)


@pytest.mark.skipif(
    sys.platform != "win32",
    reason=(
        "exercises os.path.abspath() on a Windows-style absolute path "
        "(\"D:\\\\...\"); posixpath's abspath (used on Linux/macOS) has no "
        "concept of a drive letter and treats it as relative, so this can "
        "only assert real behavior when the interpreter's os module is "
        "ntpath, i.e. on Windows"
    ),
)
def test_shell_integration_register_unregister_and_is_registered(monkeypatch):
    fake_winreg = FakeWinReg()
    monkeypatch.setattr(shell_integration, "winreg", fake_winreg)
    monkeypatch.setattr(shell_integration.sys, "frozen", False, raising=False)
    monkeypatch.setattr(shell_integration.sys, "executable", "C:\\Python\\python.exe")
    monkeypatch.setattr(shell_integration.sys, "argv", ["D:\\AI\\RED-Python\\red.py"])

    ok, msg = shell_integration.register_context_menu()
    assert ok is True
    assert "registered" in msg.lower()
    assert fake_winreg.created == [
        r"Directory\shell\RED-Python",
        r"Directory\shell\RED-Python\command",
    ]
    assert fake_winreg.values[-1][1].endswith(
        r'"D:\\AI\\RED-Python\\red.py" --scan "%1"'
    )

    assert shell_integration.is_registered() is True

    ok, msg = shell_integration.unregister_context_menu()
    assert ok is True
    assert "unregistered" in msg.lower()


def test_shell_integration_exe_mode_and_missing_delete_are_ok(monkeypatch):
    fake_winreg = FakeWinReg(fail_delete_command=True)
    monkeypatch.setattr(shell_integration, "winreg", fake_winreg)
    monkeypatch.setattr(shell_integration.sys, "frozen", True, raising=False)
    monkeypatch.setattr(shell_integration.sys, "executable", "C:\\RED-Python\\red.exe")

    ok, msg = shell_integration.register_context_menu()
    assert ok is True
    assert fake_winreg.values[-1][1] == '"C:\\RED-Python\\red.exe" --scan "%1"'

    ok, msg = shell_integration.unregister_context_menu()
    assert ok is True
    assert "unregistered" in msg.lower() or "already" in msg.lower()


def mock_app_init(monkeypatch):
    monkeypatch.setattr(app.tk.Tk, "__init__", lambda self: None)
    monkeypatch.setattr(app.tk.Tk, "title", lambda self, value: None)
    monkeypatch.setattr(app.tk.Tk, "geometry", lambda self, value: None)
    monkeypatch.setattr(app.tk.Tk, "minsize", lambda self, w, h: None)
    # tk.Tk.__init__ above is a no-op, so `self.tk` (the real _tkinter
    # interpreter handle) never gets set. Any test that reaches a real
    # `self.after(...)` call (e.g. App._stop) would recurse forever inside
    # Tk.__getattr__ trying to resolve the missing `self.tk` -- measured:
    # RecursionError, reproduced with this exact mocking setup before this
    # fix. Since there is no event loop to schedule against anyway, `after`
    # is stubbed to run its callback immediately.
    monkeypatch.setattr(
        app.tk.Tk, "after", lambda self, ms, func=None, *a: func(*a) if func else None
    )
    monkeypatch.setattr(app.App, "_apply_style", lambda self: None)
    monkeypatch.setattr(app.App, "_build", lambda self: None)
    monkeypatch.setattr(app, "Settings", FakeSettings)

def test_app_constructor(monkeypatch):
    mock_app_init(monkeypatch)
    instance = app.App()
    assert isinstance(instance.settings, FakeSettings)
    assert instance.results == []
    assert instance.scanner is None
    assert instance.cleaner is None

def test_app_path_list_management(monkeypatch):
    mock_app_init(monkeypatch)
    instance = app.App()
    # Deliberate test-double monkeypatching: fakes stand in for real tkinter
    # widgets so the App's logic can run headless. pyright correctly flags
    # these as type mismatches against the real widget classes -- that is
    # the point of a fake, not a bug.
    instance._path_entry = FakeEntry("C:/alpha")  # pyright: ignore[reportAttributeAccessIssue]
    instance._path_list = FakeListbox(["C:/beta"])  # pyright: ignore[reportAttributeAccessIssue]
    monkeypatch.setattr(app.os.path, "isdir", lambda path: True)
    instance._add_path()
    assert list(instance._path_list.items) == ["C:/beta", "C:/alpha"]  # pyright: ignore[reportAttributeAccessIssue]
    assert instance._get_paths() == ["C:/beta", "C:/alpha"]
    instance._path_list.selected = [0]  # pyright: ignore[reportAttributeAccessIssue]
    instance._remove_path()
    assert instance._get_paths() == ["C:/alpha"]

def test_app_tree_selection(monkeypatch):
    mock_app_init(monkeypatch)
    instance = app.App()
    instance._tree = FakeTree()  # pyright: ignore[reportAttributeAccessIssue]
    instance._tree.items = {"one": {}, "two": {}}  # pyright: ignore[reportAttributeAccessIssue]
    instance._sel_all()
    assert set(instance._tree.selection()) == {"one", "two"}
    instance._desel_all()
    assert instance._tree.selection() == ()

def test_app_ui_locking(monkeypatch):
    mock_app_init(monkeypatch)
    instance = app.App()
    instance._status = FakeStatus("Ready")  # pyright: ignore[reportAttributeAccessIssue]
    instance._btn_scan = FakeButton()  # pyright: ignore[reportAttributeAccessIssue]
    instance._btn_delete = FakeButton()  # pyright: ignore[reportAttributeAccessIssue]
    instance._btn_stop = FakeButton()  # pyright: ignore[reportAttributeAccessIssue]
    instance._progress = FakeProgress()  # pyright: ignore[reportAttributeAccessIssue]
    instance._lock_ui(scanning=True)
    assert instance._scanning is True and instance._deleting is False
    assert instance._btn_scan.state == "disabled"
    instance._unlock_ui()
    assert instance._scanning is False and instance._deleting is False

def test_app_explorer_and_export(monkeypatch, tmp_path):
    mock_app_init(monkeypatch)
    instance = app.App()
    instance._tree = FakeTree()  # pyright: ignore[reportAttributeAccessIssue]
    instance._status = FakeStatus("Ready")  # pyright: ignore[reportAttributeAccessIssue]
    opened = []
    # "C:/parent" must also read as existing: it's the dirname fallback for
    # a selected path that itself no longer exists ("C:/missing" below), and
    # _open_explorer only calls startfile when THAT resolved target exists.
    monkeypatch.setattr(
        app.os.path, "exists", lambda path: path.endswith("exists") or path == "C:/parent"
    )
    monkeypatch.setattr(app.os.path, "dirname", lambda path: "C:/parent")
    # os.startfile is Windows-only and does not exist as an attribute on
    # Linux/macOS's os module at all, so raising=False is required to add it
    # rather than replace it -- app.py's own call to os.startfile is real
    # code under test either way.
    monkeypatch.setattr(app.os, "startfile", lambda path: opened.append(path), raising=False)
    instance._tree.selection_value = ("C:/exists",)  # pyright: ignore[reportAttributeAccessIssue]
    instance._open_explorer()
    assert opened == ["C:/exists"]
    instance._tree.selection_value = ("C:/missing",)  # pyright: ignore[reportAttributeAccessIssue]
    instance._open_explorer()
    assert opened[-1] == "C:/parent"

    instance.results = [ScanResult(path="C:/alpha", status="empty", depth=3)]
    export_path = tmp_path / "results.csv"
    monkeypatch.setattr(app.filedialog, "asksaveasfilename", lambda **kwargs: str(export_path))
    instance._export()
    rows = list(csv.reader(export_path.open(encoding="utf-8", newline="")))
    assert rows[0] == ["Path", "Status", "Level"]
    assert rows[1] == ["C:/alpha", "empty", "3"]

def test_app_stop_action(monkeypatch):
    mock_app_init(monkeypatch)
    instance = app.App()
    instance.scanner = MagicMock()  # pyright: ignore[reportAttributeAccessIssue]
    instance.cleaner = MagicMock()  # pyright: ignore[reportAttributeAccessIssue]
    instance._scanning = True
    instance._deleting = True
    instance._append_log = MagicMock()
    instance._unlock_ui = MagicMock()
    instance._stop()
    assert instance.scanner.stop.call_args_list == [call()]
    assert instance.cleaner.stop.call_args_list == [call()]
    assert instance._append_log.call_count == 1
    assert instance._unlock_ui.call_args_list == [call()]
