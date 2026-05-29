#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RIGOR-MAESTRO v0.02: Orquestador de CoderCerberus Certificado
Implementa detencion inmediata y auto-compresion de logs con RTK.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of how this script is invoked
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8, get_centralized_version

setup_windows_utf8()
logger = logging.getLogger("rigor_maestro")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Configuracion de la suite de tests por nivel
VERSION = get_centralized_version()
BASE_VERSION = ".".join(VERSION.split(".")[:2])

# Dynamic test suite — hardcoded per-file entries removed (P6.6 portability fix).
# pytest discovers tests/test_*.py automatically; adding files here is unnecessary
# and breaks satellite projects that have different test file names.
TEST_SUITE = [
    {
        "name": "CoderCerberus Full Test Suite (pytest — dynamic discovery)",
        "command": [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
        "critical": True
    },
    {
        "name": "CoderCerberus Auditoria Forense 10D (Shield)",
        "command": [sys.executable, "scripts/audit_10d.py"],
        "critical": True
    },
    {
        "name": "CoderCerberus Permission Audit",
        "command": [sys.executable, "scripts/permission_auditor.py"],
        "critical": True
    }
]

def run_suite() -> bool:
    """Ejecuta la suite critica con compresion RTK activa."""
    version = get_centralized_version()
    print("=" * 80)
    print(f"INICIANDO RIGOR-MAESTRO v{version} (RTK ACTIVE)")
    print("=" * 80)

    try:
        from scripts.token_manager import OutputCompressor as RTKAutoCompress
        has_rtk = True
        print("  [OK] RTK Engine cargado exitosamente.")
    except ImportError as e:
        print(f"  [ERROR] RTK Engine (OutputCompressor) no encontrado. Commit bloqueado. {e}")
        sys.exit(1)

    for i, test in enumerate(TEST_SUITE):
        print(f"\n[{i+1}/{len(TEST_SUITE)}] Ejecutando: {test['name']}...")
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
            result = subprocess.run(
                test["command"], capture_output=True, text=True,
                encoding="utf-8", errors="ignore", env=env,
            )
            returncode, stdout, stderr = result.returncode, result.stdout, result.stderr

            final_stdout = stdout
            # AUTOMATIZACION RTK
            if has_rtk and len(final_stdout) > 2000:
                final_stdout, used = RTKAutoCompress.process_output(final_stdout)
                if used:
                    print("  [INFO] Log de test comprimido automáticamente con RTK.")

            if returncode == 0:
                print(f"  [PASS] {test['name']}")
            else:
                print(f"  [FAIL] {test['name']}")
                print(final_stdout)
                print(stderr)
                return False
        except Exception as e:
            logger.error("run_suite: test '%s' raised exception: %s", test["name"], e)
            return False

    print("\n" + "=" * 80)
    print("TODOS LOS TESTS PASARON")
    print("=" * 80)
    return True

def write_status_warning(status_file: Path) -> None:
    """Escribe el banner de bloqueo en STATUS.md (función auxiliar para aplanar nesting)."""
    if not status_file.exists():
        return
    try:
        content = status_file.read_text(encoding="utf-8")
        if "🚨 CHAIN-PATTERN INTERRUPT: ERROR DEADLOCK ACTIVO 🚨" in content:
            return
        warning = (
            "# STATUS.md — Project status\n\n"
            "🚨 **CHAIN-PATTERN INTERRUPT: ERROR DEADLOCK ACTIVO** 🚨\n"
            "=========================================================\n"
            "Se han detectado 3 o más fallos consecutivos en la suite de rigor.\n"
            "Las herramientas de edición del agente han sido bloqueadas automáticamente.\n"
            "**Acción del Operador Humano requerida:**\n"
            "1. Revisa los logs de error de pytest e HISTORIAL.md.\n"
            "2. Resuelve el bug o revert de forma manual.\n"
            "3. Ejecuta `python scripts/protocol_cli.py unlock` en la terminal para reactivar al agente.\n\n"
            "---\n\n"
        )
        status_file.write_text(warning + content, encoding="utf-8")
    except Exception as e:
        logger.warning("Error writing status warning to STATUS.md: %s", e)


def update_lock_state(success: bool) -> None:
    """Actualiza el estado de bloqueos en .agent_state.json (aplanado)."""
    state_file = _ROOT / ".agent_state.json"
    if not state_file.exists():
        return

    import json
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception as e:
        logger.warning("Error reading state file %s: %s", state_file, e)
        return

    consecutive_failures = state.get("consecutive_failures", 0)
    reasoning_lock = state.get("reasoning_lock", False)

    if success:
        consecutive_failures = 0
        reasoning_lock = False
    else:
        consecutive_failures += 1
        if consecutive_failures >= 3:
            reasoning_lock = True
            write_status_warning(_ROOT / "STATUS.md")

    state["consecutive_failures"] = consecutive_failures
    state["reasoning_lock"] = reasoning_lock

    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Error writing state file %s: %s", state_file, e)


if __name__ == "__main__":
    success = run_suite()
    update_lock_state(success)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
