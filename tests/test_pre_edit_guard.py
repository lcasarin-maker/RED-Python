"""
TEST: test_pre_edit_guard.py
Unit tests for CoderCerberus Pre-Edit Protocol Guard (pre_edit_guard.py).
"""

import unittest
from scripts.pre_edit_guard import evaluate

class TestPreEditGuard(unittest.TestCase):
    def test_s6_write_line_limit(self):
        """S6: Block full-file writes over 200 lines."""
        long_content = "line\n" * 205
        violations = evaluate("Write", "test_file.py", long_content)
        self.assertTrue(any("S6: Write de" in v for v in violations),
                        "Should violate S6: write size > 200 lines")

        # Edit tool should be exempt from full-file size block
        violations_edit = evaluate("Edit", "test_file.py", long_content)
        self.assertFalse(any("S6: Write de" in v for v in violations_edit),
                         "Edit tool should bypass full-file write limits")

        short_content = "line\n" * 50
        violations_short = evaluate("Write", "test_file.py", short_content)
        self.assertEqual(violations_short, [], "Short write should be clean")

    def test_s7_shell_mutations(self):
        """S7: Block shell mutation commands inside code edits."""
        shell_content = 'echo "bad code" >> target.py'
        violations = evaluate("Edit", "test_file.py", shell_content)
        self.assertTrue(any("S7: Comando shell con escritura detectado" in v for v in violations),
                        "Should block echo >> shell mutation")

        shell_pw = 'Add-Content -Path script.ps1 -Value "hello"'
        violations_pw = evaluate("Edit", "test_file.py", shell_pw)
        self.assertTrue(any("S7: Comando shell con escritura detectado" in v for v in violations_pw),
                        "Should block Add-Content shell mutation")

    def test_s19_zombie_compat_strings(self):
        """S19: Block compatibility shims and placeholder text."""
        zombie_content = "# for now compatibility shim"
        violations = evaluate("Edit", "test_file.py", zombie_content)
        self.assertTrue(any("shim explícito prohibido" in v for v in violations),
                        "Should block compatibility shims")

        fallback_content = "if new.exists() or old:"
        violations_fb = evaluate("Edit", "test_file.py", fallback_content)
        self.assertTrue(any("ruta alternativa de adopción prohibida" in v for v in violations_fb),
                        "Should block fallback exists() statements")

    def test_deprecated_path_block(self):
        """S19: Block edits inside deprecated/ folder."""
        violations = evaluate("Edit", "deprecated/old_script.py", "print('hello')")
        self.assertTrue(any("está en deprecated/ — edición prohibida" in v for v in violations),
                        "Should block edits to files inside deprecated/")

if __name__ == "__main__":
    unittest.main()
