"""Coverage-closing tests for core.py's Scanner and Cleaner.

Targets the branches `test_red_core_behaviour.py` doesn't reach: single-string
scan(), mid-loop stop(), error/edge branches in `_process_dir`, and the full
`Cleaner._run` -> `_delete_one` -> `_purge_ignorable_files` pipeline across all
three delete modes (simulate/recycle/permanent), including their error paths.
"""

from __future__ import annotations

import os
import sys

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


# --------------------------------------------------------------------------
# Scanner
# --------------------------------------------------------------------------


def test_scanner_scan_accepts_single_string_path(tmp_path):
    root = tmp_path / "container"
    leaf = root / "leaf"
    leaf.mkdir(parents=True)
    done = []
    scanner = Scanner(settings=_make_settings(), on_done=done.append)

    scanner.scan(str(root))  # not a list -- exercises the str->[str] branch

    assert scanner._thread is not None
    scanner._thread.join(timeout=5)
    # The scan root itself is never counted, only its empty descendants.
    assert done == [1]


def test_scanner_stop_sets_event():
    scanner = Scanner(settings=_make_settings())
    assert not scanner._stop.is_set()
    scanner.stop()
    assert scanner._stop.is_set()


def test_scanner_run_stops_between_roots(tmp_path):
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    root_a.mkdir()
    root_b.mkdir()
    done = []

    scanner = Scanner(settings=_make_settings(), on_done=done.append)
    scanner._stop.set()  # already stopped before _run starts iterating
    scanner._run([str(root_a), str(root_b)])

    # Nothing scanned: the per-root loop breaks immediately (line 87), so
    # neither root's _scan_root ever ran and the total stays 0.
    assert done == [0]


def test_scan_root_invalid_path_logs_error(tmp_path):
    missing = tmp_path / "does-not-exist"
    logs = []
    scanner = Scanner(settings=_make_settings(), on_log=logs.append)

    count = scanner._scan_root(str(missing))

    assert count == 0
    assert any("SCAN ERROR: invalid or missing path" in m for m in logs)


def test_scan_root_stops_mid_walk(tmp_path):
    root = tmp_path / "root"
    (root / "one").mkdir(parents=True)
    (root / "two").mkdir(parents=True)

    scanner = Scanner(settings=_make_settings())
    scanner._stop.set()  # stop is already requested before the walk begins

    count = scanner._scan_root(str(root))

    assert count == 0


def test_scan_root_handles_walk_exception(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    logs = []
    scanner = Scanner(settings=_make_settings(), on_log=logs.append)

    def boom(*_args, **_kwargs):
        raise OSError("simulated os.walk failure")
        yield  # pragma: no cover - makes this a generator function

    monkeypatch.setattr(os, "walk", boom)

    count = scanner._scan_root(str(root))

    assert count == 0
    assert any("SCAN ERROR: simulated os.walk failure" in m for m in logs)


def test_process_dir_max_depth_exceeded(tmp_path):
    root = tmp_path / "root"
    leaf = root / "a" / "b"
    leaf.mkdir(parents=True)
    scanner = Scanner(settings=_make_settings(max_depth=1))

    result = scanner._process_dir(str(leaf), [], str(root), set())

    assert result is False


def test_process_dir_symlink_skipped_when_not_following(tmp_path):
    root = tmp_path / "root"
    real = tmp_path / "real"
    real.mkdir()
    root.mkdir()
    link = root / "link"
    link.symlink_to(real, target_is_directory=True)

    scanner = Scanner(settings=_make_settings(follow_symlinks=False))
    result = scanner._process_dir(str(link), [], str(root), set())

    assert result is False


def test_process_dir_waits_for_all_subdirs_to_be_empty(tmp_path):
    root = tmp_path / "root"
    parent = root / "parent"
    child = parent / "child"
    child.mkdir(parents=True)

    scanner = Scanner(settings=_make_settings())
    # `child` is NOT in would_be_empty yet, so `parent` cannot be either.
    result = scanner._process_dir(str(parent), ["child"], str(root), set())

    assert result is False


def test_process_dir_real_file_blocks_emptiness(tmp_path):
    root = tmp_path / "root"
    target = root / "has-file"
    target.mkdir(parents=True)
    (target / "keep.txt").write_text("real content", encoding="utf-8")

    scanner = Scanner(settings=_make_settings())
    result = scanner._process_dir(str(target), [], str(root), set())

    assert result is False


def test_process_dir_min_age_hours_too_recent(tmp_path):
    root = tmp_path / "root"
    target = root / "fresh"
    target.mkdir(parents=True)

    scanner = Scanner(settings=_make_settings(min_age_hours=1000))
    result = scanner._process_dir(str(target), [], str(root), set())

    assert result is False


def test_process_dir_is_dir_ignored_by_filter_rule(tmp_path):
    root = tmp_path / "root"
    target = root / "skip_me"
    target.mkdir(parents=True)
    rules = [{"enabled": True, "type": "ignore_dir", "method": "exact", "pattern": "skip_me"}]

    scanner = Scanner(settings=_make_settings(filter_rules=rules))
    result = scanner._process_dir(str(target), [], str(root), set())

    assert result is False


def test_process_dir_protected_dir_reports_but_does_not_select(tmp_path):
    root = tmp_path / "root"
    target = root / "protected_one"
    target.mkdir(parents=True)
    found = []
    logs = []

    scanner = Scanner(
        settings=_make_settings(protected_dirs=[str(target)]),
        on_found=found.append,
        on_log=logs.append,
    )
    would_be_empty: set = set()
    result = scanner._process_dir(str(target), [], str(root), would_be_empty)

    assert result is False
    assert os.path.normcase(str(target)) in would_be_empty
    assert len(found) == 1
    assert found[0].status == "protected"
    assert found[0].selected is False
    assert any("Protected:" in m for m in logs)


def test_process_dir_never_empty_rule(tmp_path):
    root = tmp_path / "root"
    target = root / "logs"
    target.mkdir(parents=True)
    rules = [{"enabled": True, "type": "never_empty", "method": "exact", "pattern": "logs"}]
    logs = []

    scanner = Scanner(settings=_make_settings(filter_rules=rules), on_log=logs.append)
    result = scanner._process_dir(str(target), [], str(root), set())

    assert result is False
    assert any("Never-empty rule:" in m for m in logs)


# --------------------------------------------------------------------------
# Cleaner
# --------------------------------------------------------------------------


def test_cleaner_delete_starts_thread_and_stop_sets_event(tmp_path):
    root = tmp_path / "cleanup"
    root.mkdir()
    result = ScanResult(path=str(root), status="empty", depth=0, selected=True)
    done = []

    cleaner = Cleaner(settings=_make_settings(), on_done=lambda c, b: done.append((c, b)))
    assert not cleaner._stop.is_set()
    cleaner.delete([result])
    assert cleaner._thread is not None
    cleaner._thread.join(timeout=5)
    assert done == [(1, 0)]

    cleaner.stop()
    assert cleaner._stop.is_set()


def test_cleaner_run_deletes_deepest_first_and_respects_pause(tmp_path):
    shallow = tmp_path / "shallow"
    deep = tmp_path / "deep"
    shallow.mkdir()
    deep.mkdir()
    results = [
        ScanResult(path=str(shallow), status="empty", depth=1, selected=True),
        ScanResult(path=str(deep), status="empty", depth=3, selected=True),
        ScanResult(path=str(tmp_path / "unselected"), status="empty", depth=5, selected=False),
        ScanResult(path=str(tmp_path / "protected"), status="protected", depth=2, selected=False),
    ]
    deleted = []
    logs = []

    cleaner = Cleaner(
        settings=_make_settings(delete_mode="simulate", pause_ms=1),
        on_deleted=deleted.append,
        on_log=logs.append,
    )
    cleaner._run(results)

    # Deepest-first, and only selected+empty entries are candidates.
    assert [r.path for r in deleted] == [str(deep), str(shallow)]
    assert any("Process complete" in m for m in logs)


def test_cleaner_run_stops_after_max_warnings(tmp_path):
    missing_a = tmp_path / "missing_a"
    missing_b = tmp_path / "missing_b"
    results = [
        ScanResult(path=str(missing_a), status="empty", depth=1, selected=True),
        ScanResult(path=str(missing_b), status="empty", depth=1, selected=True),
    ]
    errors = []
    logs = []

    cleaner = Cleaner(
        settings=_make_settings(delete_mode="permanent", max_warnings=1),
        on_error=lambda item, exc: errors.append((item, exc)),
        on_log=logs.append,
    )
    cleaner._run(results)

    assert len(errors) == 1
    assert any("Too many errors" in m for m in logs)


def test_cleaner_run_stops_mid_deletion_loop(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    results = [
        ScanResult(path=str(first), status="empty", depth=1, selected=True),
        ScanResult(path=str(second), status="empty", depth=1, selected=True),
    ]

    cleaner = Cleaner(settings=_make_settings(delete_mode="simulate"))
    cleaner._stop.set()  # stop requested before the deletion loop starts

    cleaner._run(results)

    # Nothing simulated/deleted: the loop breaks on the first stop check.
    assert first.exists()
    assert second.exists()


def test_delete_one_permanent_mode_purges_ignorable_files_then_removes_dir(tmp_path):
    target = tmp_path / "junk"
    target.mkdir()
    (target / "empty.tmp").write_text("", encoding="utf-8")  # zero-byte -> ignorable
    result = ScanResult(path=str(target), status="empty", depth=0, selected=True)

    cleaner = Cleaner(settings=_make_settings())
    freed = cleaner._delete_one(result, "permanent")

    assert freed == 0  # zero-byte file frees 0 bytes
    assert not target.exists()


def test_delete_one_permanent_mode_ignores_chmod_failure(tmp_path, monkeypatch):
    target = tmp_path / "chmod_fails"
    target.mkdir()
    result = ScanResult(path=str(target), status="empty", depth=0, selected=True)
    real_chmod = os.chmod

    def flaky_chmod(path, *args, **kwargs):
        if os.path.normpath(path) == os.path.normpath(str(target)):
            raise OSError("simulated chmod failure")
        return real_chmod(path, *args, **kwargs)

    monkeypatch.setattr(os, "chmod", flaky_chmod)

    cleaner = Cleaner(settings=_make_settings())
    freed = cleaner._delete_one(result, "permanent")

    assert freed == 0
    assert not target.exists()  # rmdir still ran despite the chmod failure


def test_delete_one_permission_error(tmp_path, monkeypatch):
    target = tmp_path / "locked"
    target.mkdir()
    result = ScanResult(path=str(target), status="empty", depth=0, selected=True)
    errors = []

    def raise_permission_error(_path):
        raise PermissionError("simulated permission denied")

    monkeypatch.setattr(os, "rmdir", raise_permission_error)

    cleaner = Cleaner(settings=_make_settings(), on_error=lambda item, exc: errors.append((item, exc)))
    freed = cleaner._delete_one(result, "permanent")

    assert freed is None
    assert len(errors) == 1
    assert isinstance(errors[0][1], PermissionError)


def test_delete_one_generic_exception(tmp_path, monkeypatch):
    target = tmp_path / "weird"
    target.mkdir()
    result = ScanResult(path=str(target), status="empty", depth=0, selected=True)
    errors = []

    def raise_os_error(_path):
        raise OSError("simulated directory not empty")

    monkeypatch.setattr(os, "rmdir", raise_os_error)

    cleaner = Cleaner(settings=_make_settings(), on_error=lambda item, exc: errors.append((item, exc)))
    freed = cleaner._delete_one(result, "permanent")

    assert freed is None
    assert len(errors) == 1


def test_delete_one_recycle_mode_without_send2trash_dependency(tmp_path):
    # send2trash is not an installed dependency of this repo (see
    # requirements.txt): the ImportError inside `_delete_one`'s recycle
    # branch is real, not simulated, and its `except Exception` handler is
    # what this exercises.
    target = tmp_path / "to_recycle"
    target.mkdir()
    result = ScanResult(path=str(target), status="empty", depth=0, selected=True)
    errors = []
    logs = []

    cleaner = Cleaner(
        settings=_make_settings(),
        on_error=lambda item, exc: errors.append((item, exc)),
        on_log=logs.append,
    )
    freed = cleaner._delete_one(result, "recycle")

    assert freed is None
    assert len(errors) == 1
    assert any("ERROR (Recycle Bin)" in m for m in logs)


def test_delete_one_recycle_mode_success_with_fake_send2trash(tmp_path, monkeypatch):
    import types

    target = tmp_path / "to_recycle_ok"
    target.mkdir()
    result = ScanResult(path=str(target), status="empty", depth=0, selected=True)
    calls = []

    fake_module = types.SimpleNamespace(send2trash=lambda path: calls.append(path))
    monkeypatch.setitem(sys.modules, "send2trash", fake_module)

    cleaner = Cleaner(settings=_make_settings())
    freed = cleaner._delete_one(result, "recycle")

    assert freed == 0
    assert calls == [str(target)]


def test_purge_ignorable_files_handles_getsize_and_remove_errors(tmp_path, monkeypatch):
    target = tmp_path / "purge_me"
    target.mkdir()
    # Non-empty content, made ignorable via an explicit filter rule instead
    # of zero-byte emptiness: `_is_file_empty` (in filters.py) also calls
    # `os.path.getsize` to classify a file, and that call shares the same
    # patched `os.path.getsize` -- routing ignorability through a filter
    # rule instead keeps the getsize failure isolated to core.py's own
    # freed-bytes accounting, which is what this test targets.
    (target / "a.tmp").write_text("some real content", encoding="utf-8")
    (target / "b.tmp").write_text("some real content", encoding="utf-8")
    rules = [{"enabled": True, "type": "ignore_file", "method": "wildcard", "pattern": "*.tmp"}]
    real_getsize = os.path.getsize
    real_remove = os.remove

    def flaky_getsize(path):
        if os.path.basename(path) == "a.tmp":
            raise OSError("simulated getsize failure")
        return real_getsize(path)

    def flaky_remove(path):
        if os.path.basename(path) == "b.tmp":
            raise OSError("simulated remove failure")
        return real_remove(path)

    monkeypatch.setattr(os.path, "getsize", flaky_getsize)
    monkeypatch.setattr(os, "remove", flaky_remove)

    cleaner = Cleaner(settings=_make_settings(filter_rules=rules))
    freed = cleaner._purge_ignorable_files(str(target))

    # a.tmp: getsize failed (contributes 0 bytes, logged and ignored), but
    # remove still succeeds since only getsize was patched to fail for it.
    # b.tmp: getsize succeeded but remove failed (logged and ignored), so it
    # survives on disk.
    assert freed == len("some real content")  # only b.tmp's real size counted
    assert not (target / "a.tmp").exists()  # getsize failed, remove still ran
    assert (target / "b.tmp").exists()  # remove failed, file survives
