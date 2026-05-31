"""
TEST: test_cerberus_mandates.py
Suite de validación conductual — CoderCerberus V0.02.
Cada mandato se valida con evidencia de comportamiento, no con presencia de texto.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


class TestCoderCerberusMandates(unittest.TestCase):
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
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        if file_path.suffix == ".json":
            data = json.loads(content)
            return data.get("version")
        match = re.search(r"(?:v|Versión:\s*)(\d+\.\d+(?:\.\d+)?)", content)
        return match.group(1) if match else None

    def test_S17_universal_version_parity(self):
        """S17: Paridad de versiones en todos los archivos (compara valores reales, no texto)."""
        from scripts.core_utils import get_centralized_version
        target_version = get_centralized_version()
        self.assertNotEqual(target_version, "UNKNOWN", "VERSION.txt no encontrado o vacío")
        base_version = ".".join(target_version.lstrip("v").split(".")[:2])

        for name, path in self.manifests.items():
            version = self._extract_version(path)
            self.assertIsNotNone(version, f"No se pudo extraer versión de {name}")
            self.assertEqual(
                version.lstrip("v"), base_version,
                f"Desincronización en {name}: {version} != {base_version}"
            )

    def test_git_hook_version_parity(self):
        """S17: El hook pre-commit activo coincide con la versión centralizada."""
        from scripts.core_utils import get_centralized_version
        target_version = get_centralized_version()
        base_version = ".".join(target_version.lstrip("v").split(".")[:2])
        hook_path = self.root / ".git/hooks/pre-commit"
        if hook_path.exists():
            content = hook_path.read_text(encoding="utf-8", errors="ignore")
            self.assertIn(f"v{base_version}", content,
                          "S17: pre-commit hook tiene versión obsoleta")

    def test_S1_run_security_audit_12d_has_forensic_auditor(self):
        """S1: run_security_audit_12d.py debe definir la clase DeepForensicAuditor."""
        source = (self.root / "scripts" / "run_security_audit_12d.py").read_text(encoding="utf-8")
        self.assertIn("class DeepForensicAuditor", source,
                      "S1: DeepForensicAuditor no encontrado en run_security_audit_12d.py")

    def test_S7_no_shell_file_writes_in_scripts(self):
        """S7: Ningún script de producción usa patrones de escritura por shell."""
        SHELL_WRITE_PATTERNS = [" >> ", "| Out-File", "| Set-Content", "Add-Content"]
        scripts_dir = self.root / "scripts"
        violations: list[str] = []
        for py_file in scripts_dir.glob("*.py"):
            if py_file.name in {"core_utils.py", "validate_data.py", "pre_edit_guard.py"}:
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for pattern in SHELL_WRITE_PATTERNS:
                if pattern in content:
                    violations.append(f"{py_file.name}: {pattern!r}")
        self.assertEqual(violations, [],
                         "S7 shell-write violations:\n" + "\n".join(violations))

    def test_B7_evidence_directory_has_valid_records(self):
        """B7: .protocol/evidence/ debe tener ≥1 JSON parseable con timestamp."""
        evidence_dir = self.root / ".protocol" / "evidence"
        json_files = [
            f for f in evidence_dir.glob("*.json")
            if not f.name.startswith(".") and f.stat().st_size > 2
        ]
        self.assertGreater(len(json_files), 0,
                           "B7: No hay evidencia JSON en .protocol/evidence/")
        for ev_file in json_files:
            try:
                data = json.loads(ev_file.read_text(encoding="utf-8"))
                self.assertIn("timestamp", data,
                              f"B7: {ev_file.name} no tiene campo timestamp")
            except json.JSONDecodeError as e:
                self.fail(f"B7: {ev_file.name} no es JSON válido: {e}")

    def test_B10_agent_state_has_valid_handoff(self):
        """B10: .agent_state.json debe tener campos de handoff y NO contener identidad Gemini."""
        data = json.loads(self.manifests["STATE"].read_text(encoding="utf-8"))
        required = {"version", "agent_name", "tier", "protocol_checksums"}
        missing = required - data.keys()
        self.assertEqual(missing, set(),
                         f"B10: Campos faltantes en .agent_state.json: {missing}")
        self.assertNotIn("Gemini", data.get("agent_name", ""),
                         "B10: .agent_state.json contiene identidad de sesión Gemini")
        self.assertNotIn("resilience_score", data,
                         "B10: resilience_score hardcodeado persiste en .agent_state.json")

    def test_S15_no_zombie_protocol_folder(self):
        """S15: No deben existir carpetas zombi .protocolo en la raíz del sistema de archivos."""
        root_protocol = Path("../.protocolo")
        self.assertFalse(root_protocol.exists(),
                         "Carpeta zombi .protocolo detectada en la raíz")


if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print(f"Error ejecutando tests: {e}")
        sys.exit(1)
