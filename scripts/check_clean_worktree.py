#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_clean_worktree.py — VC-141: detector de "cambios eludidos / commit parcial".

Regla: cuando hay cambios sin commitear, NO se les da la vuelta — se revisan, corrigen
e integran al commit (o se gitignoran con decisión explícita). Este detector, invocado
en el hook pre-commit, bloquea si tras stagear queda algo sin decidir en el working tree.

`worktree_is_clean` es PURA (parsea `git status --porcelain`) y por eso falsable. git ya
excluye lo gitignorado del porcelain, así que la detección estricta no produce falsos
positivos por artefactos ignorados. Escape explícito: `CERBERUS_ALLOW_PARTIAL=1`.
"""
from __future__ import annotations

import os
import subprocess
import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def worktree_is_clean(porcelain: str) -> tuple[bool, list[str]]:
    """Analiza la salida de `git status --porcelain`.

    Un archivo está "eludido" (ensucia el commit) si tiene cambios en el working tree
    sin stagear (columna 2 != ' ') o es untracked (`??`). Un archivo completamente
    staged (columna 2 == ' ') entra al commit y NO ensucia. Devuelve (limpio, eludidos).
    """
    dirty: list[str] = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        if line.startswith("??"):
            dirty.append(line[3:].strip())
            continue
        worktree_col = line[1] if len(line) > 1 else " "
        if worktree_col != " ":
            dirty.append(line[3:].strip())
    return (len(dirty) == 0, dirty)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "VC-141: bloquea el commit si tras stagear queda algo eludido en el working "
            "tree (no-staged o untracked). Escape consciente: env CERBERUS_ALLOW_PARTIAL=1."
        )
    )
    parser.parse_args(argv)

    if os.getenv("CERBERUS_ALLOW_PARTIAL") == "1":
        print("[VC-141] escape CERBERUS_ALLOW_PARTIAL=1 — verificación de tree omitida.")
        return 0

    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"[VC-141] no se pudo leer git status: {result.stderr.strip()}")
        return 1

    clean, dirty = worktree_is_clean(result.stdout)
    if clean:
        return 0

    print("❌ [VC-141] Cambios eludidos: el working tree tiene archivos sin integrar al commit:")
    for path in dirty:
        print(f"   - {path}")
    print(
        "Revísalos, corrígelos e intégralos (git add) o gitignóralos con decisión explícita.\n"
        "No se les da la vuelta. Escape consciente: CERBERUS_ALLOW_PARTIAL=1."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
