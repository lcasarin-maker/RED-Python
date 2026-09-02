#!/usr/bin/env python3
"""Mide cuanto de la estructura canonica (DGX-424) ha adoptado ESTE repo. Sale 0 solo si todo.

Existe porque «adoptado» no es binario y tratarlo como si lo fuera produjo un reporte falso: el
2026-09-01 se declaro el canon «aplicado en 14 repos» y la medicion por criterio dio
**SPEC_v2 0/18, index.jsonl 0/18, gates declarados 0/18**. Estaba aplicada la parte visible —las
carpetas y las fichas— y ausente la que hace que el canon CORRA.

Imprime los ceros y distingue lo ausente de lo que no se pudo comprobar, porque un reporte con
`could_not_run > 0` no es un reporte limpio por muchas filas que pasen.

Uso:  python gates/canon_adoption.py [--json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GATES = ("ledger_schema.py", "owns_collision.py", "index_decisions.py", "canon_adoption.py",
         "pii_scan.py")


def _lee(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _gate_del_kit_vacuo() -> bool:
    """True si el gate de fichas del kit gobierna 0 mientras el ledger tiene contenido."""
    entradas = list((REPO / "ledger" / "entries").glob("*.md"))
    if not entradas:
        return False          # sin ledger no hay nada que gobernar: no es vacuidad, es vacio
    if (REPO / "tasks").is_dir():
        return False          # el sujeto viejo sigue ahi; el gate del kit aun lo ve
    return True               # ledger con contenido y sin tasks/: el gate del kit no ve nada


def criterios() -> dict[str, tuple[bool, str]]:
    """{nombre: (cumple, que falta)}. Cada uno comprobable sin juicio humano."""
    spec = _lee(REPO / "SPEC.md")
    local_hooks = _lee(REPO / ".simplecode" / "local_hooks.yaml")
    tiene_src = (REPO / "src").is_dir()
    return {
        "readme": ((REPO / "README.md").is_file(),
                   "falta README.md: la unica puerta para quien no sabe nada del repo"),
        "spec_tipado": (spec.lstrip().startswith("---") and "spec_version: 2" in spec[:600],
                        "SPEC.md sin front-matter tipado (`spec_version: 2`): sigue el esqueleto viejo"),
        "spec_requisitos": ("verify:" in spec and "SHALL" in spec,
                            "SPEC.md sin requisitos EARS con su `verify:`: un requisito sin comando es prosa"),
        "ledger": (all((REPO / "ledger" / d).is_dir() for d in ("entries", "evidence", "decisions")),
                   "falta ledger/{entries,evidence,decisions}: el estado no tiene una sola casa"),
        "index": ((REPO / "ledger" / "index.jsonl").is_file(),
                  "falta ledger/index.jsonl: los gates no tienen que leer de una pasada"),
        "gates": (all((REPO / "gates" / g).is_file() for g in GATES),
                  f"faltan gates en gates/: se esperan {', '.join(GATES)}"),
        "gates_declarados": ("ledger-schema" in local_hooks,
                             "los gates no estan declarados en .simplecode/local_hooks.yaml: "
                             "existen pero NO CORREN, y un gate que no corre no captura nada"),
        "tasks_retirado": (not (REPO / "tasks").is_dir(),
                           "tasks/ sigue vivo junto a ledger/: dos fuentes de verdad que se "
                           "contradicen, que es el problema que el canon existe para eliminar"),
        # Criterio anadido el 2026-09-01 tras el aviso de la sesion atlas-48, medido y confirmado:
        # retirar `tasks/` dejo al `backlog_verifier` del kit reportando `governed: 0` y `rc=0` en
        # los 14 repos migrados. En office2office gobernaba 790 fichas y ahora aprueba sobre cero.
        # Es la doctrina de la casa al pie de la letra —«un gate con cero capturas tras muchas
        # corridas es un defecto del instrumento, nunca evidencia de que el sujeto este limpio»—
        # y lo produje yo al mover el sujeto sin re-apuntar el instrumento.
        "gate_no_vacuo": (not _gate_del_kit_vacuo(),
                          "el `backlog_verifier` del kit gobierna 0 fichas mientras `ledger/entries/` "
                          "tiene contenido: aprueba en verde sobre un directorio que ya no existe. "
                          "Un instrumento que solo sabe aprobar es peor que ninguno. Se cierra "
                          "cuando el gate del kit lea `ledger/entries/` (pedido aguas arriba)"),
        # Criterio 11, anadido el 2026-09-02 tras un incidente real que reporto aequitas_os: un
        # agente pego 20 RFC y razones sociales de clientes en una ficha, y la migracion del canon
        # los copio verbatim al ledger. El repo se publica en GitHub. Seguridad no se recorta.
        "sin_pii": ((REPO / "gates" / "pii_scan.py").is_file(),
                    "falta `gates/pii_scan.py`: nada impide que un RFC, una CURP o una razon "
                    "social de un tercero entre al ledger y de ahi a la historia de git"),
        "tests_si_src": ((not tiene_src) or (REPO / "tests").is_dir(),
                         "hay src/ sin tests/: la suite es una implicacion del codigo, no un opcional"),
    }


def main() -> int:
    c = criterios()
    faltan = [(k, m) for k, (ok, m) in c.items() if not ok]
    if "--json" in sys.argv:
        print(json.dumps({"repo": REPO.name, "total": len(c), "cumple": len(c) - len(faltan),
                          "faltan": [k for k, _ in faltan]}, ensure_ascii=False))
        return 1 if faltan else 0
    print(f"adopcion del canon en {REPO.name}: {len(c) - len(faltan)}/{len(c)} criterios")
    for k, (ok, _) in c.items():
        print(f"  {'OK' if ok else 'NO'}  {k}")
    if faltan:
        print("\nlo que falta, y por que importa:")
        for k, m in faltan:
            print(f"  - {k}: {m}")
    return 1 if faltan else 0


if __name__ == "__main__":
    raise SystemExit(main())
