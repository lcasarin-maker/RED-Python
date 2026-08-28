"""Coverage-closing tests for red.py: delete-mode branches, the real
deletion pipeline (--permanent / default-recycle), the scan progress
heartbeat, non-CSV export (+ its error branch), and the `__main__` entry
point itself (both the CLI and the GUI-launch branches).
"""

from __future__ import annotations

import contextlib
import io
import runpy
import sys
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import red

REPO_ROOT = Path(__file__).resolve().parent.parent
RED_PY = REPO_ROOT / "red.py"


def test_setup_settings_permanent_mode():
    ns = SimpleNamespace(
        dry_run=False, permanent=True, max_depth=0, min_age=0,
        no_empty_files=False, scan_hidden=False, follow_symlinks=False,
    )
    settings = red._setup_settings(ns)
    assert settings["delete_mode"] == "permanent"


def test_setup_settings_recycle_mode_is_the_default():
    ns = SimpleNamespace(
        dry_run=False, permanent=False, max_depth=0, min_age=0,
        no_empty_files=False, scan_hidden=False, follow_symlinks=False,
    )
    settings = red._setup_settings(ns)
    assert settings["delete_mode"] == "recycle"


def test_cli_permanent_mode_actually_deletes_empty_dir(tmp_path):
    root = tmp_path / "root"
    empty = root / "empty"
    empty.mkdir(parents=True)

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = red._run_cli(["--scan", str(root), "--permanent"])

    assert exit_code == 0
    assert not empty.exists()
    assert "Deletion complete" in stdout.getvalue()


def test_cli_default_recycle_mode_logs_error_without_send2trash(tmp_path):
    # send2trash is not an installed dependency here, so the default
    # (recycle) delete mode fails closed: the folder survives and an error
    # is reported, but the CLI pipeline itself still runs to completion.
    root = tmp_path / "root"
    empty = root / "empty"
    empty.mkdir(parents=True)

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = red._run_cli(["--scan", str(root)])

    assert exit_code == 0
    assert empty.exists()  # recycle failed, nothing was actually removed
    assert "Deletion complete" in stdout.getvalue()


def test_scan_paths_prints_progress_while_waiting(monkeypatch, tmp_path):
    monkeypatch.setattr(red, "_SCAN_PROGRESS_POLL_INTERVAL_S", 0.01)

    class SlowFakeScanner:
        def __init__(self, settings, on_found, on_log, on_done):
            self._on_done = on_done

        def scan(self, paths):
            def worker():
                # A bounded wait, not a blind sleep (matches this repo's own
                # `deadlock_without_heartbeat`-driven convention elsewhere,
                # e.g. red.py's `_SCAN_PROGRESS_POLL_INTERVAL_S` heartbeat):
                # just needs to outlast the patched 0.01s poll interval so
                # `_scan_paths`'s wait loop ticks at least once.
                threading.Event().wait(timeout=0.05)
                self._on_done(0)

            threading.Thread(target=worker, daemon=True).start()

    import core
    monkeypatch.setattr(core, "Scanner", SlowFakeScanner)

    ns = SimpleNamespace(quiet=False)
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        results = red._scan_paths(ns, [str(tmp_path)], {})

    assert results == []
    assert "still scanning" in stderr.getvalue()


def test_export_results_writes_txt_format(tmp_path):
    from core import ScanResult

    out = tmp_path / "results.txt"
    results = [ScanResult(path="/a/b", status="empty", depth=2)]

    red._export_results(results, str(out))

    assert out.read_text(encoding="utf-8") == "empty\t/a/b\n"


def test_export_results_reports_write_errors(tmp_path, capsys):
    from core import ScanResult

    # A path inside a file (not a directory) can never be opened for
    # writing -- a real, portable way to force `open()` to raise.
    blocker = tmp_path / "not_a_directory"
    blocker.write_text("x", encoding="utf-8")
    bad_path = str(blocker / "results.csv")

    red._export_results([ScanResult(path="/a", status="empty", depth=0)], bad_path)

    assert "Export error" in capsys.readouterr().out


def test_main_entrypoint_cli_branch_via_runpy(monkeypatch, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.setattr(sys, "argv", ["red.py", "--scan", str(root), "--dry-run"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(RED_PY), run_name="__main__")

    assert exc_info.value.code == 0


def test_main_entrypoint_no_args_launches_gui_via_runpy(monkeypatch):
    import app

    fake_instance = MagicMock()
    fake_app_cls = MagicMock(return_value=fake_instance)
    monkeypatch.setattr(app, "App", fake_app_cls)
    monkeypatch.setattr(sys, "argv", ["red.py"])

    runpy.run_path(str(RED_PY), run_name="__main__")

    assert fake_app_cls.called
    assert fake_instance.mainloop.called
