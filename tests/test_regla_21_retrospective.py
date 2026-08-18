"""Tests for RULE #21 (docs/architecture/N5_REGLA_21_POST_SESSION_RETROSPECTIVE.md).

RULE #21 requires every session in HISTORIAL.md to close with a
`### RETROSPECTIVE` section holding a JSON block answering five fixed
questions. scripts/validate_retrospective.py is the mechanical check; this
suite proves it both accepts a compliant retrospective (GREEN) and actually
detects each way the rule can be broken (RED) -- a validator nobody has ever
seen reject anything has not demonstrated it checks anything.
"""

from __future__ import annotations

import json

import pytest

from scripts.validate_retrospective import (
    check_historial,
    extract_retrospective,
    latest_session,
    split_sessions,
    validate_retrospective_schema,
)

VALID_ANSWERS = {
    "q1_learning": "RULE #21 adds documentation overhead but detects gaps earlier.",
    "q2_violation": "NONE",
    "q3_next_agent": "Nothing unusual.",
    "q4_protocol_gap": "None found.",
    "q5_token_efficiency": {
        "efficient": True,
        "estimate_tokens": 40000,
        "actual_tokens": 38500,
        "note": "No COMPACT was needed.",
    },
}

VALID_RETRO = {
    "session_date": "2026-05-17T20:15:33Z",
    "agent": "Claude",
    "project": "Protocolo Agentes",
    "answers": VALID_ANSWERS,
}


def _session_block(retro: dict, heading: str = "## SESSION 2026-05-17 PART 7") -> str:
    return (
        f"{heading}\n\n"
        "**Task:** Example task\n\n"
        "### RETROSPECTIVE\n\n"
        "**JSON:**\n"
        "```json\n"
        f"{json.dumps(retro, indent=2)}\n"
        "```\n"
    )


def _historial(sessions: list[str]) -> str:
    return "# HISTORIAL\n\n" + "\n---\n\n".join(sessions)


# ---------------------------------------------------------------------------
# GREEN: a compliant retrospective is accepted
# ---------------------------------------------------------------------------


def test_valid_retrospective_has_no_errors():
    assert validate_retrospective_schema(VALID_RETRO) == []


def test_check_historial_accepts_valid_file(tmp_path):
    historial = tmp_path / "HISTORIAL.md"
    historial.write_text(_historial([_session_block(VALID_RETRO)]), encoding="utf-8")
    assert check_historial(historial) == []


def test_check_historial_uses_the_latest_of_several_sessions(tmp_path):
    """A stale, broken retrospective in an EARLIER session must not fail the
    check -- only the latest session is RULE #21's concern."""
    broken = dict(VALID_RETRO)
    broken["answers"] = {"q1_learning": "only one answer"}
    historial = tmp_path / "HISTORIAL.md"
    historial.write_text(
        _historial([
            _session_block(broken, heading="## SESSION 2026-05-01 OLD"),
            _session_block(VALID_RETRO, heading="## SESSION 2026-05-17 NEW"),
        ]),
        encoding="utf-8",
    )
    assert check_historial(historial) == []


def test_no_historial_file_is_not_a_violation(tmp_path):
    """RULE #21 has nothing to judge before a session exists."""
    assert check_historial(tmp_path / "HISTORIAL.md") == []


# ---------------------------------------------------------------------------
# RED: each way the rule is broken must be caught, not waved through
# ---------------------------------------------------------------------------


def test_missing_answer_key_is_caught():
    broken = json.loads(json.dumps(VALID_RETRO))
    del broken["answers"]["q2_violation"]
    errors = validate_retrospective_schema(broken)
    assert any("q2_violation" in e for e in errors), errors


def test_missing_all_five_questions_reports_all_five():
    broken = {**VALID_RETRO, "answers": {}}
    errors = validate_retrospective_schema(broken)
    for key in (
        "q1_learning", "q2_violation", "q3_next_agent",
        "q4_protocol_gap", "q5_token_efficiency",
    ):
        assert any(key in e for e in errors), (key, errors)


def test_q5_wrong_shape_is_caught():
    """q5 must be the {efficient, estimate_tokens, actual_tokens, note}
    object the rule specifies, not a bare boolean or string."""
    broken = json.loads(json.dumps(VALID_RETRO))
    broken["answers"]["q5_token_efficiency"] = True
    errors = validate_retrospective_schema(broken)
    assert any("q5_token_efficiency must be an object" in e for e in errors), errors


def test_q5_wrong_field_types_are_caught():
    broken = json.loads(json.dumps(VALID_RETRO))
    broken["answers"]["q5_token_efficiency"]["actual_tokens"] = "a lot"
    broken["answers"]["q5_token_efficiency"]["efficient"] = "yes"
    errors = validate_retrospective_schema(broken)
    assert any("actual_tokens must be an integer" in e for e in errors), errors
    assert any("efficient must be a boolean" in e for e in errors), errors


def test_empty_q2_violation_is_caught():
    """The rule requires 'RULE #X - description' or the literal 'NONE' --
    silently blank is neither."""
    broken = json.loads(json.dumps(VALID_RETRO))
    broken["answers"]["q2_violation"] = "   "
    errors = validate_retrospective_schema(broken)
    assert any("q2_violation" in e for e in errors), errors


def test_missing_retrospective_section_is_caught():
    session = "## SESSION 2026-05-17 NO RETRO\n\n**Task:** did stuff, forgot the retro.\n"
    with pytest.raises(ValueError, match="RETROSPECTIVE"):
        extract_retrospective(session)


def test_malformed_json_is_caught():
    session = (
        "## SESSION 2026-05-17 BAD JSON\n\n"
        "### RETROSPECTIVE\n\n```json\n{\"session_date\": \"2026-05-17\", oops\n```\n"
    )
    with pytest.raises(ValueError, match="not valid JSON"):
        extract_retrospective(session)


def test_check_historial_surfaces_malformed_json_as_a_finding(tmp_path):
    session = (
        "## SESSION 2026-05-17 BAD JSON\n\n"
        "### RETROSPECTIVE\n\n```json\n{not json at all\n```\n"
    )
    historial = tmp_path / "HISTORIAL.md"
    historial.write_text(_historial([session]), encoding="utf-8")
    errors = check_historial(historial)
    assert errors and "not valid JSON" in errors[0]


def test_check_historial_surfaces_missing_section_as_a_finding(tmp_path):
    session = "## SESSION 2026-05-17 NO RETRO\n\nNo retrospective written.\n"
    historial = tmp_path / "HISTORIAL.md"
    historial.write_text(_historial([session]), encoding="utf-8")
    errors = check_historial(historial)
    assert errors and "RETROSPECTIVE" in errors[0]


# ---------------------------------------------------------------------------
# split_sessions / latest_session -- the parsing this all rests on
# ---------------------------------------------------------------------------


def test_split_sessions_finds_each_heading():
    text = _historial([
        _session_block(VALID_RETRO, heading="## SESSION A"),
        _session_block(VALID_RETRO, heading="## SESSION B"),
    ])
    sessions = split_sessions(text)
    assert len(sessions) == 2
    assert sessions[0].startswith("## SESSION A")
    assert sessions[1].startswith("## SESSION B")


def test_latest_session_is_none_when_no_sessions_present():
    assert latest_session("# HISTORIAL\n\nNothing here yet.\n") is None
