from __future__ import annotations

import contextlib
import io
from pathlib import Path

import red
from core import Cleaner, ScanResult, Scanner


def _make_settings(**overrides):
    settings = {
        "filter_rules": [],
        "protected_dirs": [],
        "max_depth": 0,
        "min_age_hours": 0,
        "ignore_empty_files": True,
        "scan_hidden": False,
        "follow_symlinks": False,
        "delete_mode": "simulate",
        "pause_ms": 0,
        "max_warnings": 10,
    }
    settings.update(overrides)
    return settings


def test_cli_dry_run_exports_and_preserves_tree(tmp_path):
    root = tmp_path / "root"
    nested = root / "alpha" / "beta"
    nested.mkdir(parents=True)
    (root / "keep.txt").write_text("keep", encoding="utf-8")
    export_path = tmp_path / "results.csv"

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = red._run_cli(
            ["--scan", str(root), "--dry-run", "--export", str(export_path)]
        )

    assert exit_code == 0
    assert root.exists()
    assert nested.exists()
    assert export_path.exists()
    assert "carpetas vacías encontradas" in stdout.getvalue()
    assert "Modo simulación" in stdout.getvalue()
    assert stderr.getvalue() == ""


def test_cli_rejects_missing_paths_without_scanning(tmp_path):
    missing = tmp_path / "missing"
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = red._run_cli(["--scan", str(missing), "--dry-run"])

    assert exit_code == 1
    assert "ruta invalida o inexistente" in stderr.getvalue()
    assert "carpetas vacías encontradas" not in stdout.getvalue()


def test_scanner_finds_nested_effectively_empty_dirs(tmp_path):
    root = tmp_path / "scan"
    leaf = root / "a" / "b"
    leaf.mkdir(parents=True)
    results = []
    done = []

    scanner = Scanner(
        settings=_make_settings(),
        on_found=results.append,
        on_done=lambda count: done.append(count),
    )
    scanner.scan([str(root)])
    scanner._thread.join(timeout=5)

    assert done == [2]
    assert [Path(r.path).name for r in results] == ["b", "a"]
    assert all(r.status == "empty" for r in results)


def test_cleaner_simulate_mode_preserves_paths(tmp_path):
    root = tmp_path / "cleanup"
    root.mkdir()
    result = ScanResult(path=str(root), status="empty", depth=1, selected=True)
    logs = []
    deleted = []
    errors = []
    done = []

    cleaner = Cleaner(
        settings=_make_settings(delete_mode="simulate"),
        on_deleted=deleted.append,
        on_log=logs.append,
        on_done=lambda count, freed: done.append((count, freed)),
        on_error=lambda item, exc: errors.append((item, exc)),
    )

    assert cleaner._delete_one(result, "simulate") == 0
    assert root.exists()
    assert deleted == []
    assert errors == []
    assert any("SIMULACIÓN" in msg for msg in logs)

