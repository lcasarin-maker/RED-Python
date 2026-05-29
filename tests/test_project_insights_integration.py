"""Project insights integration tests for Cerberus."""

import io
import unittest
from contextlib import redirect_stdout

from cerberus import get_golden_summary, get_project_insight, get_project_insights
from scripts.audit_10d import DeepForensicAuditor
from scripts.generate_golden_audit import (
    build_project_insight_recommendations_section,
    build_project_insight_section,
)
from scripts.protocol_cli import ProtocolClient


class TestProjectInsightsIntegration(unittest.TestCase):
    def test_project_insights_are_loaded_and_complete(self):
        insights = get_project_insights()
        self.assertEqual(
            set(insights.keys()),
            {"PI-001", "PI-002", "PI-003", "PI-004", "PI-005", "PI-006"},
        )
        self.assertIn("imports", insights["PI-001"].lower())
        self.assertIn("assert", insights["PI-002"].lower())
        self.assertIn("usd", insights["PI-003"].lower())
        self.assertIn("cve", insights["PI-004"].lower())
        self.assertIn("routing", insights["PI-005"].lower())
        self.assertIn("estado", insights["PI-006"].lower())

    def test_individual_insight_lookup(self):
        self.assertIn("trivy", get_project_insight("PI-004").lower())
        self.assertEqual(get_project_insight("PI-999"), "")

    def test_golden_summary_tracks_insights(self):
        summary = get_golden_summary()
        self.assertGreater(summary["tokenomics"], 0)
        self.assertGreater(summary["testing_vices"], 0)
        self.assertGreater(summary["coding_vices"], 0)
        self.assertEqual(summary["project_insights"], 6)

    def test_protocol_cli_knowledge_command_exposes_insights(self):
        client = ProtocolClient()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = client.run(["knowledge"])
        output = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("project_insights=6", output)
        self.assertIn("PI-001", output)
        self.assertIn("PI-006", output)

    def test_audit_10d_knows_project_insights(self):
        auditor = DeepForensicAuditor(".")
        self.assertEqual(auditor.audit_project_insights(), [])
        recommendations = auditor.audit_project_insight_recommendations()
        self.assertEqual(set(recommendations.keys()), {f"D{i}" for i in range(1, 11)})
        self.assertTrue(any(item["insight_id"] == "PI-003" for item in recommendations["D10"]))

    def test_generate_golden_audit_has_project_insight_section(self):
        section = build_project_insight_section()
        joined = "\n".join(section)
        self.assertIn("Project Insights", joined)
        self.assertIn("PI-001", joined)
        self.assertIn("PI-006", joined)

    def test_generate_golden_audit_has_recommendation_section(self):
        section = build_project_insight_recommendations_section()
        joined = "\n".join(section)
        self.assertIn("Project Insight Recommendations by Domain", joined)
        self.assertIn("D10", joined)
        self.assertIn("tokencost", joined)
