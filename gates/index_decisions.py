#!/usr/bin/env python3
"""Genera `ledger/decisions.jsonl` desde los archivos de decisión. Nunca se escribe a mano.

El diseño canónico deja el CUERPO de una decisión sin esquema a propósito, y esa abstención
tiene su cero medido: **0 documentos del acervo cosechado de Atlas definen las secciones
internas de un ADR** — sólo hay convención de nombre de archivo (`docs/adr/NNNN-slug.md`,
cuatro dígitos, de `github_com_andreaborio_hebrus.md`). Inventar un esquema para el cuerpo
sería inventar. Lo tipado es el ÍNDICE, que es lo mínimo que un gate necesita.

Y se genera en vez de escribirse porque una tabla escrita a mano que resume otros archivos es
una segunda fuente de verdad: en Atlas ya divergió — 41 archivos en `docs/decisions/` contra
1 fila en la tabla del SPEC contra 3 narradas en `DECISIONS.md`.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUENTES = (ROOT / "docs" / "decisions",)
SALIDA = ROOT / "ledger" / "decisions.jsonl"
ESTADOS = {"proposed", "accepted", "rejected", "superseded", "deprecated"}


def main() -> int:
    # `--check` NO escribe. La invariante de `.simplecode/local_hooks.yaml` es que un gate
    # JUZGA y no escribe en el árbol que juzga; medida el 2026-08-24 sobre 19 de 19 hooks.
    # En pre-commit se invoca con `--check`; la regeneración es un acto explícito.
    check_only = "--check" in sys.argv
    filas, could_not_run = [], []
    for carpeta in FUENTES:
        if not carpeta.is_dir():
            could_not_run.append(f"{carpeta} no existe")
            continue
        for p in sorted(carpeta.glob("*.md")):
            try:
                lineas = p.read_text(encoding="utf-8").split("\n")
            except OSError as exc:
                could_not_run.append(f"{p.name}: {exc}")
                continue
            if not lineas or lineas[0].strip() != "---":
                could_not_run.append(f"{p.name}: sin frontmatter")
                continue
            fm = {}
            for ln in lineas[1:]:
                if ln.strip() == "---":
                    break
                m = re.match(r"^([a-z_]+):\s*(.*)$", ln)
                if m:
                    fm[m.group(1)] = m.group(2).strip()
            titulo = next((ln.lstrip("# ").strip() for ln in lineas if ln.startswith("# ")), p.stem)
            estado = fm.get("status", "")
            filas.append({
                "id": fm.get("id", p.stem),
                "title": titulo[:200],
                # El estado se reporta como viene; si no está en el dominio se marca, no se
                # corrige — corregirlo en silencio es inventar el dato.
                "status": estado if estado in ESTADOS else f"UNKNOWN:{estado or 'vacío'}",
                "path": str(p.relative_to(ROOT)),
            })

    contenido = "".join(json.dumps(f, ensure_ascii=False, sort_keys=True) + "\n"
                        for f in sorted(filas, key=lambda f: f["id"]))
    if check_only:
        actual = SALIDA.read_text(encoding="utf-8") if SALIDA.is_file() else ""
        if actual != contenido:
            print("  FAIL el índice está desincronizado de docs/decisions/; "
                  "regenera con: python gates/index_decisions.py")
            return 1
    else:
        SALIDA.write_text(contenido, encoding="utf-8")
    fuera = [f for f in filas if f["status"].startswith("UNKNOWN")]
    print(f"indexadas={len(filas)} fuera_de_dominio={len(fuera)} could_not_run={len(could_not_run)}")
    for f in fuera:
        print(f"  UNKNOWN {f['id']}: {f['status']}")
    for c in could_not_run:
        print(f"  COULD_NOT_RUN {c}")

    # Línea base, el mecanismo `legacy-baseline` que el SPEC declara en `gate_level` y que
    # viene de DebtLens: se bloquea la deuda NUEVA, no la histórica ya conocida y fichada.
    # Sin esto el gate fallaría en todo commit por los 21 de CANON-009 y acabaría apagado,
    # que es la peor salida: un gate apagado no captura nada y nadie lo nota.
    base = 21
    for i, a in enumerate(sys.argv):
        if a == "--baseline" and i + 1 < len(sys.argv):
            base = int(sys.argv[i + 1])
    if len(could_not_run) > base:
        print(f"  FAIL could_not_run={len(could_not_run)} supera la línea base {base}: "
              f"deuda NUEVA, no la histórica de CANON-009")
        return 1
    if len(could_not_run) < base:
        print(f"  NOTA could_not_run={len(could_not_run)} está por DEBAJO de la base {base}; "
              f"baja la base a ese número o el gate deja de proteger lo ganado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
