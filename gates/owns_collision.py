#!/usr/bin/env python3
"""Niega que dos fichas `active` declaren rutas que se solapan.

Existe porque la convención OWNS de `CLAUDE.md` es hoy una DECLARACIÓN sin mecanismo, y su
propio texto lo dice: «No es un lock ni un mecanismo de exclusión mutua: nada impide
físicamente la escritura». Eso cobró tres veces en una sola sesión el 2026-08-24 — dos coders
sobre el mismo archivo perdiendo una línea en el merge, un cambio de `.pre-commit-config.yaml`
a media sesión que dejó el gate en deadlock, y `BACKLOG.md` leído a media escritura mostrando
144 líneas y 7 fichas momentáneamente ausentes.

Luis lo pidió por su nombre: «¿Hay forma de prevenir esta violación constante de reglas?».
Un gate preventivo, no un reporte que alguien deba leer.

El solape se calcula por prefijo de ruta: `tools/` colisiona con `tools/a.py`, y `tools/ab`
NO colisiona con `tools/a` (se comparan segmentos, no cadenas).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "ledger" / "index.jsonl"


def solapan(a: str, b: str) -> bool:
    """True si una ruta contiene a la otra. Compara SEGMENTOS: `tools/ab` no cubre `tools/a`."""
    pa, pb = Path(a).parts, Path(b).parts
    n = min(len(pa), len(pb))
    return pa[:n] == pb[:n]


def main() -> int:
    if not INDEX.is_file():
        print(f"could_not_run: falta {INDEX}; corre gates/ledger_schema.py primero")
        return 1
    activas: list[tuple[str, list[str]]] = []
    ilegibles: int = 0
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            ilegibles += 1
            continue
        if e.get("status") == "active":
            activas.append((e["id"], e.get("owns") or []))

    choques = [
        (ia, ib, ra, rb)
        for i, (ia, oa) in enumerate(activas)
        for ib, ob in activas[i + 1:]
        for ra in oa for rb in ob
        if solapan(ra, rb)
    ]
    print(f"activas={len(activas)} choques={len(choques)} could_not_run={ilegibles}")
    for ia, ib, ra, rb in choques:
        print(f"  FAIL {ia} y {ib} se solapan: {ra!r} vs {rb!r}")
    return 1 if (choques or ilegibles) else 0


if __name__ == "__main__":
    raise SystemExit(main())
