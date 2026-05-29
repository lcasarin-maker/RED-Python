# cerberus/close_pending.py
"""
Utility to close a pending task.

Usage:
    python -m cerberus.close_pending <task_id>
"""

import json
import pathlib
import sys
import tempfile

def close_task(task_id: str) -> None:
    pending_path = pathlib.Path(__file__).parent / "pending_tasks.json"
    try:
        tasks = json.loads(pending_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        tasks = []

    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = "closed"
            break
    else:
        print(f"[close_pending] Task {task_id} not found.")
        sys.exit(1)

    # Atomic write: write to temp file then rename — prevents corruption on crash (P6.7).
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=pending_path.parent, prefix=".close_pending_", suffix=".tmp"
    )
    try:
        with open(tmp_fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(tasks, indent=2))
        pathlib.Path(tmp_path).replace(pending_path)
    except Exception:
        pathlib.Path(tmp_path).unlink(missing_ok=True)
        raise
    print(f"[close_pending] Task {task_id} marked as closed.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m cerberus.close_pending <task_id>")
        sys.exit(1)
    close_task(sys.argv[1])
