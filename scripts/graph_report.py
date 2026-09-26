#!/usr/bin/env python3
"""graph_report.py -- diagnóstico multi-satélite como herramienta HOJA
(TASK-RED-01), desacoplada de los árboles de importación de cada proyecto.

Regenera lo que `GRAPH_REPORT.md` describía ("Lección Cerberus D4": los
diagnósticos de flota deben inspeccionar el SISTEMA DE ARCHIVOS de cada
satélite, nunca importar sus módulos -- un satélite con un import roto o un
efecto secundario a nivel de módulo no debe poder tumbar el diagnóstico de
toda la flota). Este script no importa NADA de los repos que analiza: solo
`Path.is_dir()`/`Path.glob()`.

Uso:
    python scripts/graph_report.py --projects-dir ~/projects
    python scripts/graph_report.py --projects-dir ~/projects --json salida.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SatelliteHealth:
    """Metricas de salud de UN satelite, por inspeccion pura de archivos."""

    name: str
    has_hook: bool
    has_auditor: bool
    has_tests: bool

    @property
    def adoption_pct(self) -> int:
        return round(100 * sum((self.has_hook, self.has_auditor, self.has_tests)) / 3)

    @property
    def adoption_label(self) -> str:
        if self.adoption_pct == 100:
            return "full"
        if self.adoption_pct == 0:
            return "none"
        return "partial"


def _has_hook(root: Path) -> bool:
    """Un hook de pre-commit real, no un archivo vacio."""
    p = root / ".pre-commit-config.yaml"
    return p.is_file() and p.stat().st_size > 0


def _has_auditor(root: Path) -> bool:
    """Al menos un gate propio, no la carpeta vacia."""
    d = root / "gates"
    return d.is_dir() and any(d.glob("*.py"))


def _has_tests(root: Path) -> bool:
    """Al menos un archivo test_*.py, en tests/ o en la raiz."""
    return any(root.rglob("test_*.py"))


def scan_satellite(root: Path) -> SatelliteHealth:
    """Inspecciona UN satelite. Solo filesystem: sin `sys.path`, sin `import`."""
    return SatelliteHealth(
        name=root.name,
        has_hook=_has_hook(root),
        has_auditor=_has_auditor(root),
        has_tests=_has_tests(root),
    )


def scan_fleet(projects_dir: Path) -> list[SatelliteHealth]:
    """Un satelite es cualquier subdirectorio inmediato con `.git/`. No entra
    en subdirectorios de un satelite -- eso SI seria acoplarse a su arbol."""
    if not projects_dir.is_dir():
        return []
    satelites = []
    for child in sorted(projects_dir.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            satelites.append(scan_satellite(child))
    return satelites


def render_markdown(satelites: list[SatelliteHealth]) -> str:
    """Mismo formato que el GRAPH_REPORT.md original: full / partial / none."""
    lineas = [
        "# GRAPH REPORT — diagnostico de flota",
        f"_Generado por graph_report.py. {len(satelites)} satelites inspeccionados._",
        "",
    ]
    for etiqueta, titulo in (("full", "Full adoption"), ("partial", "Partial adoption"), ("none", "No adoption")):
        grupo = [s for s in satelites if s.adoption_label == etiqueta]
        lineas.append(f"## {titulo} ({len(grupo)}/{len(satelites)})")
        lineas.append("")
        for s in grupo:
            marca = "✅" if etiqueta == "full" else ("⚠️" if etiqueta == "partial" else "❌")
            lineas.append(
                f"- {marca} **{s.name}** ({s.adoption_pct}%) — "
                f"Hook:{'✅' if s.has_hook else '❌'} "
                f"Auditor:{'✅' if s.has_auditor else '❌'} "
                f"Tests:{'✅' if s.has_tests else '❌'}"
            )
        lineas.append("")
    return "\n".join(lineas)


def to_fleet_catalog_rows(satelites: list[SatelliteHealth]) -> list[dict]:
    """Forma compatible con `.simplecode/fleet_catalog.json` (campos
    `has_hooks`/`has_simplecode` ya existen ahi con ese mismo significado;
    aqui se nombran igual para que un lector pueda fusionar ambas fuentes
    por `name` sin traducir claves)."""
    return [
        {
            "name": s.name,
            "has_hooks": s.has_hook,
            "has_gates_auditor": s.has_auditor,
            "has_tests": s.has_tests,
            "adoption_pct": s.adoption_pct,
        }
        for s in satelites
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projects-dir", type=Path, default=Path.home() / "projects")
    ap.add_argument("--json", type=Path, default=None, help="tambien escribe este JSON")
    args = ap.parse_args(argv)

    satelites = scan_fleet(args.projects_dir)
    print(render_markdown(satelites))
    if args.json:
        args.json.write_text(
            json.dumps(to_fleet_catalog_rows(satelites), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
