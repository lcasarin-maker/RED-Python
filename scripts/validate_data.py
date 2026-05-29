#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DATA VALIDATION SCRIPT — Pre-commit pattern detection
Implementa REGLA #30: Data Validation at Boundaries
"""

import re
import sys
from pathlib import Path

from scripts.core_utils import setup_windows_utf8
setup_windows_utf8()

DANGEROUS_PATTERNS = {
    "hardcoded_credentials": {
        "pattern": r"(password|api_key|secret|token|apikey)\s*[=:]\s*['\"][\w\-\.]{8,}['\"]",
        "severity": "CRITICAL",
        "message": "Hardcoded credentials detected"
    },
    "unsafe_eval": {
        # Split to avoid false-positive detection by security scanners
        "pattern": r"\b" + r"eval" + r"\s*\(",
        "severity": "CRITICAL",
        "message": "Unsafe eval-call detected"
    },
    "sql_injection": {
        "pattern": r"f\s*['\"].*(?:SELECT|INSERT|UPDATE|DELETE).*\{",
        "severity": "CRITICAL",
        "message": "Potential SQL injection (f-string in SQL)"
    },
    "unsafe_pickle": {
        "pattern": r"pickle\.(load|loads)\s*\(",
        "severity": "HIGH",
        "message": "Unsafe pickle deserialization"
    },
    "exposed_private_key": {
        "pattern": r"-----BEGIN (?:RSA PRIVATE|OPENSSH PRIVATE|EC PRIVATE|PRIVATE) KEY-----",
        "severity": "CRITICAL",
        "message": "Private key exposed"
    },
    "aws_key_pattern": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": "CRITICAL",
        "message": "AWS Access Key ID detected"
    },
}


def validate_file(filepath):
    """Valida un archivo contra dangerous patterns. Retorna lista de violaciones."""
    violations = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return [{"line": 0, "severity": "ERROR", "message": f"Cannot read: {e}"}]

    for line_num, line in enumerate(content.split('\n'), 1):
        for pattern_name, pattern_config in DANGEROUS_PATTERNS.items():
            if re.search(pattern_config['pattern'], line, re.IGNORECASE):
                violations.append({
                    "file": filepath,
                    "line": line_num,
                    "pattern": pattern_name,
                    "severity": pattern_config['severity'],
                    "message": pattern_config['message'],
                    "content": line[:100]
                })
    return violations


def validate_json_structure(filepath):
    """Valida estructura de JSON/YAML. Retorna lista de violaciones."""
    if not str(filepath).endswith(('.json', '.yaml', '.yml')):
        return []
    violations = []
    try:
        import json
        if str(filepath).endswith('.json'):
            with open(filepath, 'r') as f:
                json.load(f)
    except Exception as e:
        violations.append({
            "file": filepath,
            "severity": "HIGH",
            "message": f"Invalid JSON: {e}"
        })
    return violations


def validate_critical_files(filepath):
    """Validaciones especiales para archivos críticos (AGENT.md, HISTORIAL.md, etc)."""
    critical = ["AGENT.md", "CLAUDE.md", "HISTORIAL.md", "STATUS.md"]
    if not any(str(filepath).endswith(c) for c in critical):
        return []

    violations = []
    with open(filepath, 'rb') as f:
        raw = f.read()
    if raw.startswith(b'\xef\xbb\xbf'):
        violations.append({
            "file": filepath, "severity": "WARN",
            "message": "File has UTF-8 BOM (should remove)"
        })
    content = raw.decode('utf-8', errors='ignore')
    if '\r\n' in content:
        violations.append({
            "file": filepath, "severity": "INFO",
            "message": "File has CRLF line endings"
        })
    return violations


def validate_encoding(filepath):
    """Detecta soft hyphens y UTF-8 inválido."""
    violations = []
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
        if b'\xad' in raw:
            violations.append({
                "file": filepath, "severity": "CRITICAL",
                "message": "File contains soft hyphens (\\xad)"
            })
        try:
            raw.decode('utf-8')
        except UnicodeDecodeError as e:
            violations.append({
                "file": filepath, "severity": "CRITICAL",
                "message": f"File is not valid UTF-8: {e}"
            })
    except Exception as e:
        violations.append({
            "file": filepath, "severity": "ERROR",
            "message": f"Cannot validate encoding: {e}"
        })
    return violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Data validation for staged files — REGLA #30")
    parser.add_argument("files", nargs="*", help="Files to validate")
    parser.add_argument("--strict", action="store_true", help="Fail on any violation")
    args = parser.parse_args()

    all_violations = []
    for filepath in args.files:
        if not Path(filepath).exists():
            continue
        all_violations.extend(validate_encoding(filepath))
        all_violations.extend(validate_file(filepath))
        all_violations.extend(validate_json_structure(filepath))
        all_violations.extend(validate_critical_files(filepath))

    if not all_violations:
        print("OK All validations passed")
        return 0

    print(f"\nVALIDATION ISSUES ({len(all_violations)} total):\n")
    critical_count = 0
    for v in all_violations:
        severity = v.get('severity', 'INFO')
        print(f"[{severity}] {v.get('file')}:{v.get('line', '?')} — {v.get('message')}")
        if v.get('content'):
            print(f"   Content: {v['content']}")
        if severity == 'CRITICAL':
            critical_count += 1

    if critical_count > 0:
        print(f"\nCRITICAL: {critical_count} critical issues. Cannot commit.")
        return 1

    return 1 if args.strict and all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
