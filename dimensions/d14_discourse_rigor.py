#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D14 Discourse Rigor (Sprint 28.5): HOOK channel - audits the agent RESPONSE,
not the repo. Migrated from the standalone script (S19, copied without a bridge;
its old `main()` that caused exit 1 on bare runs was removed). The gate SKIPS it
(channel != gate); its real entry point is `audit_response`, which the runtime
hook invokes (WARN-only until calibrated). Real clarity/ambiguity/evidence/causal
chain heuristics."""
import json
import re
from dataclasses import dataclass

from dimensions.base import Finding, Status
from dimensions.context import AuditContext


@dataclass
class DiscourseMetric:
    """Discourse quality metrics."""

    clarity_score: float
    ambiguity_count: int
    evidence_count: int
    chain_of_thought_depth: int
    status: str = "OK"  # OK, PASS, WARN, FAIL

    def __post_init__(self):
        if self.clarity_score < 0.5:
            self.status = "FAIL"
        elif self.clarity_score < 0.65:
            self.status = "WARN"
        else:
            self.status = "PASS"


class DiscourseValidator:
    """Validates discourse rigor before a response is emitted."""

    VAGUE_PHRASES = {"maybe", "perhaps", "could be", "might be", "somewhat", "kind of"}
    CITATION_PATTERNS = [r"\[[\d\w]+\]", r"cite:", r"ref:", r"link:"]
    CAUSAL_MARKERS = {
        "because",
        "therefore",
        "thus",
        "leads to",
        "results in",
        "causes",
    }

    def __init__(self, fail_on_clarity_threshold: float = 0.7, response: str = ""):
        self.fail_on_clarity_threshold = fail_on_clarity_threshold
        self.response = response
        self.metrics = None
        self.results = {}

    def measure_clarity(self) -> float:
        """Clarity via word, capitalization, and punctuation analysis."""
        if not self.response:
            return 0.0
        text = self.response.lower()
        words = text.split()
        if not words:
            return 0.0
        sentences = [s.strip() for s in self.response.split(".") if s.strip()]
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        clarity = 1.0 - min(abs(avg_words_per_sentence - 15) / 20, 1.0)
        capitalized = sum(1 for s in sentences if s and s[0].isupper())
        cap_score = capitalized / max(len(sentences), 1)
        final_clarity = (clarity * 0.6) + (cap_score * 0.4)
        return max(0.0, min(1.0, final_clarity))

    def detect_ambiguity(self) -> int:
        """Counts vague or ambiguous phrases."""
        text = self.response.lower()
        count = 0
        for phrase in self.VAGUE_PHRASES:
            count += len(re.findall(r"\b" + phrase + r"\b", text))
        return count

    def count_evidence(self) -> int:
        """Counts citations and references."""
        count = 0
        for pattern in self.CITATION_PATTERNS:
            count += len(re.findall(pattern, self.response))
        count += len(re.findall(r"\d+\s*[%ms$€]", self.response))
        return count

    def measure_chain_of_thought(self) -> int:
        """Measures logical chain depth via causal markers."""
        text = self.response.lower()
        depth = 0
        for marker in self.CAUSAL_MARKERS:
            depth += len(re.findall(r"\b" + marker + r"\b", text))
        return depth

    def validate(self) -> dict:
        """Runs all metrics and determines PASS/WARN/FAIL."""
        try:
            clarity = self.measure_clarity()
            ambiguity = self.detect_ambiguity()
            evidence = self.count_evidence()
            cot_depth = self.measure_chain_of_thought()
            self.metrics = DiscourseMetric(
                clarity_score=clarity,
                ambiguity_count=ambiguity,
                evidence_count=evidence,
                chain_of_thought_depth=cot_depth,
            )
        except (ValueError, AttributeError, TypeError) as e:
            self.metrics = DiscourseMetric(0.0, 0, 0, 0)
            self.results = {
                "clarity_score": 0.0,
                "adjusted_clarity": 0.0,
                "ambiguity_count": 0,
                "evidence_count": 0,
                "chain_of_thought_depth": 0,
                "fail_threshold": self.fail_on_clarity_threshold,
                "status": "FAIL",
                "error": str(e),
            }
            return self.results
        penalty = min(0.1 * ambiguity, 0.3)
        adjusted_clarity = max(0.0, min(1.0, clarity - penalty))
        if adjusted_clarity < 0.5:
            status = "FAIL"
        elif adjusted_clarity < self.fail_on_clarity_threshold:
            status = "WARN"
        else:
            status = "PASS"
        self.results = {
            "clarity_score": clarity,
            "adjusted_clarity": adjusted_clarity,
            "ambiguity_count": ambiguity,
            "evidence_count": evidence,
            "chain_of_thought_depth": cot_depth,
            "fail_threshold": self.fail_on_clarity_threshold,
            "status": status,
        }
        return self.results

    def report(self) -> str:
        """JSON report with metrics and verdict."""
        if not self.results:
            self.validate()
        return json.dumps(
            {
                "summary": self.results,
                "metrics": {
                    "clarity_score": (
                        self.metrics.clarity_score if self.metrics else 0.0
                    ),
                    "ambiguity_count": (
                        self.metrics.ambiguity_count if self.metrics else 0
                    ),
                    "evidence_count": (
                        self.metrics.evidence_count if self.metrics else 0
                    ),
                    "chain_of_thought_depth": (
                        self.metrics.chain_of_thought_depth if self.metrics else 0
                    ),
                },
            },
            indent=2,
        )


_STATUS_MAP = {"PASS": Status.PASS, "WARN": Status.WARN, "FAIL": Status.FAIL}


class D14DiscourseRigor:
    """D14 dimension (hook channel): rigor of the agent response."""

    id = "d14"
    name = "DISCOURSE RIGOR"
    channel = "hook"

    def audit(self, ctx: AuditContext) -> list:
        """Hook channel: does not audit the repo. The gate skips it (channel != gate)."""
        return []

    def audit_response(self, response: str, threshold: float = 0.7) -> list:
        """Runtime hook entry point: evaluates a response. PASS => no findings;
        WARN/FAIL => a Finding with the reason (WARN does not block until calibrated)."""
        res = DiscourseValidator(
            fail_on_clarity_threshold=threshold, response=response
        ).validate()
        status = _STATUS_MAP[res["status"]]
        if status is Status.PASS:
            return []
        return [
            Finding(
                self.id,
                f"clarity {res['adjusted_clarity']:.2f} < {threshold} "
                f"(ambigüedad {res['ambiguity_count']}, evidencia {res['evidence_count']})",
                status,
            )
        ]
