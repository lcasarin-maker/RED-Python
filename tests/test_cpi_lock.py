"""
TEST: test_cpi_lock.py
Unit tests for CoderCerberus Chain-Pattern Interrupt (CPI) lock and unlock CLI commands.
"""

import json
import unittest
from pathlib import Path
from scripts.pre_edit_guard import evaluate
from scripts.protocol_cli import ProtocolClient

class TestCPILock(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.state_file = self.root / ".agent_state.json"
        
        # Backup original state
        self.original_state = None
        if self.state_file.exists():
            self.original_state = json.loads(self.state_file.read_text(encoding="utf-8"))

    def tearDown(self):
        # Restore original state
        if self.original_state is not None:
            self.state_file.write_text(json.dumps(self.original_state, indent=2, ensure_ascii=False), encoding="utf-8")

    def test_cpi_lock_blocking(self):
        """Pilar 3: Verify pre_edit_guard blocks edits when reasoning_lock is active."""
        # Force lock in state file
        state = json.loads(self.state_file.read_text(encoding="utf-8"))
        state["reasoning_lock"] = True
        self.state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

        # Evaluate should return a reasoning_lock violation
        violations = evaluate("Edit", "test_file.py", "print('hello')")
        self.assertTrue(any("CPI reasoning_lock activo" in v for v in violations),
                        "Should block edits when reasoning_lock is active")

    def test_cpi_unlock_cli(self):
        """Pilar 3: Verify protocol_cli unlock command clears the lock and resets failures."""
        # Force lock in state file
        state = json.loads(self.state_file.read_text(encoding="utf-8"))
        state["reasoning_lock"] = True
        state["consecutive_failures"] = 3
        self.state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

        # Run unlock command
        client = ProtocolClient()
        code = client.command_unlock()
        self.assertEqual(code, 0, "Unlock command should succeed")

        # Verify state is cleared
        updated_state = json.loads(self.state_file.read_text(encoding="utf-8"))
        self.assertFalse(updated_state.get("reasoning_lock", True),
                         "reasoning_lock should be False after unlock")
        self.assertEqual(updated_state.get("consecutive_failures", -1), 0,
                         "consecutive_failures should be 0 after unlock")

if __name__ == "__main__":
    unittest.main()
