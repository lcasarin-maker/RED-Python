"""RED-Python core contract smoke tests."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.core_utils import get_centralized_version


VERSION = get_centralized_version()
BASE_VERSION = ".".join(VERSION.split(".")[:2])


class TestCoreContract(unittest.TestCase):
    def setUp(self):
        self.root = Path(".")
        self.version_file = self.root / "VERSION.txt"
        self.state_json = self.root / ".agent_state.json"
        self.readme = self.root / "README.md"
        self.plan = self.root / "PLAN.md"
        self.validaciones = self.root / "VALIDACIONES.md"

    def test_manifests_existence(self):
        self.assertTrue(self.readme.exists(), "README.md missing")
        self.assertTrue(self.plan.exists(), "PLAN.md missing")
        self.assertTrue(self.validaciones.exists(), "VALIDACIONES.md missing")
        self.assertTrue(self.version_file.exists(), "VERSION.txt missing")
        self.assertTrue(self.state_json.exists(), ".agent_state.json missing")

    def test_version_parity(self):
        state_content = self.state_json.read_text(encoding="utf-8", errors="ignore")
        self.assertIn(f'"version": "{BASE_VERSION}"', state_content)
        readme_content = self.readme.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("RED-Python", readme_content)
        self.assertIn("GUI", readme_content)
        self.assertIn("CLI", readme_content)

    def test_cli_documentation_matches_help(self):
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, "red.py", "--help"],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--scan", result.stdout)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("--permanent", result.stdout)

    def test_audit_6d_smoke(self):
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

    def test_core_modules_compile(self):
        for module_file in ["red.py", "app.py", "core.py", "config.py", "filters.py"]:
            module_path = self.root / module_file
            with self.subTest(module_file=module_file):
                with module_path.open("r", encoding="utf-8", errors="ignore") as handle:
                    compile(handle.read(), str(module_path), "exec")


if __name__ == "__main__":
    unittest.main()
