#!/usr/bin/env python3
"""validate_state_checkpoint.py — REGLA #19: SHA256 checkpoint validation.

Validates that HISTORIAL.md checkpoints have correct format:
SHA256 hash, timestamp, agent, files_count.

Usage:
    python scripts/validate_state_checkpoint.py [--validate] [--export FILE]

Promoted from deprecated/scripts/validate_state_checkpoint.py.
"""
import argparse
import hashlib
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

import os
os.sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.core_utils import setup_windows_utf8
setup_windows_utf8()

_logger = logging.getLogger("state_checkpoint_validator")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def compute_checkpoint_hash(content: str) -> str:
    """Return SHA256 hex digest of content string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _validate_checkpoint_data(cp: dict) -> bool:
    """Returns True if checkpoint dict has required fields and valid hash format."""
    missing = [f for f in ("timestamp", "agent", "hash", "files_count") if f not in cp]
    if missing:
        _logger.warning("Checkpoint missing fields: %s", missing)
        return False
    if not re.match(r'^[a-f0-9]{64}$', cp["hash"]):
        _logger.warning("Invalid hash format: %s...", cp["hash"][:16])
        return False
    return True


def validate_historial_checkpoints(historial_path: Path | None = None) -> bool:
    """Validate HISTORIAL.md JSON checkpoints for REGLA #19 compliance."""
    historial_path = historial_path or Path("HISTORIAL.md")
    if not historial_path.exists():
        _logger.warning("HISTORIAL.md not found at %s", historial_path)
        return True

    try:
        content = historial_path.read_text(encoding="utf-8", errors="ignore")
        checkpoints = re.findall(r'```json\s*\{[\s\S]*?"timestamp"[\s\S]*?\}\s*```', content)

        if not checkpoints:
            _logger.info("No checkpoints found in HISTORIAL.md (optional)")
            return True

        valid_count = invalid_count = 0
        for block in checkpoints:
            json_match = re.search(r'\{[\s\S]*\}', block)
            if not json_match:
                _logger.warning("Could not parse checkpoint JSON block")
                invalid_count += 1
                continue
            try:
                cp = json.loads(json_match.group())
                if _validate_checkpoint_data(cp):
                    valid_count += 1
                else:
                    invalid_count += 1
            except json.JSONDecodeError as e:
                _logger.warning("JSON parse error: %s", e)
                invalid_count += 1

        _logger.info("[OK] %d valid, %d invalid checkpoints", valid_count, invalid_count)
        return invalid_count == 0

    except Exception as e:
        _logger.error("Validation failed: %s", e)
        return False


def create_checkpoint(description: str = "Manual checkpoint") -> dict:
    """Return a new checkpoint dict (hash must be computed on write)."""
    return {
        "timestamp": datetime.now().isoformat() + "Z",
        "agent": "claude",
        "description": description,
        "hash": None,        # Caller must set: compute_checkpoint_hash(content) before writing
        "files_count": 0,   # Caller must set: count of files in snapshot
    }


def export_checkpoint_json(output_file: str = "checkpoint.json",
                            historial_path: Path | None = None) -> bool:
    """Export all JSON checkpoints from HISTORIAL.md to a JSON file."""
    historial_path = historial_path or Path("HISTORIAL.md")
    if not historial_path.exists():
        _logger.error("HISTORIAL.md not found")
        return False
    try:
        content = historial_path.read_text(encoding="utf-8", errors="ignore")
        checkpoints = []
        for match in re.findall(r'```json\s*(\{[\s\S]*?\})\s*```', content):
            try:
                checkpoints.append(json.loads(match))
            except json.JSONDecodeError as e:
                _logger.debug("export_checkpoint_json: skipping malformed JSON block: %s", e)
        Path(output_file).write_text(json.dumps(checkpoints, indent=2), encoding="utf-8")
        _logger.info("[OK] Exported %d checkpoints to %s", len(checkpoints), output_file)
        return True
    except Exception as e:
        _logger.error("Export failed: %s", e)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="REGLA #19: State checkpoint validator")
    parser.add_argument("--validate", action="store_true", help="Validate existing checkpoints")
    parser.add_argument("--export", metavar="FILE", help="Export checkpoints to JSON file")
    args = parser.parse_args()

    if args.export:
        return 0 if export_checkpoint_json(args.export) else 1
    return 0 if validate_historial_checkpoints() else 1


if __name__ == "__main__":
    sys.exit(main())
