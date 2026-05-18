"""
Smoke tests for RED-Python CLI and GUI.
REGLA #15 (Validación 6D) — Practicidad dimension validation.
"""

import subprocess
import sys
import os
from pathlib import Path


def test_cli_help_available():
    """Smoke test: CLI --help works."""
    result = subprocess.run(
        [sys.executable, "red.py", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0, f"CLI --help failed: {result.stderr}"
    assert "RED-Python" in result.stdout or "usage" in result.stdout.lower()
    print("[PASS] CLI --help is accessible")


def test_executable_exists():
    """Smoke test: dist/RED-Python.exe is built and accessible."""
    exe_path = Path(__file__).parent.parent / "dist" / "RED-Python.exe"
    assert exe_path.exists(), f"Executable not found at {exe_path}"
    assert exe_path.stat().st_size > 1_000_000, "Executable suspiciously small (<1MB)"
    print(f"[PASS] Executable exists at {exe_path} ({exe_path.stat().st_size / 1_000_000:.1f} MB)")


def test_core_modules_importable():
    """Smoke test: Core Python modules load without syntax errors."""
    modules_to_check = ["core.py", "app.py", "filters.py", "config.py"]
    for module_file in modules_to_check:
        module_path = Path(__file__).parent.parent / module_file
        try:
            with open(module_path) as f:
                compile(f.read(), module_path, 'exec')
            print(f"[PASS] {module_file} compiles successfully")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {module_file}: {e}")


if __name__ == "__main__":
    try:
        test_cli_help_available()
        test_executable_exists()
        test_core_modules_importable()
        print("\n[PASS] All smoke tests passed (Practicidad dimension validated)")
    except AssertionError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        sys.exit(1)
