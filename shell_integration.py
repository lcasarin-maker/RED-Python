"""Shell integration module for RED-Python adding context menu entries on Windows."""

import logging
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pyright's pythonPlatform is pinned to "Windows" (this is a Windows
    # desktop app), so for type-checking purposes winreg always exists --
    # an unconditional import here keeps every real usage below fully typed
    # instead of widening to `X | None` from the runtime fallback.
    import winreg
else:
    try:
        import winreg
    except ImportError:  # pragma: no cover - winreg only exists on Windows
        # Import failure is the expected, permanent state on Linux/macOS:
        # this is Windows-only registry access, not an optional dependency
        # that might get installed later. Kept as a module attribute (not
        # re-raised) so the existing cross-platform test suite can
        # `monkeypatch.setattr(shell_integration, "winreg", fake_winreg)`
        # to exercise the real register/unregister/is_registered logic
        # without a live Windows registry -- the previous unconditional
        # `import winreg` made this entire module (and every test
        # importing it) uncollectable outside Windows, which is why
        # `tests/test_shell_and_app.py` was excluded via `conftest.py`'s
        # `collect_ignore` instead of actually running here.
        winreg = None

logger = logging.getLogger(__name__)


def register_context_menu():
    """Adds 'Scan with RED-Python' to the Windows Context Menu for directories."""
    try:
        # Path to the executable or python script
        if getattr(sys, "frozen", False):
            # Running as exe
            exe_path = sys.executable
            command = f'"{exe_path}" --scan "%1"'
        else:
            # Running as script
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            command = f'"{python_exe}" "{script_path}" --scan "%1"'

        key_path = r"Directory\shell\RED-Python"

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Scan with RED-Python")
            # Optional: Add an icon if available
            # winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, command)

        return True, "Context menu registered successfully."
    except Exception as e:
        logger.exception("Failed to register context menu")
        return False, str(e)


def unregister_context_menu():
    """Removes 'Scan with RED-Python' from the Windows Context Menu."""
    try:
        key_path = r"Directory\shell\RED-Python"

        # winreg.DeleteKey doesn't work if there are subkeys, so we delete command first
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command")
        except FileNotFoundError:
            logger.debug("No command subkey to delete; already absent")

        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
        return True, "Context menu unregistered successfully."
    except FileNotFoundError:
        return True, "Already unregistered."
    except Exception as e:
        logger.exception("Failed to unregister context menu")
        return False, str(e)


def is_registered():
    """Checks if the context menu is already registered."""
    try:
        key_path = r"Directory\shell\RED-Python"
        winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        logger.exception("Failed to check context menu registration")
        return False
