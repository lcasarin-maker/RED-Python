"""
tests/test_performance.py — P4.7
Minimum performance checks for the Cerberus pipeline.
Fails if core scripts exceed time budgets — prevents performance regressions
from silently inflating CI time.

Budget thresholds (generous, to survive slow CI machines):
  run_security_audit_12d.py  — 120 s  (full 12-domain audit with 5 iterations)
  setup_validate.py  —   3 s  (bootstrap check; must be fast for pre-commit)
  verify_protocol_adoption — 15 s  (reads 17 project dirs)
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[1]


def _run_timed(script: str, args: list[str] | None = None) -> float:
    """Run a script via subprocess and return elapsed seconds."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / script)] + (args or [])
    t0 = time.perf_counter()
    subprocess.run(cmd, capture_output=True, env=env, check=False)
    return time.perf_counter() - t0


class TestPerformanceBudgets:
    def test_setup_validate_under_3s(self):
        """P4.7: setup_validate.py debe completar en <3s (pre-commit gate)."""
        elapsed = _run_timed("setup_validate.py")
        assert elapsed < 3.0, f"setup_validate.py tardó {elapsed:.1f}s (límite: 3s)"

    def test_verify_adoption_under_15s(self):
        """P4.7: verify_protocol_adoption.py debe completar en <15s."""
        elapsed = _run_timed("verify_protocol_adoption.py", ["--check"])
        assert elapsed < 15.0, f"verify_protocol_adoption.py tardó {elapsed:.1f}s (límite: 15s)"

    @pytest.mark.slow
    def test_run_security_audit_12d_under_120s(self):
        """P4.7: run_security_audit_12d.py (full audit) debe completar en <120s.
        Marcado como slow — excluir con: pytest -m 'not slow' para CI rápido."""
        elapsed = _run_timed("run_security_audit_12d.py")
        assert elapsed < 120.0, f"run_security_audit_12d.py tardó {elapsed:.1f}s (límite: 120s)"
