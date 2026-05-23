"""
TEST: test_VibeCoderProof_v5_5_mandates.py
Suite de validación exhaustiva v5.5.
Cada mandato (S1-S17, B1-B7) debe tener una validación empírica.
"""

import unittest
import json
import re
import sys
from pathlib import Path

class TestVibeCoderProofv55Mandates(unittest.TestCase):
    def setUp(self):
        self.root = Path(".")
        self.manifests = {
            "SPEC": self.root / "SPEC.md",
            "AGENT": self.root / "AGENT.md",
            "SYSTEM": self.root / "PROTOCOL_SYSTEM.md",
            "BEHAVIOR": self.root / "PROTOCOL_BEHAVIOR.md",
            "STATE": self.root / ".agent_state.json"
        }

    def _extract_version(self, file_path):
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        if file_path.suffix == '.json':
            data = json.loads(content)
            return data.get("version")
        # Regex para buscar vX.X o Versión: X.X
        match = re.search(r'(?:v|Versión:\s*)(\d+\.\d+(?:\.\d+)?)', content)
        return match.group(1) if match else None

    def test_S17_universal_version_parity(self):
        """MANDATO S17: Verifica la paridad absoluta de versiones en todos los archivos."""
        from scripts.core_utils import get_centralized_version
        target_version = get_centralized_version()
        self.assertNotEqual(target_version, "UNKNOWN", "Archivo VERSION no encontrado o vacío")
        
        # El archivo VERSION tiene formato X.X.X, los MD tienen vX.X
        # Normalizamos para comparar la base X.X
        base_version = ".".join(target_version.lstrip('v').split(".")[:2])
        
        versions = {}
        for name, path in self.manifests.items():
            version = self._extract_version(path)
            self.assertIsNotNone(version, f"No se pudo encontrar la versión en {name}")
            versions[name] = version.lstrip('v')
        
        for name, version in versions.items():
            self.assertEqual(version, base_version, f"Desincronización de versión detectada en {name}: {version} != {base_version}")

    def test_git_hook_version_parity(self):
        """S17: Verifica que el hook de pre-commit activo coincida con la versión centralizada."""
        from scripts.core_utils import get_centralized_version
        target_version = get_centralized_version()
        base_version = ".".join(target_version.lstrip('v').split(".")[:2])
        
        hook_path = self.root / ".git/hooks/pre-commit"
        if hook_path.exists():
            content = hook_path.read_text(encoding='utf-8', errors='ignore')
            self.assertIn(f"v{base_version}", content, "El Git Hook (.git/hooks/pre-commit) reporta una versión obsoleta!")

    def test_draconian_mandates_v56(self):
        """S7, S8, B8, B9: Verifica los mandatos draconianos de la v5.6."""
        sys_content = self.manifests["SYSTEM"].read_text(encoding='utf-8', errors='ignore')
        beh_content = self.manifests["BEHAVIOR"].read_text(encoding='utf-8', errors='ignore')
        
        self.assertIn("MANDATO S7: PROHIBICIÓN DE SHELL MODIFICATION", sys_content)
        self.assertIn("MANDATO S8: IMPUESTO DE DEUDA TÉCNICA", sys_content)
        self.assertIn("MANDATO B8: FOCO ABSOLUTO Y ANTI-DERIVA", beh_content)
        self.assertIn("MANDATO B9: CAUSA RAÍZ Y UMBRAL DE AMBIGÜEDAD", beh_content)

    def test_S1_to_S5_mandates_content(self):
        """S1-S5: Verifica la existencia de los mandatos técnicos core."""
        sys_content = self.manifests["SYSTEM"].read_text(encoding='utf-8', errors='ignore')
        for i in range(1, 6):
            self.assertIn(f"MANDATO S{i}:", sys_content, f"Falta MANDATO S{i} en PROTOCOL_SYSTEM.md")

    def test_B1_to_B7_mandates_content(self):
        """B1-B7: Verifica la existencia de los mandatos de comportamiento."""
        beh_content = self.manifests["BEHAVIOR"].read_text(encoding='utf-8', errors='ignore')
        for i in range(1, 8):
            self.assertIn(f"MANDATO B{i}:", beh_content, f"Falta MANDATO B{i} en PROTOCOL_BEHAVIOR.md")

    def test_S6_anti_chopped_code(self):
        """S6: Verifica reglas de protección contra truncamiento."""
        beh_content = self.manifests["BEHAVIOR"].read_text(encoding='utf-8', errors='ignore')
        self.assertIn("MANDATO S6: PROTECCIÓN CONTRA TRUNCAMIENTO", beh_content)
        self.assertIn("write_file", beh_content)

    def test_B7_ui_human_validation(self):
        """B7: Verifica la prohibición de validación UI autónoma."""
        beh_content = self.manifests["BEHAVIOR"].read_text(encoding='utf-8', errors='ignore')
        self.assertIn("MANDATO B7: ANTI-TRIUNFALISMO", beh_content)
        self.assertIn("validación humana", beh_content)

    def test_S15_protocol_locality(self):
        """S15/S17: Verifica que no existan carpetas zombi de protocolo en la raíz."""
        root_protocol = Path("../.protocolo") # Asumiendo que estamos en D:\googledrive\ai\Coder Cerberus V0.1
        self.assertFalse(root_protocol.exists(), "Carpeta zombi .protocolo detectada en la raíz!")

if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print(f"Error ejecutando tests: {e}")
        sys.exit(1)
