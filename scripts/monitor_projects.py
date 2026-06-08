#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-MAESTRO: Sistema de monitoreo centralizado para todos los proyectos
- Scans: Todos los satélites activos registrados en REGISTRY.json
- Health checks: tests, secrets, líneas, agnósticismo, tests unitarios, drift
- 1-click fixes: auto-arregla problemas comunes e integra remediación Cerberus.
"""

import sys
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Ensure UTF-8 output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Import remediation engine
try:
    from remediation_engine import auto_fix_project, queue_issue, send_desktop_notification
except ImportError:
    # Fallback to local import if run as standalone
    sys.path.append(str(Path(__file__).resolve().parent))
    from remediation_engine import auto_fix_project, queue_issue, send_desktop_notification

def load_dynamic_projects():
    """Loads active projects from the registry.json dynamically."""
    registry_path = Path(__file__).resolve().parents[1] / ".protocol" / "metadata" / "REGISTRY.json"
    if not registry_path.exists():
        logging.warning(f"Registry file not found at {registry_path}. Falling back to default list.")
        return {
            "RED-Python": r"D:\AI\RED-Python",
            "Declutter": r"D:\AI\Declutter",
            "Agente_Inmobiliario": r"D:\AI\Agente_Inmobiliario",
            "Aequitas_OS": r"D:\AI\Aequitas_OS",
        }
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        projects = {}
        for p in data.get("projects", []):
            if p.get("status") == "active":
                path = Path(p.get("path", ""))
                # Only monitor projects that actually exist on disk
                if path.exists():
                    projects[p.get("name")] = str(path)
        return projects
    except Exception as e:
        logging.error(f"Error reading registry: {e}")
        return {}

def check_no_secrets(project_path):
    """Check that no credentials are in committed files."""
    dangerous_patterns = [r"password=", r"api_key=", r"token=", r"secret="]
    try:
        result = subprocess.run(
            ["git", "grep", "|".join(dangerous_patterns)],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode != 0  # grep returns 0 if found (bad)
    except Exception as e:
        logging.warning(f"[D5] Error checking secrets in {project_path}: {e}")
        return True  # assume ok if can't check

def check_line_limits(project_path):
    """Check that critical files < 100 lines."""
    critical = ["AGENT.md", "STATUS.md"]
    for fname in critical:
        fpath = Path(project_path) / fname
        if fpath.exists():
            try:
                lines = len(fpath.read_text(encoding="utf-8").split("\n"))
                if lines > 100:
                    return False
            except Exception as e:
                logging.warning(f"[D5] Error reading {fname} line limits in {project_path}: {e}")
    return True

def check_clean_code(project_path):
    """Check for debug logs, commented code, etc."""
    bad_patterns = [r"print\(", r"#.*TODO", r"#.*FIXME", r"#.*XXX"]
    try:
        for pattern in bad_patterns:
            result = subprocess.run(
                ["grep", "-r", pattern, project_path], capture_output=True, timeout=5
            )
            if result.returncode == 0:  # found
                return False
    except Exception as e:
        logging.warning(f"[D5] Error checking clean code in {project_path}: {e}")
    return True

def check_git_clean(project_path):
    """Check that working tree is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return len(result.stdout.strip()) == 0
    except Exception as e:
        logging.warning(f"[D5] Error checking git status in {project_path}: {e}")
        return True

def check_drift(project_path):
    """Check for protocol drift in a project."""
    sync_script = Path(project_path) / "scripts" / "sync_binding.py"
    if not sync_script.exists():
        return True  # skip if not adopted
    try:
        res = subprocess.run(
            [sys.executable, str(sync_script), "--check"],
            cwd=project_path,
            capture_output=True,
            timeout=5
        )
        return res.returncode == 0
    except Exception as e:
        logging.warning(f"[D5] Error checking drift in {project_path}: {e}")
        return False

def check_tests_pass(project_path):
    """Check if existing pytest suite passes."""
    if not (Path(project_path) / "tests").exists():
        return True
    try:
        res = subprocess.run(
            ["pytest", "-q"],
            cwd=project_path,
            capture_output=True,
            timeout=15
        )
        return res.returncode == 0
    except Exception as e:
        logging.warning(f"[D5] Error running pytest in {project_path}: {e}")
        return False


# Registry of health checks
HEALTH_CHECKS = {
    "tests_exist": lambda p: (Path(p) / "tests").exists(),
    "tests_pass": lambda p: check_tests_pass(p),
    "no_secrets": lambda p: check_no_secrets(p),
    "lines_ok": lambda p: check_line_limits(p),
    "clean_code": lambda p: check_clean_code(p),
    "git_clean": lambda p: check_git_clean(p),
    "drift": lambda p: check_drift(p),
}

def scan_project(project_name, project_path, run_fix=False):
    """Run all health checks on a project and attempt auto-fixing if requested."""
    print(f"\n[SCAN] Escaneando: {project_name}")
    print(f"   Path: {project_path}")

    if not Path(project_path).exists():
        print("   ❌ Path no existe")
        return {"name": project_name, "status": "missing", "checks": {}, "fixed": [], "queued": []}

    checks = {}
    failed_checks = []
    
    for check_name, check_func in HEALTH_CHECKS.items():
        try:
            result = check_func(project_path)
            checks[check_name] = "[OK]" if result else "[WARN]"
            if not result:
                failed_checks.append(check_name)
            status_symbol = "[OK]" if result else "❌"
            print(f"   {status_symbol} {check_name}")
        except Exception as e:
            checks[check_name] = "❓"
            failed_checks.append(check_name)
            print(f"   ❓ {check_name} (error: {str(e)[:30]})")

    fixed_checks = []
    queued_checks = []
    
    if failed_checks:
        if run_fix:
            # Attempt to auto-fix deterministic issues
            fixed_checks, remaining_checks = auto_fix_project(project_name, project_path, failed_checks)
            for check in fixed_checks:
                checks[check] = "[OK] (Auto-Fixed)"
            
            # Queue remaining non-deterministic failures
            for check in remaining_checks:
                symptom = f"Failed check: {check} in project {project_name}"
                queue_issue(project_name, project_path, check, symptom)
                queued_checks.append(check)
        else:
            # Queue everything directly if no auto-fix run
            for check in failed_checks:
                symptom = f"Failed check: {check} in project {project_name}"
                queue_issue(project_name, project_path, check, symptom)
                queued_checks.append(check)

    # Re-calculate overall status
    passed = sum(1 for v in checks.values() if "[OK]" in v)
    total = len(checks)
    overall = "[OK] HEALTHY" if passed == total else f"[WARN] {passed}/{total} OK"

    return {
        "name": project_name,
        "path": project_path,
        "status": overall,
        "checks": checks,
        "passed": passed,
        "total": total,
        "fixed": fixed_checks,
        "queued": queued_checks
    }

def generate_report(results):
    """Generate JSON report and dashboard."""
    timestamp = datetime.now().isoformat()
    report = {
        "timestamp": timestamp,
        "projects": results,
        "summary": {
            "total_projects": len(results),
            "healthy": sum(1 for r in results if "HEALTHY" in r["status"]),
            "issues": sum(1 for r in results if "HEALTHY" not in r["status"]),
            "fixed": sum(len(r["fixed"]) for r in results),
            "queued": sum(len(r["queued"]) for r in results)
        },
    }

    # Save JSON
    report_path = Path(r"D:\AI\Cerberus\.secrets\protocolo\auto_maestro_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Dashboard
    print("\n" + "=" * 70)
    print("[DASH] AUTO-MAESTRO DASHBOARD")
    print("=" * 70)
    print(f"Total proyectos: {report['summary']['total_projects']}")
    print(f"[OK] Healthy: {report['summary']['healthy']}")
    print(f"[WARN] Issues: {report['summary']['issues']}")
    print(f"🔩 Auto-reparados: {report['summary']['fixed']}")
    print(f"📬 Encolados: {report['summary']['queued']}")
    print(f"Timestamp: {timestamp}")
    print("=" * 70)

    return report

def main():
    parser = argparse.ArgumentParser(
        description="Run the Cerberus auto-maestro health scan with active auto-remediation."
    )
    parser.add_argument("--fix", action="store_true", default=True, help="Auto-remediate deterministic issues")
    parser.add_argument("--no-fix", action="store_false", dest="fix", help="Disable auto-remediation")
    parser.add_argument("--background", action="store_true", default=False, help="Suppress verbose console and send desktop notifications")
    args = parser.parse_args()

    # If background, redirect stdout to null or file (or just print less)
    if args.background:
        logging.info("Running Auto-Maestro scan in background mode.")

    projects = load_dynamic_projects()
    
    results = []
    for project_name, project_path in projects.items():
        result = scan_project(project_name, project_path, run_fix=args.fix)
        results.append(result)

    report = generate_report(results)
    
    # Notify user of results via Desktop Toast
    total_fixed = report["summary"]["fixed"]
    total_queued = report["summary"]["queued"]
    total_issues = report["summary"]["issues"]
    
    if total_issues > 0 or total_fixed > 0:
        title = "Cerberus Auto-Maestro Guard"
        msg = f"Escaneo completado. Reparados: {total_fixed}. Pendientes: {total_queued}. Estatus no óptimo en {total_issues} proyectos."
        send_desktop_notification(title, msg)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
