#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_graph_report.py — Grafo de conocimiento de Cerberus (Obsidian/jsoncanvas pattern)

Genera GRAPH_REPORT.md con:
  - Mapa de satélites del REGISTRY con estado de adopción
  - God nodes del protocolo (archivos más referenciados)
  - Estado de adopción por satélite (hook / auditor / tests)
  - Exporta graph.json para consultas programáticas

Origen: Obsidian jsoncanvas (visualización de grafo de conocimiento) +
        safishamsi/graphify (god nodes, GRAPH_REPORT.md, graph.json).
"""
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger("generate_graph_report")
logging.basicConfig(level=logging.INFO, format="%(message)s")

_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = _ROOT / ".protocol" / "metadata" / "REGISTRY.json"
REPORT_PATH = _ROOT / "GRAPH_REPORT.md"
GRAPH_JSON_PATH = _ROOT / ".protocol" / "metadata" / "graph.json"

PROTOCOL_DOCS = [
    "AGENT.md", "SPEC.md", "PROTOCOL_SYSTEM.md",
    "PROTOCOL_BEHAVIOR.md", "SOURCES_OF_TRUTH.md",
]


def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        logger.error("[D5] REGISTRY.json no encontrado en %s", REGISTRY_PATH)
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("[D5] Error leyendo REGISTRY.json: %s", exc)
        return {}


def _adoption_badge(details: dict) -> str:
    hook = "✅" if details.get("hook_installed") else "❌"
    auditor = "✅" if details.get("auditor_present") else "❌"
    tests = "✅" if details.get("tests_present") else "❌"
    return f"Hook:{hook} Auditor:{auditor} Tests:{tests}"


def _god_nodes(projects: list) -> list[str]:
    """Identifica archivos de protocolo más referenciados en satélites."""
    ref_counts: dict[str, int] = {doc: 0 for doc in PROTOCOL_DOCS}
    for proj in projects:
        path = Path(proj.get("path", ""))
        if not path.exists():
            continue
        for doc in PROTOCOL_DOCS:
            if (path / doc).exists():
                ref_counts[doc] += 1
    threshold = max(1, len(projects) // 3)
    return [
        f"{doc} ({count} satélites)"
        for doc, count in sorted(ref_counts.items(), key=lambda x: -x[1])
        if count >= threshold
    ]


def _adoption_score(details: dict) -> float:
    checks = ["hook_installed", "auditor_present", "tests_present", "path_exists"]
    return sum(1 for c in checks if details.get(c)) / len(checks)


def build_graph_report(registry: dict) -> str:
    projects = registry.get("projects", [])
    total = len(projects)

    fully_adopted = [p for p in projects if _adoption_score(p.get("adoption_details", {})) == 1.0]
    partial = [p for p in projects if 0 < _adoption_score(p.get("adoption_details", {})) < 1.0]
    not_adopted = [p for p in projects if _adoption_score(p.get("adoption_details", {})) == 0]

    god_nodes = _god_nodes(projects)

    lines = [
        "# GRAPH REPORT — Cerberus Ecosystem",
        f"_Generado automáticamente. {total} satélites registrados._",
        "",
        "## God Nodes (archivos de protocolo más adoptados)",
        "",
    ]
    if god_nodes:
        for gn in god_nodes:
            lines.append(f"- 🔴 **{gn}**")
    else:
        lines.append("_Sin god nodes detectados._")

    lines += [
        "",
        f"## Adopción completa ({len(fully_adopted)}/{total})",
        "",
    ]
    for p in fully_adopted:
        lines.append(f"- ✅ **{p['name']}** — {_adoption_badge(p.get('adoption_details', {}))}")

    lines += [
        "",
        f"## Adopción parcial ({len(partial)}/{total})",
        "",
    ]
    for p in partial:
        score = int(_adoption_score(p.get("adoption_details", {})) * 100)
        lines.append(f"- ⚠️ **{p['name']}** ({score}%) — {_adoption_badge(p.get('adoption_details', {}))}")

    lines += [
        "",
        f"## Sin adopción ({len(not_adopted)}/{total})",
        "",
    ]
    for p in not_adopted:
        exists = "path existe" if p.get("adoption_details", {}).get("path_exists") else "path no existe"
        lines.append(f"- ❌ **{p['name']}** ({exists})")

    lines += [
        "",
        "## Métricas globales",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Total satélites | {total} |",
        f"| Adopción completa | {len(fully_adopted)} ({int(len(fully_adopted)/total*100) if total else 0}%) |",
        f"| Adopción parcial | {len(partial)} |",
        f"| Sin adopción | {len(not_adopted)} |",
        f"| God nodes protocolo | {len(god_nodes)} |",
    ]
    return "\n".join(lines)


def build_graph_json(registry: dict) -> dict:
    projects = registry.get("projects", [])
    nodes = [{"id": "cerberus_core", "type": "core", "label": "Cerberus Core"}]
    edges = []
    for p in projects:
        proj_name = p["name"]
        proj_path = Path(p["path"])
        node_id = proj_name.replace(" ", "_")
        score = _adoption_score(p.get("adoption_details", {}))
        
        nodes.append({
            "id": node_id,
            "type": "satellite",
            "label": proj_name,
            "adoption_score": score,
            "status": p.get("status", "unknown")
        })
        edges.append({
            "from": "cerberus_core",
            "to": node_id,
            "weight": score,
            "label": f"{int(score*100)}% adopted"
        })

        # Cargar el grafo local del satélite si existe para armar Capa 3
        local_graph_path = proj_path / ".protocol" / "metadata" / "internal_graph.json"
        if local_graph_path.is_file():
            try:
                local_data = json.loads(local_graph_path.read_text(encoding="utf-8"))
                l2 = local_data.get("layer2_docs") or {}
                l2_nodes = l2.get("nodes") or []
                l2_edges = l2.get("edges") or []

                for n in l2_nodes:
                    local_node_id = f"{node_id}:{n['id']}"
                    nodes.append({
                        "id": local_node_id,
                        "type": "doc",
                        "label": n.get("label", n["id"]),
                        "satellite": proj_name
                    })
                    edges.append({
                        "from": node_id,
                        "to": local_node_id,
                        "relation": "has_doc"
                    })

                for e in l2_edges:
                    edges.append({
                        "from": f"{node_id}:{e['source']}",
                        "to": f"{node_id}:{e['target']}",
                        "relation": e.get("relation", "links_to")
                    })
            except (OSError, json.JSONDecodeError, KeyError) as exc:
                # Merge best-effort: un satélite con grafo ilegible/corrupto no aborta
                # el ecosistema, pero se acota a errores de I/O-datos (no traga bugs).
                logger.warning("[Graph] No se pudo leer el grafo local de %s: %s", proj_name, exc)

    return {"nodes": nodes, "edges": edges,
            "generated": str(Path(__file__).name), "total_satellites": len(projects)}


def main() -> int:
    registry = _load_registry()
    if not registry:
        return 1

    report = build_graph_report(registry)
    REPORT_PATH.write_text(report, encoding="utf-8")
    logger.info("[Graph] GRAPH_REPORT.md generado → %s", REPORT_PATH)

    graph = build_graph_json(registry)
    GRAPH_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_JSON_PATH.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("[Graph] graph.json generado → %s", GRAPH_JSON_PATH)

    # Escribir también global_ecosystem_graph.json para persistencia formal de Capa 3
    global_path = GRAPH_JSON_PATH.parent / "global_ecosystem_graph.json"
    global_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("[Graph] global_ecosystem_graph.json generado → %s", global_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
