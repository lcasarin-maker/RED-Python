"""
Adversarial tests for CoderCerberus V0.02 silent-failure gates.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.chunking_validator import validate_chunks
from scripts.empirical_proof_checker import check_proof


ROOT = Path(__file__).resolve().parents[1]


class TestCoderCerberusSilentFailure(unittest.TestCase):
    def test_empirical_proof_rejects_ui_claim_without_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_dir = Path(temp_dir)
            ok = check_proof(
                "UI success verified",
                evidence_dir=evidence_dir,
                files=["app/main.html"],
            )
            self.assertFalse(ok)

    def test_chunking_validator_rejects_empty_file(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            empty_file = Path(temp_dir) / "empty.py"
            empty_file.write_text("", encoding="utf-8")
            self.assertFalse(validate_chunks(empty_file))

    def test_protocol_cli_has_no_unimplemented_stubs(self):
        content = (ROOT / "scripts" / "protocol_cli.py").read_text(encoding="utf-8")
        self.assertNotIn("Not yet implemented", content)
        self.assertNotIn("def promote", content, "promote() era un stub — debe estar eliminado (S22)")
        self.assertIn("def command_install", content)
        self.assertIn("def command_doctor", content)

    def test_pre_push_uses_configured_upstream_not_main(self):
        content = (ROOT / "scripts" / "hooks" / "pre-push").read_text(encoding="utf-8")
        self.assertNotIn("origin/main...HEAD", content)
        self.assertIn("@{u}", content)


if __name__ == "__main__":
    unittest.main()
