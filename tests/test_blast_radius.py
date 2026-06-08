#!/usr/bin/env python3
"""Tests falsables para blast radius sobre internal_graph ya normalizado."""
from scripts.blast_radius import compute_blast


def _graph(consumers_of, dependencies_of=None, path_index=None):
    return {
        "consumers_of": consumers_of,
        "dependencies_of": dependencies_of or {},
        "path_index": path_index or {},
    }


def test_cycle_detection_marks_in_cycle():
    graph = _graph(
        {
            "A": ["B"],
            "B": ["A"],
        },
        {
            "A": ["B"],
            "B": ["A"],
        },
    )
    out = compute_blast(graph, "A")
    assert out["direct"] == ["B"]
    assert out["in_cycle"] is True


def test_god_node_becomes_systemic():
    consumers = {"hub": [f"c{i}" for i in range(9)]}
    graph = _graph(
        consumers,
        {"hub": []},
    )
    out = compute_blast(graph, "hub")
    assert out["transitive_count"] == 9
    assert out["severity"] == "sistémico"


def test_leaf_without_consumers_is_local():
    out = compute_blast(_graph({}, {}), "leaf")
    assert out["direct"] == []
    assert out["transitive"] == []
    assert out["severity"] == "local"


def test_transitive_closure_is_not_underestimated():
    graph = _graph(
        {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        },
        {
            "A": [],
            "B": ["A"],
            "C": ["B"],
        },
    )
    out = compute_blast(graph, "A")
    assert out["transitive_count"] == 2
    assert out["transitive"] == ["B", "C"]
