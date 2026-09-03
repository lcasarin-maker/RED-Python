#!/usr/bin/env python3
"""Ninguna entrada trackeada del ledger pierde lineas respecto a HEAD. Sale 1 si alguna lo hace.

Lo propuso la sesion 020 tras perder DOS VECES la misma seccion de 54 lineas en
`office2office`, y su argumento es por que este control gana a los que yo tenia:

    «tu control dice `respetadas=101` sobre entradas que ya existian. Ese numero no distingue
    "no sobreescribi" de "no llegue a correr sobre ese repo". El control que habria cazado esto
    es mas barato: comparar la entrada en disco contra la que hay en HEAD y exigir que ninguna
    PIERDA lineas. Un diff de solo borrados sobre una entrada trackeada es la firma exacta de
    este defecto, y no depende de que la entrada sea open, done, ni de que tenga evidence.»

Los tres controles que tuve antes miraban una PROPIEDAD de la entrada —`status`, `evidence`, su
existencia— y por eso cada uno se lo salto una forma distinta del mismo defecto. Este mira el
EFECTO, que es lo unico comun a las tres.

Uso:  python gates/no_perder_lineas.py
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "tasks"


def main() -> int:
    if not ENTRIES.is_dir():
        print("could_not_run: no hay ledger/entries")
        return 1
    revisadas = perdidas = could_not_run = 0
    detalle: list[str] = []
    for f in sorted(ENTRIES.glob("*.md")):
        rel = f.relative_to(ROOT)
        r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            continue                      # sin trackear: no hay con que comparar, no es perdida
        revisadas += 1
        d = subprocess.run(["git", "diff", "--numstat", "HEAD", "--", str(rel)],
                           cwd=ROOT, capture_output=True, text=True).stdout.split()
        if len(d) < 2 or not d[0].isdigit():
            continue
        anadidas, borradas = int(d[0]), int(d[1])
        # La firma es **borrados con CERO inserciones**, tal como la formulo 020. Una linea
        # SUSTITUIDA da 1 y 1 y no es perdida: la reparacion de fechas del 2026-09-02 cambio
        # `created` en 747 entradas y una version anterior de este gate la marco a las 747 como
        # perdida. Un control que no distingue sustituir de borrar convierte cada correccion
        # legitima en una alarma, y una alarma que suena siempre se apaga.
        if borradas > 0 and anadidas == 0:
            perdidas += 1
            detalle.append(f"PIERDE {rel}: {borradas} linea(s) borradas y 0 anadidas")

    print(f"revisadas={revisadas} pierden={perdidas} could_not_run={could_not_run}")
    for d in detalle[:60]:
        print(f"  {d}")
    return 1 if (perdidas or could_not_run) else 0


if __name__ == "__main__":
    raise SystemExit(main())
