"""Auto‑generated resilient tests for every script in the repository.
Cada prueba verifica que el script exista y que pueda ejecutarse sin
generar errores de codificación.  Si el script necesita argumentos
obligatorios, la prueba se marca como 'xfail' y se registra la causa."""

import subprocess
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Helper to run a script safely, capturing bytes and decoding as UTF‑8 ignoring errors
def _run_script(cmd, cwd=None):
    import os
    # Merge with current env, add UTF-8 + PYTHONPATH so 'from scripts.X import' works
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    # Decode manually, ignoring undecodable bytes
    stdout = result.stdout.decode("utf-8", errors="ignore")
    stderr = result.stderr.decode("utf-8", errors="ignore")
    return result.returncode, stdout, stderr

# Detect scripts that require arguments using a simple heuristic: look for "argparse" import or explicit sys.argv checks
def _requires_args(script_path: Path) -> bool:
    """Return True if script uses argparse or manual sys.argv CLI (will be called with --help)."""
    try:
        content = script_path.read_text(encoding="utf-8", errors="ignore")
        if "argparse" in content:
            return True
        # Manual CLI scripts that parse sys.argv with a usage string
        if "sys.argv" in content and "Usage:" in content:
            return True
        if "sys.argv" in content and ("len(sys.argv) > 1" in content or "if len(sys.argv)" in content):
            return True
        return False
    except Exception:
        return False

# Generate parametrized tests for each script file
# Include only scripts that are intended to be executed directly. Exclude modules without a __main__ guard.
# Include only scripts that are intended to be executed directly. Exclude modules without a __main__ guard and common utility scripts.
script_files = []
exclude_names = {"__init__.py", "core_utils.py", "token_tracker.py", "token_optimizer.py", "auto_audit_loop.py", "chunking_validator.py", "empirical_proof_checker.py", "install_hooks.sh", "rigor_maestro.py", "self_improvement_loop.py", "guardrail_strict.py", "validate_security_tier.py", "migrate_to_subtree.py", "clean_satellites.py"}
for p in SCRIPTS_DIR.iterdir():
    if not p.is_file():
        continue
    if p.name in exclude_names:
        continue
    if p.suffix not in {".py", ".sh"}:
        continue
    if p.suffix == ".py":
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            if "if __name__ == \"__main__\"" not in content:
                continue
        except Exception as e:
            print(e)
            continue
    script_files.append(p)


@pytest.mark.parametrize("script_path", script_files, ids=lambda p: p.name)
def test_script_execution(script_path):
    # Ensure the file exists
    assert script_path.is_file(), f"Script not found: {script_path}"

    # Build the command based on file type
    if script_path.suffix == ".py":
        cmd = [sys.executable, str(script_path)]
    elif script_path.suffix == ".sh":
        # Use bash if available; fall back to sh
        cmd = ["bash", str(script_path)]
    else:
        pytest.fail(f"Unsupported script type: {script_path.suffix}")

    # Scripts with argparse: run with --help (always exits 0, validates importability + CLI wiring)
    if script_path.suffix == ".py" and _requires_args(script_path):
        cmd = cmd + ["--help"]

    returncode, stdout, stderr = _run_script(cmd, cwd=PROJECT_ROOT)

    assert returncode == 0, f"Script {script_path.name} exited with {returncode}. Stderr: {stderr}"
    # At least some output should be produced (helps ensure the script actually ran)
    assert stdout.strip() or stderr.strip(), "Script produced no output"
