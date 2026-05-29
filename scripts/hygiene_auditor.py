#!/usr/bin/env python3
"""
Repository hygiene auditor for CoderCerberus V0.02.

This module makes text corruption and unsafe legacy helpers first-class audit
failures. Repairs are intentionally deterministic and limited to files that are
part of the protocol source, not evidence logs or backups.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
import shutil

TEXT_SUFFIXES = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".sh"}
EXCLUDED_PARTS = {
    ".git",
    ".secrets",
    ".protocol",
    "__pycache__",
    ".pytest_cache",
    "deprecated",
    "antigravityfindings.md",
    "CERBERUS_ANTIGRAVITY.md",
    "findings.md",
    "PLAN.md",
    "01 Cuenza 2025",
    "decompiled-legacy",
    "bin",
    "obj",
    ".run",
    ".tools",
    "backups",
    "node_modules",
    "venv",
    "env",
    ".venv",
    ".agent-sandbox",
    "Organized",
    "test_folder",
}

MOJIBAKE_MARKERS = ("\u00c3", "\u00c2", "\u00e2", "\u00f0", "\u00ef\u00b8", "\ufffd")
TOKEN_WITH_MARKER = re.compile(r"\S*(?:\u00c3|\u00c2|\u00e2|\u00f0|\u00ef\u00b8|\ufffd)\S*")
DIRECT_REPAIRS = {
    "\u00e2\u0161\u00a0\ufe0f": "\u26a0\ufe0f",
    "\u00e2\u0153\u2026": "\u2705",
    "\u00e2\u009d\u0152": "\u274c",
    "\u00f0\u0178\u00a7\u00a0": "\U0001f9e0",
}

CP1252_REVERSE = {
    "€": 0x80,
    "‚": 0x82,
    "ƒ": 0x83,
    "„": 0x84,
    "…": 0x85,
    "†": 0x86,
    "‡": 0x87,
    "ˆ": 0x88,
    "‰": 0x89,
    "Š": 0x8A,
    "‹": 0x8B,
    "Œ": 0x8C,
    "Ž": 0x8E,
    "‘": 0x91,
    "’": 0x92,
    "“": 0x93,
    "”": 0x94,
    "•": 0x95,
    "–": 0x96,
    "—": 0x97,
    "˜": 0x98,
    "™": 0x99,
    "š": 0x9A,
    "›": 0x9B,
    "œ": 0x9C,
    "ž": 0x9E,
    "Ÿ": 0x9F,
}

LEGACY_SCRIPT_RULES: dict = {}

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()


@dataclass(frozen=True)
class HygieneFinding:
    kind: str
    path: str
    line: int
    detail: str


def is_text_source(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return False
    if any(part in EXCLUDED_PARTS for part in rel_parts):
        return False
    return path.is_file() and path.suffix.lower() in TEXT_SUFFIXES


def iter_text_sources(root: Path):
    import os
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_PARTS]
        for file in files:
            path = Path(r) / file
            if is_text_source(path, root):
                yield path


def has_mojibake(text: str) -> bool:
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def _to_original_bytes(value: str) -> bytes:
    data = bytearray()
    for char in value:
        codepoint = ord(char)
        if codepoint <= 0xFF:
            data.append(codepoint)
        elif char in CP1252_REVERSE:
            data.append(CP1252_REVERSE[char])
        else:
            raise UnicodeEncodeError("cp1252", value, 0, 1, f"unsupported {char!r}")
    return bytes(data)


def repair_token(token: str) -> str:
    if not has_mojibake(token):
        return token
    try:
        repaired = _to_original_bytes(token).decode("utf-8")
    except UnicodeError:
        repaired = token
    return repaired.replace("\u00c2\xa0", " ").replace("\u00c2 ", " ")


def repair_mojibake_text(text: str) -> str:
    for corrupted, repaired in DIRECT_REPAIRS.items():
        text = text.replace(corrupted, repaired)
    return TOKEN_WITH_MARKER.sub(lambda match: repair_token(match.group(0)), text)


def find_mojibake(root: Path) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    for path in iter_text_sources(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if has_mojibake(line):
                findings.append(
                    HygieneFinding(
                        kind="mojibake",
                        path=path.relative_to(root).as_posix(),
                        line=line_no,
                        detail=line.strip()[:160],
                    )
                )
    return findings


def repair_mojibake(root: Path) -> list[str]:
    touched: list[str] = []
    for path in iter_text_sources(root):
        original = path.read_text(encoding="utf-8", errors="replace")
        repaired = repair_mojibake_text(original)
        if repaired != original:
            path.write_text(repaired, encoding="utf-8", newline="")
            touched.append(path.relative_to(root).as_posix())
    return touched


def find_legacy_scripts(root: Path) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    for rel_path, forbidden_fragments in LEGACY_SCRIPT_RULES.items():
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "DEPRECATED_SAFE_WRAPPER = True" in text:
            continue
        for fragment in forbidden_fragments:
            line_no = next(
                (idx for idx, line in enumerate(text.splitlines(), start=1) if fragment in line),
                1,
            )
            if fragment in text:
                findings.append(
                    HygieneFinding(
                        kind="legacy_script",
                        path=rel_path,
                        line=line_no,
                        detail=f"unsafe legacy fragment: {fragment}",
                    )
                )
    return findings


def deprecate_legacy_scripts(root: Path) -> list[str]:
    touched: list[str] = []
    deprecated_dir = root / "deprecated"
    deprecated_dir.mkdir(exist_ok=True)
    for finding in find_legacy_scripts(root):
        src_path = root / finding.path
        dest_path = deprecated_dir / finding.path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dest_path))
        if finding.path not in touched:
            touched.append(finding.path)
    return touched


def find_hygiene_findings(root: Path) -> list[HygieneFinding]:
    return find_mojibake(root) + find_legacy_scripts(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit and repair repository hygiene.")
    parser.add_argument("--fix", action="store_true", help="Repair mojibake text in protocol source files")
    args = parser.parse_args()
    root = Path.cwd()

    if args.fix:
        touched = repair_mojibake(root)
        deprecated = deprecate_legacy_scripts(root)
        print(f"repaired={len(touched)} deprecated={len(deprecated)}")
        for rel in touched + deprecated:
            print(rel)

    findings = find_hygiene_findings(root)
    for finding in findings[:100]:
        print(f"{finding.kind}: {finding.path}:{finding.line}: {finding.detail}")
    if len(findings) > 100:
        print(f"... {len(findings) - 100} more findings")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
