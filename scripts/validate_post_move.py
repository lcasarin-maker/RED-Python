#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REGLA #17 — POST-MOVE VALIDATOR
Si moviste, renombraste o eliminaste un archivo → tests DEBEN pasar.
Caller: pre-commit hook.
"""
import sys
import subprocess
from pathlib import Path

from scripts.core_utils import setup_windows_utf8
setup_windows_utf8()


def detect_move_or_delete():
    """Detecta si hubo archivo movido, renombrado o eliminado en staging."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-status", "--cached"],
            capture_output=True, text=True, cwd=Path.cwd()
        )
        return [
            line for line in result.stdout.split('\n')
            if line.strip() and line.split('\t')[0] in ('D', 'R', 'T')
        ]
    except Exception as e:
        print(f"[ERROR] git diff failed: {e}")
        return []


def run_tests():
    """Ejecuta suite de tests. Retorna True si pasa."""
    test_dir = Path("tests")
    if not test_dir.exists():
        print("[WARN] tests/ not found, skipping")
        return True

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True, text=True, cwd=Path.cwd(), timeout=60
        )
        print(result.stdout)
        if result.returncode == 0:
            print("[OK] All tests passed")
            return True
        print("[FAIL] Some tests failed")
        return False
    except FileNotFoundError:
        print("[WARN] pytest not found, trying unittest")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests/", "-v"],
                capture_output=True, text=True, cwd=Path.cwd(), timeout=60
            )
            print(result.stdout)
            return result.returncode == 0
        except Exception as e:
            print(f"[WARN] No test framework found: {e}")
            return False


def validate_post_move():
    """Valida que tests pasen después de movimiento (REGLA #17)."""
    changes = detect_move_or_delete()
    if not changes:
        print("[OK] No file moves/renames detected")
        return True

    print(f"[ACTION] Detected {len(changes)} file moves/renames:")
    for change in changes:
        print(f"  {change}")

    print("\n[ACTION] Running test suite (REGLA #17)...")
    if run_tests():
        print("[OK] Tests passed after file move (REGLA #17 satisfied)")
        return True
    print("[CRITICAL] Tests FAILED after file move (REGLA #17 violated)")
    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="REGLA #17: Post-move validator")
    parser.add_argument("--force", action="store_true", help="Force test run even without moves")
    args = parser.parse_args()

    success = run_tests() if args.force else validate_post_move()
    sys.exit(0 if success else 1)
