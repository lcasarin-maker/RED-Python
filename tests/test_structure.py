"""Structural test for red_python: the canonical profile is present."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def test_canonical_structure_has_no_violations():
    """The satellite satisfies the profile its own auditor checks."""
    import audit

    assert audit.find_violations(ROOT) == []
