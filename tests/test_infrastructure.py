"""
tests/test_infrastructure.py
Infraestructura y gobernanza — CoderCerberus V0.02.

P5.4  Si no hay .git/hooks/pre-commit = fail (VT-105/VC-108)
P5.5  Centinela de dominios: audit_10d debe tener exactamente 10 dominios (VC-113/VT-108)
P5.3+P5.7  hard_excludes solo puede contener entradas del conjunto aprobado (VC-111/VT-106)
P7.1  audit_10d.py es el único entrypoint del auditor desde P7.1
"""

import os
import re
import unittest
from pathlib import Path

# Conjunto canónico de hard_excludes aprobados.
# Para añadir una nueva entrada:
#   1. Auditar el contenido del directorio con audit_10d (sin excluirlo).
#   2. Si está limpio O va a deprecated/ → añadir aquí con fecha y justificación en comentario.
APPROVED_HARD_EXCLUDES = frozenset({
    '.git',           # VCS metadata
    '__pycache__',    # Python bytecode
    '.pytest_cache',  # pytest cache
    '.ruff_cache',    # ruff cache
    'venv', 'env', '.venv',   # virtual envs
    'node_modules',   # JS deps
    '.protocol',      # governance metadata dir — codebase_map.json, evidence, manifests
    'evidence',       # .protocol/evidence — timestamped generated files, gitignored
    'backups',        # .protocol/metadata/backups — other projects' protocol copies, gitignored
    'exports',        # retrospective session exports, gitignored
    '.secrets',       # credentials, gitignored
    'deprecated',     # ÚNICA exención de negocio por protocolo CoderCerberus
    '.next',          # Generated NextJS build artifacts (P5.3)
    'dist',           # Distribution build directory (P5.3)
    'build',          # Compilation build outputs (P5.3)
    'out',            # Static HTML exports (P5.3)
    'playwright-report', # End-to-end browser testing reports
    'test-results',   # Test runs temporary artifacts
    'cfdi_downloads_sat', # Local SAT XML invoices downloads (business asset)
    'PROTOCOLO_GLOBAL', # Symlink/junction to central protocol (multi-repo lock)
})

EXPECTED_DOMAIN_COUNT = 10  # D1-D10 en audit_10d.py; si se añade D11, actualizar aquí Y el docstring


class TestInfrastructure(unittest.TestCase):

    def setUp(self):
        self.root = Path(".")
        self.auditor_path = self.root / "scripts" / "audit_10d.py"

    # -----------------------------------------------------------------------
    # P5.4 — Git hooks
    # -----------------------------------------------------------------------

    def test_pre_commit_hook_exists(self):
        """P5.4: .git/hooks/pre-commit debe existir — capa Hooks del 3-tier activa."""
        hook = self.root / ".git" / "hooks" / "pre-commit"
        self.assertTrue(hook.exists(),
            ".git/hooks/pre-commit faltante. "
            "La capa Hooks del protocolo 3-tier (Prose+Hooks+Tests) está rota. "
            "Instalar con: cp scripts/hooks/pre-commit .git/hooks/ && chmod +x .git/hooks/pre-commit")

    def test_pre_commit_hook_executable(self):
        """P5.4: El hook pre-commit debe ser ejecutable."""
        hook = self.root / ".git" / "hooks" / "pre-commit"
        if not hook.exists():
            self.skipTest("pre-commit hook no existe (ver test_pre_commit_hook_exists)")
        self.assertTrue(os.access(hook, os.X_OK),
            ".git/hooks/pre-commit existe pero no tiene permiso de ejecución.")

    def test_pre_commit_hook_references_protocol(self):
        """P5.4: El hook debe invocar la validación del protocolo (no es un hook vacío)."""
        hook = self.root / ".git" / "hooks" / "pre-commit"
        if not hook.exists():
            self.skipTest("pre-commit hook no existe (ver test_pre_commit_hook_exists)")
        content = hook.read_text(encoding='utf-8', errors='ignore')
        self.assertTrue(
            'protocol_cli' in content or 'rigor_maestro' in content or 'audit_10d' in content,
            "pre-commit hook existe pero no invoca ningún validador del protocolo.")

    # -----------------------------------------------------------------------
    # P5.5 — Nomenclature sentinel (audit_10d)
    # -----------------------------------------------------------------------

    def test_audit_10d_exists(self):
        """P7.1: audit_10d.py debe existir como único entrypoint del auditor (VC-113)."""
        self.assertTrue(self.auditor_path.exists(),
            "scripts/audit_10d.py no existe.")

    def test_audit_8d_does_not_exist(self):
        """S19 Anti-Zombie-Compat: audit_8d.py fue reemplazado por audit_10d.py (P7.1). No debe existir."""
        shim_path = self.root / "scripts" / "audit_8d.py"
        self.assertFalse(shim_path.exists(),
            "scripts/audit_8d.py no debe existir — fue reemplazado por audit_10d.py (P7.1, S19)")

    def test_audit_10d_domain_count_is_ten(self):
        """P5.5: Centinela — audit_10d.py debe tener exactamente 10 dominios D1-D10."""
        import sys
        sys.path.insert(0, str(self.root))
        import inspect as _inspect
        import re as _re
        from scripts.audit_10d import DeepForensicAuditor
        methods = [
            name for name, _ in _inspect.getmembers(DeepForensicAuditor, predicate=_inspect.isfunction)
            if _re.match(r'audit_d\d+_', name)
        ]
        self.assertEqual(len(methods), EXPECTED_DOMAIN_COUNT,
            f"audit_10d tiene {len(methods)} dominios {sorted(methods)} "
            f"(esperados: {EXPECTED_DOMAIN_COUNT}). "
            f"Actualizar EXPECTED_DOMAIN_COUNT en este test y el docstring de audit_10d.py.")

    def test_audit_10d_docstring_mentions_correct_count(self):
        """P5.5: El docstring de audit_10d.py debe mencionar '10' dominios."""
        content = self.auditor_path.read_text(encoding='utf-8')
        docstring_end = content.find('"""', content.find('"""') + 3)
        docstring = content[:docstring_end + 3]
        self.assertIn('10', docstring,
            "El docstring de audit_10d.py no menciona '10'. "
            "Mantener sincronizado con el número real de dominios.")

    # -----------------------------------------------------------------------
    # P5.3 + P5.7 — hard_excludes sentinel
    # -----------------------------------------------------------------------

    def _extract_hard_excludes(self, content: str) -> frozenset:
        """Extract hard_excludes entries, stripping inline comments."""
        m = re.search(r'self\.hard_excludes\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if not m:
            return None
        lines = m.group(1).split('\n')
        stripped = '\n'.join(re.sub(r'\s*#.*$', '', line) for line in lines)
        return frozenset(filter(None, re.findall(r"'([^']+)'", stripped)))

    def test_hard_excludes_only_approved_entries(self):
        """P5.3+P5.7: hard_excludes solo puede tener entradas del conjunto aprobado (VC-111/VT-106).
        Para añadir una entrada nueva: auditar contenido → si limpio o va a deprecated → añadir a
        APPROVED_HARD_EXCLUDES en este test con fecha y justificación."""
        content = self.auditor_path.read_text(encoding='utf-8')
        entries = self._extract_hard_excludes(content)
        self.assertIsNotNone(entries, "hard_excludes list not found in audit_10d.py — estructura cambiada?")
        unapproved = entries - APPROVED_HARD_EXCLUDES
        self.assertEqual(unapproved, frozenset(),
            f"Entradas NO aprobadas en hard_excludes: {unapproved}. "
            "Protocolo de exclusión: auditar contenido antes de excluir. "
            "Si son tooling artifacts puros, añadir a APPROVED_HARD_EXCLUDES arriba.")

    def test_hard_excludes_no_missing_approved_entries(self):
        """P5.7: Si se elimina una entry del conjunto aprobado, este test falla como advertencia."""
        content = self.auditor_path.read_text(encoding='utf-8')
        entries = self._extract_hard_excludes(content)
        if entries is None:
            self.skipTest("hard_excludes list not found")
        tooling_floor = frozenset({'.git', '__pycache__', '.pytest_cache', 'deprecated'})
        missing = tooling_floor - entries
        self.assertEqual(missing, frozenset(),
            f"Entradas mínimas faltantes en hard_excludes: {missing}. "
            "Verificar que no se eliminó accidentalmente infraestructura tooling.")
