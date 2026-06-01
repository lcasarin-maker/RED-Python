"""Project insights integration tests for Cerberus."""

import io
import json
import unittest
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from protocol_engine import (
    get_golden_summary,
    get_project_insight,
    get_project_insights,
    ingest_satellite_learnings,
)
from scripts.run_security_audit_12d import DeepForensicAuditor
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
            {
                "PI-001",
                "PI-002",
                "PI-003",
                "PI-004",
                "PI-005",
                "PI-006",
                "PI-007",
                "PI-008",
                "PI-009",
                "PI-010",
                "PI-011",
                "PI-012",
                "PI-013",
                "PI-014",
                "PI-015",
                "PI-016",
                "PI-017",
                "PI-018",
            },
        )
        self.assertIn("imports", insights["PI-001"].lower())
        self.assertIn("assert", insights["PI-002"].lower())
        self.assertIn("usd", insights["PI-003"].lower())
        self.assertIn("cve", insights["PI-004"].lower())
        self.assertIn("routing", insights["PI-005"].lower())
        self.assertIn("estado", insights["PI-006"].lower())
        self.assertIn("salida", insights["PI-007"].lower())
        self.assertIn("autorizaciones", insights["PI-008"].lower())
        self.assertIn("error", insights["PI-009"].lower())
        self.assertIn("raíz", insights["PI-010"].lower())
        self.assertIn("descript", insights["PI-011"].lower())
        self.assertIn("exclus", insights["PI-012"].lower())
        self.assertIn("vigil", insights["PI-013"].lower())
        self.assertIn("aprendiz", insights["PI-014"].lower())
        self.assertIn("circular", insights["PI-015"].lower())
        self.assertIn("doc_only", insights["PI-016"].lower())
        self.assertIn("many", insights["PI-017"].lower())
        self.assertIn("deduplic", insights["PI-018"].lower())

    def test_individual_insight_lookup(self):
        self.assertIn("trivy", get_project_insight("PI-004").lower())
        self.assertEqual(get_project_insight("PI-999"), "")

    def test_golden_summary_tracks_insights(self):
        summary = get_golden_summary()
        self.assertGreater(summary["tokenomics"], 0)
        self.assertGreater(summary["testing_vices"], 0)
        self.assertGreater(summary["coding_vices"], 0)
        self.assertEqual(summary["project_insights"], 18)

    def test_protocol_cli_knowledge_command_exposes_insights(self):
        client = ProtocolClient()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = client.run(["knowledge"])
        output = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("project_insights=18", output)
        self.assertIn("PI-001", output)
        self.assertIn("PI-018", output)

    def test_audit_12d_knows_project_insights(self):
        auditor = DeepForensicAuditor(".")
        self.assertEqual(auditor.audit_project_insights(), [])
        recommendations = auditor.audit_project_insight_recommendations()
        self.assertEqual(set(recommendations.keys()), {f"D{i}" for i in range(1, 13)})
        self.assertTrue(any(item["insight_id"] == "PI-003" for item in recommendations["D10"]))
        self.assertTrue(any(item["insight_id"] == "PI-014" for item in recommendations["D12"]))
        self.assertTrue(any(item["insight_id"] == "PI-018" for item in recommendations["D12"]))

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

    def test_satellite_learnings_are_normalized_and_deduplicated(self):
        merged = ingest_satellite_learnings(
            [
                {
                    "source": "sat-alpha",
                    "project_insights": {
                        "PI-900": "  Lección satelital nueva  ",
                        "PI-901": "Lección satelital nueva",
                    },
                },
                {
                    "source": "sat-beta",
                    "insights": {
                        "PI-902": "Otra lección distinta",
                    },
                },
            ]
        )
        self.assertIn("PI-900", merged)
        self.assertIn("PI-902", merged)
        self.assertNotIn("PI-901", merged)
        self.assertEqual(merged["PI-900"], "Lección satelital nueva")

    def test_satellite_learning_inbox_is_merged_into_project_insights(self):
        from protocol_engine import knowledge_loader

        inbox = tempfile.TemporaryDirectory()
        try:
            inbox_path = Path(inbox.name) / "satellite_learnings.json"
            inbox_path.write_text(
                json.dumps(
                    [
                        {
                            "source": "sat-e2e",
                            "project_insights": {
                                "PI-903": "Lección satelital automática",
                            },
                        }
                    ]
                ),
                encoding="utf-8",
            )

            previous_path = knowledge_loader._SATELLITE_LEARNINGS_PATH
            knowledge_loader._SATELLITE_LEARNINGS_PATH = inbox_path
            try:
                insights = knowledge_loader.get_project_insights()
            finally:
                knowledge_loader._SATELLITE_LEARNINGS_PATH = previous_path

            self.assertIn("PI-903", insights)
            self.assertEqual(insights["PI-903"], "Lección satelital automática")
        finally:
            inbox.cleanup()
