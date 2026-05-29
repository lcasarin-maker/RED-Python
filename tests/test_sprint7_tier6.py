"""
TEST: test_sprint7_tier6.py
Tests de integracion Sprint 7 -- Tier 6.
Cubre: headspace_auto_trigger, token_optimizer, compact_automation_helper.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── helpers ──────────────────────────────────────────────────────────────────

def _make_historial(path: Path, size_kb: int = 1) -> None:
    path.write_text("# HISTORIAL\n\n" + ("x" * (size_kb * 1024)), encoding="utf-8")


def _make_status(path: Path) -> None:
    path.write_text("## CAMPO 1: Project\nProject info.\n\n## CAMPO 6: Next\nNext session.\n",
                    encoding="utf-8")


# ─── headspace_auto_trigger ───────────────────────────────────────────────────

class TestHeadspaceAutoTrigger:
    def test_estimate_context_usage_empty_dir(self, tmp_path):
        from scripts.headspace_auto_trigger import HeadspaceAutoTrigger
        trigger = HeadspaceAutoTrigger(
            historial_path=tmp_path / "ghost.md",
            status_path=tmp_path / "ghost2.md",
        )
        result = trigger.estimate_context_usage()
        # Ghost historial + status contribute 0; AGENT.md/CLAUDE.md from CWD may add a baseline
        assert isinstance(result, int)
        assert result >= 0

    def test_estimate_context_usage_with_file(self, tmp_path):
        from scripts.headspace_auto_trigger import HeadspaceAutoTrigger
        h = tmp_path / "HISTORIAL.md"
        _make_historial(h, size_kb=4)
        trigger = HeadspaceAutoTrigger(historial_path=h, status_path=tmp_path / "ghost.md")
        result = trigger.estimate_context_usage()
        assert result > 0

    def test_check_below_threshold_should_compress_false(self, tmp_path):
        from scripts.headspace_auto_trigger import HeadspaceAutoTrigger
        # Empty files → 0 tokens → below 75% threshold
        trigger = HeadspaceAutoTrigger(
            historial_path=tmp_path / "ghost.md",
            status_path=tmp_path / "ghost2.md",
        )
        report = trigger.check()
        assert report["should_compress"] is False
        # Negative: empty context never exceeds threshold
        assert report["context_percentage"] < 75.0

    def test_check_report_has_required_keys(self, tmp_path):
        from scripts.headspace_auto_trigger import HeadspaceAutoTrigger
        trigger = HeadspaceAutoTrigger(
            historial_path=tmp_path / "ghost.md",
            status_path=tmp_path / "ghost2.md",
        )
        report = trigger.check()
        for key in ("context_tokens", "context_percentage", "threshold", "should_compress"):
            assert key in report

    def test_trigger_compression_returns_list(self):
        from scripts.headspace_auto_trigger import HeadspaceAutoTrigger
        trigger = HeadspaceAutoTrigger()
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "err"
        with patch("scripts.headspace_auto_trigger.subprocess.run", return_value=mock_result):
            actions = trigger.trigger_compression()
        assert isinstance(actions, list)
        assert len(actions) > 0
        # Always appends recommendation even when sub-scripts fail
        assert any("compact" in a.lower() for a in actions)
        # Negative: successful action list is empty when all sub-scripts fail
        successful = [a for a in actions if "recommend" not in a.lower() and "compact" not in a.lower()]
        assert successful == []

    def test_get_report_no_compress_when_empty(self, tmp_path):
        from scripts.headspace_auto_trigger import HeadspaceAutoTrigger
        trigger = HeadspaceAutoTrigger(
            historial_path=tmp_path / "ghost.md",
            status_path=tmp_path / "ghost2.md",
        )
        report = trigger.get_report()
        assert report["should_compress"] is False
        # Negative: no "actions" key when compress not triggered
        assert "actions" not in report

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "headspace_auto_trigger.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "setup_windows_utf8" in source

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "headspace_auto_trigger.py").read_text(encoding="utf-8")
        assert "D:" + "/GoogleDrive" not in source
        assert "D:" + chr(92) + "GoogleDrive" not in source



# ─── compact_automation_helper ────────────────────────────────────────────────

class TestCompactAutomationHelper:
    def test_run_compress_historial_failure_returns_false(self, tmp_path):
        from scripts.compact_automation_helper import CompactAutomationHelper
        helper = CompactAutomationHelper(project_dir=tmp_path)
        mock_fail = MagicMock()
        mock_fail.returncode = 1
        mock_fail.stderr = "error"
        with patch("scripts.compact_automation_helper.subprocess.run", return_value=mock_fail):
            result = helper.run_compress_historial()
        assert result is False

    def test_run_compress_historial_success_returns_true(self, tmp_path):
        from scripts.compact_automation_helper import CompactAutomationHelper
        helper = CompactAutomationHelper(project_dir=tmp_path)
        mock_ok = MagicMock()
        mock_ok.returncode = 0
        with patch("scripts.compact_automation_helper.subprocess.run", return_value=mock_ok):
            result = helper.run_compress_historial()
        assert result is True

    def test_auto_compact_prepare_returns_dict_with_timestamp(self, tmp_path):
        from scripts.compact_automation_helper import CompactAutomationHelper
        helper = CompactAutomationHelper(project_dir=tmp_path)
        mock_ok = MagicMock()
        mock_ok.returncode = 0
        with patch("scripts.compact_automation_helper.subprocess.run", return_value=mock_ok):
            results = helper.auto_compact_prepare()
        assert "timestamp" in results
        assert isinstance(results["timestamp"], str)

    def test_auto_compact_prepare_all_fail_returns_false_values(self, tmp_path):
        from scripts.compact_automation_helper import CompactAutomationHelper
        helper = CompactAutomationHelper(project_dir=tmp_path)
        mock_fail = MagicMock()
        mock_fail.returncode = 1
        mock_fail.stderr = "error"
        with patch("scripts.compact_automation_helper.subprocess.run", return_value=mock_fail):
            results = helper.auto_compact_prepare()
        bool_values = [v for k, v in results.items() if isinstance(v, bool)]
        # Negative: all 4 tasks should fail → none succeeded
        succeeded = [v for v in bool_values if v is True]
        assert succeeded == []
        assert len(bool_values) == 4

    def test_run_headspace_trigger_success(self, tmp_path):
        from scripts.compact_automation_helper import CompactAutomationHelper
        helper = CompactAutomationHelper(project_dir=tmp_path)
        mock_ok = MagicMock()
        mock_ok.returncode = 0
        with patch("scripts.compact_automation_helper.subprocess.run", return_value=mock_ok):
            result = helper.run_headspace_trigger()
        assert result is True

    def test_uses_sys_executable_not_python_string(self):
        source = (PROJECT_ROOT / "scripts" / "compact_automation_helper.py").read_text(encoding="utf-8")
        assert "sys.executable" in source
        assert '"python"' not in source

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "compact_automation_helper.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "setup_windows_utf8" in source
