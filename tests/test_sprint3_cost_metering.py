"""Sprint 3 cost metering integration tests."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.protocol_cli import ProtocolClient
from scripts.track_tokens import TokenTracker


class TestSprint3CostMetering(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.transcript_path = Path(self.temp_dir.name) / "transcript.jsonl"
        self.transcript_path.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "session_id": "sess-1",
                            "agent_id": "agent-1",
                            "model": "claude-haiku",
                            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
                        }
                    ),
                    json.dumps(
                        {
                            "session_id": "sess-1",
                            "agent_id": "agent-1",
                            "model": "claude-sonnet",
                            "tokens_estimated": 180,
                            "tokens_actual": 200,
                            "note": "manual entry",
                        }
                    ),
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_transcript_analysis_builds_cost_summary(self):
        tracker = TokenTracker(db_path=":memory:")
        try:
            summary = tracker.analyze_transcript(self.transcript_path)
        finally:
            tracker.close()

        self.assertTrue(summary["exists"])
        self.assertEqual(summary["entry_count"], 2)
        self.assertEqual(summary["sessions"], 1)
        self.assertEqual(summary["tokens_actual"], 350)
        self.assertEqual(summary["tokens_estimated"], 330)
        self.assertGreater(summary["total_cost"], 0)
        self.assertIn("claude-haiku", summary["models"])
        self.assertIn("claude-sonnet", summary["models"])

    def test_cost_report_is_human_readable(self):
        tracker = TokenTracker(db_path=":memory:")
        try:
            report = tracker.format_transcript_cost_report(self.transcript_path)
        finally:
            tracker.close()

        self.assertIn("cost: transcript=", report)
        self.assertIn("total_cost_usd=", report)
        self.assertIn("claude-sonnet", report)

    def test_protocol_cli_cost_command_supports_slash_alias(self):
        client = ProtocolClient()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = client.run(["/cost", "--transcript", str(self.transcript_path)])
        output = buffer.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("total_cost_usd=", output)
        self.assertIn("claude-haiku", output)
        self.assertIn("claude-sonnet", output)
