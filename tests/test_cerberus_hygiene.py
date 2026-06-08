"""Tests for D6 repository hygiene automation and VC-087 warning suppression."""

import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.audit_hygiene import (
    find_hygiene_findings,
    repair_mojibake,
    repair_mojibake_text,
)
from scripts.run_security_audit_12d import DeepForensicAuditor


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
            self.assertEqual(
                (root / "SPEC.md").read_text(encoding="utf-8"), "PROPÓSITO\n"
            )

    def test_legacy_scripts_are_safe_wrappers(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(find_hygiene_findings(root), [])


class VC087WarningSuppressionTests(unittest.TestCase):
    """VC-087: filterwarnings('ignore') sin comentario justificativo debe fallar D6."""

    def _auditor(self, tmp_path: Path) -> DeepForensicAuditor:
        return DeepForensicAuditor(str(tmp_path))

    def test_vc087_filterwarnings_without_comment_fails_d6(self):
        """VC-087: script con filterwarnings('ignore') sin comentario es detectado."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "bad.py").write_text(
                'import warnings\nwarnings.filterwarnings("ignore")\n',
                encoding="utf-8",
            )
            auditor = self._auditor(root)
            errors = auditor.audit_d6_anti_slop()
            vc087_errors = [e for e in errors if "VC-087" in e]
            self.assertTrue(vc087_errors, "Esperaba error VC-087 por filterwarnings sin comentario")
            self.assertIn("bad.py", vc087_errors[0])

    def test_vc087_filterwarnings_with_justification_passes_d6(self):
        """VC-087: script con filterwarnings('ignore') + comentario es aceptado."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "ok.py").write_text(
                'import warnings\nwarnings.filterwarnings("ignore")  # VC-087-OK: ruido de terceros\n',
                encoding="utf-8",
            )
            auditor = self._auditor(root)
            errors = auditor.audit_d6_anti_slop()
            vc087_errors = [e for e in errors if "VC-087" in e and "ok.py" in e]
            self.assertFalse(vc087_errors, f"No debería haber errores VC-087: {vc087_errors}")

    def test_vc087_cerberus_itself_has_no_unsuppressed_warnings(self):
        """VC-087: ningún script de Cerberus suprime warnings sin justificación."""
        auditor = DeepForensicAuditor(str(_ROOT))
        errors = auditor.audit_d6_anti_slop()
        vc087_errors = [e for e in errors if "VC-087" in e]
        self.assertFalse(
            vc087_errors,
            f"Cerberus tiene filterwarnings sin justificación:\n" + "\n".join(vc087_errors),
        )


if __name__ == "__main__":
    unittest.main()
