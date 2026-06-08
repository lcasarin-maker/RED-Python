"""
TEST: test_sprint8_tier7.py
Tests de integracion Sprint 8 -- Tier 7.
Cubre: protocol_cli (ProtocolClient).
"""

import io
from pathlib import Path
from contextlib import redirect_stdout

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
        data = json.loads(
            list(cli.evidence_dir.glob("*.json"))[0].read_text(encoding="utf-8")
        )
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

    def test_check_compact_sessions_invalid_input_raises(self):
        # Negative path (D8): non-Path input must fail loudly, not silently
        from scripts.core_utils import check_compact_sessions

        with pytest.raises(TypeError) as exc:
            check_compact_sessions(None)
        assert exc.type is TypeError

    def test_check_compact_threshold_invalid_input_raises(self):
        # Negative path (D8): non-Path input must fail loudly, not silently
        from scripts.core_utils import check_compact_threshold

        with pytest.raises(TypeError) as exc:
            check_compact_threshold(None)
        assert exc.type is TypeError

    def test_command_evidence_returns_zero(self, tmp_path):
        from scripts.protocol_cli import ProtocolClient

        cli = ProtocolClient()
        cli.evidence_dir = tmp_path / "ev"
        cli.evidence_dir.mkdir()
        result = cli.command_evidence(last_n=5)
        assert result == 0

    def test_command_hygiene_reports_clean_workspace(self, tmp_path):
        from scripts.protocol_cli import ProtocolClient

        cli = ProtocolClient()
        cli.project_root = tmp_path
        cli.evidence_dir = tmp_path / ".protocol" / "evidence"
        cli.evidence_dir.mkdir(parents=True)
        result = cli.command_hygiene()
        assert result == 0

    def test_command_hygiene_fix_removes_transient_dirs(self, tmp_path):
        from scripts.protocol_cli import ProtocolClient

        (tmp_path / "scripts" / "automation" / "__pycache__").mkdir(parents=True)
        (tmp_path / "scripts" / "dashboard" / "__pycache__").mkdir(parents=True)

        cli = ProtocolClient()
        cli.project_root = tmp_path
        cli.evidence_dir = tmp_path / ".protocol" / "evidence"
        cli.evidence_dir.mkdir(parents=True)

        result = cli.command_hygiene(fix=True)

        assert result == 0
        assert not (tmp_path / "scripts" / "automation").exists()
        assert not (tmp_path / "scripts" / "dashboard").exists()

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

    def test_run_hygiene_alias_invokes_command(self, monkeypatch):
        from scripts import protocol_cli as pcli

        calls = {}

        def capture_hygiene(self, fix=False):
            calls["fix"] = fix
            return 0

        monkeypatch.setattr(pcli.ProtocolClient, "command_hygiene", capture_hygiene)

        cli = pcli.ProtocolClient()
        result = cli.run(["hygiene", "--fix"])

        assert result == 0
        assert calls["fix"] is True

    def test_run_maintenance_invokes_explicit_post_commit_steps(
        self, monkeypatch, tmp_path
    ):
        from scripts import protocol_cli as pcli

        for rel in [
            "scripts/manage_tokens.py",
            "scripts/compress_historial.py",
            "scripts/run_self_improvement.py",
            "scripts/manage_review_queue.py",
        ]:
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("print('ok')", encoding="utf-8")

        calls = []

        def capture_run_command(command, timeout=30, cwd=None):
            calls.append((command, timeout, cwd))
            return 0, "", ""

        monkeypatch.setattr(pcli, "run_command", capture_run_command)

        cli = pcli.ProtocolClient()
        cli.project_root = tmp_path

        result = cli.run(["maintenance"])

        assert result == 0
        assert any("manage_tokens.py" in cmd[1] for cmd, _, _ in calls)
        assert any("compress_historial.py" in cmd[1] for cmd, _, _ in calls)
        assert any("run_self_improvement.py" in cmd[1] for cmd, _, _ in calls)
        assert any("manage_review_queue.py" in cmd[1] for cmd, _, _ in calls)

    def test_post_commit_hook_is_opt_in(self):
        content = (PROJECT_ROOT / "scripts" / "hooks" / "post-commit").read_text(
            encoding="utf-8"
        )
        assert "CERBERUS_POSTCOMMIT_AUTOMATION" in content
        assert "protocol_cli.py maintenance" in content
        assert 'manage_review_queue.py" --enqueue' not in content

    def test_run_propagate_alias_invokes_global_sync_apply(self, monkeypatch):
        from scripts import protocol_cli as pcli

        calls = {}

        def capturing_run_command(command, timeout=30, cwd=None):
            calls["command"] = command
            calls["timeout"] = timeout
            calls["cwd"] = cwd
            return (0, "global sync ok", "")

        monkeypatch.setattr(pcli, "run_command", capturing_run_command)

        cli = pcli.ProtocolClient()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = cli.run(["propagate"])

        assert result == 0
        assert calls["command"][1] == "scripts/global_sync_safe.py"
        assert "--apply" in calls["command"]
        assert calls["timeout"] == 600
        assert "propagate complete" in buffer.getvalue()

    def test_command_install_no_hooks_dir_returns_one(self, tmp_path):
        from scripts.protocol_cli import ProtocolClient

        cli = ProtocolClient()
        cli.project_root = tmp_path
        result = cli.command_install()
        # Negative: no scripts/hooks/ directory → should fail
        assert result == 1

    def test_no_typing_imports(self):
        source = (PROJECT_ROOT / "scripts" / "protocol_cli.py").read_text(
            encoding="utf-8"
        )
        assert "from typing import" not in source
        assert "Dict" not in source
        assert "List" not in source
