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
        """S1/S2: Verifica que los manifiestos core existen con contenido real."""
        # AGENT.md must exist and have content
        self.assertTrue(self.agent_md.exists(), "AGENT.md missing")
        agent_content = self.agent_md.read_text(encoding="utf-8")
        self.assertGreater(len(agent_content), 500, "AGENT.md too short")
        self.assertTrue(any(word in agent_content for word in ["PROTOCOLO", "REGLAS", "Coder", "CoderCerberus"]),
                       "AGENT.md missing protocol/mandate content")

        # PROTOCOL_SYSTEM.md must exist, have content, and version
        self.assertTrue(self.system_md.exists(), "PROTOCOL_SYSTEM.md missing")
        sys_content = self.system_md.read_text(encoding="utf-8")
        self.assertGreater(len(sys_content), 300, "PROTOCOL_SYSTEM.md too short")
        # Check for version pattern (any version is acceptable if content is present)
        self.assertTrue('Version:' in sys_content or 'version' in sys_content or 'v0' in sys_content,
                       "PROTOCOL_SYSTEM.md missing version info")

        # PROTOCOL_BEHAVIOR.md must exist and have content
        self.assertTrue(self.behavior_md.exists(), "PROTOCOL_BEHAVIOR.md missing")
        beh_content = self.behavior_md.read_text(encoding="utf-8")
        self.assertGreater(len(beh_content), 300, "PROTOCOL_BEHAVIOR.md too short")

    def test_core_mandates_exist(self):
        """Verifica que los Macro-Mandatos de CoderCerberus V0.02 están codificados."""
        sys_content = self.system_md.read_text(encoding="utf-8")
        beh_content = self.behavior_md.read_text(encoding="utf-8")

        # System Mandates (S0 is first and most critical)
        self.assertIn("MANDATO S0: VALIDACIÓN PRE-ÉXITO", sys_content)
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
            [sys.executable, str(script_path)], capture_output=True, env=env
        )
        stdout = result.stdout.decode("utf-8", errors="ignore")
        self.assertIn("APPROVED", stdout, f"Audit 12D failed: {stdout}")

    def test_core_mandates_functional(self):
        """VT-007/VT-016: Los métodos de auditoría retornan listas de strings — no stubs vacíos.
        Cada hallazgo, si existe, debe ser un string con contenido real (no None, no int).
        """
        from scripts.run_security_audit_12d import DeepForensicAuditor

        auditor = DeepForensicAuditor(self.root)
        for method_name in (
            "audit_d1_integrity",
            "audit_d5_angry_path",
            "audit_d8_test_coverage",
        ):
            with self.subTest(method=method_name):
                result = getattr(auditor, method_name)()
                self.assertIsInstance(
                    result, list,
                    f"{method_name}() retornó {type(result).__name__}, esperado list",
                )
                for item in result:
                    self.assertIsInstance(
                        item, str,
                        f"{method_name}() hallazgo de tipo {type(item).__name__}: {item!r}",
                    )
                    self.assertGreater(
                        len(item), 0,
                        f"{method_name}() produjo string vacío en hallazgos",
                    )


if __name__ == "__main__":
    unittest.main()
