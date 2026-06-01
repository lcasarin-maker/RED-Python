"""Smoke test de ejecutabilidad para cada script del repo.
Cada prueba verifica que el script exista y corra sin errores de import/codificación.
Los scripts con argparse/CLI se invocan con --help (valida wiring sin efectos).
No usa xfail: un script que no corre limpio es un fallo real, no un fallo esperado."""

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

# Generate parametrized tests for each script file.
# El filtro de __main__ (abajo) ya omite los módulos importables sin entrypoint.
# Esta lista contiene SOLO scripts que SÍ tienen __main__ pero es inseguro/inútil
# correr en un smoke test: destructivos o con efectos de estado sin --help seguro.
# (Sprint 6: minimal & real — verificado empíricamente con exit codes. Se podaron
#  2 entradas stale [scripts borrados] + 4 redundantes [sin __main__, ya auto-omitidas]
#  y se re-incluyó run_compliance_tests [--help exit 0].)
script_files = []
exclude_names = {
    "install_hooks.sh",          # muta los git hooks del repo
    "clean_satellites.py",       # destructivo: limpia .protocol-core de satélites
    "migrate_to_subtree.py",     # destructivo: migración git subtree
    "run_self_improvement.py",  # ignora --help y corre el loop completo (cuelga, exit 124)
    "detect_rule_code_drift.py",       # sin invocación segura sin args (exit 1 en bare)
    "track_tokens.py",          # sin invocación segura sin args (exit 1 en bare)
    "validate_security_tier.py", # corre la validación completa con efectos de estado
    "generate_rule_test_scaffold.py",  # efectos de estado: crea archivos de test
    "generate_rules_docs.py",    # efectos de estado: regenera documentación
}
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
