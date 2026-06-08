#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHASE 2: Empirical Proof Validation - Require logs/screenshots/test output for claims"""

import hashlib
import json
import logging
import subprocess
from datetime import datetime, timezone
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


def _is_dir_or_path_string(val: str) -> bool:
    """Checks if a string represents a directory or contains path separators."""
    if Path(val).is_dir():
        return True
    return "/" in val or "\\" in val


def _iter_json_evidence(evidence_dir: Path):
    for json_path in evidence_dir.glob("*.json"):
        try:
            yield json_path, json.loads(
                json_path.read_text(encoding="utf-8", errors="ignore")
            )
        except Exception as e:
            _logger.debug("_iter_json_evidence: error reading %s: %s", json_path, e)


def _latest_git_commit_epoch(root: Path | None = None) -> float | None:
    if root is None:
        root = Path.cwd()
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
        _logger.debug("_latest_git_commit_epoch: git lookup failed: %s", e)
        return None


def _timestamp_to_epoch(value: object) -> float | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _evidence_is_fresh_enough(data: dict, min_epoch: float | None) -> bool:
    if min_epoch is None:
        return True
    evidence_epoch = _timestamp_to_epoch(data.get("timestamp"))
    if evidence_epoch is None:
        return False
    return evidence_epoch >= min_epoch


def _claim_has_matching_evidence(claim_text: str, evidence_dir: Path) -> bool:
    claim_lower = claim_text.lower()
    min_epoch = _latest_git_commit_epoch()
    for _, data in _iter_json_evidence(evidence_dir):
        if not _evidence_is_fresh_enough(data, min_epoch):
            continue
        haystack = " ".join(
            str(data.get(key, ""))
            for key in ("claim", "operation", "command", "output_log")
        )
        haystack = f"{haystack} {' '.join(data.get('files_touched', []))}".lower()
        if claim_lower in haystack:
            return True
    return False


def _files_have_matching_evidence(files: list[str], evidence_dir: Path) -> bool:
    for file_rel in files:
        file_path = Path.cwd() / file_rel
        if not file_path.exists():
            return False
        if not _has_evidence_for_file(file_rel, evidence_dir):
            return False
    return True


def _extract_claim_text(claim_or_dir: str | Path | None) -> str | None:
    if isinstance(claim_or_dir, str) and not _is_dir_or_path_string(claim_or_dir):
        claim_text = claim_or_dir.strip()
        return claim_text or None
    return None


def check_proof(
    claim_or_dir: str | Path | None = None,
    evidence_dir: Path | None = None,
    files: list[str] | None = None,
) -> bool:
    """Validates that evidence directory has proof files (logs, screenshots, test output)."""
    actual_dir = evidence_dir
    if actual_dir is None:
        if isinstance(claim_or_dir, Path):
            actual_dir = claim_or_dir
        elif isinstance(claim_or_dir, str) and _is_dir_or_path_string(claim_or_dir):
            actual_dir = Path(claim_or_dir)
        else:
            actual_dir = Path.cwd() / ".protocol" / "evidence"
    actual_dir = Path(actual_dir)
    if not actual_dir.exists():
        return False
    evidence_files = (
        list(actual_dir.glob("*.json"))
        + list(actual_dir.glob("*.log"))
        + list(actual_dir.glob("*.txt"))
    )
    if not evidence_files:
        return False
    if files and not _files_have_matching_evidence(files, actual_dir):
        return False
    claim_text = _extract_claim_text(claim_or_dir)
    if claim_text and not _claim_has_matching_evidence(claim_text, actual_dir):
        return False
    return True


def changed_files(root: Path | None = None) -> list[str]:
    """Returns list of changed files detected by git."""
    if root is None:
        root = Path.cwd()
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(root),
        )
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


def _evidence_matches(
    data: dict,
    ui_path: Path,
    ui_file_rel: str,
    current_hash: str,
    json_path: Path,
    min_epoch: float | None = None,
) -> bool:
    """Returns True if evidence data matches file by name, hash, and screenshot."""
    target = data.get("target_file", "")
    if not target:
        return False
    if Path(target).name != ui_path.name and target != ui_file_rel:
        return False
    if data.get("file_hash", "") != current_hash:
        return False
    if not _evidence_is_fresh_enough(data, min_epoch):
        return False
    return _screenshot_exists(data.get("screenshot", ""), json_path)


def _has_evidence_for_file(ui_file_rel: str, evidence_dir: Path) -> bool:
    """Returns True if evidence exists for the UI file, or if the file does not exist."""
    ui_path = Path.cwd() / ui_file_rel
    if not ui_path.exists():
        return True
    current_hash = get_file_hash(ui_path)
    min_epoch = _latest_git_commit_epoch()
    for json_path in evidence_dir.glob("*.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8", errors="ignore"))
            if _evidence_matches(
                data,
                ui_path,
                ui_file_rel,
                current_hash,
                json_path,
                min_epoch=min_epoch,
            ):
                return True
        except Exception as e:
            _logger.debug("_has_evidence_for_file: error reading %s: %s", json_path, e)
    return False


def has_human_validation(
    file_list: list[str], evidence_dir: Path | None = None
) -> bool:
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
    return [
        f for f in changed_file_list if any(f.endswith(ext) for ext in ui_extensions)
    ]
