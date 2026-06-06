"""RED-Python version and CLI contract tests."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


class TestVersionAndContract(unittest.TestCase):
    def setUp(self):
        self.root = Path(".")
        self.manifests = {
            "PLAN": self.root / "PLAN.md",
            "VERSION": self.root / "VERSION.txt",
            "STATE": self.root / ".agent_state.json",
        }
        self.docs = {
            "README": self.root / "README.md",
            "VALIDACIONES": self.root / "VALIDACIONES.md",
        }

    def _extract_version(self, file_path: Path):
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        if file_path.name == "VERSION.txt":
            return content.strip()
        if file_path.suffix == ".json":
            data = json.loads(content)
            return data.get("version")
        match = re.search(r"(?:v|Versión:\s*)(\d+\.\d+(?:\.\d+)?)", content)
        return match.group(1) if match else None

    def test_version_parity(self):
        versions = {}
        for name, path in self.manifests.items():
            version = self._extract_version(path)
            self.assertIsNotNone(version, f"No se pudo encontrar la versión en {name}")
            versions[name] = version.lstrip("v")

        expected_base = ".".join(versions["VERSION"].split(".")[:2])
        for name, version in versions.items():
            self.assertEqual(
                ".".join(version.split(".")[:2]),
                expected_base,
                f"Desincronización de versión en {name}: {version} != {expected_base}",
            )

    def test_cli_help_contract(self):
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
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("--permanent", result.stdout)
        self.assertIn("--export", result.stdout)

    def test_readme_contract(self):
        content = self.docs["README"].read_text(encoding="utf-8", errors="ignore")
        self.assertIn("Remove Empty Directories", content)
        self.assertIn("GUI", content)
        self.assertIn("CLI", content)
        self.assertIn("--scan", content)

    def test_validation_contract(self):
        content = self.docs["VALIDACIONES"].read_text(encoding="utf-8", errors="ignore")
        self.assertIn("REGLA #15", content)
        self.assertIn("Practicidad", content)
        self.assertIn("tests", content.lower())

    def test_focused_audit_entrypoint(self):
        audit_path = self.root / "scripts" / "audit_6d.py"
        self.assertTrue(audit_path.exists(), "audit_6d.py missing")
        result = subprocess.run(
            [sys.executable, str(audit_path)],
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
