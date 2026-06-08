#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""blast_radius.py — cálculo de blast radius sobre Capa 1 ya normalizada.

`compute_blast()` es pura: consume el dict de `.protocol/metadata/internal_graph.json`
y devuelve impacto inverso, fan-in/fan-out, ciclo y severidad sin reparsear AST.
"""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from collections import deque
from datetime import datetime
from pathlib import Path


def _norm_target(target: str) -> str:
    return target.replace("\\", "/").strip()


def _resolve_target(internal_graph: dict, target: str) -> tuple[str, str]:
    norm = _norm_target(target)
    path_index = internal_graph.get("path_index") or {}
    if norm in path_index:
        return norm, path_index[norm]
    if norm.lower() in path_index:
        return norm.lower(), path_index[norm.lower()]
    return norm, norm


def _severity(count: int) -> str:
    if count == 0:
        return "local"
    if count <= 3:
        return "medio"
    if count <= 8:
        return "alto"
    return "sistémico"


def compute_blast(internal_graph: dict, target: str) -> dict:
    """Calcula el blast radius de un target ya indexado en internal_graph."""
    consumers_of = internal_graph.get("consumers_of") or {}
    dependencies_of = internal_graph.get("dependencies_of") or {}
    target_key, resolved_target = _resolve_target(internal_graph, target)

    direct = sorted(set(consumers_of.get(resolved_target, [])))
    transitive: list[str] = []
    visited: set[str] = set()
    queue = deque(direct)
    in_cycle = False

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        transitive.append(current)
        for nxt in consumers_of.get(current, []):
            if nxt == resolved_target:
                in_cycle = True
                continue
            if nxt not in visited:
                queue.append(nxt)

    fan_in = len(direct)
    fan_out = len(set(dependencies_of.get(resolved_target, [])))
    transitive = sorted(set(transitive))
    return {
        "target": target,
        "resolved_target": resolved_target,
        "direct": direct,
        "transitive": transitive,
        "transitive_count": len(transitive),
        "fan_in": fan_in,
        "fan_out": fan_out,
        "in_cycle": in_cycle,
        "severity": _severity(len(transitive)),
    }


def _latest_source_mtime(repo_root: Path) -> float:
    latest = 0.0
    for folder in ("scripts", "protocol_engine"):
        root = repo_root / folder
        if not root.is_dir():
            continue
        for py_file in root.rglob("*.py"):
            try:
                latest = max(latest, py_file.stat().st_mtime)
            except OSError as exc:
                logging.getLogger(__name__).debug("mtime unreadable for %s: %s", py_file, exc)
    return latest


def _read_internal_graph(out_path: Path) -> dict | None:
    try:
        return json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _generated_timestamp(payload: dict | None) -> float:
    generated = (payload or {}).get("generated", "")
    if not isinstance(generated, str):
        return 0.0
    try:
        return datetime.fromisoformat(generated).timestamp()
    except ValueError:
        return 0.0


def load_internal_graph(repo_root: Path | None = None) -> dict:
    repo_root = Path(repo_root or Path(__file__).resolve().parent.parent)
    out_path = repo_root / ".protocol" / "metadata" / "internal_graph.json"
    payload = _read_internal_graph(out_path) if out_path.exists() else None
    if payload and _generated_timestamp(payload) >= _latest_source_mtime(repo_root):
        return payload
    subprocess.run(
        [sys.executable, "scripts/internal_graph.py"],
        cwd=str(repo_root),
        check=True,
    )
    return _read_internal_graph(out_path) or {}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or "--help" in argv or "-h" in argv:
        print("Usage: python scripts/blast_radius.py <target> [--json]")
        if not argv:
            return 2
        return 0
    if not argv:
        print("Usage: python scripts/blast_radius.py <target> [--json]")
        return 2
    json_mode = "--json" in argv
    argv = [arg for arg in argv if arg != "--json"]
    if not argv:
        print("usage: python scripts/blast_radius.py <target> [--json]")
        return 2
    internal_graph = load_internal_graph()
    result = compute_blast(internal_graph, argv[0])
    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            f"[BLAST] {result['resolved_target']} -> {result['severity']} "
            f"(direct={result['fan_in']}, transitive={result['transitive_count']}, "
            f"cycle={result['in_cycle']})"
        )
        if result["direct"]:
            print(f"  direct consumers: {', '.join(result['direct'])}")
        if result["transitive"]:
            print(f"  transitive impact: {', '.join(result['transitive'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
