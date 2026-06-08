#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_imports.py — Health check de imports del paquete scripts/.
Recorre todos los módulos e intenta importarlos. Reporta fallos anticipadamente.
Caller: run_audit.ps1 como primer paso antes de pytest.

Uso:
    python -m scripts.check_imports
"""
import os
import sys
import importlib
import pkgutil
from pathlib import Path

sys.path.append(os.getcwd())  # Required for standalone execution
from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()


def _module_names(package_name: str) -> list:
    """Retorna nombres completos de sub-módulos del paquete dado."""
    base_path = Path(__file__).parent
    module_names = []
    for _, mod_name, is_pkg in pkgutil.iter_modules([str(base_path)]):
        full_name = f"{package_name}.{mod_name}"
        module_names.append(full_name)
        if is_pkg:
            module_names.extend(_module_names(full_name))
    return module_names


def main() -> int:
    package = "scripts"
    errors: list = []
    for mod_name in _module_names(package):
        print(f"Importing: {mod_name}")
        try:
            importlib.import_module(mod_name)
        except Exception as exc:
            errors.append((mod_name, str(exc)))

    if errors:
        print("\nIMPORT ERRORS DETECTED:")
        for mod, err in errors:
            print(f"  [FAIL] {mod}: {err}")
        return 1

    print(f"\n[OK] All {len(_module_names(package))} modules import cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
