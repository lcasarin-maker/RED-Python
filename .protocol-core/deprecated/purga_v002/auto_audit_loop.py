#!/usr/bin/env python3
"""auto_audit_loop.py — Retry-until-pass audit loop for Cerberus.

Runs audit_10d.py repeatedly, calling protocol_cli doctor --fix on each failure,
stopping only when the audit exits clean (code 0) or MAX_ATTEMPTS is reached.

Usage:
    python scripts/auto_audit_loop.py [--max N] [--audit-cmd CMD]
"""
import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

import os
os.sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.core_utils import setup_windows_utf8
from scripts.token_manager import OutputCompressor
setup_windows_utf8()

_logger = logging.getLogger("auto_audit_loop")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_AUDIT = [sys.executable, "scripts/audit_10d.py"]
_DEFAULT_DOCTOR = [sys.executable, "scripts/protocol_cli.py", "doctor", "--fix"]


def run_audit_loop(max_attempts: int = 100,
                   audit_cmd: list[str] | None = None,
                   doctor_cmd: list[str] | None = None) -> int:
    """Retry audit until clean pass or max_attempts exhausted.

    Returns 0 on clean pass, 1 on max attempts reached.
    """
    audit_cmd = audit_cmd or _DEFAULT_AUDIT
    doctor_cmd = doctor_cmd or _DEFAULT_DOCTOR

    for attempt in range(1, max_attempts + 1):
        _logger.info("=== Audit attempt %d/%d ===", attempt, max_attempts)
        try:
            result = subprocess.run(
                audit_cmd, cwd=str(_PROJECT_ROOT),
                capture_output=True, text=True, timeout=120
            )
        except Exception as e:
            _logger.error("audit_cmd failed: %s", e)
            return 1

        print(result.stdout)
        if result.returncode == 0:
            _logger.info("Audit passed — no further action required.")
            return 0

        _logger.warning("Audit failed — attempting automatic fix (attempt %d).", attempt)
        try:
            doc_res = subprocess.run(
                doctor_cmd, cwd=str(_PROJECT_ROOT),
                capture_output=True, text=True, timeout=60
            )
            print(doc_res.stdout)
            if doc_res.stderr:
                _logger.debug("Doctor stderr: %s", doc_res.stderr)
        except Exception as e:
            _logger.error("doctor_cmd failed: %s", e)

        time.sleep(1)

    _logger.error("Maximum attempts (%d) reached without a clean audit. Manual intervention required.", max_attempts)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Retry-until-pass audit loop for Cerberus.")
    parser.add_argument("--max", type=int, default=100, help="Maximum retry attempts (default: 100)")
    args = parser.parse_args()
    return run_audit_loop(max_attempts=args.max)


if __name__ == "__main__":
    sys.exit(main())
