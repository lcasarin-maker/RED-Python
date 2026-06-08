#!/usr/bin/env python3
"""Tests para D14 Discourse Rigor (migrada a dimensions/ en Sprint 28.5, canal hook)."""
import json
import pytest
from dimensions.base import Status
from dimensions.context import AuditContext
from dimensions.d14_discourse_rigor import (
    D14DiscourseRigor,
    DiscourseMetric,
    DiscourseValidator,
)


class TestDiscourseMetric:
    """Test DiscourseMetric model."""

    def test_creation(self):
        """Create metric."""
        m = DiscourseMetric(
            clarity_score=0.8,
            ambiguity_count=1,
            evidence_count=2,
            chain_of_thought_depth=3,
        )
        assert m.clarity_score == 0.8
        assert m.status == "PASS"

    def test_status_fail(self):
        """Low clarity → FAIL."""
        m = DiscourseMetric(
            clarity_score=0.4,
            ambiguity_count=5,
            evidence_count=0,
            chain_of_thought_depth=0,
        )
        assert m.status == "FAIL"

    def test_status_warn(self):
        """Medium clarity → WARN."""
        m = DiscourseMetric(
            clarity_score=0.6,
            ambiguity_count=2,
            evidence_count=1,
            chain_of_thought_depth=1,
        )
        assert m.status == "WARN"


class TestDiscourseValidator:
    """Test discourse validator."""

    def test_initialization(self):
        """Initialize validator."""
        v = DiscourseValidator(fail_on_clarity_threshold=0.7, response="test response")
        assert v.fail_on_clarity_threshold == 0.7
        assert v.response == "test response"

    def test_measure_clarity_high(self):
        """High clarity: well-structured sentences."""
        response = "This is clear. Each sentence is short. Punctuation is correct."
        v = DiscourseValidator(response=response)
        clarity = v.measure_clarity()
        assert clarity > 0.5

    def test_measure_clarity_low(self):
        """Low clarity: very long sentences."""
        response = "This is a very long sentence that goes on and on without proper structure making it difficult to read"
        v = DiscourseValidator(response=response)
        clarity = v.measure_clarity()
        assert clarity >= 0.0

    def test_detect_ambiguity_high(self):
        """High ambiguity: many vague phrases."""
        response = "Maybe this could be perhaps something kind of complex somewhat"
        v = DiscourseValidator(response=response)
        count = v.detect_ambiguity()
        assert count >= 4

    def test_detect_ambiguity_low(self):
        """Low ambiguity: specific statements."""
        response = (
            "This is exactly what we need. The process is clear and deterministic."
        )
        v = DiscourseValidator(response=response)
        count = v.detect_ambiguity()
        assert count == 0

    def test_count_evidence_citations(self):
        """Count citations and references."""
        response = "According to [1] and [2], the approach is proven. See ref: link: metrics show 95%."
        v = DiscourseValidator(response=response)
        count = v.count_evidence()
        assert count >= 3  # [1], [2], 95%

    def test_count_evidence_empty(self):
        """No evidence."""
        response = "Just some words without citations"
        v = DiscourseValidator(response=response)
        count = v.count_evidence()
        assert count == 0

    def test_measure_chain_of_thought_deep(self):
        """Deep chain of thought."""
        response = "Because of X, therefore Y. This leads to Z, which results in W."
        v = DiscourseValidator(response=response)
        depth = v.measure_chain_of_thought()
        assert depth >= 3

    def test_measure_chain_of_thought_shallow(self):
        """No causal chain."""
        response = "This is a statement. Another statement follows."
        v = DiscourseValidator(response=response)
        depth = v.measure_chain_of_thought()
        assert depth == 0

    def test_validate_pass(self):
        """Validate passes high-quality response."""
        response = "Clearly, this approach works. Because [1] shows 99% success. Therefore, deploy immediately. See ref: metrics prove 50ms latency."
        v = DiscourseValidator(fail_on_clarity_threshold=0.6, response=response)
        v.validate()
        assert v.results["status"] in ["PASS", "WARN"]

    def test_validate_fail(self):
        """Validate fails very low-quality response (high ambiguity + poor clarity)."""
        response = "maybe maybe maybe could be could be could be kind of kind of kind of something something"
        v = DiscourseValidator(fail_on_clarity_threshold=0.8, response=response)
        v.validate()
        # Very high ambiguity with poor structure → FAIL
        assert v.results["status"] in ["FAIL", "WARN"]

    def test_report_json_format(self):
        """Report is valid JSON."""
        response = "Clear response with [1] citation because of logical flow."
        v = DiscourseValidator(response=response)
        v.validate()
        report = v.report()
        data = json.loads(report)
        assert "summary" in data
        assert "metrics" in data
        assert data["summary"]["status"] in ["PASS", "WARN", "FAIL"]

    def test_full_integration(self):
        """Full integration: high clarity, low ambiguity, evidence, chain of thought."""
        response = """
        The solution is clear and proven. Because [1] demonstrates 98% effectiveness, therefore we recommend immediate adoption.
        This leads to significant cost reduction (30% savings), resulting in faster time-to-market. Cite: deployment shows 5ms latency.
        """
        v = DiscourseValidator(fail_on_clarity_threshold=0.65, response=response)
        v.validate()
        assert v.results["ambiguity_count"] <= 1
        assert v.results["evidence_count"] >= 2
        assert v.results["chain_of_thought_depth"] >= 2


class TestD14Dimension:
    """Envoltura Dimension (Sprint 28.5): canal hook + audit_response falsable."""

    def test_is_hook_channel_and_skips_repo(self, tmp_path):
        d = D14DiscourseRigor()
        assert d.id == "d14" and d.channel == "hook"
        assert d.audit(AuditContext(tmp_path)) == []  # hook: no audita el repo

    def test_audit_response_clear_passes(self):
        """Respuesta clara y con evidencia => sin findings."""
        resp = (
            "Clearly, this works. Because [1] shows 99% success, therefore deploy. "
            "See ref: metrics prove 50ms latency."
        )
        assert D14DiscourseRigor().audit_response(resp, threshold=0.6) == []

    def test_audit_response_vague_goes_red(self):
        """Respuesta vaga/ambigua => Finding WARN/FAIL (falsable: va a rojo)."""
        resp = "maybe maybe could be could be kind of kind of somewhat somewhat perhaps"
        findings = D14DiscourseRigor().audit_response(resp, threshold=0.8)
        assert findings and all(
            f.status in (Status.WARN, Status.FAIL) for f in findings
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
