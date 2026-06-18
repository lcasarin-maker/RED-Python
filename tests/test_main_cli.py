from __future__ import annotations

import contextlib
import io

import red


def test_main_cli_smoke(tmp_path):
    root = tmp_path / "main"
    root.mkdir()

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = red._run_cli(["--scan", str(root), "--dry-run"])

    assert exit_code == 0
    assert "empty folders found" in stdout.getvalue()
    assert stderr.getvalue() == ""
