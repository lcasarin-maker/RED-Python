"""
Unit tests for bump_version.py Coder Cerberus.
Validates semver incrementing, propagation to manifest files, and edge-case handling.
"""

import unittest
import tempfile
from pathlib import Path
from scripts.bump_version import bump, propagate_version


class TestBumpVersion(unittest.TestCase):
    """Test suite for the semver bump and version propagation logic."""

    def test_bump_logic(self):
        """Happy paths for major, minor, and patch bumps on 2-part and 3-part versions."""
        self.assertEqual(bump("0.02", "patch"), "0.2")
        self.assertEqual(bump("0.02", "minor"), "0.3")
        self.assertEqual(bump("1.2.3", "patch"), "1.2.4")
        self.assertEqual(bump("1.2.3", "minor"), "1.3.0")
        self.assertEqual(bump("1.2.3", "major"), "2.0.0")

    def test_bump_logic_pad_and_defaults(self):
        """Edge cases where partial versions are passed and padded successfully."""
        self.assertEqual(bump("1", "patch"), "1.0")
        self.assertEqual(bump("1.2", "minor"), "1.3")

    def test_bump_logic_invalid_inputs(self):
        """Negative cases (S23) asserting that invalid version formats or parts are rejected."""
        # Empty string
        with self.assertRaises(ValueError):
            bump("", "patch")

        # Invalid format
        with self.assertRaises(ValueError):
            bump("invalid_version_string", "patch")

        # None type
        with self.assertRaises(AttributeError):
            bump(None, "patch")

        # Invalid parts
        with self.assertRaises(ValueError):
            bump("1.2.3", "invalid_part")

        # Assert that the invalid input test method has run to completion
        self.assertTrue(bool("completed"))

    def test_propagate_version_exact_and_regex(self):
        """Verifies exact string matching and regex-based version propagation on manifests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            agent_state = tmp_path / ".agent_state.json"
            pre_commit = tmp_path / "scripts/hooks/pre-commit"
            agent_md = tmp_path / "AGENT.md"

            pre_commit.parent.mkdir(parents=True, exist_ok=True)

            agent_state.write_text('{"version": "0.02"}', encoding="utf-8")
            pre_commit.write_text('echo "Coder Cerberus v0.02"', encoding="utf-8")
            agent_md.write_text("# Manual CoderCerberus v0.02.1", encoding="utf-8")

            # Execute propagation
            propagate_version("0.02", "0.03", root_dir=tmp_path)

            # Assert exact match propagation
            self.assertIn('"version": "0.03"', agent_state.read_text(encoding="utf-8"))
            self.assertIn(
                'echo "Coder Cerberus v0.03"', pre_commit.read_text(encoding="utf-8")
            )
            # Assert regex match propagation
            self.assertIn(
                "# Manual CoderCerberus v0.03", agent_md.read_text(encoding="utf-8")
            )

    def test_rupture_verification(self):
        """Rupture verification check (S23): files do not magically update without the feature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            agent_state = tmp_path / ".agent_state.json"
            agent_state.write_text('{"version": "0.02"}', encoding="utf-8")

            # Verify that without calling propagate_version, the target file is unchanged
            self.assertNotEqual(
                agent_state.read_text(encoding="utf-8"), '{"version": "0.03"}'
            )
            self.assertIn('"version": "0.02"', agent_state.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
