#!/usr/bin/env python3
"""Tests para Sprint 24 — D13 Observable Behavior"""
import json
import tempfile
from pathlib import Path
import pytest
from dimensions.d13_observable import (
    count_tokens,
    estimate_cost,
    DecisionLogger,
    DivergenceDetector,
    D13Report,
    D13Observable,
)


class TestTokenMeter:
    def test_count_tokens_valid_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello world" * 100)
            temp_path = f.name
        try:
            assert count_tokens(temp_path) > 0
        finally:
            Path(temp_path).unlink()

    def test_count_tokens_nonexistent_file(self):
        assert count_tokens("/nonexistent/path.txt") == 0

    def test_estimate_cost(self):
        assert estimate_cost(1000, rate_per_1k=0.002) == pytest.approx(0.002, rel=0.01)

    def test_estimate_cost_zero(self):
        assert estimate_cost(0) == 0.0


class TestDecisionLogger:
    def test_log_decision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DecisionLogger(log_dir=tmpdir)
            decision_id = logger.log_decision(
                agent="TestAgent",
                decision="test",
                reasoning="test",
                action="test",
                result="OK",
            )
            assert len(decision_id) > 0 and logger.log_file.exists()

    def test_log_file_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DecisionLogger(log_dir=tmpdir)
            logger.log_decision(
                agent="Agent1",
                decision="dec1",
                reasoning="r1",
                action="a1",
                result="r1",
            )
            with open(logger.log_file, "r") as f:
                record = json.loads(f.readline())
            assert "decision_id" in record and record["agent"] == "Agent1"

    def test_multiple_decisions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DecisionLogger(log_dir=tmpdir)
            for i in range(3):
                logger.log_decision(
                    agent=f"A{i}",
                    decision=f"d{i}",
                    reasoning=f"r{i}",
                    action="a",
                    result="OK",
                )
            assert len(open(logger.log_file).readlines()) == 3


class TestDivergenceDetector:
    def test_check_allowed_action(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("PUEDE: read files\nPUEDE: execute tests\n")
            f.flush()
            temp_path = f.name
        try:
            detector = DivergenceDetector(agent_md_path=temp_path)
            assert detector.check("read files")["allowed"] is True
        finally:
            Path(temp_path).unlink()

    def test_check_disallowed_action(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("NO PUEDE: delete critical files\n")
            f.flush()
            temp_path = f.name
        try:
            detector = DivergenceDetector(agent_md_path=temp_path)
            result = detector.check("delete critical files")
            assert result["allowed"] is False and result["severity"] == "CRITICAL"
        finally:
            Path(temp_path).unlink()

    def test_check_unknown_action(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("PUEDE: read\n")
            f.flush()
            temp_path = f.name
        try:
            detector = DivergenceDetector(agent_md_path=temp_path)
            assert detector.check("unknown")["severity"] == "WARNING"
        finally:
            Path(temp_path).unlink()


class TestD13Report:
    def test_generate_json(self):
        report = D13Report()
        data = report.generate_json()
        assert "timestamp" in data and "tokens" in data

    def test_generate_html(self):
        report = D13Report()
        html = report.generate_html()
        assert "<html>" in html and "D13" in html


class TestD13Observable:
    """Dimensión hook D13 (Sprint 28.5): canal hook + observe_session falsable."""

    def test_is_hook_and_skips_repo(self):
        d = D13Observable()
        assert d.id == "d13" and d.channel == "hook"
        assert d.audit(None) == []  # hook: no audita el repo

    def test_observe_session_sums_usage(self, tmp_path):
        t = tmp_path / "tr.jsonl"
        t.write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "hi"}],
                        "usage": {"output_tokens": 40},
                    },
                }
            )
            + "\n"
            + json.dumps({"type": "user", "message": {"role": "user", "content": "x"}})
            + "\n"
            + json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "tool_use"}],
                        "usage": {"output_tokens": 10},
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        obs = D13Observable().observe_session(str(t))
        assert obs == {"assistant_messages": 2, "output_tokens": 50}

    def test_observe_session_missing_transcript_is_zero(self, tmp_path):
        obs = D13Observable().observe_session(str(tmp_path / "no.jsonl"))
        assert obs == {"assistant_messages": 0, "output_tokens": 0}

    def test_observe_session_counts_only_after_compact_marker(self, tmp_path):
        """C4 (TK-031): tras un /compact, mide SOLO el delta posterior al marcador.
        El marcador real de esta versión de Claude Code es isCompactSummary:true
        (NO type=="summary"). Sin el fix se sumaba la sesión entera → re-bloqueo."""
        t = tmp_path / "tr.jsonl"
        t.write_text(
            # Pre-compact: tokens enormes que NO deben contarse
            json.dumps(
                {
                    "type": "assistant",
                    "message": {"usage": {"output_tokens": 999_999}},
                }
            )
            + "\n"
            # Marcador real de compact (type user + isCompactSummary)
            + json.dumps(
                {"type": "user", "isCompactSummary": True, "compactMetadata": None}
            )
            + "\n"
            # Post-compact: solo esto cuenta
            + json.dumps(
                {"type": "assistant", "message": {"usage": {"output_tokens": 7}}}
            )
            + "\n"
            + json.dumps(
                {"type": "assistant", "message": {"usage": {"output_tokens": 3}}}
            )
            + "\n",
            encoding="utf-8",
        )
        obs = D13Observable().observe_session(str(t))
        assert obs == {"assistant_messages": 2, "output_tokens": 10}

    def test_observe_session_ignores_legacy_summary_key(self, tmp_path):
        """Una línea type=="summary" (clave vieja) NO es marcador → mide todo."""
        t = tmp_path / "tr.jsonl"
        t.write_text(
            json.dumps({"type": "summary", "summary": "viejo"})
            + "\n"
            + json.dumps(
                {"type": "assistant", "message": {"usage": {"output_tokens": 5}}}
            )
            + "\n",
            encoding="utf-8",
        )
        obs = D13Observable().observe_session(str(t))
        assert obs == {"assistant_messages": 1, "output_tokens": 5}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
