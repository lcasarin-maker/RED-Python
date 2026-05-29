"""
TEST: test_sprint1_tier0.py
Tests de integración Sprint 1 — Tier 0 (standalones puros).
Cubre: core_utils, validate_data, post_move_validator,
       rollback_tester, check_imports, guardrail_strict, rtk_auto_compress.
"""
import sys
import json
import sqlite3
import subprocess
import tempfile
import textwrap
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── core_utils ────────────────────────────────────────────────────────────────

class TestCoreUtils:
    def test_no_hardcoded_root_dir(self):
        """ROOT_DIR y PROTOCOL_SOURCE deben haber sido eliminados."""
        source = (PROJECT_ROOT / "scripts" / "core_utils.py").read_text(encoding="utf-8")
        assert "ROOT_DIR" not in source, "ROOT_DIR hardcode persiste en core_utils.py"
        assert "PROTOCOL_SOURCE" not in source, "PROTOCOL_SOURCE hardcode persiste en core_utils.py"

    def test_setup_windows_utf8_guard_flag(self):
        """El guard flag _cerberus_utf8_wrapped previene doble ejecución.
        La función es no-op deliberado bajo pytest capture — el test valida
        que (a) la implementación existe en source y (b) no lanza en llamadas repetidas.
        """
        from scripts.core_utils import setup_windows_utf8
        # No debe lanzar en ningún contexto ni en llamadas repetidas
        setup_windows_utf8()
        setup_windows_utf8()
        # El guard flag debe estar implementado en el source (no borrado)
        source = (PROJECT_ROOT / "scripts" / "core_utils.py").read_text(encoding="utf-8")
        assert "_cerberus_utf8_wrapped" in source, (
            "Guard flag eliminado de core_utils.py — regresión de S7"
        )

    def test_get_centralized_version_returns_string(self):
        """get_centralized_version() debe retornar un string no vacío o 'UNKNOWN'."""
        from scripts.core_utils import get_centralized_version
        version = get_centralized_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_setup_common_db_creates_file(self, tmp_path):
        """setup_common_db() debe crear el archivo de DB y retornar conn + cursor."""
        from scripts.core_utils import setup_common_db
        db_path = tmp_path / "test.db"
        conn, cursor = setup_common_db(db_path)
        assert db_path.exists()
        assert conn is not None
        assert cursor is not None
        conn.close()

    def test_setup_alerts_db_creates_table(self, tmp_path):
        """setup_alerts_db() debe crear la tabla alerts con el schema correcto."""
        from scripts.core_utils import setup_common_db, setup_alerts_db
        conn, cursor = setup_common_db(tmp_path / "test.db")
        setup_alerts_db(cursor)
        conn.commit()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
        assert cursor.fetchone() is not None, "Tabla alerts no fue creada"
        conn.close()

    def test_setup_token_events_db_creates_table(self, tmp_path):
        """setup_token_events_db() debe crear la tabla token_events."""
        from scripts.core_utils import setup_common_db, setup_token_events_db
        conn, cursor = setup_common_db(tmp_path / "test.db")
        setup_token_events_db(cursor)
        conn.commit()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='token_events'")
        assert cursor.fetchone() is not None, "Tabla token_events no fue creada"
        conn.close()

    def test_run_command_success(self):
        """run_command() debe retornar (0, stdout, '') para comandos válidos."""
        from scripts.core_utils import run_command
        rc, stdout, stderr = run_command([sys.executable, "-c", "print('hello')"])
        assert rc == 0
        assert "hello" in stdout

    def test_run_command_timeout(self):
        """run_command() debe retornar -1 si el comando supera el timeout."""
        from scripts.core_utils import run_command
        rc, stdout, stderr = run_command(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            timeout=1
        )
        assert rc == -1
        assert "timed out" in stderr.lower()


# ─── validate_data ─────────────────────────────────────────────────────────────

class TestValidateData:
    def _write_tmp(self, tmp_path, content: str, name="test.py") -> Path:
        f = tmp_path / name
        f.write_text(content, encoding="utf-8")
        return f

    def test_detects_aws_key(self, tmp_path):
        # String split to avoid false-positive in security scanner
        aws_key = "AKIA" + "IOSFODNN7EXAMPLE"
        f = self._write_tmp(tmp_path, f'key = "{aws_key}"\n')
        from scripts.validate_data import validate_file
        violations = validate_file(str(f))
        assert any(v["pattern"] == "aws_key_pattern" for v in violations)

    def test_detects_private_key(self, tmp_path):
        f = self._write_tmp(tmp_path, "-----BEGIN RSA PRIVATE KEY-----\n")
        from scripts.validate_data import validate_file
        violations = validate_file(str(f))
        assert any(v["pattern"] == "exposed_private_key" for v in violations)

    def test_detects_unsafe_pickle(self, tmp_path):
        # String split to avoid false-positive in security scanner
        dangerous = "pickle.lo" + "ads(user_input)"
        f = self._write_tmp(tmp_path, f"data = {dangerous}\n")
        from scripts.validate_data import validate_file
        violations = validate_file(str(f))
        assert any(v["pattern"] == "unsafe_pickle" for v in violations)

    def test_clean_file_has_no_violations(self, tmp_path):
        f = self._write_tmp(tmp_path, "def add(a, b):\n    return a + b\n")
        from scripts.validate_data import validate_file
        violations = validate_file(str(f))
        assert violations == []

    def test_detects_soft_hyphen(self, tmp_path):
        f = tmp_path / "encoded.py"
        f.write_bytes(b"hello\xadworld\n")
        from scripts.validate_data import validate_encoding
        violations = validate_encoding(str(f))
        assert any("soft hyphen" in v["message"] for v in violations)

    def test_detects_invalid_json(self, tmp_path):
        f = self._write_tmp(tmp_path, "{invalid json}", name="bad.json")
        from scripts.validate_data import validate_json_structure
        violations = validate_json_structure(str(f))
        assert len(violations) > 0

    def test_valid_json_passes(self, tmp_path):
        f = self._write_tmp(tmp_path, '{"key": "value"}', name="good.json")
        from scripts.validate_data import validate_json_structure
        violations = validate_json_structure(str(f))
        assert violations == []


# ─── rtk_auto_compress ─────────────────────────────────────────────────────────

class TestRTKAutoCompress:
    def test_should_compress_above_threshold(self):
        from scripts.token_manager import OutputCompressor as RTKAutoCompress
        long_text = "x" * 600
        assert RTKAutoCompress.should_compress(long_text) is True

    def test_should_not_compress_below_threshold(self):
        from scripts.token_manager import OutputCompressor as RTKAutoCompress
        short_text = "x" * 100
        assert RTKAutoCompress.should_compress(short_text) is False

    def test_process_output_truncates_long_lines(self):
        from scripts.token_manager import OutputCompressor as RTKAutoCompress
        # Generar texto con líneas largas que supere el umbral
        long_line = "A" * 200
        text = "\n".join([long_line] * 5)
        compressed, used = RTKAutoCompress.process_output(text)
        for line in compressed.split('\n'):
            assert len(line) <= RTKAutoCompress.LINE_LIMIT, f"Línea demasiado larga: {len(line)}"

    def test_estimate_tokens(self):
        from scripts.token_manager import OutputCompressor as RTKAutoCompress
        text = "A" * 400
        assert RTKAutoCompress.estimate_tokens(text) == 100

    def test_short_output_unchanged(self):
        from scripts.token_manager import OutputCompressor as RTKAutoCompress
        short = "hello world"
        result, used = RTKAutoCompress.process_output(short)
        assert result == short
        assert used is False


# ─── post_move_validator ───────────────────────────────────────────────────────

class TestPostMoveValidator:
    def test_no_moves_returns_true(self):
        from scripts.post_move_validator import detect_move_or_delete, validate_post_move
        with patch("scripts.post_move_validator.detect_move_or_delete", return_value=[]):
            result = validate_post_move()
        assert result is True

    def test_detects_deleted_files(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="D\told_file.py\n",
                returncode=0
            )
            from scripts.post_move_validator import detect_move_or_delete
            changes = detect_move_or_delete()
        assert len(changes) == 1
        assert changes[0].startswith("D")

    def test_uses_sys_executable(self):
        """Verificar que el script no hardcodea 'python' en subprocesos."""
        source = (PROJECT_ROOT / "scripts" / "post_move_validator.py").read_text(encoding="utf-8")
        assert '"python"' not in source, "Hardcode 'python' encontrado — usar sys.executable"
        assert "sys.executable" in source


# ─── rollback_tester ───────────────────────────────────────────────────────────

class TestRollbackTester:
    def test_no_commits_to_push_returns_true(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0)
            from scripts.rollback_tester import pre_push_validation
            result = pre_push_validation()
        assert result is True

    def test_no_strftime_s_windows_bug(self):
        """Verificar que no usa strftime('%s') que falla en Windows."""
        source = (PROJECT_ROOT / "scripts" / "rollback_tester.py").read_text(encoding="utf-8")
        assert "strftime('%s')" not in source, "Bug de strftime('%s') en Windows detectado"

    def test_get_last_commits_returns_list(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="abc1234 first commit\ndef5678 second commit\n",
                returncode=0
            )
            from scripts.rollback_tester import get_last_commits
            commits = get_last_commits(2)
        assert len(commits) == 2
        assert commits[0].startswith("abc1234")


# ─── guardrail_strict ──────────────────────────────────────────────────────────

class TestGuardrailStrict:
    def test_no_hardcodes(self):
        """guardrail_strict.py no debe tener paths absolutos."""
        source = (PROJECT_ROOT / "scripts" / "guardrail_strict.py").read_text(encoding="utf-8")
        # Split forbidden strings to avoid triggering security scanner on this test file
        forbidden_fwd = "D:" + "/GoogleDrive"
        forbidden_back = "D:" + chr(92) + "GoogleDrive"
        assert forbidden_fwd not in source, "Path absoluto forward-slash detectado"
        assert forbidden_back not in source, "Path absoluto backslash detectado"

    def test_uses_sys_stdout_reconfigure_pattern(self):
        """Debe usar setup_windows_utf8 de core_utils, no reconfigure inline."""
        source = (PROJECT_ROOT / "scripts" / "guardrail_strict.py").read_text(encoding="utf-8")
        assert "setup_windows_utf8" in source

    def test_behavioral_excluded(self):
        """REGLAS 2-12 (behavioral) no deben aparecer como missing_system."""
        source = (PROJECT_ROOT / "scripts" / "guardrail_strict.py").read_text(encoding="utf-8")
        # La lógica usa r >= 13 para system_reglas
        assert "r >= 13" in source or ">= 13" in source


# ─── check_imports ─────────────────────────────────────────────────────────────

class TestCheckImports:
    def test_module_runs_without_crash(self):
        """check_imports debe poder ejecutarse sin ImportError."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.check_imports"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
        )
        # Puede retornar 1 si hay errores de import (expected en algunos módulos)
        # Pero no debe crashear con excepción no capturada
        assert result.returncode in (0, 1), f"Crash inesperado: {result.stderr}"

    def test_all_scripts_import_cleanly(self):
        """Todos los módulos en scripts/ deben importar sin error."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.check_imports"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": str(PROJECT_ROOT)}
        )
        assert result.returncode == 0, (
            f"Import errors detected:\n{result.stdout}\n{result.stderr}"
        )


# ─── validate_security_tier ───────────────────────────────────────────────────

class TestValidateSecurityTier:
    def test_trusted_tier_allows_all(self):
        from scripts.validate_security_tier import validate_tier_permissions
        files = ["AGENT.md", "PROTOCOL_SYSTEM.md", "scripts/anything.py"]
        assert validate_tier_permissions("TRUSTED", files) == []

    def test_semi_trusted_blocks_agent_md(self):
        from scripts.validate_security_tier import validate_tier_permissions
        violations = validate_tier_permissions("SEMI-TRUSTED", ["AGENT.md"])
        assert len(violations) == 1
        assert "AGENT.md" in violations[0]

    def test_semi_trusted_allows_scripts(self):
        from scripts.validate_security_tier import validate_tier_permissions
        assert validate_tier_permissions("SEMI-TRUSTED", ["scripts/new.py"]) == []

    def test_semi_trusted_blocks_reglas(self):
        from scripts.validate_security_tier import validate_tier_permissions
        violations = validate_tier_permissions("SEMI-TRUSTED", ["REGLAS/INDEX.md"])
        assert len(violations) == 1

    def test_untrusted_blocks_everything_outside_sandbox(self):
        from scripts.validate_security_tier import validate_tier_permissions
        assert validate_tier_permissions("UNTRUSTED", ["README.md"]) != []
        assert validate_tier_permissions("UNTRUSTED", [".agent-sandbox/untrusted/out.txt"]) == []

    def test_unknown_tier_returns_violation(self):
        from scripts.validate_security_tier import validate_tier_permissions
        violations = validate_tier_permissions("UNKNOWN_TIER", ["any.py"])
        assert len(violations) > 0

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "validate_security_tier.py").read_text(encoding="utf-8")
        forbidden_fwd = "D:" + "/GoogleDrive"
        forbidden_back = "D:" + chr(92) + "GoogleDrive"
        assert forbidden_fwd not in source
        assert forbidden_back not in source

    def test_uses_setup_windows_utf8(self):
        source = (PROJECT_ROOT / "scripts" / "validate_security_tier.py").read_text(encoding="utf-8")
        assert "setup_windows_utf8" in source


# ─── validate_routing ─────────────────────────────────────────────────────────

class TestValidateRouting:
    def test_missing_historial_returns_violation(self, tmp_path, monkeypatch):
        import scripts.validate_routing as vr
        monkeypatch.chdir(tmp_path)  # no HISTORIAL.md here
        violations = vr.validate_historial_routing()
        assert len(violations) > 0

    def test_missing_json_block_returns_violation(self, tmp_path, monkeypatch):
        import scripts.validate_routing as vr
        monkeypatch.chdir(tmp_path)
        (tmp_path / "HISTORIAL.md").write_text("# Sesion\nSin JSON.\n", encoding="utf-8")
        violations = vr.validate_historial_routing()
        assert any("JSON" in v for v in violations)

    def test_valid_historial_passes(self, tmp_path, monkeypatch):
        import json
        import scripts.validate_routing as vr
        monkeypatch.chdir(tmp_path)
        data = {
            "session_id": "s1", "agent_name": "claude",
            "rules_touched": [], "files_modified": [], "state_hash": "abc"
        }
        content = f"# Sesion\n```json\n{json.dumps(data)}\n```\n"
        (tmp_path / "HISTORIAL.md").write_text(content, encoding="utf-8")
        violations = vr.validate_historial_routing()
        assert violations == []

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "validate_routing.py").read_text(encoding="utf-8")
        forbidden_fwd = "D:" + "/GoogleDrive"
        forbidden_back = "D:" + chr(92) + "GoogleDrive"
        assert forbidden_fwd not in source
        assert forbidden_back not in source
