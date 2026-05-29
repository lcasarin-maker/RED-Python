#!/usr/bin/env python3
"""
audit_6d_expanded.py v1.2 — PHASE 2/3 Silent Failure Enforcement

Implements 6-domain audit (Code Structure, Functionality, Human Validation,
Security & I/O, State Integrity, Workspace Cleanup).
Returns exit 0 only if ALL required domains pass.
D6 is read-only; repair belongs in --fix mode via hygiene_auditor.
"""

import argparse
import json
import logging
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

# Bootstrap sys.path so scripts.* imports work regardless of invocation method
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8
from scripts.chunking_validator import validate_chunks
from scripts.empirical_proof_checker import changed_files, has_human_validation, ui_files
from scripts.hygiene_auditor import (
    deprecate_legacy_scripts,
    find_hygiene_findings,
    repair_mojibake,
)
from scripts.permission_auditor import run as run_permission_audit

setup_windows_utf8()
logger = logging.getLogger("audit_6d_expanded")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

_SECRET_PATTERN = re.compile(
    r'(?:password|api_key|secret|token)\s*=\s*["\']([A-Za-z0-9+/=\-_]{20,})["\']',
    re.IGNORECASE,
)


class SilentFailureEnforcer:
    """Orchestrates 6-domain validation to prevent silent failures."""

    def __init__(self, fix: bool = True):
        self.root = Path.cwd()
        self.failures: dict[str, str] = {}
        self.fix = fix

    # ── Workspace repair ──────────────────────────────────────────────────────

    def auto_fix_workspace_hygiene(self) -> None:
        """Repair D6 hygiene issues before the read-only domains run."""
        repaired = repair_mojibake(self.root)
        deprecated = deprecate_legacy_scripts(self.root)
        cleaned = self.cleanup_workspace_artifacts()
        logger.info(
            "D6 auto-fix: repaired=%s deprecated=%s cleaned=%s",
            len(repaired),
            len(deprecated),
            len(cleaned),
        )

    def cleanup_workspace_artifacts(self) -> list[Path]:
        """Remove generated workspace artifacts that may be recreated by tests."""
        def _remove_readonly(func, path, _exc_info):
            Path(path).chmod(stat.S_IWRITE)
            func(path)

        candidates: list[Path] = []
        for pattern in ["**/__pycache__", "**/*.pyc", "**/.pytest_cache", "**/.coverage*"]:
            candidates.extend(
                p for p in self.root.glob(pattern)
                if ".git" not in p.parts and ".secrets" not in p.parts
            )
        cleaned: list[Path] = []
        for artifact in sorted(set(candidates), key=lambda p: len(p.parts), reverse=True):
            if not artifact.exists():
                continue
            try:
                if artifact.is_dir():
                    shutil.rmtree(artifact, onerror=_remove_readonly)
                else:
                    artifact.chmod(stat.S_IWRITE)
                    artifact.unlink()
                cleaned.append(artifact)
            except Exception as e:
                logger.warning("cleanup_workspace_artifacts: could not remove %s: %s", artifact, e)
        return cleaned

    # ── Domain audits ─────────────────────────────────────────────────────────

    def audit_domain_1_code_structure(self) -> bool:
        """D1: Code Structure — no warnings, type safety, whitelist, version parity."""
        logger.info("D1: Code Structure validation...")
        try:
            result = subprocess.run(
                [sys.executable, "scripts/audit_10d.py"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                logger.info("  D1 PASSED")
                return True
            self.failures["D1"] = "audit_10d.py failed"
            logger.error("  D1 FAILED: %s", result.stderr[:200])
            return False
        except Exception as e:
            self.failures["D1"] = str(e)
            logger.error("  D1 ERROR: %s", e)
            return False

    def audit_domain_2_functionality(self) -> bool:
        """D2: Functionality — unit tests pass, no silent errors."""
        logger.info("D2: Functionality validation...")
        tests_dir = self.root / "tests"

        if not tests_dir.exists():
            self.failures["D2"] = "tests/ directory missing"
            logger.error("  D2 FAILED: tests/ not found")
            return False

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=120,
                cwd=str(self.root),
            )
            if result.returncode != 0:
                self.failures["D2"] = "pytest suite failed"
                logger.error("  D2 FAILED: tests did not pass")
                return False
            logger.info("  D2 PASSED")
            return True
        except Exception as e:
            self.failures["D2"] = str(e)
            logger.error("  D2 ERROR: %s", str(e)[:120])
            return False

    def audit_domain_3_human_validation(self) -> bool:
        """D3: Human Validation — required when changed files touch UI surfaces."""
        logger.info("D3: Human Validation...")
        changed = changed_files(self.root)
        changed_ui = ui_files(changed)
        if not changed_ui:
            logger.info("  D3 PASSED (no UI-facing changed files)")
            return True
        if has_human_validation(changed_ui, evidence_dir=self.root / ".protocol" / "evidence"):
            logger.info("  D3 PASSED (human/browser evidence verified)")
            return True
        self.failures["D3"] = "UI files changed without tied human/browser evidence: " + ", ".join(changed_ui)
        logger.error("  D3 FAILED: %s", self.failures["D3"])
        return False

    def audit_domain_4_security_io(self) -> bool:
        """D4: Security & I/O — no secrets, permission audit clean."""
        logger.info("D4: Security & I/O validation...")
        found_secrets: list[tuple[str, int]] = []

        for py_file in self.root.glob("**/*.py"):
            if "test" in py_file.parts or ".venv" in py_file.parts or "deprecated" in py_file.parts:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                matches = _SECRET_PATTERN.findall(content)
                if matches:
                    found_secrets.append((str(py_file), len(matches)))
            except Exception as e:
                logger.debug("audit_domain_4: error scanning %s: %s", py_file, e)

        if found_secrets:
            self.failures["D4"] = f"Found {len(found_secrets)} hardcoded secret(s)"
            logger.error("  D4 FAILED: Hardcoded secrets detected")
            return False

        if not run_permission_audit(self.root):
            self.failures["D4"] = "Dangerous agent permissions detected"
            logger.error("  D4 FAILED: permission audit failed")
            return False

        logger.info("  D4 PASSED")
        return True

    def audit_domain_5_state_integrity(self) -> bool:
        """D5: State Integrity — critical files present, chunks valid."""
        logger.info("D5: State Integrity validation...")
        critical_files = [
            self.root / "AGENT.md",
            self.root / "SPEC.md",
            self.root / ".agent_state.json",
            self.root / "PROTOCOL_SYSTEM.md",
            self.root / "PROTOCOL_BEHAVIOR.md",
        ]

        for fpath in critical_files:
            if not fpath.exists():
                self.failures["D5"] = f"Missing: {fpath.name}"
                logger.error("  D5 FAILED: %s missing", fpath.name)
                return False
            if fpath.stat().st_size == 0:
                self.failures["D5"] = f"Empty: {fpath.name}"
                logger.error("  D5 FAILED: %s is empty", fpath.name)
                return False

        try:
            with open(self.root / ".agent_state.json", encoding="utf-8") as fh:
                state = json.load(fh)
            if "version" not in state:
                self.failures["D5"] = "Missing 'version' in .agent_state.json"
                logger.error("  D5 FAILED: Invalid state structure")
                return False
        except Exception as e:
            self.failures["D5"] = str(e)
            logger.error("  D5 FAILED: %s", e)
            return False

        for rel in changed_files(self.root):
            path = self.root / rel
            if path.is_file() and not validate_chunks(path):
                self.failures["D5"] = f"Chunk validation failed: {rel}"
                logger.error("  D5 FAILED: %s", rel)
                return False

        logger.info("  D5 PASSED")
        return True

    def audit_domain_6_workspace_cleanup(self) -> bool:
        """D6: Workspace Hygiene — read-only artifact and encoding detection."""
        logger.info("D6: Workspace Hygiene (read-only)...")
        try:
            if self.fix:
                cleaned = self.cleanup_workspace_artifacts()
                if cleaned:
                    logger.info("  D6 auto-cleaned %s artifact(s)", len(cleaned))

            artifacts: list[Path] = []
            for pattern in ["**/__pycache__", "**/*.pyc", "**/.pytest_cache", "**/.coverage*"]:
                artifacts.extend(
                    p for p in self.root.glob(pattern) if ".git" not in p.parts
                )
            if artifacts:
                self.failures["D6"] = f"{len(artifacts)} cleanup artifact(s) present"
                logger.error("  D6 FAILED: %s", self.failures["D6"])
                return False

            hygiene_findings = find_hygiene_findings(self.root)
            if hygiene_findings:
                first = hygiene_findings[0]
                self.failures["D6"] = (
                    f"{len(hygiene_findings)} hygiene finding(s); first: "
                    f"{first.kind} at {first.path}:{first.line}"
                )
                logger.error("  D6 FAILED: %s", self.failures["D6"])
                return False

            logger.info("  D6 PASSED")
            return True
        except Exception as e:
            self.failures["D6"] = str(e)
            logger.error("  D6 FAILED: %s", e)
            return False

    # ── Orchestration ─────────────────────────────────────────────────────────

    def run(self) -> int:
        """Execute all 6 domains. Return 0 only if ALL pass."""
        logger.info("=" * 70)
        logger.info("PHASE 2/3: SILENT FAILURE ENFORCEMENT (6-Domain Audit)")
        logger.info("=" * 70)

        if self.fix:
            self.auto_fix_workspace_hygiene()

        results: dict[str, bool] = {
            "D1 Code Structure":    self.audit_domain_1_code_structure(),
            "D2 Functionality":     self.audit_domain_2_functionality(),
            "D3 Human Validation":  self.audit_domain_3_human_validation(),
            "D4 Security & I/O":    self.audit_domain_4_security_io(),
            "D5 State Integrity":   self.audit_domain_5_state_integrity(),
            "D6 Workspace Cleanup": self.audit_domain_6_workspace_cleanup(),
        }

        logger.info("=" * 70)
        passed = sum(results.values())
        total = len(results)
        logger.info("RESULTS: %s/%s domains passed", passed, total)

        if all(results.values()):
            logger.info("VERDICT: APPROVED (Silent failure prevented)")
            return 0

        logger.error("VERDICT: REJECTED (Failed domains detected)")
        for domain, ok in results.items():
            status = "PASS" if ok else "FAIL"
            logger.error("  [%s] %s", status, domain)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run expanded 6-domain silent-failure audit")
    parser.add_argument(
        "--fix", action="store_true", default=True,
        help="Repair supported D6 hygiene issues before auditing (default: enabled)",
    )
    parser.add_argument(
        "--no-fix", action="store_true",
        help="Disable D6 auto-repair (read-only mode)",
    )
    args = parser.parse_args()
    fix_mode = not args.no_fix
    return SilentFailureEnforcer(fix=fix_mode).run()


if __name__ == "__main__":
    sys.exit(main())
