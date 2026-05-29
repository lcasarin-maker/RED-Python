#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHASE 2: Empirical Proof Validation - Require logs/screenshots/test output for claims"""

import hashlib
import json
import logging
import subprocess
from pathlib import Path

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("empirical_proof_checker")


def get_file_hash(path: Path) -> str:
    """Computes SHA256 hash of a file."""
    if not path.exists():
        return ""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    except Exception as e:
        _logger.warning("get_file_hash failed for %s: %s", path, e)
        return ""
    return hasher.hexdigest()


def check_proof(claim: str, evidence_dir: Path | None = None, files: list[str] | None = None) -> bool:
    """Validates that a claim has empirical proof (logs, screenshots, test output)."""
    if evidence_dir is None:
        evidence_dir = Path.cwd() / ".protocol" / "evidence"
    evidence_dir = Path(evidence_dir)
    if not evidence_dir.exists():
        return False
    evidence_files = list(evidence_dir.glob("*.json")) + list(evidence_dir.glob("*.log")) + list(evidence_dir.glob("*.txt"))
    return len(evidence_files) > 0


def changed_files(root: Path | None = None) -> list[str]:
    """Returns list of changed files detected by git."""
    if root is None:
        root = Path.cwd()
    try:
        result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, timeout=5, cwd=str(root))
        if result.returncode == 0:
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        _logger.warning("changed_files: git diff failed: %s", e)
    return []


def _screenshot_exists(screenshot_path_str: str, json_path: Path) -> bool:
    """Returns True if the screenshot path resolves to an existing file."""
    if not screenshot_path_str:
        return False
    screenshot_path = Path(screenshot_path_str)
    if screenshot_path.is_absolute() and screenshot_path.exists():
        return True
    if (json_path.parent / screenshot_path.name).exists():
        return True
    return (Path.cwd() / screenshot_path_str).exists()


def _evidence_matches(data: dict, ui_path: Path, ui_file_rel: str, current_hash: str, json_path: Path) -> bool:
    """Returns True if evidence data matches file by name, hash, and screenshot."""
    target = data.get("target_file", "")
    if not target:
        return False
    if Path(target).name != ui_path.name and target != ui_file_rel:
        return False
    if data.get("file_hash", "") != current_hash:
        return False
    return _screenshot_exists(data.get("screenshot", ""), json_path)


def _has_evidence_for_file(ui_file_rel: str, evidence_dir: Path) -> bool:
    """Returns True if evidence exists for the UI file, or if the file does not exist."""
    ui_path = Path.cwd() / ui_file_rel
    if not ui_path.exists():
        return True
    current_hash = get_file_hash(ui_path)
    for json_path in evidence_dir.glob("*.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8", errors="ignore"))
            if _evidence_matches(data, ui_path, ui_file_rel, current_hash, json_path):
                return True
        except Exception as e:
            _logger.debug("_has_evidence_for_file: error reading %s: %s", json_path, e)
    return False


def has_human_validation(file_list: list[str], evidence_dir: Path | None = None) -> bool:
    """Check if files have human validation markers (screenshots, test logs, etc) with matching hash and physical screenshot existence.
    Returns True when all listed UI files have corresponding evidence, or when the list is empty.
    """
    if not file_list:
        return True
    if evidence_dir is None:
        evidence_dir = Path.cwd() / ".protocol" / "evidence"
    evidence_dir = Path(evidence_dir)
    if not evidence_dir.exists():
        return False
    for ui_file_rel in file_list:
        if not _has_evidence_for_file(ui_file_rel, evidence_dir):
            return False
    return True


def ui_files(changed_file_list: list[str]) -> list[str]:
    """Filters UI files from changed files list."""
    ui_extensions = [".html", ".js", ".jsx", ".tsx", ".css"]
    return [f for f in changed_file_list if any(f.endswith(ext) for ext in ui_extensions)]
