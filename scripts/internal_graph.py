#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""internal_graph.py — Grafo Capa 1 interno de Cerberus (C3, ancla VC-069).

Capa 1 = código interno (módulos .py, imports, llamadas), distinta de la Capa 2
(ecosistema de satélites en generate_graph_report.py). Adopta el motor externo
`graphify` (offline, AST tree-sitter) como extractor y NORMALIZA su salida
node-link a métricas accionables: orphans / god_nodes / entry_points /
consumers_of / dependencies_of / path_index.

La función `derive_internal_graph` es PURA (sin I/O) y por eso falsable. La
orquestación (staging temporal + invocación de graphify + limpieza) se añade aparte
para no contaminar el repo con el `graph.json` crudo del motor.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

# Relaciones de graphify que cuentan como acoplamiento de CÓDIGO. Se excluyen
# 'contains' (estructural archivo→símbolo) y 'rationale_for' (docstring→símbolo).
CODE_RELATIONS = frozenset(
    {"calls", "imports", "references", "imports_from", "re_exports"}
)
GOD_DEGREE = 8  # grado total (in+out) a partir del cual un nodo es "god-node"


def _node_path(node: dict) -> str | None:
    for key in ("label", "source_file", "path", "source_path", "file_path"):
        value = node.get(key)
        if isinstance(value, str) and value:
            return value.replace("\\", "/")
    return None


def _collect_code_edges(nodes: list[dict], links: list[dict]) -> tuple[dict, dict, int]:
    inbound: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    outbound: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    code_edges = 0
    for link in links:
        if link.get("relation") not in CODE_RELATIONS:
            continue
        src, tgt = link.get("source"), link.get("target")
        if src not in inbound or tgt not in inbound:
            continue
        outbound[src].append(tgt)
        inbound[tgt].append(src)
        code_edges += 1
    return inbound, outbound, code_edges


def _build_path_index(nodes: list[dict], is_file: dict[str, bool]) -> dict[str, str]:
    path_index: dict[str, str] = {}
    for node in nodes:
        if not is_file.get(node["id"]):
            continue
        path = _node_path(node)
        if path and path not in path_index:
            path_index[path] = node["id"]
    return path_index


def derive_internal_graph(graph: dict) -> dict:
    """Deriva métricas Capa 1 desde un graph.json node-link de graphify.

    Devuelve un dict con: generated, node_count, edge_count, god_nodes (grado
    alto), orphans (código no-archivo sin aristas de código = candidato muerto),
    entry_points (sin entrada, con salida = raíces) y consumers_of (mapa inverso).
    """
    nodes = graph.get("nodes", [])
    links = graph.get("links", [])

    is_file = {n["id"]: str(n.get("label", "")).endswith(".py") for n in nodes}
    is_code = {n["id"]: n.get("file_type") == "code" for n in nodes}
    inbound, outbound, code_edges = _collect_code_edges(nodes, links)

    def degree(nid: str) -> int:
        return len(inbound[nid]) + len(outbound[nid])

    orphans = sorted(
        nid for nid in inbound
        if is_code.get(nid) and not is_file.get(nid) and degree(nid) == 0
    )
    entry_points = sorted(
        nid for nid in inbound if not inbound[nid] and outbound[nid]
    )
    god_nodes = sorted(nid for nid in inbound if degree(nid) >= GOD_DEGREE)
    consumers_of = {nid: sorted(set(srcs)) for nid, srcs in inbound.items() if srcs}
    dependencies_of = {
        nid: sorted(set(tgts)) for nid, tgts in outbound.items() if tgts
    }

    return {
        "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "node_count": len(nodes),
        "edge_count": code_edges,
        "god_nodes": god_nodes,
        "orphans": orphans,
        "entry_points": entry_points,
        "consumers_of": consumers_of,
        "dependencies_of": dependencies_of,
        "path_index": _build_path_index(nodes, is_file),
    }


def _doc_node_id(md_file: Path, wiki_dir: Path) -> str:
    """H4: id estable por ruta relativa al vault (evita colisión de stems)."""
    return md_file.relative_to(wiki_dir).with_suffix("").as_posix().lower()


def _strip_volatile(payload: dict) -> dict:
    """Devuelve una copia del payload sin los campos de timestamp `generated`
    (raíz, layer1_ast, layer2_docs) para comparar SUSTANCIA, no el reloj."""
    clean = json.loads(json.dumps(payload))  # deep copy serializable
    clean.pop("generated", None)
    for layer in ("layer1_ast", "layer2_docs"):
        if isinstance(clean.get(layer), dict):
            clean[layer].pop("generated", None)
    return clean


def _substance_changed(out_path: Path, new_payload: dict) -> bool:
    """True si el grafo nuevo difiere del existente en algo más que `generated`.
    Compara dicts parseados (no strings) para no falsear cambios por orden/formato."""
    if not out_path.is_file():
        return True
    try:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True
    return _strip_volatile(existing) != _strip_volatile(new_payload)


def extraction_is_trustworthy(layer1_ast: dict) -> bool:
    """Contrato H5: ¿la medición de Layer 1 es confiable o fue un falso verde?

    Devuelve False solo si el extractor reventó (`extraction_status == "failed"`).
    Un grafo legítimamente vacío ('ok' / 'empty_no_targets') SÍ es confiable: medir
    cero símbolos es distinto de no-poder-medir. Los consumidores (alignment_checker)
    deben abortar con FAIL ante un grafo no confiable, nunca tratarlo como '0 orphans'.
    """
    return layer1_ast.get("extraction_status") != "failed"


def _build_symbol_aliases(code_symbols: set[str]) -> dict[str, str]:
    """Fase 2b: mapa alias-corto → id-completo para matching ergonómico de [[links]].

    Para cada símbolo `a_b_c` registra sus sufijos (`b_c`, `c`) — así un doc puede
    escribir [[blast_radius]] y alcanzar `scripts_blast_radius`. Solo conserva aliases
    ÚNICOS (mapean a un único símbolo y no chocan con un id completo); los ambiguos se
    descartan para no emitir aristas `documents` falsas.
    """
    owners: dict[str, set[str]] = {}
    for sym in code_symbols:
        parts = sym.split("_")
        for i in range(1, len(parts)):  # i=0 es el id completo → ya lo cubre exact-match
            owners.setdefault("_".join(parts[i:]), set()).add(sym)
    return {
        alias: next(iter(syms))
        for alias, syms in owners.items()
        if len(syms) == 1 and alias not in code_symbols
    }


def _parse_obsidian_links(
    content: str,
    node_id: str,
    stem_index: dict[str, list[str]],
    edges: list,
    code_symbols: set[str] | None = None,
    symbol_aliases: dict[str, str] | None = None,
) -> None:
    obsidian_re = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    for match in obsidian_re.finditer(content):
        raw = match.group(1).strip().split("#")[0]
        if not raw:
            continue
        target_stem = Path(raw).stem.lower()
        # Stem ambiguo (varios docs) → edge a cada candidato, sin perder ninguno.
        for target_id in stem_index.get(target_stem, []):
            edges.append({
                "source": node_id,
                "target": target_id,
                "relation": "links_to"
            })
        # H1 + Fase 2b: si el target matchea un símbolo de código (Layer 1) por id
        # exacto O por alias ergonómico, emitir edge 'documents' (doc→código). Puede
        # coexistir con un links_to a un .md homónimo. Separadores . / \ - → '_'.
        if code_symbols:
            norm = re.sub(r"[ ./\\-]+", "_", raw.strip().lower())
            target = norm if norm in code_symbols else (symbol_aliases or {}).get(norm)
            if target:
                edges.append({
                    "source": node_id,
                    "target": target,
                    "relation": "documents"
                })


def _parse_markdown_links(content: str, node_id: str, parent_dir: Path, wiki_dir: Path, edges: list) -> None:
    markdown_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for match in markdown_re.finditer(content):
        path_str = match.group(1).strip().split("#")[0]
        if path_str.startswith(("http://", "https://", "file://", "mailto:", "#")):
            continue
        link_path = (parent_dir / path_str).resolve()
        if link_path.exists() and link_path.suffix == ".md":
            try:
                target_id = _doc_node_id(link_path, wiki_dir.resolve())
            except ValueError:
                target_id = link_path.stem.lower()  # link fuera del vault
            edges.append({
                "source": node_id,
                "target": target_id,
                "relation": "links_to"
            })


def extract_layer2_docs_graph(wiki_dir: Path, code_symbols: set[str] | None = None) -> dict:
    """Escanea un directorio de wiki/conocimiento local y extrae sus nodos/aristas.

    Parsea enlaces Obsidian [[Link]] y estándar de Markdown a archivos .md. Si se
    pasa `code_symbols` (ids de Layer 1), los [[links]] que matchean un símbolo de
    código generan aristas `documents` (doc→código) para habilitar la alineación.
    """
    if not wiki_dir.is_dir():
        return {"nodes": [], "edges": [], "node_count": 0, "edge_count": 0}

    # Fase 2b: índice de aliases ergonómicos para resolver [[nombre_corto]] al id
    # completo del símbolo. Se construye una vez por extracción.
    symbol_aliases = _build_symbol_aliases(code_symbols) if code_symbols else {}

    nodes = []
    edges = []

    all_md = list(wiki_dir.rglob("*.md"))
    # Índice stem → [node_ids] para resolver [[links]] aun con stems repetidos.
    stem_index: dict[str, list[str]] = {}
    for f in all_md:
        stem_index.setdefault(f.stem.lower(), []).append(_doc_node_id(f, wiki_dir))

    for md_file in all_md:
        node_id = _doc_node_id(md_file, wiki_dir)
        nodes.append({
            "id": node_id,
            "label": md_file.name,
            "type": "doc"
        })

        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            # D5-OK: Log warning rather than silent pass
            logging.warning("No se pudo leer la nota de wiki %s: %s", md_file, e)
            continue

        _parse_obsidian_links(content, node_id, stem_index, edges, code_symbols, symbol_aliases)
        _parse_markdown_links(content, node_id, md_file.parent, wiki_dir, edges)

    # Deduplicar enlaces
    seen = set()
    deduped_edges = []
    for edge in edges:
        pair = (edge["source"], edge["target"])
        if pair not in seen:
            seen.add(pair)
            deduped_edges.append(edge)

    return {
        "nodes": nodes,
        "edges": deduped_edges,
        "node_count": len(nodes),
        "edge_count": len(deduped_edges)
    }


_SKIP_DIRS = {"__pycache__", "graphify-out", ".git"}


def _only_python(directory: str, names: list[str]) -> set[str]:
    """Ignore callable para copytree: conserva SOLO dirs y archivos .py."""
    ignored: set[str] = set()
    for name in names:
        if name in _SKIP_DIRS:
            ignored.add(name)
            continue
        full = Path(directory) / name
        if full.is_file() and not name.endswith(".py"):
            ignored.add(name)
    return ignored


def _run_graphify(stage_dir: Path) -> Path:
    """Extractor por defecto: graphify update OFFLINE (sin LLM) sobre el staging."""
    subprocess.run(
        ["graphify", "update", str(stage_dir)],
        cwd=str(stage_dir), check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return stage_dir / "graphify-out" / "graph.json"


def build_internal_graph(
    repo_root: Path,
    targets: tuple[str, ...] = ("scripts", "protocol_engine"),
    out_path: Path | None = None,
    runner: Callable[[Path], Path] = _run_graphify,
) -> Path:
    """Construye el grafo local vía staging temporal (sin contaminar el repo).

    El output incluye `layer1_ast` y `layer2_docs`, además de las claves
    raíz para mantener paridad retrospectiva con blast_radius.py.
    """
    repo_root = Path(repo_root)
    if out_path is None:
        out_path = repo_root / ".protocol" / "metadata" / "internal_graph.json"

    existing_targets = [t for t in targets if (repo_root / t).is_dir()]
    derived = None
    # H2: distinguir 'ok' (medido) de 'empty_no_targets' (nada que medir) de
    # 'failed' (el extractor reventó). Un fallo NO debe degradar a éxito-vacío.
    status = "empty_no_targets" if not existing_targets else "ok"

    if existing_targets:
        stage = Path(tempfile.mkdtemp(prefix="cerb_capa1_"))
        try:
            for target in existing_targets:
                src = repo_root / target
                shutil.copytree(src, stage / target, ignore=_only_python)
            try:
                graph_json = runner(stage)
                graph = json.loads(Path(graph_json).read_text(encoding="utf-8"))
                derived = derive_internal_graph(graph)
            except Exception as exc:
                status = "failed"
                logging.getLogger(__name__).warning(
                    "No se pudo extraer el grafo de código (Layer 1 AST): %s", exc
                )
        finally:
            shutil.rmtree(stage, ignore_errors=True)

    if derived is None:
        derived = {
            "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "node_count": 0,
            "edge_count": 0,
            "god_nodes": [],
            "orphans": [],
            "entry_points": [],
            "consumers_of": {},
            "dependencies_of": {},
            "path_index": {}
        }
    derived["extraction_status"] = status

    # Conjunto de símbolos de código (Layer 1) para resolver edges doc→código.
    code_symbols: set[str] = set(derived.get("god_nodes", []))
    code_symbols |= set(derived.get("entry_points", []))
    code_symbols |= set(derived.get("orphans", []))
    code_symbols |= set(derived.get("consumers_of", {}))
    code_symbols |= set(derived.get("dependencies_of", {}))
    for _tgts in derived.get("dependencies_of", {}).values():
        code_symbols.update(_tgts)

    # Extraer Capa 2 (wiki local). H3: probar varios candidatos en orden de
    # preferencia — Cerberus no tiene docs/knowledge ni Wiki, su vault de
    # arquitectura vive en docs/architecture. El primero existente gana.
    wiki_candidates = ("docs/knowledge", "Wiki", "docs/architecture", "docs")
    wiki_dir = next(
        (repo_root / c for c in wiki_candidates if (repo_root / c).is_dir()),
        repo_root / "docs" / "knowledge",
    )

    layer2 = extract_layer2_docs_graph(wiki_dir, code_symbols=code_symbols)

    final_payload = {
        **derived,  # Compatibilidad raíz
        "layer1_ast": derived,
        "layer2_docs": layer2
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # VC-141: escritura idempotente. Si la sustancia (todo menos los timestamps
    # `generated`) es idéntica al archivo existente, NO reescribir — así el hook no
    # ensucia el working tree con un timestamp nuevo en cada commit.
    if not _substance_changed(out_path, final_payload):
        return out_path
    out_path.write_text(
        json.dumps(final_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out_path


# Candidatos de auto-detección cuando se da --repo-root sin --targets. Incluye
# `protocol_engine` para no perder el motor de Cerberus (antes lo excluía → bug).
_AUTODETECT_CANDIDATES = ("scripts", "protocol_engine", "tests", "src", "app")


def _auto_detect_targets(repo: Path) -> tuple[str, ...]:
    """Targets de código presentes en el repo (orden estable). Pura y falsable."""
    return tuple(c for c in _AUTODETECT_CANDIDATES if (repo / c).is_dir())


def main() -> int:
    """CLI: regenera el grafo de código y wiki de un repositorio."""
    import argparse
    parser = argparse.ArgumentParser(
        description="internal_graph.py — Grafo local de Satélites."
    )
    parser.add_argument("--repo-root", type=str, help="Ruta al directorio raíz del repositorio")
    parser.add_argument("--targets", type=str, help="Directorios de código separados por coma")
    parser.add_argument("--out", type=str, help="Ruta del archivo JSON de salida")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]

    targets = ("scripts", "protocol_engine")
    if args.targets:
        targets = tuple(t.strip() for t in args.targets.split(",") if t.strip())
    elif args.repo_root:
        # Auto-detectar carpetas si no se especifican targets en un satélite.
        targets = _auto_detect_targets(repo)

    out_path = Path(args.out).resolve() if args.out else None
    out = build_internal_graph(repo, targets=targets, out_path=out_path)
    data = json.loads(out.read_text(encoding="utf-8"))

    ast_data = data.get("layer1_ast") or {}
    docs_data = data.get("layer2_docs") or {}

    print(
        f"[Local Graph] {out} — "
        f"Layer 1 AST: {ast_data.get('node_count', 0)} nodos, {ast_data.get('edge_count', 0)} aristas | "
        f"Layer 2 Docs: {docs_data.get('node_count', 0)} nodos, {docs_data.get('edge_count', 0)} aristas"
    )
    # H2/H5: si el extractor falló, fallar RUIDOSAMENTE (exit 1) en lugar de
    # reportar un grafo vacío como éxito. El falso verde se propaga al exit code.
    if not extraction_is_trustworthy(ast_data):
        print(
            "[ERROR] Extracción de Layer 1 falló (extraction_status='failed'): "
            "el grafo NO es confiable. ¿graphify instalado? No tratar como '0 símbolos'."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
