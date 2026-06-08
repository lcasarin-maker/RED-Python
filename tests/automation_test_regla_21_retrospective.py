"""
TEST: test_regla_21_retrospective.py
Parte de la suite de validacion de Coder Cerberus V0.1.
"""

import json
import re
from pathlib import Path


def test_historial_has_latest_retrospective():
    """REGLA #21: RETROSPECTIVE sections (if present) must be valid"""
    historial_path = Path("HISTORIAL.md")

    with open(historial_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if RETROSPECTIVE exists (not mandatory yet, but if it does, it must be valid)
    if "### RETROSPECTIVE" in content:
        # Find latest SESIÓN section
        sesion_pattern = r"## SESIÓN \d{4}-\d{2}-\d{2}.*?(?=## SESIÓN|$)"
        matches = re.findall(sesion_pattern, content, re.DOTALL)

        if matches:
            latest_sesion = matches[-1]
            assert (
                "### RETROSPECTIVE" in latest_sesion
            ), "Latest SESIÓN has RETROSPECTIVE elsewhere but not in latest. Ensure consistency."

    print("✓ REGLA #21 check 1: RETROSPECTIVE format (if present) is valid")


def test_retrospective_json_valid():
    """REGLA #21: RETROSPECTIVE JSON (if present) must be valid and complete"""
    historial_path = Path("HISTORIAL.md")

    with open(historial_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract RETROSPECTIVE JSON block (optional - may not exist yet)
    json_pattern = r'### RETROSPECTIVE.*?"session_date".*?}.*?\n```'
    match = re.search(json_pattern, content, re.DOTALL)

    if not match:
        # No retrospective yet - this is OK for early rollout
        print("✓ REGLA #21 check 2: No retrospectives yet (REGLA #21 new)")
        return

    json_str = match.group(0)
    json_block = json_str.split("```json\n")[1].split("\n```")[0]

    # Parse and validate
    try:
        retrospective = json.loads(json_block)
    except json.JSONDecodeError as e:
        raise AssertionError(f"RETROSPECTIVE JSON is malformed: {e}")

    # Validate required fields
    required_keys = ["session_date", "agent", "project", "answers"]
    for key in required_keys:
        assert key in retrospective, f"Missing field: {key}"

    # Validate answers has all 5 questions
    answers = retrospective["answers"]
    question_keys = [
        "q1_learning",
        "q2_violation",
        "q3_next_agent",
        "q4_protocol_gap",
        "q5_token_efficiency",
    ]
    for qkey in question_keys:
        assert qkey in answers, f"Missing answer: {qkey}"

    # Validate q5 structure
    q5 = answers["q5_token_efficiency"]
    assert isinstance(q5, dict), "q5_token_efficiency must be dict"
    assert "efficient" in q5, "q5 missing 'efficient' boolean"
    assert "estimate_tokens" in q5, "q5 missing 'estimate_tokens'"
    assert "actual_tokens" in q5, "q5 missing 'actual_tokens'"

    print("✓ REGLA #21 check 2: RETROSPECTIVE JSON is valid and complete")


def test_retrospective_answers_not_empty():
    """REGLA #21: All 5 questions must have non-empty answers (if retrospective exists)"""
    historial_path = Path("HISTORIAL.md")

    with open(historial_path, "r", encoding="utf-8") as f:
        content = f.read()

    json_pattern = r'### RETROSPECTIVE.*?"session_date".*?}.*?\n```'
    match = re.search(json_pattern, content, re.DOTALL)

    if not match:
        # No retrospective yet
        print("✓ REGLA #21 check 3: No retrospectives yet to validate")
        return

    json_str = match.group(0)
    json_block = json_str.split("```json\n")[1].split("\n```")[0]
    retrospective = json.loads(json_block)

    answers = retrospective["answers"]

    # Q1-Q4 must be non-empty strings
    for q in ["q1_learning", "q2_violation", "q3_next_agent", "q4_protocol_gap"]:
        assert answers[q], f"{q} is empty or null"
        assert len(str(answers[q]).strip()) > 0, f"{q} has only whitespace"

    # Q5 fields must be filled
    q5 = answers["q5_token_efficiency"]
    assert q5["estimate_tokens"] > 0, "estimate_tokens must be > 0"
    assert q5["actual_tokens"] > 0, "actual_tokens must be > 0"
    assert q5["note"], "token efficiency note is empty"

    print("✓ REGLA #21 check 3: All answers are filled (non-empty)")


def test_retrospective_token_efficiency_valid():
    """REGLA #21: Token efficiency calculation must be valid (if retrospective exists)"""
    historial_path = Path("HISTORIAL.md")

    with open(historial_path, "r", encoding="utf-8") as f:
        content = f.read()

    json_pattern = r'### RETROSPECTIVE.*?"session_date".*?}.*?\n```'
    match = re.search(json_pattern, content, re.DOTALL)

    if not match:
        # No retrospective yet
        print("✓ REGLA #21 check 4: No retrospectives yet to validate")
        return

    json_str = match.group(0)
    json_block = json_str.split("```json\n")[1].split("\n```")[0]
    retrospective = json.loads(json_block)

    q5 = retrospective["answers"]["q5_token_efficiency"]
    estimate = q5["estimate_tokens"]
    actual = q5["actual_tokens"]
    is_efficient = q5["efficient"]

    # Calculate efficiency ratio
    efficiency_ratio = actual / estimate if estimate > 0 else 0

    # Check consistency: efficient=True should mean ratio < 1.1
    if is_efficient:
        assert (
            efficiency_ratio < 1.1
        ), f"Marked as efficient but ratio is {efficiency_ratio:.2f} (should be <1.1)"
    else:
        # Could be > 1.1 or other reason documented in note
        pass

    print(
        f"✓ REGLA #21 check 4: Token efficiency valid (ratio: {efficiency_ratio:.2f})"
    )


if __name__ == "__main__":
    test_historial_has_latest_retrospective()
    test_retrospective_json_valid()
    test_retrospective_answers_not_empty()
    test_retrospective_token_efficiency_valid()
    print("\n✅ All REGLA #21 tests PASSED")
