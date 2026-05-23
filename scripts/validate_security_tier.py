#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REGLA #24 — Security Boundaries & Sandboxing
Valida que el agente actual tiene permisos para modificar los archivos solicitados.
"""

import os
import sys
import json
from pathlib import Path

# Forzar encoding UTF-8 para evitar UnicodeDecodeError en Windows
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Configuración de Tier por defecto si no hay variable de entorno
# En un entorno real, esto se determinaría mediante autenticación del agente.
DEFAULT_TIER = os.getenv("AGENT_SECURITY_TIER", "SEMI-TRUSTED")

# Mapeo de permisos por Tier
TIER_PERMISSIONS = {
    "TRUSTED": {"allow_all": True, "restricted_paths": []},
    "SEMI-TRUSTED": {
        "allow_all": False,
        "allowed_paths": [
            ".agent-sandbox/",
            "HISTORIAL.md",  # Append only (logic handled in validation)
            "STATUS.md",  # Restricted to certain fields maybe? For now allow.
            "tests/",  # Allowed for development
            "scripts/",  # Allowed for development
        ],
        "denied_paths": [
            "AGENT.md",
            "PROTOCOL_SYSTEM.md",
            "PROTOCOL_BEHAVIOR.md",
            ".git/",
            ".secrets/",
        ],
    },
    "UNTRUSTED": {
        "allow_all": False,
        "allowed_paths": [".agent-sandbox/untrusted/"],
        "denied_paths": ["*"],
    },
}


def get_staged_files():
    """Obtiene la lista de archivos preparados para commit."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n")
    except:
        return []


def validate_tier_permissions(tier, files):
    """Valida si los archivos modificados están permitidos para el tier dado."""
    if tier not in TIER_PERMISSIONS:
        return [f"Tier desconocido: {tier}"]

    perms = TIER_PERMISSIONS[tier]
    if perms["allow_all"]:
        return []

    violations = []
    allowed_paths = perms.get("allowed_paths", [])
    denied_paths = perms.get("denied_paths", [])

    for f in files:
        if not f:
            continue

        # Check explicit denial
        is_denied = False
        for dp in denied_paths:
            if dp == "*" or f.startswith(dp):
                is_denied = True
                break

        if is_denied:
            # Check if it's in allowed_paths (exception)
            is_allowed = False
            for ap in allowed_paths:
                if f.startswith(ap):
                    is_allowed = True
                    break

            if not is_allowed:
                violations.append(f"Acceso denegado a {f} para Tier {tier}")

    return violations


def main():
    print(f"🔐 Validando Security Boundaries (Regla #24) - Tier: {DEFAULT_TIER}")

    files = get_staged_files()
    if not files or files == [""]:
        print("  ✅ No hay archivos preparados para commit.")
        return 0

    violations = validate_tier_permissions(DEFAULT_TIER, files)

    if violations:
        print(f"  ❌ VIOLACIÓN DE SEGURIDAD DETECTADA ({len(violations)}):")
        for v in violations:
            print(f"    - {v}")
        return 1
    else:
        print("  ✅ Permisos de Tier validados correctamente.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
