#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUARDRAIL ESTRICTO — DETECTOR DE INCONSISTENCIAS REGLA-CÓDIGO
Bloquea commits si hay REGLAS SISTEMA (13+) documentadas sin implementación.
Caller: pre-commit hook.
"""
import os
import sys
import re
from pathlib import Path

sys.path.append(os.getcwd())  # Required for standalone execution
from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()

_REGLA_PATTERN = re.compile(r"REGLA #(\d+)")
_REGLA_NUM_PATTERN = re.compile(r"#(\d+)")
_FUTURE_INLINE = re.compile(r"#(\d+)\s*\[FUTURE\]", re.IGNORECASE)
_FUTURE_FULL = re.compile(r"REGLA\s+#(\d+).*\[FUTURE\]", re.IGNORECASE)


def _read_md_files():
    """Itera sobre todos los .md del proyecto. Yields (path, content)."""
    for md in Path(".").rglob("*.md"):
        try:
            yield md, md.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[WARN] Cannot read {md}: {e}", file=sys.stderr)


def _extract_prose_only_from_line(line: str) -> set:
    """Extrae números de REGLA marcados [PROSE-ONLY] de una sola línea."""
    found = set()
    if "[PROSE-ONLY]" not in line.upper():
        return found
    for match in _REGLA_PATTERN.finditer(line):
        found.add(int(match.group(1)))
    for match in _REGLA_NUM_PATTERN.finditer(line):
        found.add(int(match.group(1)))
    return found


def get_documented_reglas() -> list:
    """Números de REGLA documentados en cualquier .md del proyecto."""
    reglas = set()
    for _, content in _read_md_files():
        for match in _REGLA_PATTERN.finditer(content):
            reglas.add(int(match.group(1)))
    return sorted(reglas)


def get_future_reglas() -> set:
    """REGLAS marcadas [FUTURE] — en backlog, sin código aún."""
    reglas = set()
    for _, content in _read_md_files():
        for match in _FUTURE_INLINE.finditer(content):
            reglas.add(int(match.group(1)))
        for match in _FUTURE_FULL.finditer(content):
            reglas.add(int(match.group(1)))
    return reglas


def get_prose_only_reglas() -> set:
    """REGLAS marcadas [PROSE-ONLY] — human-enforced, sin código."""
    reglas = set()
    for _, content in _read_md_files():
        for line in content.split("\n"):
            reglas.update(_extract_prose_only_from_line(line))
    return reglas


def get_implemented_reglas() -> set:
    """REGLAS con implementación detectada en scripts/ o .git/hooks/."""
    reglas = set()
    for hook in Path(".git/hooks").glob("*"):
        if hook.is_file() and not hook.name.endswith(".sample"):
            try:
                content = hook.read_text(errors="ignore")
                for match in _REGLA_PATTERN.finditer(content):
                    reglas.add(int(match.group(1)))
            except Exception as e:
                print(f"[WARN] Cannot read hook {hook}: {e}", file=sys.stderr)
    for script in Path("scripts").glob("*.py"):
        try:
            content = script.read_text(errors="ignore")
            for match in _REGLA_PATTERN.finditer(content):
                reglas.add(int(match.group(1)))
        except Exception as e:
            print(f"[WARN] Cannot read script {script}: {e}", file=sys.stderr)
    return reglas


def main() -> bool:
    documented = get_documented_reglas()
    implemented = get_implemented_reglas()
    future_reglas = get_future_reglas()
    prose_only_reglas = get_prose_only_reglas()

    # REGLAS 2-12: Behavioral (prose-enforced, no requieren código)
    # REGLAS 13+:  System (requieren código)
    system_reglas = set(r for r in documented if r >= 13)
    missing_system = (system_reglas - implemented) - future_reglas - prose_only_reglas

    print()
    print("=" * 70)
    print("GUARDRAIL: PARIDAD REGLA-CODIGO (SISTEMA ONLY)")
    print("=" * 70)
    print(f"Documentadas: {len(documented)} | System 13+: {len(system_reglas)}")
    print(f"Implementadas: {sorted(implemented)}")
    print(f"[FUTURE]: {sorted(future_reglas) if future_reglas else []}")
    print(f"[PROSE-ONLY]: {sorted(prose_only_reglas) if prose_only_reglas else []}")
    print(
        f"Faltando codigo (BLOQUEANTE): {sorted(missing_system) if missing_system else []}"
    )
    print("=" * 70)

    if missing_system:
        print("\nBLOQUEO: REGLAS SISTEMA sin codigo:")
        for r in sorted(missing_system):
            tier = "TIER 2" if r < 25 else "TIER 3"
            print(f"  - REGLA #{r} ({tier})")
        return False

    print("\n[OK] Protocolo completo y consistente")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
