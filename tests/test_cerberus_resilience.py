"""
TEST: test_cerberus_resilience.py
Suite de validación de resiliencia dinámica — CoderCerberus V0.02.
Elimina hardcoded strings para permitir evolución del protocolo sin romper tests.
"""

import os
import unittest
import subprocess
import sys
from pathlib import Path

# Inyectar path para scripts locales
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.core_utils import get_centralized_version

VERSION = get_centralized_version()
BASE_VERSION = ".".join(VERSION.split(".")[:2])

class TestCoderCerberusResilience(unittest.TestCase):
    def setUp(self):
        self.root = Path(".")
        self.agent_md = self.root / "AGENT.md"
        self.system_md = self.root / "PROTOCOL_SYSTEM.md"
        self.behavior_md = self.root / "PROTOCOL_BEHAVIOR.md"

    def test_version_sync_in_manifests(self):
        """Mandato S17: Verifica que los manifiestos reporten la versión base correcta."""
        for f in [self.system_md, self.behavior_md, self.agent_md]:
            content = f.read_text(encoding='utf-8', errors='ignore')
            self.assertIn(f"v{BASE_VERSION}", content, f"Versión mismatch en {f.name}")

    def test_core_mandates_presence(self):
        """Verifica la existencia de mandatos críticos en cualquiera de los manifiestos core."""
        sys_content = self.system_md.read_text(encoding='utf-8', errors='ignore')
        beh_content = self.behavior_md.read_text(encoding='utf-8', errors='ignore')
        all_content = sys_content + "\n" + beh_content
        
        # Verificar mandatos técnicos (S1-S9, S17)
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 17]:
            self.assertIn(f"MANDATO S{i}:", all_content, f"Falta Mandato S{i} en los manifiestos")
            
        # Verificar mandatos de comportamiento (B1-B11)
        for i in range(1, 12):
            self.assertIn(f"MANDATO B{i}:", all_content, f"Falta Mandato B{i} en los manifiestos")

    def test_audit_10d_dynamic_pass(self):
        """S1: Verifica que el Gatekeeper actual apruebe el repositorio (audit_10d)."""
        script_path = self.root / "scripts/audit_10d.py"
        self.assertTrue(script_path.exists(), "audit_10d.py missing")

        env = os.environ.copy()
        env["PYTHONPATH"] = env.get("PYTHONPATH", "") + os.pathsep + os.getcwd()

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, encoding='utf-8', env=env
        )
        self.assertEqual(result.returncode, 0,
            f"audit_10d falló (exit {result.returncode}):\n{result.stdout[-500:]}")

if __name__ == "__main__":
    unittest.main()
