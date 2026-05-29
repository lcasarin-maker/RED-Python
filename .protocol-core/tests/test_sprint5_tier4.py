"""
TEST: test_sprint5_tier4.py
Tests de integracion Sprint 5 -- Tier 4.
Cubre: global_sync_safe (GlobalSyncManager), rigor_maestro (run_suite).
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── GlobalSyncManager ────────────────────────────────────────────────────────

class TestGlobalSyncManager:
    def _make_registry(self, root: Path, projects: list) -> None:
        vib_dir = root / ".protocol" / "metadata"
        vib_dir.mkdir(parents=True, exist_ok=True)
        (vib_dir / "REGISTRY.json").write_text(
            json.dumps({"projects": projects}),
            encoding="utf-8",
        )

    def test_load_registry_missing_returns_empty(self, tmp_path):
        from scripts.global_sync_safe import GlobalSyncManager
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        result = mgr.load_registry()
        assert result == {}

    def test_load_registry_valid_json(self, tmp_path):
        from scripts.global_sync_safe import GlobalSyncManager
        self._make_registry(tmp_path, [{"name": "proj", "path": "/x", "role": "PROJECT"}])
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        reg = mgr.load_registry()
        assert "projects" in reg
        assert len(reg["projects"]) == 1

    def test_sync_project_skips_core_path(self, tmp_path):
        from scripts.global_sync_safe import GlobalSyncManager
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        result = mgr.sync_project({"name": "core", "path": str(tmp_path)})
        assert result["status"] == "skipped"
        assert result["reason"] == "core_path"

    def test_sync_project_skips_missing_path(self, tmp_path):
        from scripts.global_sync_safe import GlobalSyncManager
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        missing = tmp_path / "nonexistent_project"
        result = mgr.sync_project({"name": "ghost", "path": str(missing)})
        assert result["status"] == "skipped"
        assert result["reason"] == "path_not_found"

    def test_sync_project_skips_non_git_repo(self, tmp_path):
        from scripts.global_sync_safe import GlobalSyncManager
        proj = tmp_path / "not_git"
        proj.mkdir()
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        result = mgr.sync_project({"name": "not_git", "path": str(proj)})
        assert result["status"] == "skipped"
        assert result["reason"] == "not_git_repo"

    def test_sync_project_dry_run_returns_preview(self, tmp_path):
        from scripts.global_sync_safe import GlobalSyncManager
        proj = tmp_path / "proj"
        proj.mkdir()
        (proj / ".git").mkdir()
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        result = mgr.sync_project({"name": "proj", "path": str(proj)}, dry_run=True)
        assert result["status"] == "dry_run"
        assert "files" in result

    def test_sync_all_dry_run_no_writes(self, tmp_path):
        from scripts.global_sync_safe import GlobalSyncManager
        proj = tmp_path / "p1"
        proj.mkdir()
        (proj / ".git").mkdir()
        self._make_registry(tmp_path, [
            {"name": "core", "path": str(tmp_path), "role": "CORE"},
            {"name": "p1", "path": str(proj), "role": "PROJECT"},
        ])
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        with patch.object(mgr, "_copy_protocol_files_impl", return_value=[], create=True):
            result = mgr.sync_all(dry_run=True)
        assert result["mode"] == "dry_run"
        # Negative: failed count must be zero for a dry run of a valid project
        assert result["failed"] == 0

    def test_discover_no_env_var_returns_empty(self, tmp_path, monkeypatch):
        from scripts.global_sync_safe import GlobalSyncManager
        monkeypatch.delenv("CERBERUS_AI_ROOT", raising=False)
        mgr = GlobalSyncManager(core_path=str(tmp_path))
        result = mgr._discover_new_projects({})
        assert result == []

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "global_sync_safe.py").read_text(encoding="utf-8")
        assert "D:" + "/GoogleDrive" not in source
        assert "D:" + chr(92) + "GoogleDrive" not in source

    def test_no_unused_random_import(self):
        source = (PROJECT_ROOT / "scripts" / "global_sync_safe.py").read_text(encoding="utf-8")
        assert "import random" not in source

    def test_no_evidence_logger_dead_attr(self):
        source = (PROJECT_ROOT / "scripts" / "global_sync_safe.py").read_text(encoding="utf-8")
        assert "self.evidence_logger" not in source


# ─── rigor_maestro ────────────────────────────────────────────────────────────

class TestRigorMaestro:
    def test_test_suite_is_nonempty_list(self):
        from scripts.rigor_maestro import TEST_SUITE
        assert isinstance(TEST_SUITE, list)
        assert len(TEST_SUITE) > 0

    def test_all_suite_entries_have_required_keys(self):
        from scripts.rigor_maestro import TEST_SUITE
        required = {"name", "command", "critical"}
        missing_keys = [t for t in TEST_SUITE if not required.issubset(t.keys())]
        assert missing_keys == []

    def test_all_commands_use_sys_executable(self):
        from scripts.rigor_maestro import TEST_SUITE
        bad = [t for t in TEST_SUITE if t["command"][0] != sys.executable]
        assert bad == []

    def test_run_suite_returns_true_when_all_pass(self):
        from scripts.rigor_maestro import run_suite
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 passed"
        mock_result.stderr = ""
        with patch("scripts.rigor_maestro.subprocess.run", return_value=mock_result):
            result = run_suite()
        assert result is True

    def test_run_suite_returns_false_on_failure(self):
        from scripts.rigor_maestro import run_suite
        mock_fail = MagicMock()
        mock_fail.returncode = 1
        mock_fail.stdout = "FAILED"
        mock_fail.stderr = "error output"
        with patch("scripts.rigor_maestro.subprocess.run", return_value=mock_fail):
            result = run_suite()
        assert result is False

    def test_run_suite_returns_false_on_exception(self):
        from scripts.rigor_maestro import run_suite
        with patch("scripts.rigor_maestro.subprocess.run", side_effect=OSError("no proc")):
            result = run_suite()
        assert result is False

    def test_no_sys_path_append(self):
        source = (PROJECT_ROOT / "scripts" / "rigor_maestro.py").read_text(encoding="utf-8")
        assert "sys.path.append" not in source

    def test_subprocess_imported_at_module_level(self):
        source = (PROJECT_ROOT / "scripts" / "rigor_maestro.py").read_text(encoding="utf-8")
        lines = source.splitlines()
        import_line = next((i for i, l in enumerate(lines) if l.strip() == "import subprocess"), None)
        assert import_line is not None
        # Must be before any function/class definition
        first_def = next(i for i, l in enumerate(lines) if l.startswith("def ") or l.startswith("class "))
        assert import_line < first_def

    def test_uses_setup_windows_utf8(self):
        source = (PROJECT_ROOT / "scripts" / "rigor_maestro.py").read_text(encoding="utf-8")
        assert "setup_windows_utf8" in source
