#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHASE 2: File Chunking Validation - Ensure files are non-empty, syntactically valid, and free of hallucination loops"""

import ast
import json
from pathlib import Path

<<<<<<< HEAD:scripts/chunking_validator.py
=======
from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("chunking_validator")


>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b:scripts/validate_chunking.py
def detect_repetition_loops(content: str) -> bool:
    """Detects repeating sequence loops characteristic of LLM hallucinations."""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) < 10:
        return False

    for i in range(len(lines) - 4):
        for size in range(1, 5):
            block = lines[i : i + size]
            reps = 0
            idx = i + size
            while idx + size <= len(lines) and lines[idx : idx + size] == block:
                reps += 1
                idx += size
            if reps >= 4:  # Detected loop repeating 4+ times
                return True
    return False


def validate_chunks(file_path) -> bool:
    """Validates that a file meets chunking requirements (non-empty, valid syntax, no hallucination loops)."""
    file_path = Path(file_path)
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    if not content or len(content.strip()) == 0:
        return False

    # Detect hallucination loops
    if detect_repetition_loops(content):
        return False

    # Validate syntax
    if file_path.suffix == ".py":
        try:
            ast.parse(content)
        except SyntaxError:
            return False
    elif file_path.suffix == ".json":
        try:
            json.loads(content)
        except Exception:
            return False

    return True
