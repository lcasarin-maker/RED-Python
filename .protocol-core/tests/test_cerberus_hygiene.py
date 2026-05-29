"""Tests for D6 repository hygiene automation."""

import tempfile
import unittest
from pathlib import Path

from scripts.hygiene_auditor import (
    find_hygiene_findings,
    repair_mojibake,
    repair_mojibake_text,
)
from scripts.chunking_validator import validate_chunks


class HygieneV57Tests(unittest.TestCase):
    def test_mojibake_repair_handles_spanish_and_emoji_sequences(self):
        corrupted = "Validación ✅ 🧠 núcleo".encode("utf-8").decode("cp1252")
        repaired = repair_mojibake_text(corrupted)
        self.assertIn("Validación", repaired)
        self.assertIn("✅", repaired)
        self.assertIn("🧠", repaired)
        self.assertIn("núcleo", repaired)

    def test_findings_clear_after_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corrupted = "PROPÓSITO\n".encode("utf-8").decode("cp1252")
            (root / "SPEC.md").write_text(corrupted, encoding="utf-8")
            self.assertEqual(len(find_hygiene_findings(root)), 1)

            touched = repair_mojibake(root)

            self.assertEqual(touched, ["SPEC.md"])
            self.assertEqual(find_hygiene_findings(root), [])
            self.assertEqual((root / "SPEC.md").read_text(encoding="utf-8"), "PROPÓSITO\n")

    def test_legacy_scripts_are_safe_wrappers(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(find_hygiene_findings(root), [])



if __name__ == "__main__":
    unittest.main()
