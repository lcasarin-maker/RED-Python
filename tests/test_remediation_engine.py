#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for remediation_engine.py
"""

import sys
import json
from pathlib import Path
import pytest

# Adjust PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import remediation_engine

@pytest.fixture
def temp_queue_file(tmp_path, monkeypatch):
    """Overrides QUEUE_PATH to use a temp directory."""
    temp_queue = tmp_path / "remediation_queue.json"
    monkeypatch.setattr(remediation_engine, "QUEUE_PATH", temp_queue)
    return temp_queue

class TestRemediationEngine:
    def test_send_desktop_notification_no_crash(self, monkeypatch):
        """Verifies that sending notification does not crash the script."""
        called = []
        def inline_runner(cmd, *args, **kwargs):
            called.append(cmd)
            from subprocess import CompletedProcess
            return CompletedProcess(cmd, 0, b"", b"")
            
        monkeypatch.setattr(remediation_engine.subprocess, "run", inline_runner)
        
        remediation_engine.send_desktop_notification("Test Title", "Test Message", timeout=1)
        assert len(called) == 1
        assert "powershell" in called[0][0]

    def test_queue_issue_creation(self, temp_queue_file):
        """Verifies new issues are correctly added to the queue."""
        assert not temp_queue_file.exists()
        
        remediation_engine.queue_issue(
            project_name="TestProject",
            project_path=Path("/d/AI/TestProject"),
            check_name="tests_exist",
            symptom="No tests folder found"
        )
        
        assert temp_queue_file.exists()
        queue = remediation_engine.load_remediation_queue()
        assert len(queue) == 1
        assert queue[0]["project_name"] == "TestProject"
        assert queue[0]["check_name"] == "tests_exist"
        assert queue[0]["status"] == "pending"

    def test_queue_issue_no_duplicates(self, temp_queue_file):
        """Verifies duplicate issues update the timestamp/symptom instead of duplicating."""
        remediation_engine.queue_issue(
            project_name="TestProject",
            project_path=Path("/d/AI/TestProject"),
            check_name="tests_exist",
            symptom="Initial symptom"
        )
        
        remediation_engine.queue_issue(
            project_name="TestProject",
            project_path=Path("/d/AI/TestProject"),
            check_name="tests_exist",
            symptom="Updated symptom"
        )
        
        queue = remediation_engine.load_remediation_queue()
        assert len(queue) == 1
        assert queue[0]["symptom"] == "Updated symptom"

    def test_auto_fix_project_non_deterministic_remains(self, tmp_path):
        """Tests that non-deterministic checks are not modified and remain failed."""
        (tmp_path / "main.py").write_text("print('hello')\n")
        
        fixed, remaining = remediation_engine.auto_fix_project(
            project_name="TestProject",
            project_path=tmp_path,
            failed_checks=["tests_exist", "lines_ok"]
        )
        
        assert len(fixed) == 0
        assert "tests_exist" in remaining
        assert "lines_ok" in remaining

    def test_auto_fix_project_ruff_format(self, tmp_path, monkeypatch):
        """Tests that formatting is attempted and successfully classified as fixed."""
        bad_code = "def foo(x):\n  return x\n"
        (tmp_path / "bad.py").write_text(bad_code)
        
        called = []
        def inline_runner(cmd, cwd=None, *args, **kwargs):
            called.append(cmd)
            from subprocess import CompletedProcess
            return CompletedProcess(cmd, 0, b"", b"")
            
        monkeypatch.setattr(remediation_engine.subprocess, "run", inline_runner)
        
        fixed, remaining = remediation_engine.auto_fix_project(
            project_name="TestProject",
            project_path=tmp_path,
            failed_checks=["clean_code"]
        )
        
        assert "clean_code" in fixed
        assert "clean_code" not in remaining
        assert len(called) >= 1
