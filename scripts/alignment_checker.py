#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""alignment_checker.py — Linter de alineación Código (Capa 1) ↔ Docs (Capa 2).

Fase 2 de la arquitectura federada. Consume `internal_graph.json` (ya enriquecido
con aristas `documents` doc→código en Fase 1) y detecta desalineamientos:

  - **code_orphans**: símbolos críticos (god_nodes / entry_points) sin documentación
    → FAIL (lo que es central debe estar documentado).
  - **doc_orphans**: docs sin enlaces; arch/guide → WARN (toleran no mapear a código),
    module-specific → FAIL (si documentas un módulo, debe existir).

Respeta `extraction_status`: si Layer 1 no es confiable (graphify falló) ABORTA con
FAIL, nunca declara "0 orphans" sobre una medición rota (anti falso-verde, H2/H5).

Las funciones de detección son PURAS (dict→list) y por eso falsables. La orquestación
con I/O vive en `check_alignment` / `main`.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.internal_graph import _AUTODETECT_CANDIDATES, extraction_is_trustworthy

logger = logging.getLogger("alignment_checker")

# Heurística de clasificación de docs (MVP). arch/guide toleran no documentar código
# (WARN); el resto se asume module-specific (FAIL). El refinamiento por contenido es 2b.
_ARCH_HINTS = (
    "architecture", "design", "overview", "readme", "index", "guide",
    "tutorial", "vision", "roadmap", "principles", "home", "about",
)


def documented_code_ids(layer2: dict) -> set[str]:
    """Ids de símbolos de código que tienen al menos una arista `documents`."""
    return {
        edge["target"]
        for edge in layer2.get("edges", [])
        if edge.get("relation") == "documents"
    }


def _is_documentable_symbol(sym: str, code_namespaces: tuple[str, ...]) -> bool:
    """¿`sym` es un símbolo arquitectónico documentable (Fase 2c)?

    Excluye dos clases de artefacto mecánico de graphify que son god_nodes por grado
    pero NO superficie de API documentable:
      - sufijo `_py_path`: la constante `Path(__file__)` por módulo (alto grado porque
        cada función del módulo la referencia), no una unidad documentable.
      - símbolos fuera de los namespaces de código del repo (p.ej. `ast` stdlib): no los
        gobernamos, no exigimos documentarlos.
    Match por prefijo, no por primer segmento (`protocol_engine_init` pertenece al
    namespace `protocol_engine` aunque el separador sea `_`).
    """
    if sym.endswith("_py_path"):
        return False
    return any(sym == ns or sym.startswith(ns + "_") for ns in code_namespaces)


def critical_symbols(layer1: dict, code_namespaces: tuple[str, ...] | None = None) -> set[str]:
    """Símbolos críticos para alineación = god_nodes documentables (Fase 2c).

    Los entry_points (todo `_main`) ya NO se exigen: tener `main()` no es criticidad
    arquitectónica, son 140 raíces de CLI cuya documentación sería ruido.
    """
    namespaces = code_namespaces if code_namespaces is not None else _AUTODETECT_CANDIDATES
    return {
        s for s in layer1.get("god_nodes", [])
        if _is_documentable_symbol(s, namespaces)
    }


def detect_code_orphans(
    layer1: dict,
    documented: set[str],
    code_namespaces: tuple[str, ...] | None = None,
) -> list[dict]:
    """god_nodes documentables sin arista `documents` → orphan crítico (FAIL)."""
    orphans = []
    for sym in sorted(critical_symbols(layer1, code_namespaces)):
        if sym in documented:
            continue
        orphans.append({
            "code_id": sym,
            "type": "god_node",
            "severity": "FAIL",
            "message": "Símbolo crítico (god_node) sin documentación en la vault",
        })
    return orphans


def _classify_doc(label: str) -> str:
    low = label.lower()
    return "arch" if any(hint in low for hint in _ARCH_HINTS) else "concept"


def detect_doc_orphans(layer2: dict) -> list[dict]:
    """Docs sin ninguna arista saliente (ni documentan código ni enlazan docs) → WARN.

    Un doc huérfano es higiene (smell), NO una falla de correctitud: la doctrina, las
    reglas y la arquitectura conceptual legítimamente no referencian código. Por eso es
    **advisory (WARN)**, no gate. El invariante bloqueante vive del lado del código
    (god_nodes críticos documentados, `detect_code_orphans`). La detección de doc→código
    *stale* (un `[[símbolo]]` que ya no existe) requiere parsear los links crudos y queda
    como trabajo futuro. Un nodo con `skip_align: true` se excluye del reporte.
    """
    sourcing = {edge["source"] for edge in layer2.get("edges", [])}
    orphans = []
    for node in layer2.get("nodes", []):
        if node.get("skip_align"):
            continue
        if node["id"] in sourcing:
            continue
        cls = _classify_doc(node.get("label", node["id"]))
        orphans.append({
            "doc_id": node["id"],
            "classification": cls,
            "severity": "WARN",
            "message": f"Doc sin enlaces a código ni a otros docs ({cls}) — advisory",
        })
    return orphans


def generate_report(layer1: dict, layer2: dict) -> dict:
    """Sintetiza el reporte de alineación con severidad y exit_code.

    Si la extracción de Layer 1 no es confiable, aborta con `untrustworthy` (exit 1):
    no se puede afirmar alineación sobre una medición rota.
    """
    if not extraction_is_trustworthy(layer1):
        return {
            "status": "untrustworthy",
            "exit_code": 1,
            "message": (
                "Layer 1 extraction_status='failed': el grafo de código no es "
                "confiable. Alineación abortada (no es '0 orphans', es no-medible)."
            ),
            "code_orphans": [],
            "doc_orphans": [],
            "summary": {},
        }

    documented = documented_code_ids(layer2)
    code_orphans = detect_code_orphans(layer1, documented)
    doc_orphans = detect_doc_orphans(layer2)
    all_findings = code_orphans + doc_orphans
    fails = [f for f in all_findings if f["severity"] == "FAIL"]
    warns = [f for f in all_findings if f["severity"] == "WARN"]

    critical = critical_symbols(layer1)
    documented_critical = len(critical) - len(code_orphans)
    coverage = round(100 * documented_critical / len(critical), 1) if critical else 100.0

    return {
        "status": "checked",
        "exit_code": 1 if fails else 0,
        "code_orphans": code_orphans,
        "doc_orphans": doc_orphans,
        "summary": {
            "critical_symbols": len(critical),
            "documented_critical": documented_critical,
            "critical_coverage_pct": coverage,
            "fail_count": len(fails),
            "warn_count": len(warns),
        },
    }


_GATE_MARKER = Path(".protocol") / "align_gate.enabled"


def align_gate_enabled(repo_root: Path) -> bool:
    """True si el repo optó por el gate bloqueante (marcador `.protocol/align_gate.enabled`).

    Opt-in deliberado: align-check es ADVISORY por defecto para no brickear los satélites
    aún no documentados al heredar el pre-commit. Un repo activa el gate solo cuando pagó
    su deuda de contenido (god_nodes críticos documentados).
    """
    return (Path(repo_root) / _GATE_MARKER).is_file()


def gate_exit_code(report: dict, gate_enabled: bool) -> int:
    """Exit code efectivo: el real del reporte si el gate está activo; si no, 0 (advisory)."""
    return report.get("exit_code", 0) if gate_enabled else 0


def check_alignment(repo_root: Path, report_path: Path | None = None) -> dict:
    """Orquestador con I/O: carga el grafo del satélite y escribe el reporte JSON."""
    repo_root = Path(repo_root)
    graph_path = repo_root / ".protocol" / "metadata" / "internal_graph.json"
    if not graph_path.is_file():
        raise FileNotFoundError(f"internal_graph.json no encontrado: {graph_path}")

    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        # Manejo de error real: un grafo ilegible/corrupto NO es alineación verde.
        logger.error("No se pudo leer/parsear el grafo %s: %s", graph_path, exc)
        return {
            "status": "error",
            "exit_code": 1,
            "message": f"Grafo ilegible o corrupto: {exc}",
            "code_orphans": [],
            "doc_orphans": [],
            "summary": {},
        }

    layer1 = graph.get("layer1_ast", {})
    layer2 = graph.get("layer2_docs", {})
    report = generate_report(layer1, layer2)

    if report_path is None:
        report_path = repo_root / ".protocol" / "metadata" / "alignment_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> int:
    """CLI: ejecuta la alineación sobre un repo y devuelve el exit_code del reporte."""
    import argparse

    parser = argparse.ArgumentParser(description="Linter de alineación Código↔Docs.")
    parser.add_argument("--repo-root", type=str, default=".", help="Raíz del repositorio")
    parser.add_argument("--report-path", type=str, help="Ruta del reporte JSON de salida")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    report_path = Path(args.report_path).resolve() if args.report_path else None
    report = check_alignment(repo, report_path=report_path)

    gate_on = align_gate_enabled(repo)
    effective = gate_exit_code(report, gate_on)
    mode = "GATE" if gate_on else "ADVISORY"
    summary = report.get("summary", {})
    print(
        f"[Alignment:{mode}] status={report['status']} exit={effective} | "
        f"FAIL={summary.get('fail_count', 0)} WARN={summary.get('warn_count', 0)} | "
        f"cobertura crítica={summary.get('critical_coverage_pct', 0)}%"
    )
    if not gate_on and report.get("exit_code", 0) != 0:
        print(
            "  (ADVISORY: hay FAILs pero el gate no está activo en este repo; "
            "crea .protocol/align_gate.enabled para bloquear)"
        )
    return effective


if __name__ == "__main__":
    raise SystemExit(main())
