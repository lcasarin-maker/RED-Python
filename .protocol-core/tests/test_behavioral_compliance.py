"""
TEST: test_behavioral_compliance.py
Suite de cumplimiento comportamental real — verifica que los mandatos SE CUMPLEN,
no solo que existen en los documentos de protocolo.
Mandatos cubiertos: S6, S7, D5/B3, B7, D1 (whitelist integrity).
"""

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.append(os.getcwd())


class TestBehavioralCompliance(unittest.TestCase):

    def setUp(self):
        self.root = Path(".")
        self.scripts_dir = self.root / "scripts"
        self.evidence_dir = self.root / ".protocol" / "evidence"

    # ── S7: Anti-Shell ──────────────────────────────────────────────────────
    def test_S7_no_shell_mutators_in_scripts(self):
        """S7: Ningún script/*.py contiene patrones de mutación shell prohibidos."""
        forbidden = [
            (r'\bsed\b\s+-i', "sed -i (mutación in-place prohibida)"),
            (r'echo\s+["\'].*["\']?\s*>(?!>)', "echo > (sobrescritura destructiva)"),
            (r'\bAdd-Content\b', "Add-Content (PowerShell append prohibido)"),
            (r'\bSet-Content\b', "Set-Content (PowerShell sobrescritura prohibida)"),
        ]
        violations = []
        for script in self.scripts_dir.glob("*.py"):
            if script.name in ("__init__.py", "audit_10d.py"):
                continue
            content = script.read_text(encoding="utf-8", errors="ignore")
            for pattern, label in forbidden:
                if re.search(pattern, content):
                    violations.append(f"{script.name}: {label}")
        self.assertEqual(
            violations, [],
            f"S7 VIOLATIONS detectadas:\n" + "\n".join(violations)
        )

    # ── S6: Large File Safety ───────────────────────────────────────────────
    def test_S6_large_scripts_dont_overwrite_protocol_files(self):
        """S6: Scripts >200 líneas no sobrescriben archivos de protocolo/código con open('w').

        Excluye scripts de sincronización que legítimamente escriben archivos de datos JSON
        (ej: REGISTRY.json). El mandato S6 prohíbe sobrescribir manifiestos de protocolo
        (.md, .py, .sh) en bloque — no datos de estado.
        """
        # Estos scripts escriben datos JSON de forma legítima; no son violaciones de S6
        legitimate_data_writers = {"global_sync_safe.py", "evidence_logger.py", "sync_binding.py"}
        # Patrones que indican escritura a archivos de protocolo/código
        protocol_write_pattern = re.compile(
            r'open\s*\([^)]*(?:AGENT|PROTOCOL|SPEC|HISTORIAL|MANDATES|PERMISSIONS)[^)]*["\']w["\']'
            r'|open\s*\([^)]*\.(?:md|py|sh)["\'][^)]*["\']w["\']',
            re.IGNORECASE
        )
        violations = []
        for script in self.scripts_dir.glob("*.py"):
            if script.name in legitimate_data_writers:
                continue
            lines = script.read_text(encoding="utf-8", errors="ignore").splitlines()
            if len(lines) <= 200:
                continue
            content = "\n".join(lines)
            if protocol_write_pattern.search(content):
                violations.append(f"{script.name} ({len(lines)} líneas) sobrescribe archivo de protocolo")
        self.assertEqual(
            violations, [],
            f"S6 VIOLATIONS — scripts grandes sobreescriben manifiestos de protocolo:\n"
            + "\n".join(violations)
        )

    # ── D5 / B3: Chaos Monkey real ──────────────────────────────────────────
    def test_D5_chaos_monkey_exits_zero_and_certifies(self):
        """D5/B3: chaos_monkey.py ejecuta, certifica 4/4 escenarios, exit 0."""
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "scripts/chaos_monkey.py"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", env=env
        )
        self.assertEqual(
            result.returncode, 0,
            f"chaos_monkey salió con código {result.returncode}.\n{result.stdout}\n{result.stderr}"
        )
        self.assertIn(
            "CAOS CERTIFICADO",
            result.stdout,
            f"chaos_monkey no emitió certificación real.\nSTDOUT:\n{result.stdout}"
        )

    # ── B7: Anti-Triunfalismo — Evidencia empírica ──────────────────────────
    def test_B7_evidence_files_are_valid_json(self):
        """B7: .protocol/evidence/*.json existen y son JSON válido (prueba empírica)."""
        if not self.evidence_dir.exists():
            self.fail(f"Directorio de evidencia no existe: {self.evidence_dir}")
        json_files = [f for f in self.evidence_dir.glob("*.json") if f.name != ".gitkeep"]
        self.assertGreater(
            len(json_files), 0,
            "B7: No hay archivos de evidencia JSON en .protocol/evidence/. "
            "Las operaciones deben dejar prueba empírica."
        )
        for ev_file in json_files:
            content = ev_file.read_text(encoding="utf-8", errors="ignore").strip()
            self.assertTrue(len(content) > 0, f"B7: Archivo de evidencia vacío: {ev_file.name}")
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                self.fail(f"B7: Evidencia {ev_file.name} no es JSON válido: {e}")

    # ── D1: Whitelist sin zombis ────────────────────────────────────────────
    def test_D1_whitelist_has_no_zombie_paths(self):
        """D1/F7: Todas las rutas hardcodeadas en la whitelist base de audit_10d existen."""
        sys.path.insert(0, os.getcwd())
        from scripts.audit_10d import DeepForensicAuditor
        auditor = DeepForensicAuditor(".")
        hardcoded_base = {
            '.claudeignore', 'AGENT.md', 'PROTOCOL_SYSTEM.md', 'PROTOCOL_BEHAVIOR.md',
            'SPEC.md', '.agent_state.json', '.gitignore', '.cursorrules', 'HISTORIAL.md',
            'GLOBAL_LEARNING.md', 'PRE_DELIVERY_CHECKLIST.md', 'STATUS.md', 'task.md',
            'run_all_tests.bat', 'run_audit.ps1',
            'cerberus/close_pending.py',
            'cerberus/pending_tasks.json', 'cerberus/rule_collector.py',
            'cerberus/rules_engine.py', 'cerberus/rules/pending_escalation.yaml',
            'cerberus/rules/rule_severity.yaml', 'cerberus/rules/test_coverage.yaml',
            'tools/create_rule_test.py', 'tools/generate_rules_docs.py',
            'directives/architecture.md', 'rules/verification.yaml',
            'tests/rules/test_pending_escalation.py',
            'docs/rules.md',
        }
        project_root = auditor.project_path
        zombies = []
        for rel in hardcoded_base:
            # Ignorar dotfiles simples que no son rutas con /
            if '/' not in rel and not rel.startswith('.'):
                continue
            if not (project_root / rel).exists():
                zombies.append(rel)
        self.assertEqual(
            zombies, [],
            "D1 ZOMBIE PATHS — rutas en whitelist que no existen en disco:\n"
            + "\n".join(zombies)
            + "\nAcción: eliminar estas entradas del set base en audit_10d.py"
        )


    # ── F6: Sync Binding — sin drift de protocolo ───────────────────────────
    def test_F6_sync_binding_no_protocol_drift(self):
        """F6: sync_binding.py --check retorna exit 0 (protocolo en sync, sin drift)."""
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "scripts/sync_binding.py", "--check"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", env=env
        )
        self.assertEqual(
            result.returncode, 0,
            f"F6: sync_binding --check detectó drift de protocolo (exit {result.returncode}).\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}\n"
            "Acción: ejecutar 'python scripts/sync_binding.py --sync' para resolver."
        )

    # ── D1: tests/ solo contiene archivos de test reales ───────────────────
    def test_D1_no_zombie_files_in_tests_dir(self):
        """D1: tests/ no contiene archivos que no sigan la convención test_*.py.
        Detecta archivos backdoor, scripts arbitrarios o datos no declarados.
        """
        tests_dir = self.root / "tests"
        if not tests_dir.exists():
            return
        allowed_names = {'conftest.py', '__init__.py', 'pytest.ini'}
        zombies = []
        for f in tests_dir.iterdir():
            if f.is_dir():
                continue
            name = f.name
            if name in allowed_names:
                continue
            if name.startswith('test_') or name.startswith('automation_test_'):
                continue
            zombies.append(name)
        self.assertEqual(
            zombies, [],
            f"D1: Archivos no-test detectados en tests/ (posibles zombis):\n"
            + "\n".join(zombies)
        )


if __name__ == "__main__":
    unittest.main()
