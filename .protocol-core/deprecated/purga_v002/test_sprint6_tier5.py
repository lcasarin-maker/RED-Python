"""
TEST: test_sprint6_tier5.py
Tests de integracion Sprint 6 -- Tier 5.
Cubre: compress_historial, cache_protocol_rules, auto_export_retrospective,
       smart_context_extractor.
"""
import json
import sqlite3
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── helpers ──────────────────────────────────────────────────────────────────

def _write_historial(path: Path, n_sessions: int = 2, old: bool = False) -> None:
    date = "2020-01-01" if old else "2099-12-31"
    content = ""
    for i in range(n_sessions):
        content += f"## SESION [{date}-S{i}]\n**Date:** {date}\nContent of session {i}.\n\n"
    path.write_text(content, encoding="utf-8")


def _write_regla(path: Path, num: int, title: str, rule_type: str = "SPEC") -> None:
    path.write_text(
        f"# REGLA #{num} — {title}\n\n**Estado:** active\n\n{rule_type} rule description here.\n",
        encoding="utf-8",
    )


# ─── compress_historial ───────────────────────────────────────────────────────

class TestCompressHistorial:
    def test_missing_historial_returns_false(self, tmp_path):
        from scripts.compress_historial import compress_historial
        result = compress_historial(tmp_path / "ghost.md", tmp_path / "archive")
        assert result is False

    def test_no_sessions_to_archive_returns_true(self, tmp_path):
        from scripts.compress_historial import compress_historial
        h = tmp_path / "HISTORIAL.md"
        # Future date session — not old enough to archive
        _write_historial(h, n_sessions=1, old=False)
        result = compress_historial(h, tmp_path / "archive", days_threshold=30)
        assert result is True
        # Negative: no archive file created for recent sessions
        assert list((tmp_path / "archive").glob("*.md")) == []

    def test_old_sessions_archived(self, tmp_path):
        from scripts.compress_historial import compress_historial
        h = tmp_path / "HISTORIAL.md"
        _write_historial(h, n_sessions=2, old=True)
        arc = tmp_path / "archive"
        result = compress_historial(h, arc, days_threshold=1)
        assert result is True
        archive_files = list(arc.glob("*.md"))
        assert len(archive_files) > 0

    def test_parse_sessions_returns_list(self):
        from scripts.compress_historial import parse_sessions
        content = "## SESION [2024-01-01-S1]\nContent\n\n## SESION [2024-01-02-S2]\nContent\n"
        sessions = parse_sessions(content)
        assert isinstance(sessions, list)
        assert len(sessions) == 2

    def test_parse_sessions_empty_content(self):
        from scripts.compress_historial import parse_sessions
        result = parse_sessions("# Just a header\nNo sessions here.")
        assert result == []

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "compress_historial.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "setup_windows_utf8" in source


# ─── cache_protocol_rules ─────────────────────────────────────────────────────

class TestCacheProtocolRules:
    def test_build_cache_missing_rules_dir_returns_false(self, tmp_path):
        from scripts.cache_protocol_rules import build_cache
        result = build_cache(tmp_path / "REGLAS", tmp_path / "cache.json")
        assert result is False

    def test_build_cache_empty_rules_dir_returns_false(self, tmp_path):
        from scripts.cache_protocol_rules import build_cache
        rules_dir = tmp_path / "REGLAS"
        rules_dir.mkdir()
        result = build_cache(rules_dir, tmp_path / "cache.json")
        assert result is False

    def test_build_cache_creates_valid_json(self, tmp_path):
        from scripts.cache_protocol_rules import build_cache
        rules_dir = tmp_path / "REGLAS"
        rules_dir.mkdir()
        _write_regla(rules_dir / "N01_test.md", 1, "Test Rule")
        cache_file = tmp_path / "cache.json"
        result = build_cache(rules_dir, cache_file)
        assert result is True
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert data["total_rules"] == 1
        assert len(data["rules"]) == 1

    def test_load_cache_missing_returns_none(self, tmp_path):
        from scripts.cache_protocol_rules import load_cache
        result = load_cache(tmp_path / "ghost.json")
        assert result is None

    def test_load_cache_valid_returns_dict(self, tmp_path):
        from scripts.cache_protocol_rules import build_cache, load_cache
        rules_dir = tmp_path / "REGLAS"
        rules_dir.mkdir()
        _write_regla(rules_dir / "N01_rule.md", 1, "Rule One")
        cache_file = tmp_path / "rules.json"
        build_cache(rules_dir, cache_file)
        loaded = load_cache(cache_file)
        assert loaded is not None
        assert "rules" in loaded

    def test_extract_rule_info_parses_number_and_title(self, tmp_path):
        from scripts.cache_protocol_rules import extract_rule_info
        f = tmp_path / "N07_sample.md"
        _write_regla(f, 7, "Sample Rule Title")
        info = extract_rule_info(f)
        assert info["number"] == 7
        assert "Sample Rule Title" in info["title"]

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "cache_protocol_rules.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source


# ─── auto_export_retrospective ────────────────────────────────────────────────

class TestAutoExportRetrospective:
    def test_extract_latest_session_missing_historial_returns_none(self, tmp_path):
        from scripts.auto_export_retrospective import AutoExportRetrospective
        exp = AutoExportRetrospective(historial_path=tmp_path / "ghost.md")
        result = exp.extract_latest_session()
        assert result is None

    def test_extract_latest_session_no_sessions_returns_none(self, tmp_path):
        from scripts.auto_export_retrospective import AutoExportRetrospective
        h = tmp_path / "HISTORIAL.md"
        h.write_text("# HISTORIAL\n\nNo session blocks here.\n", encoding="utf-8")
        exp = AutoExportRetrospective(historial_path=h)
        result = exp.extract_latest_session()
        assert result is None

    def test_auto_export_no_session_returns_status(self, tmp_path):
        from scripts.auto_export_retrospective import AutoExportRetrospective
        h = tmp_path / "HISTORIAL.md"
        h.write_text("# HISTORIAL\n\nEmpty.\n", encoding="utf-8")
        exp = AutoExportRetrospective(historial_path=h)
        result = exp.auto_export(export_json=False, export_db=False)
        assert result.get("status") == "no_session_found"

    def test_export_to_json_creates_file(self, tmp_path):
        from scripts.auto_export_retrospective import AutoExportRetrospective
        from uuid import uuid4
        exp = AutoExportRetrospective()
        session = {
            "session_id": str(uuid4()),
            "timestamp": "2099-01-01T00:00:00",
            "learning": "test learning",
            "violation": None,
            "next_agent_knows": None,
            "protocol_gaps": None,
            "token_efficiency": None,
        }
        out_dir = tmp_path / "exports"
        path = exp.export_to_json(session, out_dir)
        assert Path(path).exists()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert data["learning"] == "test learning"

    def test_setup_db_creates_table(self, tmp_path):
        from scripts.auto_export_retrospective import AutoExportRetrospective
        db = tmp_path / "test.db"
        exp = AutoExportRetrospective(db_path=str(db))
        exp.setup_db()
        conn = sqlite3.connect(str(db))
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        assert "retrospectives" in tables

    def test_uses_env_var_for_db_path(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CERBERUS_DB_PATH", str(tmp_path / "env.db"))
        from scripts.auto_export_retrospective import AutoExportRetrospective
        exp = AutoExportRetrospective()
        assert "env.db" in str(exp.db_path)

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "auto_export_retrospective.py").read_text(encoding="utf-8")
        assert "D:" + "/GoogleDrive" not in source
        assert "D:" + chr(92) + "GoogleDrive" not in source


# ─── smart_context_extractor ──────────────────────────────────────────────────

class TestSmartContextExtractor:
    def test_extract_keywords_finds_terms(self):
        from scripts.smart_context_extractor import extract_keywords
        kws = extract_keywords("fix heartbeat timeout in scraper.py")
        assert "heartbeat" in kws
        assert "scraper.py" in kws

    def test_extract_keywords_empty_task(self):
        from scripts.smart_context_extractor import extract_keywords
        kws = extract_keywords("")
        assert isinstance(kws, set)
        # Negative: empty task produces no keywords
        assert kws == set()

    def test_parse_status_md_returns_campos(self, tmp_path):
        from scripts.smart_context_extractor import parse_status_md
        content = "## CAMPO 1: Project\nproject info\n\n## CAMPO 6: Next\nnext session info"
        campos = parse_status_md(content)
        assert "1" in campos
        assert "6" in campos

    def test_parse_status_md_empty_returns_empty_dict(self):
        from scripts.smart_context_extractor import parse_status_md
        result = parse_status_md("No CAMPO sections here.")
        assert result == {}

    def test_score_campo_campo6_has_high_score(self):
        from scripts.smart_context_extractor import score_campo_relevance
        score = score_campo_relevance("6", "next session content", {"test"})
        assert score > 0.3

    def test_extract_relevant_context_returns_tuple(self, tmp_path):
        from scripts.smart_context_extractor import extract_relevant_context
        status = tmp_path / "STATUS.md"
        status.write_text(
            "## CAMPO 1: Project\nProj info\n\n## CAMPO 6: Next session\nDo heartbeat fix\n",
            encoding="utf-8",
        )
        ctx, saved, report = extract_relevant_context("fix heartbeat", status)
        assert isinstance(ctx, str)
        assert isinstance(saved, float)
        assert "keywords_found" in report

    def test_auto_compact_decision_returns_tuple(self, tmp_path):
        from scripts.smart_context_extractor import auto_compact_decision
        hist = tmp_path / "HISTORIAL.md"
        status = tmp_path / "STATUS.md"
        hist.write_text("# HISTORIAL\n\nShort.\n", encoding="utf-8")
        status.write_text("## CAMPO 1: Project\nProject info.\n", encoding="utf-8")
        should, reason, rec = auto_compact_decision(hist, status)
        assert isinstance(should, bool)
        # Negative: small files should NOT need compact
        assert should is False
        assert reason is None

    def test_uses_scripts_core_utils(self):
        source = (PROJECT_ROOT / "scripts" / "smart_context_extractor.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "setup_windows_utf8" in source
