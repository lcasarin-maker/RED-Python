#!/usr/bin/env python3
"""
permission_auditor.py v1.0 - Agent permission configuration auditor.

Fails when Claude/Gemini/Codex local configuration grants broad shell, Python,
Git destructive, or global-sync apply permissions outside protocol_cli controls.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core_utils import setup_windows_utf8

setup_windows_utf8()
logger = logging.getLogger("permission_auditor")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


DANGEROUS_PATTERNS = {
    "Bash(python)": "generic Python execution bypasses protocol_cli",
    "Bash(python *)": "generic Python wildcard execution bypasses protocol_cli",
    "Bash(python -c": "inline Python can execute arbitrary code",
    "Bash(powershell -Command": "broad PowerShell command execution is unsafe",
    "Bash(git reset": "git reset can discard or rewrite work",
    "Bash(git rm": "git rm is destructive without protocol review",
    "Bash(git clean": "git clean can delete untracked work",
    "Bash(git revert": "git revert alters history dynamically and is forbidden under Mandato S21",
    "Bash(git push --force": "force push can overwrite remote history",
    "Bash(python scripts/global_sync_safe.py)": "global sync apply must require explicit --apply review",
    "Bash(python scripts/global_sync_safe.py --apply": "global sync apply is not allowed in agent settings",
    "Bash(python scripts/global_sync_v5.py": "legacy sync entrypoint must not be granted directly",
}

REQUIRED_SAFE_PERMISSIONS = {
    "Bash(python scripts/protocol_cli.py check)",
    "Bash(python scripts/protocol_cli.py sync --dry-run)",
    "Bash(python scripts/run_security_audit_12d.py)",
}


def _load_permissions(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc

    allow = data.get("permissions", {}).get("allow", [])
    if not isinstance(allow, list):
        raise ValueError(f"{path}: permissions.allow must be a list")
    return [str(item) for item in allow]


def audit_permission_file(path: Path, require_safe_baseline: bool = False) -> list[str]:
    """Return audit findings for a Claude settings file."""
    findings: list[str] = []
    permissions = _load_permissions(path)

    for permission in permissions:
        for pattern, reason in DANGEROUS_PATTERNS.items():
            if permission.startswith(pattern) or permission == pattern:
                findings.append(
                    f"{path}: forbidden permission {permission!r} ({reason})"
                )

    if require_safe_baseline:
        missing = sorted(REQUIRED_SAFE_PERMISSIONS.difference(permissions))
        for permission in missing:
            findings.append(f"{path}: missing required safe permission {permission!r}")

    return findings


def candidate_files(root: Path) -> list[tuple[Path, bool]]:
    """Return settings files to audit with whether each must contain baseline permissions."""
    return [
        (root / ".claude" / "settings.template.json", True),
        (root / ".claude" / "settings.local.json", False),
    ]


def run(root: Path) -> bool:
    """Audit known permission files under root."""
    all_findings: list[str] = []
    audited = 0
    candidate_exists = False

    for path, require_baseline in candidate_files(root):
        if not path.exists():
            continue
        candidate_exists = True
        audited += 1
        all_findings.extend(
            audit_permission_file(path, require_safe_baseline=require_baseline)
        )

    if not candidate_exists:
        logger.info("Permission audit skipped (no permission config files found)")
        return True

    if all_findings:
        logger.error("Permission audit failed:")
        for finding in all_findings:
            logger.error("  - %s", finding)
        return False

    logger.info("Permission audit passed (%s file(s) checked)", audited)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit agent permission settings")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--path",
        type=Path,
        action="append",
        default=[],
        help="Specific settings file to audit",
    )
    args = parser.parse_args()

    if args.path:
        findings = []
        for path in args.path:
            findings.extend(audit_permission_file(path, require_safe_baseline=False))
        if findings:
            for finding in findings:
                logger.error(finding)
            return 1
        logger.info("Permission audit passed (%s file(s) checked)", len(args.path))
        return 0

    return 0 if run(args.root) else 1


if __name__ == "__main__":
    sys.exit(main())
