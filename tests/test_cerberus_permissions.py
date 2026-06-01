"""
Tests for CoderCerberus V0.02 agent permission enforcement.
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_permissions import audit_permission_file


class TestCoderCerberusPermissions(unittest.TestCase):
    def _settings_file(self, permissions: list[str]) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "settings.json"
        path.write_text(json.dumps({"permissions": {"allow": permissions}}), encoding="utf-8")
        return path

    def test_rejects_generic_python_and_git_reset(self):
        path = self._settings_file([
            "Bash(python)",
            "Bash(git reset *)",
        ])
        findings = audit_permission_file(path)
        self.assertGreaterEqual(len(findings), 2)

    def test_accepts_safe_protocol_permissions(self):
        path = self._settings_file([
            "Bash(python scripts/protocol_cli.py check)",
            "Bash(python scripts/protocol_cli.py sync --dry-run)",
            "Bash(python scripts/audit_6d_expanded.py)",
        ])
        self.assertEqual(audit_permission_file(path, require_safe_baseline=True), [])


if __name__ == "__main__":
    unittest.main()
