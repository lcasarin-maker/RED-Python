#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RULE #21 (Post-session retrospective) -- schema validator.

RULE #21 (docs/architecture/N5_REGLA_21_POST_SESSION_RETROSPECTIVE.md) requires
that every session logged in HISTORIAL.md end with a `### RETROSPECTIVE`
section holding a JSON-parseable block that answers five fixed questions
(q1_learning, q2_violation, q3_next_agent, q4_protocol_gap,
q5_token_efficiency). This module is that check, made mechanical: given the
text of HISTORIAL.md (or any single session block), it extracts the latest
retrospective and reports every way it deviates from the five-question schema.

Deliberately narrow: it does not require HISTORIAL.md to exist, and does not
require any specific number of sessions. RULE #21 governs the SHAPE of a
retrospective once one is written, not whether the file is adopted --  that is
a workflow decision outside what a schema validator can honestly police.

Module stays stdlib-only, matching scripts/satellite_governance.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_SESSION_HEADER = re.compile(r"^##\s+SESSION\b.*$", re.MULTILINE)
_RETRO_JSON_FENCE = re.compile(
    r"###\s+RETROSPECTIVE.*?```json\s*(.*?)\s*```",
    re.DOTALL,
)

REQUIRED_ANSWER_KEYS = (
    "q1_learning",
    "q2_violation",
    "q3_next_agent",
    "q4_protocol_gap",
    "q5_token_efficiency",
)

REQUIRED_Q5_KEYS = ("efficient", "estimate_tokens", "actual_tokens", "note")

REQUIRED_TOP_KEYS = ("session_date", "agent", "project", "answers")


def split_sessions(historial_text: str) -> list[str]:
    """Split HISTORIAL.md content into per-session chunks, in file order.

    A "session" starts at a `## SESSION ...` heading and runs to the next one
    (or end of file). Content before the first heading is not a session.
    """
    starts = [m.start() for m in _SESSION_HEADER.finditer(historial_text)]
    if not starts:
        return []
    bounds = starts + [len(historial_text)]
    return [historial_text[bounds[i]:bounds[i + 1]] for i in range(len(starts))]


def latest_session(historial_text: str) -> str | None:
    """The last session chunk in the file, or None if there are none."""
    sessions = split_sessions(historial_text)
    return sessions[-1] if sessions else None


def extract_retrospective(session_text: str) -> dict:
    """Parse the RETROSPECTIVE JSON block out of one session's text.

    Raises ValueError -- with a message naming exactly what is missing or
    malformed -- rather than returning None, because a validator that
    swallows the reason is not distinguishable from one that never ran.
    """
    match = _RETRO_JSON_FENCE.search(session_text)
    if not match:
        raise ValueError(
            "no '### RETROSPECTIVE' section with a ```json fenced block found"
        )
    raw = match.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"RETROSPECTIVE block is not valid JSON: {exc}") from exc


def validate_retrospective_schema(data: dict) -> list[str]:
    """Every way `data` deviates from RULE #21's five-question schema.

    Empty list means compliant. Never raises -- a schema check that raises on
    the very input it exists to judge is a bug, not a strict validator.
    """
    errors: list[str] = []

    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            errors.append(f"missing top-level key: {key!r}")

    answers = data.get("answers")
    if answers is None:
        if "answers" in data:
            errors.append("'answers' must be an object, got null")
        return errors
    if not isinstance(answers, dict):
        errors.append(f"'answers' must be an object, got {type(answers).__name__}")
        return errors

    for key in REQUIRED_ANSWER_KEYS:
        if key not in answers:
            errors.append(f"missing answers.{key}")

    q2 = answers.get("q2_violation")
    if "q2_violation" in answers and (not isinstance(q2, str) or not q2.strip()):
        errors.append("answers.q2_violation must be a non-empty string ('NONE' if none)")

    q5 = answers.get("q5_token_efficiency")
    if "q5_token_efficiency" in answers:
        if not isinstance(q5, dict):
            errors.append(
                f"answers.q5_token_efficiency must be an object, got {type(q5).__name__}"
            )
        else:
            for key in REQUIRED_Q5_KEYS:
                if key not in q5:
                    errors.append(f"missing answers.q5_token_efficiency.{key}")
            if "efficient" in q5 and not isinstance(q5["efficient"], bool):
                errors.append("answers.q5_token_efficiency.efficient must be a boolean")
            for numeric_key in ("estimate_tokens", "actual_tokens"):
                if numeric_key in q5 and not isinstance(q5[numeric_key], int):
                    errors.append(
                        f"answers.q5_token_efficiency.{numeric_key} must be an integer"
                    )

    return errors


def check_historial(historial_path: Path) -> list[str]:
    """High-level entry point: validate the latest session's retrospective.

    Returns [] if `historial_path` does not exist or has no session yet --
    RULE #21 has nothing to judge before a session is written. Otherwise
    returns the schema errors for the latest session's retrospective, or a
    single-item list naming why none could be extracted.
    """
    if not historial_path.exists():
        return []
    text = historial_path.read_text(encoding="utf-8")
    session = latest_session(text)
    if session is None:
        return []
    try:
        data = extract_retrospective(session)
    except ValueError as exc:
        return [str(exc)]
    return validate_retrospective_schema(data)


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("HISTORIAL.md")
    problems = check_historial(target)
    if problems:
        print(f"RULE #21 violations in latest session of {target}:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print(f"RULE #21: latest session retrospective in {target} is valid (or none to check)")
    sys.exit(0)
