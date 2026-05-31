"""
TEST: test_sprint2_tier1.py
Tests de integración Sprint 2 — Tier 1 (scripts con dependencia en core_utils + DB).
Cubre: evidence_logger, token_tracker, alerts_viewer, deadlock_resolver, sync_binding.
"""
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


# ─── evidence_logger ──────────────────────────────────────────────────────────

class TestEvidenceLogger:
    def test_log_operation_creates_file(self, tmp_path):
        from scripts.evidence_logger import EvidenceLogger
        el = EvidenceLogger(root=tmp_path)
        path = el.log_operation(
            operation="audit",
            agent_name="claude",
            command="run_security_audit_12d.py",
            outcome="success",
        )
        assert Path(path).exists()

    def test_log_operation_valid_json(self, tmp_path):
        from scripts.evidence_logger import EvidenceLogger
        el = EvidenceLogger(root=tmp_path)
        path = el.log_operation("sync", "claude", "sync_binding.py", "success")
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert data["operation"] == "sync"
        assert data["agent_name"] == "claude"
        assert "timestamp" in data

    def test_retrieve_evidence_empty_dir(self, tmp_path):
        from scripts.evidence_logger import EvidenceLogger
        el = EvidenceLogger(root=tmp_path)
        # Remove evidence dir to simulate missing
        import shutil
        shutil.rmtree(tmp_path / ".protocol", ignore_errors=True)
        result = el.retrieve_evidence()
        assert result == []

    def test_retrieve_evidence_returns_logged(self, tmp_path):
        from scripts.evidence_logger import EvidenceLogger
        el = EvidenceLogger(root=tmp_path)
        el.log_operation("commit", "claude", "git commit", "success")
        results = el.retrieve_evidence()
        assert len(results) >= 1
        assert results[0]["operation"] == "commit"

    def test_validate_operation_no_evidence_returns_false(self, tmp_path):
        from scripts.evidence_logger import EvidenceLogger
        el = EvidenceLogger(root=tmp_path)
        # No evidence logged → must return False (negative path)
        result = el.validate_operation_approved("nonexistent_op")
        assert result is False

    def test_validate_operation_approved_with_d3(self, tmp_path):
        from scripts.evidence_logger import EvidenceLogger
        el = EvidenceLogger(root=tmp_path)
        el.log_operation(
            "promote", "claude", "promote.py", "success",
            validation_domains={"D3": True},
        )
        assert el.validate_operation_approved("promote") is True

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "evidence_logger.py").read_text(encoding="utf-8")
        forbidden = "D:" + "/GoogleDrive"
        assert forbidden not in source


# ─── token_tracker ────────────────────────────────────────────────────────────

class TestTokenTracker:
    def test_log_completion_inserts_row(self, tmp_path):
        from scripts.token_tracker import TokenTracker
        db = str(tmp_path / "tokens.db")
        tracker = TokenTracker(db_path=db)
        tracker.log_completion("agent1", "sess1", "claude-haiku", 1000, 1100)
        conn = sqlite3.connect(db)
        count = conn.execute("SELECT COUNT(*) FROM token_events").fetchone()[0]
        conn.close()
        tracker.close()
        assert count == 1

    def test_variance_alert_generated(self, tmp_path):
        """Varianza >20% debe generar alerta en tabla alerts."""
        from scripts.token_tracker import TokenTracker
        db = str(tmp_path / "tokens.db")
        tracker = TokenTracker(db_path=db)
        # 50% variance → alert
        tracker.log_completion("agent1", "sess1", "claude-haiku", 1000, 1500)
        alerts = tracker.get_alerts()
        tracker.close()
        assert len(alerts) > 0

    def test_no_alert_for_small_variance(self, tmp_path):
        """Varianza ≤20% NO debe generar alerta."""
        from scripts.token_tracker import TokenTracker
        db = str(tmp_path / "tokens.db")
        tracker = TokenTracker(db_path=db)
        # 5% variance → no alert
        tracker.log_completion("agent1", "sess1", "claude-haiku", 1000, 1050)
        alerts = tracker.get_alerts()
        tracker.close()
        assert alerts == []

    def test_get_summary_returns_list(self, tmp_path):
        from scripts.token_tracker import TokenTracker
        db = str(tmp_path / "tokens.db")
        tracker = TokenTracker(db_path=db)
        tracker.log_completion("agent1", "sess1", "claude-haiku", 500, 500)
        result = tracker.get_summary(days=30)
        tracker.close()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_uses_scripts_core_utils_import(self):
        """Verifica que usa import absoluto scripts.core_utils, no relativo."""
        source = (PROJECT_ROOT / "scripts" / "token_tracker.py").read_text(encoding="utf-8")
        assert "from scripts.core_utils import" in source
        assert "from .core_utils import" not in source

    def test_close_does_not_raise(self, tmp_path):
        from scripts.token_tracker import TokenTracker
        db = str(tmp_path / "tokens.db")
        tracker = TokenTracker(db_path=db)
        tracker.close()
        tracker.close()  # segunda llamada no debe crash
        # Verify object remains consistent (db_path preserved) after double-close
        assert tracker.db_path == Path(db)


# ─── alerts_viewer ────────────────────────────────────────────────────────────

class TestAlertsViewer:
    def _create_db_with_alerts(self, db_path: Path):
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity TEXT, type TEXT, message TEXT, agent_id TEXT
            )
        """)
        cursor.execute("INSERT INTO alerts (severity, type, message, agent_id) VALUES (?, ?, ?, ?)",
                       ("warn", "deadlock_detected", "Agent blocked", "claude"))
        cursor.execute("INSERT INTO alerts (severity, type, message, agent_id) VALUES (?, ?, ?, ?)",
                       ("info", "token_variance", "Variance 25%", "claude"))
        conn.commit()
        conn.close()

    def test_get_alerts_missing_db_returns_empty(self, tmp_path):
        from scripts.alerts_viewer import AlertsViewer
        viewer = AlertsViewer(db_path=str(tmp_path / "nonexistent.db"))
        # Negative: DB does not exist → returns []
        result = viewer.get_alerts()
        assert result == []

    def test_get_alerts_returns_rows(self, tmp_path):
        from scripts.alerts_viewer import AlertsViewer
        db = tmp_path / "state.db"
        self._create_db_with_alerts(db)
        viewer = AlertsViewer(db_path=str(db))
        alerts = viewer.get_alerts(limit=10)
        assert len(alerts) == 2

    def test_filter_by_severity(self, tmp_path):
        from scripts.alerts_viewer import AlertsViewer
        db = tmp_path / "state.db"
        self._create_db_with_alerts(db)
        viewer = AlertsViewer(db_path=str(db))
        # Only warn alerts
        warns = viewer.get_alerts(severity="warn")
        non_warn = [a for a in warns if a[1] != "warn"]
        assert non_warn == []

    def test_summary_returns_counts(self, tmp_path):
        from scripts.alerts_viewer import AlertsViewer
        db = tmp_path / "state.db"
        self._create_db_with_alerts(db)
        viewer = AlertsViewer(db_path=str(db))
        counts = viewer.summary()
        assert "warn" in counts
        assert counts["warn"] == 1

    def test_display_alerts_empty_no_crash(self, tmp_path, capsys):
        from scripts.alerts_viewer import AlertsViewer
        viewer = AlertsViewer(db_path=str(tmp_path / "x.db"))
        viewer.display_alerts([])
        out = capsys.readouterr().out
        assert "No alerts" in out

    def test_uses_env_var_for_db_path(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CERBERUS_DB_PATH", str(tmp_path / "env.db"))
        from scripts.alerts_viewer import AlertsViewer
        viewer = AlertsViewer()
        assert "env.db" in str(viewer.db_path)

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "alerts_viewer.py").read_text(encoding="utf-8")
        forbidden_fwd = "D:" + "/GoogleDrive"
        forbidden_back = "D:" + chr(92) + "GoogleDrive"
        assert forbidden_fwd not in source
        assert forbidden_back not in source


# ─── deadlock_resolver ────────────────────────────────────────────────────────

class TestDeadlockResolver:
    def _build_db(self, db_path: Path, agent: str, status: str, age_minutes: int = 0) -> None:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE agent_heartbeats (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME, agent_id TEXT, status TEXT
        )""")
        cursor.execute("""CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            severity TEXT, type TEXT, message TEXT, agent_id TEXT
        )""")
        interval = f"-{age_minutes} minutes"
        cursor.execute(
            "INSERT INTO agent_heartbeats (timestamp, agent_id, status) VALUES (datetime('now', ?), ?, ?)",
            (interval, agent, status)
        )
        conn.commit()
        conn.close()

    def test_check_all_empty_db_returns_zero(self, tmp_path):
        """Negative: DB sin agentes → 0 alertas."""
        db = tmp_path / "state.db"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE agent_heartbeats (id INTEGER PRIMARY KEY, timestamp DATETIME, agent_id TEXT, status TEXT)")
        conn.execute("CREATE TABLE alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, severity TEXT, type TEXT, message TEXT, agent_id TEXT)")
        conn.commit()
        conn.close()
        from scripts.deadlock_resolver import DeadlockResolver
        resolver = DeadlockResolver(str(db), threshold_minutes=1)
        alerts = resolver.check_all_agents()
        assert alerts == 0

    def test_blocked_agent_generates_alert(self, tmp_path):
        db = tmp_path / "state.db"
        self._build_db(db, "test_agent", "blocked", age_minutes=15)
        from scripts.deadlock_resolver import DeadlockResolver
        resolver = DeadlockResolver(str(db), threshold_minutes=1)
        alerts = resolver.check_all_agents()
        assert alerts > 0

    def test_fresh_alive_agent_no_alert(self, tmp_path):
        db = tmp_path / "state.db"
        self._build_db(db, "healthy", "alive", age_minutes=0)
        from scripts.deadlock_resolver import DeadlockResolver
        resolver = DeadlockResolver(str(db), threshold_minutes=60)
        alerts = resolver.check_all_agents()
        assert alerts == 0

    def test_no_hardcoded_paths(self):
        source = (PROJECT_ROOT / "scripts" / "deadlock_resolver.py").read_text(encoding="utf-8")
        forbidden_fwd = "D:" + "/GoogleDrive"
        assert forbidden_fwd not in source


# ─── sync_binding ─────────────────────────────────────────────────────────────

class TestSyncBinding:
    def test_check_changes_no_state_file(self, tmp_path):
        """Sin .agent_state.json todos los archivos aparecen como modificados."""
        from scripts.sync_binding import ProtocolSyncManager
        mgr = ProtocolSyncManager(root_dir=tmp_path)
        has_changes, changed = mgr.check_changes()
        assert isinstance(has_changes, bool)
        assert isinstance(changed, set)

    def test_update_checksums_writes_file(self, tmp_path):
        from scripts.sync_binding import ProtocolSyncManager
        mgr = ProtocolSyncManager(root_dir=tmp_path)
        mgr.update_checksums()
        state = json.loads((tmp_path / ".agent_state.json").read_text(encoding="utf-8"))
        assert "protocol_checksums" in state
        assert "last_sync" in state

    def test_no_changes_after_update(self, tmp_path):
        """Tras update_checksums, check_changes debe retornar has_changes=False."""
        # Crear los archivos de protocolo para que existan
        for fname in ["AGENT.md", "SPEC.md", "PROTOCOL_SYSTEM.md", "PROTOCOL_BEHAVIOR.md"]:
            (tmp_path / fname).write_text(f"# {fname}", encoding="utf-8")
        from scripts.sync_binding import ProtocolSyncManager
        mgr = ProtocolSyncManager(root_dir=tmp_path)
        mgr.update_checksums()
        # Recargar manager para que lea el estado guardado
        mgr2 = ProtocolSyncManager(root_dir=tmp_path)
        has_changes, changed = mgr2.check_changes()
        assert has_changes is False
        assert changed == set()

    def test_change_detected_after_file_modified(self, tmp_path):
        for fname in ["AGENT.md", "SPEC.md", "PROTOCOL_SYSTEM.md", "PROTOCOL_BEHAVIOR.md"]:
            (tmp_path / fname).write_text(f"# {fname}", encoding="utf-8")
        from scripts.sync_binding import ProtocolSyncManager
        mgr = ProtocolSyncManager(root_dir=tmp_path)
        mgr.update_checksums()
        # Modificar un archivo → debe detectar cambio
        (tmp_path / "AGENT.md").write_text("# AGENT.md — MODIFIED", encoding="utf-8")
        mgr2 = ProtocolSyncManager(root_dir=tmp_path)
        has_changes, changed = mgr2.check_changes()
        assert has_changes is True
        assert "AGENT.md" in changed

    def test_uses_setup_windows_utf8(self):
        source = (PROJECT_ROOT / "scripts" / "sync_binding.py").read_text(encoding="utf-8")
        assert "setup_windows_utf8" in source
        # No debe tener el bloque inline antiguo
        assert "sys.stdout.reconfigure" not in source
