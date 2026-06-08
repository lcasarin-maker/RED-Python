#!/usr/bin/env python3
"""
evidence_logger.py v1.0 — PHASE 3 Formal Evidence Logging

Logs all protocol operations with timestamp, command, output, files touched, and result.
Every operation generates JSON evidence for audit trail and reversal cost accounting.
"""

import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))
from core_utils import setup_windows_utf8

setup_windows_utf8()
logger = logging.getLogger("evidence_logger")


def _latest_git_commit_epoch(root: Path) -> float | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(root),
        )
        if result.returncode != 0:
            return None
        raw = result.stdout.strip()
        return float(raw) if raw else None
    except Exception as e:
        logger.debug("_latest_git_commit_epoch failed for %s: %s", root, e)
        return None


def _parse_iso_epoch(value: str | None) -> float | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


class EvidenceLogger:
    """Centralized evidence logging for all protocol operations."""

    def __init__(self, root: Path = None):
        self.root = root or Path.cwd()
        self.evidence_dir = self.root / ".protocol" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def log_operation(
        self,
        operation: str,
        agent_name: str,
        command: str,
        outcome: str,
        files_touched: list = None,
        validation_domains: dict = None,
        output_log: str = None,
        human_approval_required: bool = False,
    ) -> str:
        """
        Log a protocol operation with empirical evidence.

        Args:
            operation: Type of operation (sync, audit, commit, promote, etc.)
            agent_name: Agent executing the operation (Claude, Gemini, etc.)
            command: Command executed
            outcome: Result (success, failure, blocked)
            files_touched: List of files modified/created/deleted
            validation_domains: Dict of domain validations {D1: True, D2: False, ...}
            output_log: Terminal output or logs from the operation
            human_approval_required: Whether human approval is needed for next step

        Returns:
            Path to evidence JSON file
        """
        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.isoformat()

        evidence = {
            "timestamp": timestamp_str,
            "operation": operation,
            "agent_name": agent_name,
            "command": command,
            "outcome": outcome,
            "files_touched": files_touched or [],
            "validation_domains": validation_domains or {},
            "human_approval_required": human_approval_required,
            "output_log": output_log or "",
        }

        # Generate filename with timestamp and operation type
        filename = (
            f"{now_utc.strftime('%Y%m%d_%H%M%S_%f')}_{operation}_{uuid4().hex[:8]}.json"
        )
        evidence_path = self.evidence_dir / filename

        try:
            with open(evidence_path, "w", encoding="utf-8") as f:
                json.dump(evidence, f, indent=2, ensure_ascii=False)
            logger.info(f"📋 Evidence logged: {filename}")
            return str(evidence_path)
        except Exception as e:
            logger.error(f"Failed to log evidence: {e}")
            raise

    def retrieve_evidence(self, operation: str = None, last_n: int = 5) -> list:
        """
        Retrieve operation evidence logs.

        Args:
            operation: Filter by operation type (optional)
            last_n: Return last N operations (default 5)

        Returns:
            List of evidence dictionaries
        """
        if not self.evidence_dir.exists():
            logger.warning("No evidence directory found")
            return []

        evidence_files = sorted(self.evidence_dir.glob("*.json"), reverse=True)

        evidence_list = []
        for evidence_file in evidence_files[:last_n]:
            try:
                with open(evidence_file, "r", encoding="utf-8") as f:
                    evidence = json.load(f)
                    if operation is None or evidence.get("operation") == operation:
                        evidence_list.append(evidence)
            except Exception as e:
                logger.warning(f"Failed to read {evidence_file}: {e}")

        return evidence_list

    def validate_operation_approved(self, operation_type: str) -> bool:
        """
        Check if operation has empirical proof from human validation (D3).

        Args:
            operation_type: Type of operation to validate

        Returns:
            True if evidence exists and D3 validation passed
        """
        evidence_list = self.retrieve_evidence(operation=operation_type, last_n=1)

        if not evidence_list:
            logger.warning(f"No evidence found for operation: {operation_type}")
            return False

        latest = evidence_list[0]
        d3_domains = latest.get("validation_domains", {})
        latest_ts = _parse_iso_epoch(latest.get("timestamp"))
        min_epoch = _latest_git_commit_epoch(Path.cwd())
        if min_epoch is not None and latest_ts is None:
            logger.warning("⚠️  Operation evidence lacks timestamp")
            return False
        if min_epoch is not None and latest_ts is not None and latest_ts < min_epoch:
            logger.warning("⚠️  Operation evidence is stale")
            return False

        if d3_domains.get("D3", False):
            logger.info("✅ Operation approved: human validation in evidence")
            return True

        if latest.get("human_approval_required"):
            logger.warning("⚠️  Operation requires human approval")
            return False

        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: evidence_logger.py <operation> [--retrieve]")
        print("  evidence_logger.py audit --retrieve")
        sys.exit(1)

    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    el = EvidenceLogger()

    if sys.argv[-1] == "--retrieve":
        operation = sys.argv[1]
        evidence = el.retrieve_evidence(operation=operation)
        print(json.dumps(evidence, indent=2))
    else:
        logger.info("EvidenceLogger initialized")
