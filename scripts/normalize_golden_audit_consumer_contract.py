#!/usr/bin/env python3
"""Normalize GS audit metadata for Cerberus consumer contracts.

The Golden Standard can name downstream checks that do not physically exist in
Cerberus. Keeping those names as validating mechanisms creates theater: tests
can pass by finding string literals instead of executable validators.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AUDIT_JSON = ROOT / ".protocol" / "metadata" / "golden_standard_audit.json"


def _real_python_defs() -> str:
    chunks: list[str] = []
    for base in (ROOT / "tests", ROOT / "scripts"):
        for path in base.rglob("*.py"):
            if path.name == "generate_golden_audit.py":
                continue
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def main() -> int:
    db = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    real_defs = _real_python_defs()
    normalized = 0

    for entry in db.values():
        mechanism = str(entry.get("validating_mechanism", "")).strip()
        if not mechanism or mechanism == "DOC_ONLY":
            continue
        if f"def {mechanism}" in real_defs:
            continue

        entry["status"] = "DOC_ONLY"
        entry["validating_mechanism"] = "DOC_ONLY"
        entry.setdefault("downstream_verification", "required")
        entry["action"] = (
            "Consumer-contract rule from Golden Standard: Cerberus does not "
            "currently have a physical generic validator for this ID, so it is "
            "preserved honestly as DOC_ONLY with downstream verification instead "
            "of a circular fallback mechanism."
        )
        normalized += 1

    AUDIT_JSON.write_text(
        json.dumps(db, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"normalized={normalized}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
