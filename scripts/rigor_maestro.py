#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RIGOR-MAESTRO v5.3: Orquestador de VibeCoderProof Certificado
Implementa detencion inmediata y auto-compresion de logs con RTK.
"""

import sys
import os
from pathlib import Path

# Inyectar el root del proyecto en el path para resolver scripts.*
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.core_utils import setup_windows_utf8, get_centralized_version

setup_windows_utf8()

# Configuracion de la suite de tests por nivel
VERSION = get_centralized_version()
BASE_VERSION = ".".join(VERSION.split(".")[:2])

TEST_SUITE = [
    {
        "name": f"VibeCoderProof v{VERSION} Mandates & Parity Validation (S17/B7)",
        "command": [sys.executable, "tests/test_v55_rigor.py"],
        "critical": True
    },
    {
        "name": f"VibeCoderProof v{BASE_VERSION} Core Resilience (Angry Path)",
        "command": [sys.executable, "tests/test_fortaleza_v4_core.py"],
        "critical": True
    },
    {
        "name": f"VibeCoderProof v{BASE_VERSION} Dynamic Resilience (Angry Path)",
        "command": [sys.executable, "tests/test_resilience_v57.py"],
        "critical": True
    },

    {
        "name": f"Auditoria Forense 6D v{BASE_VERSION} (Shield)",
        "command": [sys.executable, str(ROOT / "scripts" / "audit_6d.py")],
        "critical": True
    },

    {
        "name": f"Agent Permission Audit v{BASE_VERSION}",
        "command": [sys.executable, str(ROOT / "scripts" / "permission_auditor.py")],
        "critical": True
    }
]

def run_suite() -> bool:
    """Ejecuta la suite critica con compresion RTK activa."""
    version = get_centralized_version()
    print("=" * 80)
    print(f"🚀 INICIANDO RIGOR-MAESTRO v{version} (RTK ACTIVE)")
    print("=" * 80)

    # Corregir importacion de RTK
    try:
        from scripts.rtk_auto_compress import RTKAutoCompress
        has_rtk = True
        print("  ✅ RTK Engine cargado exitosamente.")
    except ImportError as e:
        has_rtk = False
        print(f"  [WARN] RTKAutoCompress no encontrado: {e}")

    for i, test in enumerate(TEST_SUITE):
        print(f"\n[{i+1}/{len(TEST_SUITE)}] Ejecutando: {test['name']}...")
        try:
            # Forzar PYTHONPATH para el subproceso
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
            
            import subprocess
            result = subprocess.run(
                test["command"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                env=env,
                cwd=str(ROOT),
            )
            returncode, stdout, stderr = result.returncode, result.stdout, result.stderr

            final_stdout = stdout
            # AUTOMATIZACION RTK
            if has_rtk and len(final_stdout) > 2000:
                final_stdout, used = RTKAutoCompress.process_output(final_stdout)
                if used:
                    print("  [INFO] Log de test comprimido automáticamente con RTK.")

            if returncode == 0:
                print(f"  ✅ {test['name']} PASSED (100%)")
            else:
                print(f"  ❌ {test['name']} FAILED")
                print(final_stdout)
                print(stderr)
                return False
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return False

    print("\n" + "=" * 80)
    print("🎯 TODOS LOS TESTS PASARON AL 100%")
    print("=" * 80)
    return True

if __name__ == "__main__":
    if run_suite():
        sys.exit(0)
    else:
        sys.exit(1)
