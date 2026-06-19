from __future__ import annotations

from pathlib import Path

import filters


def test_match_rule_supports_all_methods(tmp_path):
    full_path = tmp_path / "Folder Name"
    full_path.mkdir()
    file_path = full_path / "Sample.TXT"
    file_path.write_text("content", encoding="utf-8")

    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "wildcard", "pattern": "*.txt"}
    )
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "contains", "pattern": "amp"}
    )
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "startswith", "pattern": "sam"}
    )
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "endswith", "pattern": "txt"}
    )
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "exact", "pattern": "SAMPLE.TXT"}
    )
    assert filters.match_rule(
        "sample.txt",
        str(file_path),
        {"enabled": True, "method": "exact_path", "pattern": str(file_path)},
    )
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "regex_name", "pattern": r"sample\.(txt|md)"}
    )
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "regex_path", "pattern": r"Folder Name"}
    )
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": True, "method": "regex_name", "pattern": "["}
    ) is False
    assert filters.match_rule(
        "sample.txt", str(file_path), {"enabled": False, "method": "wildcard", "pattern": "*.txt"}
    ) is False


def test_filter_helpers_classify_rules_and_paths(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    child = root / "child"
    child.mkdir()
    ignored = child / "skip.tmp"
    ignored.write_text("ignore", encoding="utf-8")
    empty = child / "empty.txt"
    empty.write_text("", encoding="utf-8")
    hidden = child / ".hidden.txt"
    hidden.write_text("secret", encoding="utf-8")

    rules = [
        {"enabled": True, "type": "ignore_file", "method": "wildcard", "pattern": "*.tmp"},
        {"enabled": True, "type": "ignore_dir", "method": "exact", "pattern": "child"},
        {"enabled": True, "type": "never_empty", "method": "startswith", "pattern": "chi"},
    ]
    settings = {
        "filter_rules": rules,
        "ignore_empty_files": True,
        "scan_hidden": False,
        "follow_symlinks": False,
    }

    assert filters.is_file_ignored("skip.tmp", str(ignored), rules)
    assert filters.is_dir_ignored("child", str(child), rules)
    assert filters.is_never_empty("child", str(child), rules)
    assert filters.is_protected(str(child), [str(child)])
    assert filters.has_only_ignorable_files(str(child), settings)
    assert sorted(Path(path).name for path in filters.collect_ignorable_files(str(child), settings)) == [
        ".hidden.txt",
        "empty.txt",
        "skip.tmp",
    ]


def test_long_path_helpers_and_hidden_detection():
    path = r"C:\tmp\folder"
    assert filters.long_path(path).startswith("\\\\?\\") or filters.long_path(path) == path
    assert filters.strip_long_prefix("\\\\?\\C:\\tmp\\folder") == "C:\\tmp\\folder"
    assert filters.is_hidden(".dotfile")
    assert isinstance(filters.is_system("regular.txt"), bool)
    assert filters.get_age_hours("missing-file") == float("inf")
