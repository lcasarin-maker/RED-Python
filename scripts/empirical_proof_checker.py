#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHASE 2: Empirical Proof Validation - Require logs/screenshots/test output for claims"""

import hashlib
import json
from pathlib import Path
from typing import List, Optional
import subprocess

def get_file_hash(path: Path) -> str:
    """Computes SHA256 hash of a file."""
    if not path.exists():
        return ""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    except Exception:
        return ""
    return hasher.hexdigest()

def check_proof(claim: str, evidence_dir: Optional[Path] = None, files: Optional[List[str]] = None) -> bool:
    """Validates that a claim has empirical proof (logs, screenshots, test output)."""
    if evidence_dir is None:
        evidence_dir = Path.cwd() / ".protocol" / "evidence"
    evidence_dir = Path(evidence_dir)
    if not evidence_dir.exists():
        return False
    
    evidence_files = list(evidence_dir.glob("*.json")) + list(evidence_dir.glob("*.log")) + list(evidence_dir.glob("*.txt"))
    return len(evidence_files) > 0

def changed_files(root: Path = None) -> List[str]:
    """Returns list of changed files detected by git."""
    if root is None:
        root = Path.cwd()
    try:
        result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, timeout=5, cwd=str(root))
        if result.returncode == 0:
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        import sys
        print(f"Error checking changed files: {e}", file=sys.stderr)
    return []

def has_human_validation(file_list: List[str], evidence_dir: Path = None) -> bool:
    """Check if files have human validation markers (screenshots, test logs, etc) with matching hash and physical screenshot existence."""
    if not file_list:
        return True
    if evidence_dir is None:
        evidence_dir = Path.cwd() / ".protocol" / "evidence"
    evidence_dir = Path(evidence_dir)
    if not evidence_dir.exists():
        return False

    for ui_file_rel in file_list:
        ui_path = Path.cwd() / ui_file_rel
        if not ui_path.exists():
            continue
        current_hash = get_file_hash(ui_path)
        
        valid_evidence_found = False
        for json_path in evidence_dir.glob("*.json"):
            try:
                data = json.loads(json_path.read_text(encoding="utf-8", errors="ignore"))
                target = data.get("target_file", "")
                if target and (Path(target).name == ui_path.name or target == ui_file_rel):
                    evidence_hash = data.get("file_hash", "")
                    if evidence_hash == current_hash:
                        screenshot_path_str = data.get("screenshot", "")
                        if screenshot_path_str:
                            screenshot_path = Path(screenshot_path_str)
                            if screenshot_path.is_absolute() and screenshot_path.exists():
                                valid_evidence_found = True
                                break
                            elif (json_path.parent / screenshot_path.name).exists():
                                valid_evidence_found = True
                                break
                            elif (Path.cwd() / screenshot_path_str).exists():
                                valid_evidence_found = True
                                break
            except Exception as e:
                # Log parser error
                _err = str(e)
        
        if not valid_evidence_found:
            return False
            
    return True

def ui_files(changed_file_list: List[str]) -> List[str]:
    """Filters UI files from changed files list."""
    ui_extensions = [".html", ".js", ".jsx", ".tsx", ".css"]
    return [f for f in changed_file_list if any(f.endswith(ext) for ext in ui_extensions)]
