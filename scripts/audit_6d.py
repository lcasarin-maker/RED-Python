#!/usr/bin/env python3
"""Current 6D audit entrypoint for RED-Python.

This auditor checks the active contract of the repository:
README, version/state parity, module importability, and the focused
test suite that represents supported behavior.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "00 audit"
AUDIT_CONTRACT = AUDIT_DIR / "02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md"
REQUIRED_FILES = [
    "README.md",
    "PLAN.md",
    "VALIDACIONES.md",
    "VERSION.txt",
    ".agent_state.json",
    "red.py",
    "app.py",
    "core.py",
    "config.py",
    "filters.py",
]


def _version_base() -> str:
    version = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
    return ".".join(version.lstrip("v").split(".")[:2])


def _required_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).exists()]
    if missing:
        print(f"[FAIL] missing required files: {', '.join(missing)}")
        print("REJECTED")
        return 1

    audit_missing = [
        str(path.relative_to(ROOT))
        for path in (AUDIT_DIR / "README.md", AUDIT_CONTRACT)
        if not path.exists()
    ]
    if audit_missing:
        print(f"[FAIL] missing audit contract files: {', '.join(audit_missing)}")
        print("REJECTED")
        return 1

    base_version = _version_base()
    import json

    state = json.loads(_required_text(ROOT / ".agent_state.json"))
    if state.get("version") != base_version:
        print(f"[FAIL] .agent_state.json version mismatch: {state.get('version')} != {base_version}")
        print("REJECTED")
        return 1

    readme = _required_text(ROOT / "README.md")
    plan = _required_text(ROOT / "PLAN.md")
    validaciones = _required_text(ROOT / "VALIDACIONES.md")
    if "RED-Python" not in readme:
        print("[FAIL] README.md missing product contract text")
        print("REJECTED")
        return 1
    if "00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md" not in readme:
        print("[FAIL] README.md missing external audit contract reference")
        print("REJECTED")
        return 1
    if f"v{base_version}" not in plan:
        print("[FAIL] PLAN.md missing version marker")
        print("REJECTED")
        return 1
    if "00 audit" not in plan:
        print("[FAIL] PLAN.md missing audit contract reference")
        print("REJECTED")
        return 1
    if "REGLA #15" not in validaciones:
        print("[FAIL] VALIDACIONES.md missing validation rule reference")
        print("REJECTED")
        return 1

    audit_contract = _required_text(AUDIT_CONTRACT)
    audit_contract_lower = audit_contract.lower()
    if "external audit" not in audit_contract_lower and "auditoria exterior" not in audit_contract_lower:
        print("[FAIL] 00 audit contract missing external audit instruction")
        print("REJECTED")
        return 1
    if "phase 0" not in audit_contract_lower and "fase 0" not in audit_contract_lower:
        print("[FAIL] 00 audit contract missing phase 0")
        print("REJECTED")
        return 1
    if "phase 6" not in audit_contract_lower and "fase 6" not in audit_contract_lower:
        print("[FAIL] 00 audit contract missing phase 6")
        print("REJECTED")
        return 1

    for module_name in ("red.py", "app.py", "core.py", "config.py", "filters.py"):
        try:
            compile(_required_text(ROOT / module_name), str(ROOT / module_name), "exec")
        except SyntaxError as exc:
            print(f"[FAIL] syntax error in {module_name}: {exc}")
            print("REJECTED")
            return 1

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_main.py", "tests/test_functional.py", "tests/test_gui_smoke.py", "tests/test_main_cli.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        print("[FAIL] focused test suite failed")
        print("REJECTED")
        return 1

    print("VERDICT FINAL: APPROVED")
    print("APPROVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
