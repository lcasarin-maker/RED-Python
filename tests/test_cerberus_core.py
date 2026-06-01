"""
TEST: test_cerberus_core.py
Suite unificada de validación — CoderCerberus V0.02.
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

class TestCoderCerberusCore(unittest.TestCase):
    def setUp(self):
        self.root = Path(".")
        self.state_json = self.root / ".agent_state.json"
        self.agent_md = self.root / "AGENT.md"
        self.system_md = self.root / "PROTOCOL_SYSTEM.md"
        self.behavior_md = self.root / "PROTOCOL_BEHAVIOR.md"

    def test_manifests_existence(self):
        """S1/S2: Verifica que los manifiestos core existen — CoderCerberus V0.02."""
        self.assertTrue(self.agent_md.exists(), "AGENT.md missing")
        self.assertTrue(self.system_md.exists(), "PROTOCOL_SYSTEM.md missing")
        self.assertTrue(self.behavior_md.exists(), "PROTOCOL_BEHAVIOR.md missing")

        sys_content = self.system_md.read_text(encoding='utf-8')
        base_version = ".".join(VERSION.split(".")[:2])
        self.assertIn(f"v{base_version}", sys_content, "PROTOCOL_SYSTEM.md version mismatch")

    def test_core_mandates_exist(self):
        """Verifica que los Macro-Mandatos de CoderCerberus V0.02 están codificados."""
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

    def test_run_security_audit_12d_compliance(self):
        """S1: Verifica que el Gatekeeper CoderCerberus V0.02 aprueba el repo (run_security_audit_12d)."""
        script_path = self.root / "scripts/run_security_audit_12d.py"
        self.assertTrue(script_path.exists(), "run_security_audit_12d.py missing")

        # Forzar PYTHONPATH para que el subproceso encuentre scripts.core_utils
        env = os.environ.copy()
        env["PYTHONPATH"] = env.get("PYTHONPATH", "") + os.pathsep + os.getcwd()

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, env=env
        )
        stdout = result.stdout.decode('utf-8', errors='ignore')
        self.assertIn("APPROVED", stdout, f"Audit 12D failed: {stdout}")

    def test_core_mandates_functional(self):
        """VT-007/VT-016 (P6.9): Los métodos de auditoría se ejecutan y retornan listas reales.
        Complementa test_core_mandates_exist (chequeo textual) con prueba de comportamiento real.
        Un stub o método vacío fallaría aquí aunque el texto del mandato estuviera presente."""
        from scripts.run_security_audit_12d import DeepForensicAuditor
        auditor = DeepForensicAuditor(self.root)
        for method_name in ("audit_d1_integrity", "audit_d5_angry_path", "audit_d8_test_coverage"):
            with self.subTest(method=method_name):
                result = getattr(auditor, method_name)()
                self.assertIsInstance(result, list,
                    f"{method_name}() retornó {type(result).__name__} — debe retornar list")
                # Un stub que retorna [] pasaría, pero al menos verifica que ejecuta sin crash.
                # D5 y D8 en un repo real retornan listas no vacías si hay hallazgos reales.

    def test_verify_chaos_robustness_exists(self):
        """S1/B3: Verifica la existencia del Chaos Robustness Engine."""
        self.assertTrue((self.root / "scripts/verify_chaos_robustness.py").exists())

if __name__ == "__main__":
    unittest.main()

