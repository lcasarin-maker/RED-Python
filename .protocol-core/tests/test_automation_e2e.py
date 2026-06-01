#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
END-TO-END AUTOMATION TESTS — FASE 7 (LIVE & RESCUED)
Valida que toda la automatización activa y las reglas de higiene funcionan correctamente.
"""

import pytest
import tempfile
import sqlite3
import re
import base64
from pathlib import Path

class TestAutomationE2E:
    """7 smoke tests para validar la automatización completa y viva del sistema."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment with temporary database"""
        # Use temporary directory for test database (no hardcoded paths)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db = str(Path(self.temp_dir.name) / "test_protocol.db")
        yield
        # Cleanup
        self.temp_dir.cleanup()

    def test_1_pre_commit_credentials_blocked(self):
        """Test: run_security_audit_12d.py detecta credenciales e impide commits inseguros"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_creds.py"
            # Generate fake credential dynamically (no hardcoded strings)
            fake_key = "sk-" + ("a" * 20)
            test_file.write_text(f'api_key = "{fake_key}"')

            from scripts.run_security_audit_12d import DeepForensicAuditor
            auditor = DeepForensicAuditor(Path(tmpdir))
            errors = auditor.audit_d7_data_security()

            assert any("Credenciales hardcodeadas" in err for err in errors)

    def test_2_retrospective_validation(self):
        """Test: Validaciones de retrospectiva en HISTORIAL.md operan correctamente"""
        from tests.automation_test_regla_21_retrospective import test_retrospective_json_valid
        # Verify REGLA #28: HISTORIAL.md must exist for retrospective validation
        historial_path = Path("HISTORIAL.md")
        assert historial_path.exists(), "HISTORIAL.md must exist for REGLA #28 validation"
        # Function raises AssertionError if JSON validation fails
        test_retrospective_json_valid()

    def test_3_token_tracker_logging(self):
        """Test: Token tracker auto-logs eventos y escribe en base de datos sqlite"""
        from scripts.track_tokens import TokenTracker

        tracker = TokenTracker(self.test_db)

        # Log an event
        tracker.log_completion(
            agent_id="test_claude",
            session_id="test_session_001",
            model="claude-haiku",
            tokens_estimated=2000,
            tokens_actual=1800,
            note="Test event"
        )

        # Verify in DB
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM token_events WHERE agent_id=?", ("test_claude",))
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1
        tracker.close()

    def test_5_heartbeat_monitor_pings(self):
        """Test: Heartbeat monitor registra pings de agentes y escribe JSONs válidos"""
        import json
        from scripts.monitor_heartbeat import HeartbeatMonitor

        # Use temporary directory for heartbeat files (no hardcoded paths)
        heartbeat_temp = tempfile.TemporaryDirectory()
        monitor = HeartbeatMonitor(heartbeat_dir=heartbeat_temp.name)

        # Create a temporary project directory to monitor
        project_temp = tempfile.TemporaryDirectory()

        try:
            heartbeat = monitor.ping_project("test_project_e2e", project_temp.name)

            # Verify heartbeat object is valid
            assert heartbeat is not None, "Heartbeat should not be None"
            assert "timestamp" in heartbeat, "Heartbeat should have timestamp"
            assert "project" in heartbeat, "Heartbeat should have project field"
            assert "status" in heartbeat, "Heartbeat should have status field"

            # Verify heartbeat file was created
            hfile = Path(heartbeat_temp.name) / "test_project_e2e_heartbeat.json"
            assert hfile.exists(), f"Heartbeat file should be created at {hfile}"

            # Verify heartbeat file contains valid JSON
            with open(hfile, 'r', encoding='utf-8') as f:
                file_contents = json.load(f)
            assert file_contents["project"] == "test_project_e2e", "File should contain correct project name"
            assert file_contents["status"] in ["alive", "blocked"], "File status should be valid"
        finally:
            # Cleanup
            heartbeat_temp.cleanup()
            project_temp.cleanup()

    def test_6_deadlock_detection(self):
        """Test: Deadlock resolver detecta bloqueos en base a heartbeats de agentes"""
        from scripts.resolve_deadlocks import DeadlockResolver

        resolver = DeadlockResolver(self.test_db, threshold_minutes=1)

        # Setup DB with blocked agent
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE agent_heartbeats (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME,
                agent_id TEXT,
                status TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE alerts (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity TEXT,
                type TEXT,
                message TEXT,
                agent_id TEXT
            )
        """)

        # Insert old, blocked heartbeat
        cursor.execute(
            "INSERT INTO agent_heartbeats (timestamp, agent_id, status) VALUES (datetime('now', '-15 minutes'), 'test_agent', 'blocked')"
        )
        conn.commit()
        conn.close()

        # Check for deadlock
        alerts = resolver.check_all_agents()

        # Should have detected deadlock
        assert alerts > 0

    def test_7_encoding_fix(self):
        """Test: audit_hygiene.py detecta y repara mojibakes y codificaciones corruptas"""
        from scripts.audit_hygiene import has_mojibake, repair_mojibake_text

        # Positive: detects known mojibake markers
        assert has_mojibake("normal text \u00c3\u00c2 corrupt")

        # Negative path: clean text must never be flagged (no false positives)
        clean_samples = ["hello world", "code clean", "normal text"]
        false_positives = [s for s in clean_samples if has_mojibake(s)]
        assert false_positives == []

        # Test: repair_mojibake_text repairs CP1252 mojibake artifacts
        corrupted = "Atención \u00e2\u0161\u00a0\ufe0f Alerta"
        repaired = repair_mojibake_text(corrupted)
        assert "\u26a0\ufe0f" in repaired  # Should contain warning icon emoji
