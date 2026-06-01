#!/usr/bin/env python3
# repair_failing_tests.py
"""Automated iterative test repair runner.
Runs the test suite, stops at the first failure, analyses the error,
applies an automatic fix, re-runs the failing test, and repeats until
all tests pass or a maximum number of attempts is reached.
"""

import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent

# ---------- Helper Functions ----------

def run_tests(stop_on_fail: bool = True):
    """Run the unittest suite.
    Returns (exit_code, stdout, stderr).
    """
    cmd = [sys.executable, "-m", "unittest", "discover", "-v"]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
    )
    # Decode output safely, ignoring undecodable bytes
    stdout = proc.stdout.decode('utf-8', errors='ignore')
    stderr = proc.stderr.decode('utf-8', errors='ignore')
    return proc.returncode, stdout, stderr

def parse_failure(stdout: str):
    """Extract failing test details from unittest output.
    Returns a dict with file, module, class, method, traceback, message.
    """
    fail_pat = r"FAIL: (\w+) \(([^)]+)\)"
    m = re.search(fail_pat, stdout)
    if m:
        method = m.group(1)
        full_class = m.group(2)
        cls = full_class.split('.')[-1]
        module_path = ".".join(full_class.split('.')[:-1])
        file_path = REPO_ROOT / (module_path.replace('.', '/') + ".py")
        # grab traceback block after the FAIL line
        trace_pat = r"FAIL: .*?\n(Traceback[\s\S]+?)\n\n"
        trace_match = re.search(trace_pat, stdout)
        traceback = trace_match.group(1) if trace_match else ""
    else:
        # Fallback: look for any Traceback block (e.g., errors not marked as FAIL)
        trace_pat = r"Traceback[\s\S]+?(?=\n\n|$)"
        trace_match = re.search(trace_pat, stdout)
        traceback = trace_match.group(0) if trace_match else ""
        method = "<unknown>"
        cls = "<unknown>"
        module_path = ""
        # Guess file from first line of traceback if possible
        file_path = REPO_ROOT
    # final error message line
    msg_pat = r"(?:AssertionError|ImportError|AttributeError|SyntaxError): (.*)"
    msg_match = re.search(msg_pat, traceback)
    message = msg_match.group(1) if msg_match else ""
    return {
        "file": str(file_path),
        "module": module_path,
        "class": cls,
        "method": method,
        "traceback": traceback,
        "message": message,
    }

# ---------- Repair Handlers ----------

def handle_version_mismatch(info):
    """Synchronise version strings across SPEC.md, pre-commit hook, and tests.
    Returns True on success.
    """
    version_file = REPO_ROOT / "VERSION.txt"
    try:
        central = version_file.read_text().strip()
        if not central.startswith('v'):
            central = 'v' + central
    except Exception:
        return False
    # SPEC.md
    spec_path = REPO_ROOT / "SPEC.md"
    spec = spec_path.read_text(encoding='utf-8')
    spec_new = re.sub(r"\*\*Versi\u00f3n:\*\*\s*[^\n]+",
                       f"**Versión:** {central}", spec)
    spec_path.write_text(spec_new, encoding='utf-8')
    # pre-commit hook
    hook_path = REPO_ROOT / ".git/hooks/pre-commit"
    if hook_path.exists():
        hook = hook_path.read_text(encoding='utf-8')
        hook = re.sub(r"v\d+\.\d+", central, hook)
        hook_path.write_text(hook, encoding='utf-8')
    # test files with version literals
    for tf in REPO_ROOT.rglob('test_*.py'):
        txt = tf.read_text(encoding='utf-8')
        if re.search(r"v\d+\.\d+", txt):
            txt = re.sub(r"v\d+\.\d+", central, txt)
            tf.write_text(txt, encoding='utf-8')
    return True

def handle_missing_whitelist(info):
    """Reporta un archivo fuera de la whitelist — NO la edita automáticamente (S19/ASI-02).

    La whitelist de `_extract_whitelist()` en scripts/run_security_audit_12d.py es un CONTROL
    DE SEGURIDAD. Auto-ensancharla para silenciar un fallo del auditor es el mismo anti-patrón
    que el pip-install automático (VC-116): el auto-repair derrotaría al gate. Además la lógica
    previa apuntaba a `scripts/audit_10d.py` (renombrado → inexistente) y asumía la whitelist en
    una sola línea (hoy es multilínea), por lo que estaba doblemente rota.

    Fix: escalar al operador humano, que decide si el archivo legítimamente pertenece a la
    whitelist y lo agrega a mano en `_extract_whitelist`. Devuelve False (no auto-resuelto).
    """
    msg = info.get('message', '')
    m = re.search(r"'([^']+)'", msg)
    filename = m.group(1) if m else '<desconocido>'
    print(
        f"[import_error_guard] Archivo fuera de whitelist: '{filename}'.\n"
        "    NO se auto-agrega (la whitelist es un control de seguridad; auto-ensancharla\n"
        "    derrotaria al auditor - ver VC-116/ASI-02).\n"
        "    Accion humana: si es legitimo, agregalo a mano en\n"
        "    scripts/run_security_audit_12d.py::_extract_whitelist (set `base`)."
    )
    return False

def handle_lint_issues(_):
    """Run ruff to auto-fix lint/style issues.
    Uses the correct `ruff check . --fix` command. Errors are ignored – the goal is
    to apply any automatic fixes and let the test suite continue.
    Returns True always (unless ruff cannot be executed at all).
    """
    try:
        # Run ruff with proper argument order
        subprocess.run([sys.executable, "-m", "ruff", "check", ".", "--fix"], cwd=REPO_ROOT, check=False)
    except Exception as e:
        print(f"Ruff execution failed: {e}")
        return False
    return True

def handle_import_error(info):
    """Report missing module — does NOT install packages automatically (P6.2 / ASI-02).
    Silent pip install is forbidden: supply chain injection risk + breaks isolated envs.
    Fix: manually run  pip install <module>  or add to requirements.txt.
    Returns False so the repair loop escalates to the human operator.
    """
    msg = info.get('message', '')
    m = re.search(r"No module named '([^']+)'", msg)
    if not m:
        return False
    module = m.group(1)
    print(f"[import_error_guard] ImportError: module '{module}' missing. "
          f"Install manually: pip install {module}", flush=True)
    return False  # do not auto-install

# Register handlers with simple predicates
ERROR_HANDLERS = [
    (lambda i: 'version' in i.get('message', '').lower(), handle_version_mismatch),
    (lambda i: 'whitelist' in i.get('message', '').lower() or 'missing' in i.get('message', '').lower(), handle_missing_whitelist),
    (lambda i: 'ImportError' in i.get('traceback', ''), handle_import_error),
    (lambda i: True, handle_lint_issues),  # fallback lint fix
]

def _commit_fix(handler_name):
    """Commitea el fix aplicado (solo bajo opt-in commit_each, P6.2)."""
    subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT)
    subprocess.run(["git", "commit", "-m", f"Auto-fix: {handler_name}"], cwd=REPO_ROOT)


def _retest_passes(info):
    """Re-corre solo el test que fallaba; True si ahora pasa."""
    test_cmd = [sys.executable, "-m", "unittest",
                f"{info['module']}.{info['class']}.{info['method']}"]
    sub = subprocess.run(test_cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    return sub.returncode == 0


def _apply_handlers(info, commit_each):
    """Aplica los handlers al fallo. Devuelve (made_change, test_passes)."""
    made_change = False
    for pred, handler in ERROR_HANDLERS:
        if not pred(info):
            continue
        print(f"Attempting handler {handler.__name__}...")
        try:
            fixed = handler(info)
        except Exception as e:
            print(f"Handler raised: {e}")
            fixed = False
        if not fixed:
            continue
        made_change = True
        print("Handler succeeded.")
        if commit_each:
            _commit_fix(handler.__name__)
        if _retest_passes(info):
            print("Failing test now passes. Continuing suite.")
            return True, True
        print("Test still fails after fix, trying next handler.")
    return made_change, False


def main(max_iterations: int = 10, commit_each: bool = False):
    # commit_each=False by default — auto-commit requires explicit opt-in (P6.2)
    for _ in range(max_iterations):
        rc, out, _ = run_tests(stop_on_fail=True)
        if rc == 0:
            print("All tests passed!")
            return 0
        info = parse_failure(out)
        if not info:
            print("Unable to parse failure, aborting.")
            return 1
        print(f"Failure detected: {info['file']}::{info['class']}.{info['method']}")
        made_change, _ = _apply_handlers(info, commit_each)
        if not made_change:
            print("No automatic fix applicable. Stopping.")
            return 1
    print("Maximum iterations reached without full success.")
    return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Loop de auto-reparacion de tests (corre ruff --fix, sincroniza versiones, "
                    "reescribe el hook pre-commit). DESTRUCTIVO: requiere --run explicito.")
    parser.add_argument("--run", action="store_true",
                        help="Ejecuta el loop de reparacion (sin esto, solo imprime ayuda).")
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--commit-each", action="store_true",
                        help="Commitea tras cada fix (opt-in, P6.2).")
    args = parser.parse_args()
    if not args.run:
        parser.print_help()
        sys.exit(0)
    sys.exit(main(max_iterations=args.max_iterations, commit_each=args.commit_each))
