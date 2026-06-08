"""
TEST: test_regla_24_security.py
Parte de la suite de validacion de Coder Cerberus V0.1.
"""

import unittest
from scripts.validate_security_tier import validate_tier_permissions


class TestRegla24Security(unittest.TestCase):
    def test_trusted_tier_allows_everything(self):
        """Tier TRUSTED debe permitir cualquier archivo."""
        files = ["AGENT.md", "REGLAS/N1_REGLA_1.md", "scripts/dangerous.py"]
        violations = validate_tier_permissions("TRUSTED", files)
        self.assertEqual(len(violations), 0)

    def test_semi_trusted_tier_restrictions(self):
        """Tier SEMI-TRUSTED debe bloquear archivos sensibles y permitir sandbox/scripts."""
        # Archivos denegados
        denied = ["AGENT.md", "REGLAS/INDEX.md", ".secrets/tokens.db"]
        violations = validate_tier_permissions("SEMI-TRUSTED", denied)
        self.assertEqual(len(violations), 3)

        # Archivos permitidos
        allowed = ["scripts/new_script.py", "tests/test_something.py", "HISTORIAL.md"]
        violations = validate_tier_permissions("SEMI-TRUSTED", allowed)
        self.assertEqual(len(violations), 0)

    def test_untrusted_tier_blocks_all(self):
        """Tier UNTRUSTED debe bloquear todo excepto su carpeta sandbox."""
        files = ["scripts/test.py", "README.md"]
        violations = validate_tier_permissions("UNTRUSTED", files)
        self.assertEqual(len(violations), 2)

        allowed = [".agent-sandbox/untrusted/output.txt"]
        violations = validate_tier_permissions("UNTRUSTED", allowed)
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
