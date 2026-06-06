"""RED-Python resilience smoke tests."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.core_utils import get_centralized_version


VERSION = get_centralized_version()
BASE_VERSION = ".".join(VERSION.split(".")[:2])


class TestResilienceV57(unittest.TestCase):
    def setUp(self):
        self.root = Path(".")
        self.version_file = self.root / "VERSION.txt"
        self.state_json = self.root / ".agent_state.json"
        self.readme = self.root / "README.md"
        self.plan = self.root / "PLAN.md"
        self.validaciones = self.root / "VALIDACIONES.md"

    def test_version_sync_in_manifests(self):
        version_text = self.version_file.read_text(encoding="utf-8", errors="ignore").strip()
        self.assertEqual(version_text, BASE_VERSION)

        state_text = self.state_json.read_text(encoding="utf-8", errors="ignore")
        self.assertIn(f'"version": "{BASE_VERSION}"', state_text)

    def test_current_contract_docs_exist(self):
        for path in [self.readme, self.plan, self.validaciones]:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"{path.name} missing")
                content = path.read_text(encoding="utf-8", errors="ignore")
                self.assertIn("RED-Python", content)

    def test_cli_help_and_invalid_path_behaviour(self):
        result = subprocess.run(
            [sys.executable, "red.py", "--help"],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--scan", result.stdout)

        invalid = subprocess.run(
            [sys.executable, "red.py", "--scan", "C:\\__red_python_missing__", "--dry-run"],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        self.assertNotEqual(invalid.returncode, 0)
        invalid_output = (invalid.stderr + invalid.stdout).lower()
        self.assertTrue(
            "ruta invalida" in invalid_output or "inexistente" in invalid_output
        )

    def test_audit_6d_dynamic_pass(self):
        script_path = self.root / "scripts" / "audit_6d.py"
        self.assertTrue(script_path.exists(), "audit_6d.py missing")

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("APPROVED", result.stdout)


if __name__ == "__main__":
    unittest.main()
