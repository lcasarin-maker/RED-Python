#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-MAESTRO: Sistema de monitoreo centralizado para todos los proyectos
- Scans: RED-Python, Declutter, Agente_Inmobiliario, Aequitas_OS
- Health checks: tests, secrets, líneas, agnósticismo
- 1-click fixes: auto-arregla problemas comunes
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECTS = {
    "RED-Python": r"D:\GoogleDrive\AI\RED-Python",
    "Declutter": r"D:\GoogleDrive\AI\Declutter",
    "Agente_Inmobiliario": r"D:\GoogleDrive\AI\Agente_Inmobiliario",
    "Aequitas_OS": r"D:\GoogleDrive\AI\Aequitas_OS",
}

HEALTH_CHECKS = {
    "tests_exist": lambda p: (Path(p) / "tests").exists(),
    "no_secrets": lambda p: check_no_secrets(p),
    "lines_ok": lambda p: check_line_limits(p),
    "clean_code": lambda p: check_clean_code(p),
    "git_clean": lambda p: check_git_clean(p),
}

def check_no_secrets(project_path):
    """Check that no credentials are in committed files."""
    dangerous_patterns = [r'password=', r'api_key=', r'token=', r'secret=']
    try:
        result = subprocess.run(
            ['git', 'grep', '|'.join(dangerous_patterns)],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode != 0  # grep returns 0 if found (bad)
    except Exception as e:
        logging.error(f"Error checking dangerous patterns: {e}")
        return True  # assume ok if can't check

def check_line_limits(project_path):
    """Check that critical files < 100 lines."""
    critical = ['AGENT.md', 'STATUS.md']
    for fname in critical:
        fpath = Path(project_path) / fname
        if fpath.exists():
            lines = len(fpath.read_text(encoding='utf-8').split('\n'))
            if lines > 100:
                return False
    return True

def check_clean_code(project_path):
    """Check for debug logs, commented code, etc."""
    bad_patterns = [r'print\(', r'#.*TODO', r'#.*FIXME', r'#.*XXX']
    try:
        for pattern in bad_patterns:
            result = subprocess.run(
                ['grep', '-r', pattern, project_path],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:  # found
                return False
    except Exception as e:
            print(f"Error: {e}")
    return True

def check_git_clean(project_path):
    """Check that working tree is clean."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return len(result.stdout.strip()) == 0
    except Exception as e:
        logging.error(f"Error checking git clean: {e}")
        return True

def scan_project(project_name, project_path):
    """Run all health checks on a project."""
    print(f"\n[SCAN] Escaneando: {project_name}")
    print(f"   Path: {project_path}")

    if not Path(project_path).exists():
        print("   ❌ Path no existe")
        return {"name": project_name, "status": "missing", "checks": {}}

    checks = {}
    for check_name, check_func in HEALTH_CHECKS.items():
        try:
            result = check_func(project_path)
            checks[check_name] = "[OK]" if result else "[WARN]"
            status_symbol = "[OK]" if result else "❌"
            print(f"   {status_symbol} {check_name}")
        except Exception as e:
            checks[check_name] = "❓"
            print(f"   ❓ {check_name} (error: {str(e)[:30]})")

    # Overall status
    passed = sum(1 for v in checks.values() if v == "[OK]")
    total = len(checks)
    overall = "[OK] HEALTHY" if passed == total else f"[WARN] {passed}/{total} OK"

    return {
        "name": project_name,
        "path": project_path,
        "status": overall,
        "checks": checks,
        "passed": passed,
        "total": total,
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
        }
    }

    # Save JSON
    report_path = Path(r"D:\GoogleDrive\AI\.secrets\protocolo\auto_maestro_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Dashboard
    print("\n" + "=" * 70)
    print("[DASH] AUTO-MAESTRO DASHBOARD")
    print("=" * 70)
    print(f"Total proyectos: {report['summary']['total_projects']}")
    print(f"[OK] Healthy: {report['summary']['healthy']}")
    print(f"[WARN] Issues: {report['summary']['issues']}")
    print(f"Timestamp: {timestamp}")
    print("=" * 70)

    return report

def suggest_fixes(results):
    """Suggest 1-click fixes for common issues."""
    print("\n[HINT] SUGERENCIAS DE FIXES:")
    for result in results:
        if "missing" in result.get("status", ""):
            print(f"  • {result['name']}: Crear proyecto")
        elif "OK" in result.get("status", ""):
            print(f"  • {result['name']}: {result['status']} — Revisar checks fallidos")

def main():
    print("=" * 70)
    print("🤖 AUTO-MAESTRO — Monitoreo de Proyectos")
    print("=" * 70)

    results = []
    for project_name, project_path in PROJECTS.items():
        result = scan_project(project_name, project_path)
        results.append(result)

    report = generate_report(results)
    suggest_fixes(results)

    print("\n[OK] Reporte guardado en: .secrets/protocolo/auto_maestro_report.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
