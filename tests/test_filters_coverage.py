"""Coverage-closing tests for filters.py's remaining branches: empty pattern,
the Windows-only nt branches (exercised via `os.name` monkeypatching, since
their logic is plain string/attribute manipulation that needs no real
Windows filesystem), `is_protected`'s name-match fallback, and the defensive
`except Exception` branches around file-attribute lookups.
"""

from __future__ import annotations

import os

import filters


def _settings(**overrides):
    settings = {
        "filter_rules": [],
        "follow_symlinks": False,
        "ignore_empty_files": True,
        "scan_hidden": False,
    }
    settings.update(overrides)
    return settings


def test_match_rule_empty_pattern_never_matches():
    assert filters.match_rule("name.txt", "/a/name.txt", {"enabled": True, "pattern": "  "}) is False


def test_long_path_adds_windows_prefix_when_platform_is_nt(monkeypatch):
    monkeypatch.setattr(filters.os, "name", "nt")
    result = filters.long_path("C:/some/path")
    assert result.startswith("\\\\?\\")


def test_long_path_leaves_posix_paths_untouched():
    assert filters.long_path("/some/path") == "/some/path"


def test_is_hidden_checks_windows_file_attribute_when_nt(monkeypatch):
    monkeypatch.setattr(filters.os, "name", "nt")

    class FakeStat:
        st_file_attributes = filters.stat.FILE_ATTRIBUTE_HIDDEN

    monkeypatch.setattr(filters.os, "stat", lambda path: FakeStat())
    assert filters.is_hidden("not-dotfile.txt") is True


def test_is_hidden_swallows_stat_errors_on_nt(monkeypatch, capsys):
    monkeypatch.setattr(filters.os, "name", "nt")

    def raise_stat(_path):
        raise OSError("simulated stat failure")

    monkeypatch.setattr(filters.os, "stat", raise_stat)
    assert filters.is_hidden("not-dotfile.txt") is False
    assert "Ignored Exception" in capsys.readouterr().err


def test_is_system_checks_windows_file_attribute_when_nt(monkeypatch):
    monkeypatch.setattr(filters.os, "name", "nt")

    class FakeStat:
        st_file_attributes = filters.stat.FILE_ATTRIBUTE_SYSTEM

    monkeypatch.setattr(filters.os, "stat", lambda path: FakeStat())
    assert filters.is_system("anything") is True


def test_is_system_swallows_stat_errors_on_nt(monkeypatch, capsys):
    monkeypatch.setattr(filters.os, "name", "nt")

    def raise_stat(_path):
        raise OSError("simulated stat failure")

    monkeypatch.setattr(filters.os, "stat", raise_stat)
    assert filters.is_system("anything") is False
    assert "Ignored Exception" in capsys.readouterr().err


def test_is_protected_ignores_blank_entries(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    assert filters.is_protected(str(target), ["", "   "]) is False


def test_is_protected_matches_by_basename_fallback(tmp_path):
    target = tmp_path / "MyProject"
    target.mkdir()
    # Not a path prefix match -- an unrelated directory that merely SHARES a
    # basename with the target is still treated as protected.
    assert filters.is_protected(str(target), ["/somewhere/else/MyProject"]) is True


def test_file_empty_check_disabled_by_settings(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    assert filters._is_file_empty(str(empty_file), _settings(ignore_empty_files=False)) is False


def test_file_empty_check_swallows_getsize_errors(monkeypatch):
    def raise_getsize(_path):
        raise OSError("simulated getsize failure")

    monkeypatch.setattr(filters.os.path, "getsize", raise_getsize)
    assert filters._is_file_empty("/does/not/matter", _settings()) is False


def test_file_hidden_check_disabled_by_scan_hidden_setting(tmp_path):
    dotfile = tmp_path / ".hidden"
    dotfile.write_text("x", encoding="utf-8")
    assert filters._is_file_hidden(str(dotfile), _settings(scan_hidden=True)) is False


def test_file_hidden_check_swallows_errors(monkeypatch):
    def raise_is_hidden(_path):
        raise OSError("simulated is_hidden failure")

    monkeypatch.setattr(filters, "is_hidden", raise_is_hidden)
    assert filters._is_file_hidden("/does/not/matter", _settings()) is False


def test_is_ignorable_file_swallows_isdir_errors(monkeypatch):
    def raise_isdir(_path):
        raise OSError("simulated isdir failure")

    monkeypatch.setattr(filters.os.path, "isdir", raise_isdir)
    # isdir failing is treated as "skip it" (True = ignorable), fail-safe.
    assert filters._is_ignorable_file("entry", "/does/not/matter", _settings()) is True


def test_is_ignorable_file_skips_symlinks_when_not_following(tmp_path):
    real = tmp_path / "real.txt"
    real.write_text("content", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(real)

    assert filters._is_ignorable_file("link.txt", str(link), _settings(follow_symlinks=False)) is True


def test_has_only_ignorable_files_returns_false_on_listdir_error(monkeypatch):
    def raise_listdir(_path):
        raise PermissionError("simulated permission denied")

    monkeypatch.setattr(filters.os, "listdir", raise_listdir)
    assert filters.has_only_ignorable_files("/does/not/matter", _settings()) is False


def test_collect_ignorable_files_skips_entries_whose_isdir_check_fails(tmp_path, monkeypatch):
    target = tmp_path / "mixed"
    target.mkdir()
    (target / "real_file.txt").write_text("keep me", encoding="utf-8")
    (target / "empty.tmp").write_text("", encoding="utf-8")
    (target / "subdir").mkdir()  # real directories are skipped, not collected
    real_isdir = os.path.isdir

    def flaky_isdir(path):
        if os.path.basename(path) == "real_file.txt":
            raise OSError("simulated isdir failure")
        return real_isdir(path)

    monkeypatch.setattr(filters.os.path, "isdir", flaky_isdir)

    result = filters.collect_ignorable_files(str(target), _settings())

    # real_file.txt: isdir check raised -> treated as "continue", excluded.
    # empty.tmp: zero-byte -> ignorable, included.
    assert {os.path.basename(p) for p in result} == {"empty.tmp"}
