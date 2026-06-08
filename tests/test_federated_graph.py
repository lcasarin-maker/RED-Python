"""Tests para la extracción y derivación de grafos federados de dos capas locales."""
import pytest
import json
from pathlib import Path
from scripts.internal_graph import (
    extract_layer2_docs_graph,
    build_internal_graph,
    extraction_is_trustworthy,
    _auto_detect_targets,
)
from scripts.generate_graph_report import build_graph_json


def test_extract_layer2_docs_graph(tmp_path):
    wiki_dir = tmp_path / "docs" / "knowledge"
    wiki_dir.mkdir(parents=True)
    
    note1 = wiki_dir / "note1.md"
    note1.write_text("Link to [[note2]]", encoding="utf-8")
    note2 = wiki_dir / "note2.md"
    note2.write_text("Back to [[note1]]", encoding="utf-8")
    
    graph = extract_layer2_docs_graph(wiki_dir)
    assert graph["node_count"] == 2
    assert graph["edge_count"] == 2
    
    nodes = {n["id"] for n in graph["nodes"]}
    assert "note1" in nodes
    assert "note2" in nodes

def test_extract_layer2_docs_graph_nonexistent():
    # Negative path: nonexistent directory returns empty graph
    graph = extract_layer2_docs_graph(Path("/nonexistent/path/here"))
    assert graph["nodes"] == []  # == []

def test_doc_links_to_code_symbol(tmp_path):
    """H1: un [[symbol]] que matchea un símbolo de Layer 1 emite edge 'documents'
    (doc→código), no solo doc↔doc. Sin esto, la alineación código-docs es imposible."""
    wiki = tmp_path / "docs" / "knowledge"
    wiki.mkdir(parents=True)
    (wiki / "arch.md").write_text(
        "El módulo [[scripts_core_utils]] centraliza utilidades.", encoding="utf-8"
    )
    graph = extract_layer2_docs_graph(wiki, code_symbols={"scripts_core_utils"})
    documents = [e for e in graph["edges"] if e["relation"] == "documents"]
    assert any(e["target"] == "scripts_core_utils" for e in documents)


def test_ergonomic_alias_matches_short_name(tmp_path):
    """Fase 2b: un [[nombre_corto]] resuelve al símbolo completo. Un doc escribe
    [[blast_radius]] y debe emitir 'documents' → scripts_blast_radius sin exigir el
    id completo. Sin esto el linter es inusable (nadie escribe [[scripts_x_y]])."""
    wiki = tmp_path / "docs" / "knowledge"
    wiki.mkdir(parents=True)
    (wiki / "arch.md").write_text("El [[blast_radius]] calcula impacto.", encoding="utf-8")
    graph = extract_layer2_docs_graph(wiki, code_symbols={"scripts_blast_radius"})
    documents = [e for e in graph["edges"] if e["relation"] == "documents"]
    assert any(e["target"] == "scripts_blast_radius" for e in documents)


def test_ambiguous_alias_emits_no_edge(tmp_path):
    """Angry Path 2b: si un alias corto mapea a >1 símbolo, NO se auto-resuelve
    (evita aristas 'documents' falsas). [[run]] con dos símbolos *_run → sin edge."""
    wiki = tmp_path / "docs" / "knowledge"
    wiki.mkdir(parents=True)
    (wiki / "a.md").write_text("Ver [[run]].", encoding="utf-8")
    graph = extract_layer2_docs_graph(wiki, code_symbols={"scripts_a_run", "scripts_b_run"})
    documents = [e for e in graph["edges"] if e["relation"] == "documents"]
    assert documents == []


def test_dotted_separator_normalizes_to_alias(tmp_path):
    """Fase 2b: separadores ergonómicos (. / -) en el link normalizan a '_' antes de
    resolver. [[core.utils]] debe alcanzar scripts_core_utils vía alias 'core_utils'."""
    wiki = tmp_path / "docs" / "knowledge"
    wiki.mkdir(parents=True)
    (wiki / "a.md").write_text("Mod [[core.utils]].", encoding="utf-8")
    graph = extract_layer2_docs_graph(wiki, code_symbols={"scripts_core_utils"})
    documents = [e for e in graph["edges"] if e["relation"] == "documents"]
    assert any(e["target"] == "scripts_core_utils" for e in documents)


def test_layer2_without_code_symbols_unchanged(tmp_path):
    """H1 no-regresión: sin code_symbols, comportamiento doc↔doc intacto."""
    wiki = tmp_path / "docs" / "knowledge"
    wiki.mkdir(parents=True)
    (wiki / "a.md").write_text("[[b]]", encoding="utf-8")
    (wiki / "b.md").write_text("texto", encoding="utf-8")
    graph = extract_layer2_docs_graph(wiki)
    assert all(e["relation"] == "links_to" for e in graph["edges"])


def test_duplicate_stems_no_collision(tmp_path):
    """H4: dos index.md en dirs distintos NO deben colapsar al mismo node_id."""
    wiki = tmp_path / "docs" / "knowledge"
    (wiki / "architecture").mkdir(parents=True)
    (wiki / "guide").mkdir(parents=True)
    (wiki / "architecture" / "index.md").write_text("arch", encoding="utf-8")
    (wiki / "guide" / "index.md").write_text("guide", encoding="utf-8")

    graph = extract_layer2_docs_graph(wiki)
    ids = {n["id"] for n in graph["nodes"]}
    assert graph["node_count"] == 2
    assert len(ids) == 2  # sin colisión: ids distintos por ruta


def test_idempotent_write_no_substance_change(tmp_path):
    """VC-141: regenerar el grafo sin cambios de sustancia NO debe reescribir el
    archivo (preserva `generated`). Evita que el hook ensucie el working tree con
    timestamps nuevos en cada commit = falso positivo perpetuo del detector."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "mod.py").write_text("x = 1\n", encoding="utf-8")

    def canned_runner(_stage):
        graph = {"nodes": [], "links": []}
        gp = _stage / "graph.json"
        gp.write_text(json.dumps(graph), encoding="utf-8")
        return gp

    out = build_internal_graph(tmp_path, targets=("scripts",), runner=canned_runner)
    first = json.loads(out.read_text(encoding="utf-8"))["generated"]

    build_internal_graph(tmp_path, targets=("scripts",), runner=canned_runner)
    second = json.loads(out.read_text(encoding="utf-8"))["generated"]
    assert first == second  # sustancia idéntica → archivo intacto


def test_no_silent_graph_degradation(tmp_path):
    """H5: contrato que un consumidor (alignment) usa para no ser engañado por un
    falso verde. El auditor D5 sintáctico NO detecta el swallow de internal_graph
    (solo marca pass/continue); este test de contrato sí lo hace.

    - Grafo con extractor que falló → NO es trustworthy (no interpretar como 0 orphans).
    - Grafo legítimamente vacío (sin targets) → SÍ es trustworthy (medición válida).
    """
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "mod.py").write_text("x = 1\n", encoding="utf-8")

    def failing_runner(_stage):
        raise RuntimeError("graphify ausente")

    failed = build_internal_graph(tmp_path, targets=("scripts",), runner=failing_runner)
    failed_l1 = json.loads(failed.read_text(encoding="utf-8"))["layer1_ast"]
    assert extraction_is_trustworthy(failed_l1) is False

    empty = build_internal_graph(tmp_path, targets=("inexistente",))
    empty_l1 = json.loads(empty.read_text(encoding="utf-8"))["layer1_ast"]
    assert extraction_is_trustworthy(empty_l1) is True


def test_extraction_failed_is_marked(tmp_path):
    """H2: si el extractor (graphify) falla, el grafo NO debe degradar a un
    'éxito vacío' (todo ceros + exit 0). Debe marcar extraction_status='failed'
    para que el consumidor distinga 'no hay código' de 'no se pudo medir'."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "mod.py").write_text("x = 1\n", encoding="utf-8")

    def failing_runner(_stage):
        raise RuntimeError("graphify no instalado")

    out = build_internal_graph(tmp_path, targets=("scripts",), runner=failing_runner)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["layer1_ast"]["extraction_status"] == "failed"


def test_extraction_empty_targets_is_not_failed(tmp_path):
    """Angry Path H2: sin targets reales es 'empty_no_targets', NO 'failed'.
    Distinguir vacío-legítimo de fallo-de-medición."""
    out = build_internal_graph(tmp_path, targets=("inexistente",))
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["layer1_ast"]["extraction_status"] == "empty_no_targets"


def test_auto_detect_includes_protocol_engine(tmp_path):
    """Bug: `--repo-root` sin `--targets` usaba candidates sin `protocol_engine`,
    así que Cerberus perdía su propio motor del grafo. El auto-detect debe incluir
    `protocol_engine` cuando el dir existe, sin perder los demás candidatos."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "protocol_engine").mkdir()
    targets = _auto_detect_targets(tmp_path)
    assert "protocol_engine" in targets
    assert "scripts" in targets


def test_auto_detect_omits_absent_dirs(tmp_path):
    """No-regresión: el auto-detect solo incluye dirs existentes (un satélite sin
    protocol_engine no debe recibirlo)."""
    (tmp_path / "src").mkdir()
    targets = _auto_detect_targets(tmp_path)
    assert "protocol_engine" not in targets
    assert targets == ("src",)


def test_layer3_ecosystem_merge(tmp_path):
    proj1 = tmp_path / "proj1"
    proj1.mkdir()
    (proj1 / ".protocol" / "metadata").mkdir(parents=True)
    
    local_graph = proj1 / ".protocol" / "metadata" / "internal_graph.json"
    local_graph_data = {
        "generated": "2026-06-07T00:00:00",
        "node_count": 0,
        "edge_count": 0,
        "god_nodes": [],
        "orphans": [],
        "entry_points": [],
        "consumers_of": {},
        "dependencies_of": {},
        "path_index": {},
        "layer2_docs": {
            "nodes": [
                {"id": "doc1", "label": "doc1.md"}
            ],
            "edges": []
        }
    }
    local_graph.write_text(json.dumps(local_graph_data), encoding="utf-8")
    
    registry = {
        "projects": [
            {
                "name": "proj1",
                "path": str(proj1),
                "status": "active",
                "adoption_details": {
                    "hook_installed": True,
                    "auditor_present": True,
                    "tests_present": True,
                    "path_exists": True
                }
            }
        ]
    }
    
    global_graph = build_graph_json(registry)
    nodes_ids = {n["id"] for n in global_graph["nodes"]}
    assert "proj1" in nodes_ids
    assert "proj1:doc1" in nodes_ids
