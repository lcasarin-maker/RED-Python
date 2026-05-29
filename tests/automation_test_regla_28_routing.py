"""
TEST: test_regla_28_routing.py
Parte de la suite de validacion de Coder Cerberus V0.1.
"""

import unittest
import json
from pathlib import Path
from scripts.validate_routing import validate_historial_routing

class TestRegla28Routing(unittest.TestCase):
    def setUp(self):
        self.temp_historial = Path("HISTORIAL_TEST.md")
        # Mocking the Path in validate_routing is hard without libraries, 
        # so we'll just rename the real one briefly if needed or use a separate test file.
        # But wait, validate_historial_routing uses Path("HISTORIAL.md").
        # I'll create a temporary HISTORIAL.md and restore it.
        self.real_historial = Path("HISTORIAL.md")
        self.backup_historial = Path("HISTORIAL.bak")
        if self.real_historial.exists():
            self.real_historial.rename(self.backup_historial)

    def tearDown(self):
        if self.real_historial.exists():
            self.real_historial.unlink()
        if self.backup_historial.exists():
            self.backup_historial.rename(self.real_historial)

    def write_historial(self, content):
        self.real_historial.write_text(content, encoding='utf-8')

    def test_missing_json_blocks(self):
        """Debe fallar si no hay bloques JSON."""
        self.write_historial("## SESIÓN 1\nSin retrospectiva.")
        violations = validate_historial_routing()
        self.assertTrue(any("No se encontró bloque JSON" in v for v in violations))

    def test_invalid_json(self):
        """Debe fallar si el JSON es inválido."""
        self.write_historial("## SESIÓN 1\n```json\n{ invalid: json }\n```")
        violations = validate_historial_routing()
        self.assertTrue(any("JSON en HISTORIAL.md es inválido" in v for v in violations))

    def test_missing_required_fields(self):
        """Debe fallar si faltan campos obligatorios."""
        data = {"session_id": "123", "agent_name": "Claude"}
        self.write_historial(f"## SESIÓN 1\n```json\n{json.dumps(data)}\n```")
        violations = validate_historial_routing()
        self.assertTrue(any("Campos JSON faltantes" in v for v in violations))

    def test_valid_routing_json(self):
        """Debe pasar si el JSON es completo y válido."""
        data = {
            "session_id": "123",
            "agent_name": "Gemini",
            "rules_touched": [28],
            "files_modified": ["HISTORIAL.md"],
            "state_hash": "abc"
        }
        self.write_historial(f"## SESIÓN 1\n```json\n{json.dumps(data)}\n```")
        violations = validate_historial_routing()
        self.assertEqual(len(violations), 0)

if __name__ == "__main__":
    unittest.main()
