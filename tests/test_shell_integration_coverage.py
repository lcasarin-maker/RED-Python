"""Coverage-closing tests for shell_integration.py's remaining branches:
the non-frozen script-path command line, and the error branches of
register/unregister/is_registered that `test_shell_and_app.py`'s happy-path
tests don't reach. All exercised via a fake `winreg`, matching the existing
pattern -- no real Windows registry involved.
"""

from __future__ import annotations

import shell_integration


class _Key:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class RaisingWinReg:
    """CreateKey always fails -- exercises register_context_menu's outer
    `except Exception` branch."""

    HKEY_CLASSES_ROOT = object()
    REG_SZ = object()

    def CreateKey(self, root, path):
        raise OSError("simulated registry failure")


class AlreadyGoneWinReg:
    """Both DeleteKey calls raise FileNotFoundError -- the whole key is
    already absent, exercising unregister_context_menu's OUTER
    FileNotFoundError branch (distinct from the inner one that only covers
    the `\\command` subkey)."""

    HKEY_CLASSES_ROOT = object()

    def DeleteKey(self, root, path):
        raise FileNotFoundError(path)


class ExplodingDeleteWinReg:
    """DeleteKey raises something other than FileNotFoundError -- exercises
    unregister_context_menu's generic `except Exception` branch."""

    HKEY_CLASSES_ROOT = object()

    def DeleteKey(self, root, path):
        if path.endswith("\\command"):
            raise FileNotFoundError(path)  # inner branch: no subkey, fine
        raise PermissionError("simulated permission denied")


class NotRegisteredWinReg:
    HKEY_CLASSES_ROOT = object()

    def OpenKey(self, root, path):
        raise FileNotFoundError(path)


class ExplodingOpenWinReg:
    HKEY_CLASSES_ROOT = object()

    def OpenKey(self, root, path):
        raise PermissionError("simulated permission denied")


def test_register_context_menu_uses_script_path_when_not_frozen(monkeypatch):
    calls = []

    class RecordingWinReg:
        HKEY_CLASSES_ROOT = object()
        REG_SZ = object()

        def CreateKey(self, root, path):
            return _Key()

        def SetValue(self, key, name, regtype, value):
            calls.append(value)

    monkeypatch.setattr(shell_integration, "winreg", RecordingWinReg())
    monkeypatch.setattr(shell_integration.sys, "frozen", False, raising=False)

    ok, msg = shell_integration.register_context_menu()

    assert ok is True
    # Non-frozen branch quotes BOTH the interpreter and the script path,
    # unlike the frozen-exe branch which only quotes the executable.
    assert calls[-1].startswith(f'"{shell_integration.sys.executable}" "')
    assert calls[-1].endswith('--scan "%1"')


def test_register_context_menu_reports_registry_failure(monkeypatch):
    monkeypatch.setattr(shell_integration, "winreg", RaisingWinReg())

    ok, msg = shell_integration.register_context_menu()

    assert ok is False
    assert "simulated registry failure" in msg


def test_unregister_context_menu_when_key_already_fully_absent(monkeypatch):
    monkeypatch.setattr(shell_integration, "winreg", AlreadyGoneWinReg())

    ok, msg = shell_integration.unregister_context_menu()

    assert ok is True
    assert "already unregistered" in msg.lower()


def test_unregister_context_menu_reports_unexpected_failure(monkeypatch):
    monkeypatch.setattr(shell_integration, "winreg", ExplodingDeleteWinReg())

    ok, msg = shell_integration.unregister_context_menu()

    assert ok is False
    assert "simulated permission denied" in msg


def test_is_registered_true_when_key_present(monkeypatch):
    class PresentWinReg:
        HKEY_CLASSES_ROOT = object()

        def OpenKey(self, root, path):
            return _Key()

    monkeypatch.setattr(shell_integration, "winreg", PresentWinReg())

    assert shell_integration.is_registered() is True


def test_is_registered_false_when_key_missing(monkeypatch):
    monkeypatch.setattr(shell_integration, "winreg", NotRegisteredWinReg())

    assert shell_integration.is_registered() is False


def test_is_registered_false_on_unexpected_error(monkeypatch):
    monkeypatch.setattr(shell_integration, "winreg", ExplodingOpenWinReg())

    assert shell_integration.is_registered() is False
