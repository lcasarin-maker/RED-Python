"""
TEST: test_sprint8_tier7.py
Tests de integracion Sprint 8 -- Tier 7.
Cubre: protocol_cli (ProtocolClient).
"""
from pathlib import Path

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
