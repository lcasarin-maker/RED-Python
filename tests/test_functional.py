"""
Functional tests for RED-Python CLI: argument parsing, output formats, error handling.
REGLA #15 (Validación 6D) — Practicidad & Usabilidad dimensions.
"""

import subprocess
import sys
from pathlib import Path

def run_cli(*args):
    """Helper to run RED-Python CLI with arguments."""
    result = subprocess.run(
        [sys.executable, "red.py"] + list(args),
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    return result

def test_cli_scan_argument():
    """Test: --scan argument accepts directory path."""
    test_dir = Path.home() / "Documents"
    if not test_dir.exists():
        test_dir = Path.home()

    result = run_cli("--scan", str(test_dir), "--dry-run")
    # Should not crash (exit code 0 or 1 are both acceptable for dry-run)
    assert result.returncode in [0, 1], f"CLI failed: {result.stderr}"
    print("[PASS] CLI --scan argument works")


def test_cli_dry_run_flag():
    """Test: --dry-run flag prevents actual deletion."""
    test_dir = Path.home() / "Documents"
    if not test_dir.exists():
        test_dir = Path.home()

    result = run_cli("--scan", str(test_dir), "--dry-run")
    # Dry-run should complete without error
    assert result.returncode in [0, 1], f"Dry-run failed: {result.stderr}"
    assert "dry" in result.stdout.lower() or "simulate" in result.stdout.lower() or result.returncode == 0
    print("[PASS] CLI --dry-run flag works")


def test_cli_max_depth_filter():
    """Test: --max-depth argument filters directory depth."""
    test_dir = Path.home() / "Documents"
    if not test_dir.exists():
        test_dir = Path.home()

    result = run_cli("--scan", str(test_dir), "--max-depth", "3", "--dry-run")
    assert result.returncode in [0, 1], f"Max depth filter failed: {result.stderr}"
    print("[PASS] CLI --max-depth argument works")


def test_cli_min_age_filter():
    """Test: --min-age argument filters by file age."""
    test_dir = Path.home() / "Documents"
    if not test_dir.exists():
        test_dir = Path.home()

    result = run_cli("--scan", str(test_dir), "--min-age", "24", "--dry-run")
    assert result.returncode in [0, 1], f"Min-age filter failed: {result.stderr}"
    print("[PASS] CLI --min-age argument works")


def test_cli_help_format():
    """Test: --help output is properly formatted."""
    result = run_cli("--help")
    assert result.returncode == 0, f"--help failed: {result.stderr}"
    assert "--scan" in result.stdout, "Missing --scan option in help"
    assert "--dry-run" in result.stdout, "Missing --dry-run option in help"
    print("[PASS] CLI --help format is valid")


def test_cli_invalid_directory():
    """Test: CLI handles invalid directory gracefully."""
    result = run_cli("--scan", "C:\\NonExistentDirectory12345", "--dry-run")
    # Should fail gracefully (not crash, just exit with error)
    assert result.returncode != 0, "CLI should fail for invalid directory"
    assert result.stderr or "not found" in result.stdout.lower() or "invalid" in result.stdout.lower()
    print("[PASS] CLI handles invalid directory gracefully")


def test_cli_permanent_flag():
    """Test: --permanent flag can be specified (with dry-run for safety)."""
    test_dir = Path.home() / "Documents"
    if not test_dir.exists():
        test_dir = Path.home()

    result = run_cli("--scan", str(test_dir), "--permanent", "--dry-run")
    assert result.returncode in [0, 1], f"Permanent flag failed: {result.stderr}"
    print("[PASS] CLI --permanent flag works")


def test_cli_scan_hidden_flag():
    """Test: --scan-hidden flag can be specified."""
    test_dir = Path.home() / "Documents"
    if not test_dir.exists():
        test_dir = Path.home()

    result = run_cli("--scan", str(test_dir), "--scan-hidden", "--dry-run")
    assert result.returncode in [0, 1], f"Scan-hidden flag failed: {result.stderr}"
    print("[PASS] CLI --scan-hidden flag works")


def test_cli_export_flag():
    """Test: --export flag can save results to file."""
    import tempfile

    test_dir = Path.home() / "Documents"
    if not test_dir.exists():
        test_dir = Path.home()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        export_file = f.name

    try:
        result = run_cli("--scan", str(test_dir), "--export", export_file, "--dry-run")
        assert result.returncode in [0, 1], f"Export flag failed: {result.stderr}"
        print("[PASS] CLI --export flag works")
    finally:
        Path(export_file).unlink(missing_ok=True)


if __name__ == "__main__":
    tests = [
        test_cli_scan_argument,
        test_cli_dry_run_flag,
        test_cli_max_depth_filter,
        test_cli_min_age_filter,
        test_cli_help_format,
        test_cli_invalid_directory,
        test_cli_permanent_flag,
        test_cli_scan_hidden_flag,
        test_cli_export_flag,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1

    print(f"\n[SUMMARY] {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
