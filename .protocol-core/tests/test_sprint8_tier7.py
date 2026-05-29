"""
TEST: test_sprint8_tier7.py
Tests de integracion Sprint 8 -- Tier 7.
Cubre: protocol_cli (ProtocolClient), automation_scheduler (AutomationScheduler).
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── protocol_cli ─────────────────────────────────────────────────────────────

class TestProtocolClient:
    def test_log_evidence_creates_json_file(self, tmp_path):
        from scripts.protocol_cli import ProtocolClient
        cli = ProtocolClient()
        cli.evidence_dir = tmp_path / "evidence"
        cli.evidence_dir.mkdir()
        cli._log_evidence("test_op", "success", {"key": "value"})
        files = list((tmp_path / "evidence").glob("*.json"))
        assert len(files) == 1

    def test_log_evidence_json_contains_operation(self, tmp_path):
        import json
        from scripts.protocol_cli import ProtocolClient
        cli = ProtocolClient()
        cli.evidence_dir = tmp_path / "ev"
        cli.evidence_dir.mkdir()
        cli._log_evidence("check", "failure", {"detail": "x"})
        data = json.loads(list(cli.evidence_dir.glob("*.json"))[0].read_text(encoding="utf-8"))
        assert data["operation"] == "check"
        assert data["outcome"] == "failure"

    def test_check_compact_no_historial_returns_none(self, tmp_path):
        # P6.8: function moved to core_utils — test the canonical location
        from scripts.core_utils import check_compact_sessions
        result = check_compact_sessions(tmp_path)
        assert result is None

    def test_calculate_compact_threshold_returns_dict(self):
        # P6.8: function moved to core_utils — test the canonical location
        from scripts.core_utils import check_compact_threshold
        ctx = check_compact_threshold(Path("."))
        assert "context_pct" in ctx
        assert "status" in ctx
        assert ctx["context_pct"] >= 0

    def test_calculate_compact_threshold_status_values(self):
        # P6.8: function moved to core_utils — test the canonical location
        from scripts.core_utils import check_compact_threshold
        ctx = check_compact_threshold(Path("."))
        assert ctx["status"] in ("SAFE", "WARNING", "COMPACT_NOW")

    def test_command_evidence_returns_zero(self, tmp_path):
        from scripts.protocol_cli import ProtocolClient
        cli = ProtocolClient()
        cli.evidence_dir = tmp_path / "ev"
        cli.evidence_dir.mkdir()
        result = cli.command_evidence(last_n=5)
        assert result == 0

    def test_run_unknown_command_returns_127(self):
        from scripts.protocol_cli import ProtocolClient
        cli = ProtocolClient()
        result = cli.run(["nonexistent_command"])
        assert result == 127

    def test_run_help_returns_zero(self):
        from scripts.protocol_cli import ProtocolClient
        cli = ProtocolClient()
        result = cli.run(["--help"])
        assert result == 0

    def test_command_install_no_hooks_dir_returns_one(self, tmp_path):
        from scripts.protocol_cli import ProtocolClient
        cli = ProtocolClient()
        cli.project_root = tmp_path
        result = cli.command_install()
        # Negative: no scripts/hooks/ directory → should fail
        assert result == 1

    def test_no_typing_imports(self):
        source = (PROJECT_ROOT / "scripts" / "protocol_cli.py").read_text(encoding="utf-8")
        assert "from typing import" not in source
        assert "Dict" not in source
        assert "List" not in source


# ─── automation_scheduler ─────────────────────────────────────────────────────

class TestAutomationScheduler:
    def test_default_tasks_not_empty(self):
        from scripts.automation_scheduler import AutomationScheduler
        sched = AutomationScheduler()
        assert len(sched.tasks) > 0

    def test_custom_tasks_accepted(self):
        from scripts.automation_scheduler import AutomationScheduler
        tasks = [{"name": "t1", "script": "scripts/sync_binding.py --check", "interval_s": 60}]
        sched = AutomationScheduler(tasks=tasks)
        assert len(sched.tasks) == 1
        assert sched.tasks[0]["name"] == "t1"

    def test_due_tasks_all_due_at_start(self):
        from scripts.automation_scheduler import AutomationScheduler
        tasks = [{"name": "t1", "script": "scripts/sync_binding.py --check", "interval_s": 1}]
        sched = AutomationScheduler(tasks=tasks)
        # At start, no tasks have run → all are due
        due = sched.due_tasks()
        assert len(due) == 1

    def test_due_tasks_none_due_after_run(self):
        from scripts.automation_scheduler import AutomationScheduler
        import time
        tasks = [{"name": "t1", "script": "x", "interval_s": 9999}]
        sched = AutomationScheduler(tasks=tasks)
        sched._last_run["t1"] = time.monotonic()
        due = sched.due_tasks()
        # Negative: tasks just run with large interval should NOT be due
        assert due == []

    def test_run_once_failure_reflected_in_results(self):
        from scripts.automation_scheduler import AutomationScheduler
        tasks = [{"name": "fail_task", "script": "scripts/__does_not_exist__.py", "interval_s": 60}]
        sched = AutomationScheduler(tasks=tasks)
        mock_fail = MagicMock()
        mock_fail.returncode = 1
        mock_fail.stderr = "not found"
        with patch("scripts.automation_scheduler.subprocess.run", return_value=mock_fail):
            results = sched.run_once()
        assert results["fail_task"] is False
        # Negative: failed tasks list is non-empty
        failed = [k for k, v in results.items() if not v]
        assert failed == ["fail_task"]

    def test_run_once_success_returns_true(self):
        from scripts.automation_scheduler import AutomationScheduler
        tasks = [{"name": "ok_task", "script": "scripts/sync_binding.py --check", "interval_s": 60}]
        sched = AutomationScheduler(tasks=tasks)
        mock_ok = MagicMock()
        mock_ok.returncode = 0
        with patch("scripts.automation_scheduler.subprocess.run", return_value=mock_ok):
            results = sched.run_once()
        assert results["ok_task"] is True

    def test_tick_only_runs_due_tasks(self):
        from scripts.automation_scheduler import AutomationScheduler
        import time
        tasks = [
            {"name": "due",     "script": "x", "interval_s": 0},
            {"name": "not_due", "script": "y", "interval_s": 9999},
        ]
        sched = AutomationScheduler(tasks=tasks)
        sched._last_run["not_due"] = time.monotonic()
        mock_ok = MagicMock()
        mock_ok.returncode = 0
        with patch("scripts.automation_scheduler.subprocess.run", return_value=mock_ok):
            results = sched.tick()
        # Only the due task should appear in results
        assert "due" in results
        assert "not_due" not in results

    def test_uses_sys_executable_not_python_string(self):
        source = (PROJECT_ROOT / "scripts" / "automation_scheduler.py").read_text(encoding="utf-8")
        assert "sys.executable" in source
        assert '"python"' not in source

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "automation_scheduler.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "setup_windows_utf8" in source
