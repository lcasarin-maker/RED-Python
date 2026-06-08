#!/usr/bin/env python3
"""Review queue — rastrea commits que tocan tests/ o scripts/ para revision humana.
Escribe en .protocol/review_queue.json. Invocable como modulo o CLI (--enqueue / --list / --ack).
"""
import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

QUEUE_FILE = Path(__file__).parents[1] / ".protocol" / "review_queue.json"


def _load() -> list:
    if not QUEUE_FILE.exists():
        return []
    try:
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list) -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(
        json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def enqueue() -> None:
    """Agrega el HEAD commit actual a la cola si toca tests/ o scripts/."""
    commit_hash = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], text=True
    ).strip()
    changed = (
        subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"],
            text=True,
        )
        .strip()
        .splitlines()
    )
    relevant = [f for f in changed if f.startswith(("tests/", "scripts/"))]
    if not relevant:
        return
    items = _load()
    hashes = {i["commit"] for i in items}
    if commit_hash in hashes:
        return
    items.append(
        {
            "commit": commit_hash,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "files": relevant,
            "verified": False,
        }
    )
    _save(items)
    print(f"[ReviewQueue] {commit_hash} encolado ({len(relevant)} archivos).")


def list_pending() -> list:
    return [i for i in _load() if not i.get("verified")]


def acknowledge(commit_hash: str) -> None:
    items = _load()
    for item in items:
        if item["commit"].startswith(commit_hash):
            item["verified"] = True
            item["verified_at"] = datetime.now().isoformat(timespec="seconds")
    _save(items)
    print(f"[ReviewQueue] {commit_hash} marcado como verificado.")


def _print_pending() -> None:
    pending = list_pending()
    if pending:
        print(f"[ReviewQueue] {len(pending)} commits pendientes de revision:")
        for p in pending:
            print(f"  {p['commit']} ({p['timestamp']}) — {', '.join(p['files'])}")
    else:
        print("[ReviewQueue] Sin pendientes.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "--list"
    if cmd == "--enqueue":
        enqueue()
    elif cmd == "--ack" and len(sys.argv) > 2:
        acknowledge(sys.argv[2])
    else:
        _print_pending()
