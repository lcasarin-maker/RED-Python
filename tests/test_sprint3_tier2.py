"""
TEST: test_sprint3_tier2.py
Tests de integración Sprint 3 — Tier 2.
Cubre: permission_auditor, empirical_proof_checker, chunking_validator, hygiene_auditor.
"""
import ast
import json
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── permission_auditor ───────────────────────────────────────────────────────

class TestPermissionAuditor:
    def _make_settings(self, path: Path, allow: list) -> None:
        path.write_text(
            json.dumps({"permissions": {"allow": allow}}),
            encoding="utf-8",
        )

    def test_clean_settings_passes(self, tmp_path):
        from scripts.audit_permissions import audit_permission_file
        f = tmp_path / "settings.json"
        self._make_settings(f, ["Bash(python scripts/protocol_cli.py check)"])
        findings = audit_permission_file(f)
        assert findings == []

    def test_dangerous_git_reset_flagged(self, tmp_path):
        from scripts.audit_permissions import audit_permission_file
        f = tmp_path / "settings.json"
        self._make_settings(f, ["Bash(git reset --hard)"])
        findings = audit_permission_file(f)
        assert len(findings) > 0
        assert "git reset" in findings[0]

    def test_dangerous_python_c_flagged(self, tmp_path):
        from scripts.audit_permissions import audit_permission_file
        f = tmp_path / "settings.json"
        self._make_settings(f, ["Bash(python -c 'import os; os.system(\"rm -rf /\")'])"])
        findings = audit_permission_file(f)
        assert len(findings) > 0

    def test_missing_baseline_flagged(self, tmp_path):
        from scripts.audit_permissions import audit_permission_file
        f = tmp_path / "settings.json"
        self._make_settings(f, [])  # no required safe perms
        findings = audit_permission_file(f, require_safe_baseline=True)
        # Must flag all 3 missing required permissions
        assert len(findings) == 3

    def test_invalid_json_raises(self, tmp_path):
        from scripts.audit_permissions import audit_permission_file
        f = tmp_path / "settings.json"
        f.write_text("{invalid", encoding="utf-8")
        with pytest.raises(ValueError) as exc_info:
            audit_permission_file(f)
        assert "invalid JSON" in str(exc_info.value)

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "audit_permissions.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "sys.path.insert" not in source

    def test_run_missing_template_returns_false(self, tmp_path):
        from scripts.audit_permissions import run
        # No .claude/settings.template.json → template missing → False
        result = run(tmp_path)
        assert result is False

    def test_run_with_valid_template_passes(self, tmp_path):
        from scripts.audit_permissions import run
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        f = claude_dir / "settings.template.json"
        self._make_settings(f, [
            "Bash(python scripts/protocol_cli.py check)",
            "Bash(python scripts/protocol_cli.py sync --dry-run)",
            "Bash(python scripts/audit_6d_expanded.py)",
        ])
        result = run(tmp_path)
        assert result is True


# ─── empirical_proof_checker ──────────────────────────────────────────────────

class TestEmpiricalProofChecker:
    def test_check_proof_missing_evidence_dir_returns_false(self, tmp_path):
        from scripts.check_empirical_proof import check_proof
        result = check_proof("some_claim", evidence_dir=tmp_path / "nonexistent")
        assert result is False

    def test_check_proof_empty_dir_returns_false(self, tmp_path):
        from scripts.check_empirical_proof import check_proof
        ev = tmp_path / ".protocol" / "evidence"
        ev.mkdir(parents=True)
        result = check_proof("some_claim", evidence_dir=ev)
        assert result is False

    def test_check_proof_with_json_evidence_returns_true(self, tmp_path):
        from scripts.check_empirical_proof import check_proof
        ev = tmp_path / ".protocol" / "evidence"
        ev.mkdir(parents=True)
        (ev / "proof.json").write_text('{"ok": true}', encoding="utf-8")
        result = check_proof("some_claim", evidence_dir=ev)
        assert result is True

    def test_ui_files_filters_correctly(self):
        from scripts.check_empirical_proof import ui_files
        changed = ["src/app.js", "scripts/audit.py", "styles/main.css", "README.md"]
        result = ui_files(changed)
        assert "src/app.js" in result
        assert "styles/main.css" in result
        # Negative: non-UI files excluded
        non_ui = [f for f in result if not any(f.endswith(e) for e in [".html", ".js", ".jsx", ".tsx", ".css"])]
        assert non_ui == []

    def test_has_human_validation_empty_list_returns_true(self, tmp_path):
        from scripts.check_empirical_proof import has_human_validation
        # Empty file_list → vacuously true
        assert has_human_validation([]) is True

    def test_has_human_validation_missing_evidence_dir_returns_false(self, tmp_path):
        from scripts.check_empirical_proof import has_human_validation
        result = has_human_validation(["some.js"], evidence_dir=tmp_path / "noexist")
        assert result is False

    def test_get_file_hash_nonexistent_returns_empty(self, tmp_path):
        from scripts.check_empirical_proof import get_file_hash
        h = get_file_hash(tmp_path / "ghost.py")
        assert h == ""

    def test_get_file_hash_real_file_returns_hex(self, tmp_path):
        from scripts.check_empirical_proof import get_file_hash
        f = tmp_path / "test.py"
        f.write_text("x = 1", encoding="utf-8")
        h = get_file_hash(f)
        assert len(h) == 64  # SHA256 hex digest
        assert h != ""

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "check_empirical_proof.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "setup_windows_utf8" in source


# ─── chunking_validator ───────────────────────────────────────────────────────

class TestChunkingValidator:
    def test_valid_py_file_passes(self, tmp_path):
        from scripts.validate_chunking import validate_chunks
        f = tmp_path / "sample.py"
        f.write_text("def hello():\n    return 'world'\n", encoding="utf-8")
        assert validate_chunks(f) is True

    def test_nonexistent_file_returns_false(self, tmp_path):
        from scripts.validate_chunking import validate_chunks
        result = validate_chunks(tmp_path / "ghost.py")
        assert result is False

    def test_empty_file_returns_false(self, tmp_path):
        from scripts.validate_chunking import validate_chunks
        f = tmp_path / "empty.py"
        f.write_text("", encoding="utf-8")
        assert validate_chunks(f) is False

    def test_syntax_error_py_returns_false(self, tmp_path):
        from scripts.validate_chunking import validate_chunks
        f = tmp_path / "bad.py"
        f.write_text("def broken(\n", encoding="utf-8")
        assert validate_chunks(f) is False

    def test_valid_json_passes(self, tmp_path):
        from scripts.validate_chunking import validate_chunks
        f = tmp_path / "data.json"
        f.write_text('{"key": "value"}', encoding="utf-8")
        assert validate_chunks(f) is True

    def test_invalid_json_returns_false(self, tmp_path):
        from scripts.validate_chunking import validate_chunks
        f = tmp_path / "bad.json"
        f.write_text("{not valid json}", encoding="utf-8")
        assert validate_chunks(f) is False

    def test_hallucination_loop_detected(self, tmp_path):
        from scripts.validate_chunking import detect_repetition_loops
        repeated_line = "print('hello world')\n"
        content = repeated_line * 20  # 20 identical lines
        assert detect_repetition_loops(content) is True

    def test_no_loop_in_normal_content(self, tmp_path):
        from scripts.validate_chunking import detect_repetition_loops
        content = "\n".join(f"line_{i} = {i}" for i in range(20))
        assert detect_repetition_loops(content) is False

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "validate_chunking.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "setup_windows_utf8" in source


# ─── hygiene_auditor ──────────────────────────────────────────────────────────

class TestHygieneAuditor:
    def test_has_mojibake_detects_corruption(self):
        from scripts.audit_hygiene import has_mojibake
        # Build at runtime with chr() — avoids embedding the literal character in source,
        # which would itself be flagged by the hygiene_auditor on this test file.
        # chr(0xC3) = U+00C3, a known mojibake marker.
        corrupted = "texto " + chr(0xC3) + chr(0xA9) + " corrupto"
        assert has_mojibake(corrupted) is True

    def test_has_mojibake_clean_text_returns_false(self):
        from scripts.audit_hygiene import has_mojibake
        clean_samples = ["hello world", "normal text", "clean code"]
        false_positives = [s for s in clean_samples if has_mojibake(s)]
        assert false_positives == []

    def test_repair_mojibake_text_fixes_corruption(self):
        from scripts.audit_hygiene import repair_mojibake_text
        # Build corrupted/expected at runtime with chr() to keep source clean.
        # DIRECT_REPAIRS key: chr(0xe2)+chr(0x161)+chr(0xa0)+chr(0xfe0f) -> warning emoji
        corrupted = chr(0xe2) + chr(0x161) + chr(0xa0) + chr(0xfe0f)
        expected = chr(0x26a0) + chr(0xfe0f)   # U+26A0 U+FE0F = warning sign emoji
        assert repair_mojibake_text(corrupted) == expected

    def test_find_mojibake_empty_dir_returns_empty(self, tmp_path):
        from scripts.audit_hygiene import find_mojibake
        results = find_mojibake(tmp_path)
        assert results == []

    def test_find_mojibake_clean_file_no_findings(self, tmp_path):
        from scripts.audit_hygiene import find_mojibake
        f = tmp_path / "clean.md"
        f.write_text("# Clean markdown file", encoding="utf-8")
        findings = find_mojibake(tmp_path)
        assert findings == []

    def test_find_mojibake_corrupt_file_flagged(self, tmp_path):
        from scripts.audit_hygiene import find_mojibake
        f = tmp_path / "corrupt.md"
        # bytes([0xC3, 0x83]) = UTF-8 encoding of U+00C3, a known mojibake marker
        f.write_bytes(b"texto " + bytes([0xC3, 0x83]) + b" corrupto")
        findings = find_mojibake(tmp_path)
        assert len(findings) > 0
        assert findings[0].kind == "mojibake"
    def test_uses_setup_windows_utf8(self):
        source = (PROJECT_ROOT / "scripts" / "audit_hygiene.py").read_text(encoding="utf-8")
        assert "setup_windows_utf8" in source
        assert "sys.stdout.reconfigure" not in source

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "audit_hygiene.py").read_text(encoding="utf-8")
        forbidden_fwd = "D:" + "/GoogleDrive"
        forbidden_back = "D:" + chr(92) + "GoogleDrive"
        assert forbidden_fwd not in source
        assert forbidden_back not in source
