"""TEST"""
"""
TEST: test_VibeCoderProof_v5_core.py
Suite unificada de validación del Coder Cerberus V0.1 (VibeCoderProof v5.0 VibeCoderProof).
Valida los Mandatos S1-S5 (SISTEMA) y B1-B5 (BEHAVIOR).
"""

import os
import unittest
import subprocess
import sys
from pathlib import Path

# Forzar encoding UTF-8
if sys.platform == "win32":
    if not os.getenv("PYTEST_CURRENT_TEST") and "pytest" not in sys.modules:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="ignore")

from scripts.core_utils import get_centralized_version
VERSION = get_centralized_version()

class TestVibeCoderProofCoreV5(unittest.TestCase):
    def setUp(self):
        self.root = Path(".")
        self.state_json = self.root / ".agent_state.json"
        self.agent_md = self.root / "AGENT.md"
        self.system_md = self.root / "PROTOCOL_SYSTEM.md"
        self.behavior_md = self.root / "PROTOCOL_BEHAVIOR.md"

    def test_manifests_existence(self):
        """S1/S2: Verifica que los manifiestos core existen y son v5.6."""
        self.assertTrue(self.agent_md.exists(), "AGENT.md missing")
        self.assertTrue(self.system_md.exists(), "PROTOCOL_SYSTEM.md missing")
        self.assertTrue(self.behavior_md.exists(), "PROTOCOL_BEHAVIOR.md missing")
        
        # El sistema ha sido consolidado a v5.6
        sys_content = self.system_md.read_text(encoding='utf-8')
        base_version = ".".join(VERSION.split(".")[:2])
        self.assertIn(f"v{base_version}", sys_content, "PROTOCOL_SYSTEM.md version mismatch")

    def test_v50_mandates_exist(self):
        """Verifica que los Macro-Mandatos de la v5.0 están codificados."""
        sys_content = self.system_md.read_text(encoding='utf-8')
        beh_content = self.behavior_md.read_text(encoding='utf-8')
        
        # System Mandates
        self.assertIn("MANDATO S1: RIGOR DE VALID", sys_content)
        self.assertIn("MANDATO S2: ARQUITECTURA E INTEGRIDAD", sys_content)
        self.assertIn("MANDATO S3: SEGURIDAD Y CONFINAMIENTO", sys_content)
        
        # Behavior Mandates
        self.assertIn("MANDATO B1: DOCTRINA DEL FALLO INHERENTE", beh_content)
        self.assertIn("MANDATO B2: BOOTSTRAP RITUAL", beh_content)
        self.assertIn("MANDATO B3: ANGRY PATH", beh_content)

    def test_audit_6d_v53_compliance(self):
        """S1: Verifica que el Gatekeeper v5.3 aprueba el repo."""
        script_path = self.root / "scripts/audit_6d.py"
        self.assertTrue(script_path.exists(), "audit_6d.py missing")
        
        # Forzar PYTHONPATH para que el subproceso encuentre scripts.core_utils
        env = os.environ.copy()
        env["PYTHONPATH"] = env.get("PYTHONPATH", "") + os.pathsep + os.getcwd()
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, env=env
        )
        stdout = result.stdout.decode('utf-8', errors='ignore')
        self.assertIn("APPROVED", stdout, f"Audit 6D failed: {stdout}")

    def test_chaos_monkey_exists(self):
        """S1/B3: Verifica la existencia del Chaos Monkey Engine."""
        self.assertTrue((self.root / "scripts/chaos_monkey.py").exists())

if __name__ == "__main__":
    unittest.main()

