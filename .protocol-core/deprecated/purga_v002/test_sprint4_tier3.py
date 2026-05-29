"""
TEST: test_sprint4_tier3.py
Tests de integracion Sprint 4 -- Tier 3.
Cubre: audit_6d_expanded (SilentFailureEnforcer, 6 domains).
"""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── helpers ──────────────────────────────────────────────────────────────────

def _make_valid_state(root: Path) -> None:
    """Create the minimal protocol files needed for D5 to pass."""
    for fname in ["AGENT.md", "SPEC.md", "PROTOCOL_SYSTEM.md", "PROTOCOL_BEHAVIOR.md"]:
        (root / fname).write_text(f"# {fname}", encoding="utf-8")
    (root / ".agent_state.json").write_text(
        json.dumps({"version": "0.02", "protocol_checksums": {}}),
        encoding="utf-8",
    )


def _make_tests_dir(root: Path) -> None:
    """Create a minimal tests/ directory with one passing test."""
    tests = root / "tests"
    tests.mkdir(exist_ok=True)
    (tests / "test_dummy.py").write_text(
        "def test_ok():\n    assert True\n",
        encoding="utf-8",
    )


# ─── SilentFailureEnforcer unit tests ─────────────────────────────────────────

class TestSilentFailureEnforcer:
    def test_init_sets_fix_flag(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer(fix=False)
        assert enforcer.fix is False

    def test_init_default_fix_true(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        assert enforcer.fix is True

    def test_cleanup_workspace_artifacts_removes_pycache(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        # Create a __pycache__ dir
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "mod.pyc").write_bytes(b"\x00")
        cleaned = enforcer.cleanup_workspace_artifacts()
        # Negative: pycache must be gone after cleanup
        assert not pycache.exists()
        assert len(cleaned) > 0

    def test_cleanup_skips_git_dir(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        # .git/__pycache__ must NOT be cleaned
        git_pycache = tmp_path / ".git" / "__pycache__"
        git_pycache.mkdir(parents=True)
        enforcer.cleanup_workspace_artifacts()
        assert git_pycache.exists()  # must survive

    def test_failures_dict_starts_empty(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        # No domain should be pre-populated — full negative path
        populated = [k for k in enforcer.failures]
        assert populated == []


# ─── Domain 3 (human validation) ──────────────────────────────────────────────

class TestDomain3HumanValidation:
    def test_no_ui_changes_passes(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        with patch("scripts.audit_6d_expanded.changed_files", return_value=[]):
            result = enforcer.audit_domain_3_human_validation()
        assert result is True

    def test_ui_changes_without_evidence_fails(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        with patch("scripts.audit_6d_expanded.changed_files", return_value=["app.js"]), \
             patch("scripts.audit_6d_expanded.ui_files", return_value=["app.js"]), \
             patch("scripts.audit_6d_expanded.has_human_validation", return_value=False):
            result = enforcer.audit_domain_3_human_validation()
        assert result is False
        assert "D3" in enforcer.failures


# ─── Domain 4 (security) ──────────────────────────────────────────────────────

class TestDomain4Security:
    def test_no_secrets_passes(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        (tmp_path / "safe.py").write_text('x = 1\n', encoding="utf-8")
        with patch("scripts.audit_6d_expanded.run_permission_audit", return_value=True):
            result = enforcer.audit_domain_4_security_io()
        assert result is True

    def test_hardcoded_secret_fails(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        # Write file with a 20+ char token value that matches the secret pattern.
        # Key split to avoid the D7 scanner triggering on this test file itself.
        fake_key = "AKIAIOSFODNN7EX" + "AMPLE1234567890"
        (tmp_path / "leak.py").write_text(
            f'api_key = "{fake_key}"\n',
            encoding="utf-8",
        )
        with patch("scripts.audit_6d_expanded.run_permission_audit", return_value=True):
            result = enforcer.audit_domain_4_security_io()
        assert result is False
        assert "D4" in enforcer.failures

    def test_permission_audit_failure_fails_domain(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        with patch("scripts.audit_6d_expanded.run_permission_audit", return_value=False):
            result = enforcer.audit_domain_4_security_io()
        assert result is False
        assert "D4" in enforcer.failures


# ─── Domain 5 (state integrity) ───────────────────────────────────────────────

class TestDomain5StateIntegrity:
    def test_all_critical_files_present_passes(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        _make_valid_state(tmp_path)
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        with patch("scripts.audit_6d_expanded.changed_files", return_value=[]):
            result = enforcer.audit_domain_5_state_integrity()
        assert result is True

    def test_missing_agent_md_fails(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        _make_valid_state(tmp_path)
        (tmp_path / "AGENT.md").unlink()
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        result = enforcer.audit_domain_5_state_integrity()
        assert result is False
        assert "D5" in enforcer.failures

    def test_invalid_state_json_fails(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        _make_valid_state(tmp_path)
        (tmp_path / ".agent_state.json").write_text("{bad json", encoding="utf-8")
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        result = enforcer.audit_domain_5_state_integrity()
        assert result is False
        assert "D5" in enforcer.failures

    def test_missing_version_key_fails(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        _make_valid_state(tmp_path)
        (tmp_path / ".agent_state.json").write_text('{"no_version": true}', encoding="utf-8")
        enforcer = SilentFailureEnforcer()
        enforcer.root = tmp_path
        with patch("scripts.audit_6d_expanded.changed_files", return_value=[]):
            result = enforcer.audit_domain_5_state_integrity()
        assert result is False


# ─── Domain 6 (workspace cleanup) ─────────────────────────────────────────────

class TestDomain6WorkspaceCleanup:
    def test_clean_workspace_passes(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        enforcer = SilentFailureEnforcer(fix=False)
        enforcer.root = tmp_path
        with patch("scripts.audit_6d_expanded.find_hygiene_findings", return_value=[]):
            result = enforcer.audit_domain_6_workspace_cleanup()
        assert result is True
        # No D6 failure should be recorded for a clean workspace
        d6_failures = [k for k in enforcer.failures if k == "D6"]
        assert d6_failures == []

    def test_hygiene_findings_fail_domain(self, tmp_path):
        from scripts.audit_6d_expanded import SilentFailureEnforcer
        from scripts.hygiene_auditor import HygieneFinding
        enforcer = SilentFailureEnforcer(fix=False)
        enforcer.root = tmp_path
        fake_finding = HygieneFinding(kind="mojibake", path="test.md", line=1, detail="corrupted")
        with patch("scripts.audit_6d_expanded.find_hygiene_findings", return_value=[fake_finding]):
            result = enforcer.audit_domain_6_workspace_cleanup()
        assert result is False
        assert "D6" in enforcer.failures


# ─── Source quality checks ─────────────────────────────────────────────────────

class TestAudit6dExpandedSource:
    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "audit_6d_expanded.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        # sys.path bootstrap is required for direct CLI invocation (rigor_maestro.py pattern)

    def test_no_relative_imports(self):
        source = (PROJECT_ROOT / "scripts" / "audit_6d_expanded.py").read_text(encoding="utf-8")
        # All imports must be absolute
        assert "from .core_utils" not in source
        assert "from .chunking_validator" not in source

    def test_re_imported_at_module_level(self):
        source = (PROJECT_ROOT / "scripts" / "audit_6d_expanded.py").read_text(encoding="utf-8")
        lines = source.splitlines()
        # import re must appear in the top-level imports, not inside a function
        import_line = next((i for i, l in enumerate(lines) if l.strip() == "import re"), None)
        assert import_line is not None
        # Must be before the first class definition
        class_line = next(i for i, l in enumerate(lines) if l.startswith("class "))
        assert import_line < class_line

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "audit_6d_expanded.py").read_text(encoding="utf-8")
        assert "D:" + "/GoogleDrive" not in source
        assert "D:" + chr(92) + "GoogleDrive" not in source

    def test_uses_sys_executable(self):
        source = (PROJECT_ROOT / "scripts" / "audit_6d_expanded.py").read_text(encoding="utf-8")
        assert "sys.executable" in source
        # Must NOT use bare "python" string in subprocess calls
        assert 'subprocess.run(["python"' not in source
