#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REGLA #28 — Multi-Agent Coordination & Routing
Valida que HISTORIAL.md contiene la sección de retrospectiva JSON obligatoria.
"""

import sys
import re
import json
from pathlib import Path

# Forzar encoding UTF-8 para evitar UnicodeDecodeError en Windows
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

<<<<<<< HEAD
=======
try:
    from scripts.core_utils import setup_windows_utf8

    setup_windows_utf8()
except ImportError as e:
    import logging

    logging.debug(f"setup_windows_utf8 not available: {e}")
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b


def validate_historial_routing():
    """Verifica que la última sesión en HISTORIAL.md tiene JSON válido."""
    historial_path = Path("HISTORIAL.md")
    if not historial_path.exists():
        return [f"HISTORIAL.md no existe"]

    content = historial_path.read_text(encoding="utf-8")

<<<<<<< HEAD
=======
    content = historial_path.read_text(encoding="utf-8")

>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
    # Buscar bloques de JSON en el historial
    # Buscamos el último bloque ```json ... ```
    json_blocks = re.findall(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)

    if not json_blocks:
        return ["No se encontró bloque JSON de retrospectiva en HISTORIAL.md"]

    last_json_str = json_blocks[-1]

    try:
        data = json.loads(last_json_str)
    except json.JSONDecodeError as e:
        return [f"JSON en HISTORIAL.md es inválido: {e}"]

    # Campos obligatorios según REGLA #28
    required_fields = [
        "session_id",
        "agent_name",
        "rules_touched",
        "files_modified",
        "state_hash",
    ]
    missing = [f for f in required_fields if f not in data]

    if missing:
        return [f"Campos JSON faltantes en HISTORIAL.md: {missing}"]

    return []


def main():
    print("🛤️  Validando Multi-Agent Routing (Regla #28)")

    violations = validate_historial_routing()

    if violations:
        print(f"  ❌ VIOLACIÓN DE ROUTING DETECTADA ({len(violations)}):")
        for v in violations:
            print(f"    - {v}")
        return 1
    else:
        print("  ✅ Estructura de Routing en HISTORIAL.md validada correctamente.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
