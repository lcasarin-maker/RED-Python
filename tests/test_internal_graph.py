#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests falsables del derivador Capa 1 (C3, ancla VC-069).

Ejercen la función PURA `derive_internal_graph`: desde un graph.json node-link
de graphify deriva orphans/god_nodes/entry_points/consumers_of/dependencies_of/
path_index usando SOLO las relaciones de código (calls/imports/references),
ignorando contains/rationale_for."""
import json
from pathlib import Path

from scripts.internal_graph import derive_internal_graph, build_internal_graph


def _graph(nodes, links):
    return {"directed": False, "multigraph": False, "graph": {},
            "nodes": nodes, "links": links, "hyperedges": []}


def _node(nid, label):
    return {"id": nid, "label": label, "file_type": "code",
            "source_file": "a.py", "source_location": "L1"}


def _link(src, tgt, relation):
    return {"source": src, "target": tgt, "relation": relation, "weight": 1.0}


def test_derives_orphans_entrypoints_consumers():
    """foo() llama a bar(); dead() no se conecta con nada; 'contains' se ignora."""
    g = _graph(
        nodes=[
            _node("afile", "a.py"),
            _node("foo", "foo()"),
            _node("bar", "bar()"),
            _node("dead", "dead()"),
        ],
        links=[
            _link("afile", "foo", "contains"),   # estructural → ignorado
            _link("foo", "bar", "calls"),         # foo consume bar
        ],
    )
    out = derive_internal_graph(g)
    # dead(): sin aristas de código y no es archivo → huérfano (código muerto)
    assert "dead" in out["orphans"]
    assert "bar" not in out["orphans"] and "foo" not in out["orphans"]
    # foo: sin entrada, con salida → entry point
    assert "foo" in out["entry_points"]
    # bar es consumido por foo
    assert out["consumers_of"]["bar"] == ["foo"]
    assert out["dependencies_of"]["foo"] == ["bar"]
    # sin god-nodes con grado < umbral
    assert out["god_nodes"] == []


def test_god_node_by_degree():
    """Un nodo con muchas aristas de código entra en god_nodes."""
    hub = "hub"
    nodes = [_node(hub, "hub()")] + [_node(f"c{i}", f"c{i}()") for i in range(9)]
    links = [_link(f"c{i}", hub, "calls") for i in range(9)]  # 9 inbound a hub
    out = derive_internal_graph(_graph(nodes, links))
    assert hub in out["god_nodes"]


def test_ignores_non_code_relations_for_degree():
    """rationale_for/contains NO cuentan como grado de código."""
    g = _graph(
        nodes=[_node("x", "x()"), _node("r", "doc")],
        links=[_link("x", "r", "rationale_for")],
    )
    out = derive_internal_graph(g)
    # x solo tiene una arista rationale_for → grado de código 0 → huérfano
    assert "x" in out["orphans"]


def test_derives_path_index_for_file_nodes():
    """El índice de rutas debe resolver el nodo archivo para el blast CLI."""
    out = derive_internal_graph(
        _graph(
            nodes=[_node("file_node", "scripts/mod.py"), _node("fn", "fn()")],
            links=[],
        )
    )
    assert out["path_index"]["scripts/mod.py"] == "file_node"


def test_build_uses_staging_and_writes_distinct_artifact(tmp_path):
    """Orquestación: copia targets a staging, invoca el extractor inyectado,
    normaliza y escribe internal_graph.json (nombre DISTINTO de Capa 2 graph.json).
    El staging se limpia; el repo nunca ve graphify-out/."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "mod.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    captured = {}

    def _inline_runner(stage_dir: Path) -> Path:
        # Verifica que el target fue copiado al staging (no se tocó el repo real)
        captured["copied"] = (stage_dir / "scripts" / "mod.py").is_file()
        gout = stage_dir / "graphify-out"
        gout.mkdir(parents=True, exist_ok=True)
        gj = gout / "graph.json"
        gj.write_text(json.dumps({
            "nodes": [
                {"id": "foo", "label": "foo()", "file_type": "code"},
                {"id": "dead", "label": "dead()", "file_type": "code"},
            ],
            "links": [],
        }), encoding="utf-8")
        return gj

    out_path = repo / ".protocol" / "metadata" / "internal_graph.json"
    result = build_internal_graph(
        repo, targets=("scripts",), out_path=out_path, runner=_inline_runner
    )

    assert captured["copied"] is True
    assert result == out_path and out_path.is_file()
    # Nombre deconflictado de Capa 2
    assert out_path.name == "internal_graph.json" and out_path.name != "graph.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert "dead" in data["orphans"]
    # El repo no quedó con artefactos crudos del motor
    assert not (repo / "graphify-out").exists()
    assert not (repo / "scripts" / "graphify-out").exists()
