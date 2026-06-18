from __future__ import annotations

import json
from pathlib import Path

from scripts.satellite_governance import (
    LearningSignal,
    build_learning_event,
    classify_scope,
    load_learning_event,
    validate_satellite_layout,
)


ROOT = Path(__file__).resolve().parents[1]


def test_satellite_layout_is_complete():
    assert validate_satellite_layout(ROOT) == []


def test_learning_signal_scopes_are_preserved():
    local = LearningSignal(
        source="tests",
        category="tests",
        summary="local fix",
        root_cause="local issue",
        fix="local fix",
        evidence=("tests/test_satellite_governance.py",),
    )
    promoted = LearningSignal(
        source="tests",
        category="tokenomics",
        summary="cc fix",
        root_cause="shared issue",
        fix="shared fix",
        evidence=("docs/learning/SATELLITE_LEARNING_FLOW.md",),
        scope="cc",
        recommendation="promote-cc",
    )

    assert classify_scope(local) == "local"
    assert classify_scope(promoted) == "cc"


def test_learning_event_round_trip(tmp_path):
    signal = LearningSignal(
        source="tests",
        category="tests",
        summary="Replace theatrical checks with behavior tests.",
        root_cause="Text-only assertions hid regressions.",
        fix="Add behavior-based tests.",
        evidence=("tests/test_satellite_governance.py",),
        scope="cc",
        recommendation="promote-cc",
        impact="Better signal and lower maintenance.",
        token_savings="Reduced duplicated explanation.",
    )
    event = build_learning_event(signal, repo="RED-Python")

    assert event["repo"] == "RED-Python"
    assert event["source"] == "tests"
    assert event["scope"] == "cc"
    assert event["recommendation"] == "promote-cc"
    assert event["evidence"] == ["tests/test_satellite_governance.py"]

    path = tmp_path / "learning.json"
    path.write_text(json.dumps(event, indent=2), encoding="utf-8")
    loaded = load_learning_event(path)

    assert loaded["summary"] == signal.summary
    assert loaded["fix"] == signal.fix
