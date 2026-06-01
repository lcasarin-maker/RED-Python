#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the canonical Golden Standard into catalog YAML fragments.

This keeps the manifest thin while preserving a merged in-memory view for Cerberus.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Golden_Standard" / "golden_standard.yaml"


def _load_source_lines() -> list[str]:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Golden Standard source not found: {SOURCE}")
    return SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)


def _slice(lines: list[str], start: int, end: int | None) -> str:
    return "".join(lines[start:end])


def _find_index(lines: list[str], prefix: str) -> int:
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            return index
    raise KeyError(f"Could not find section starting with {prefix!r}")


def _is_manifest(lines: list[str]) -> bool:
    return any(line.startswith("catalogs:") for line in lines)


def main() -> int:
    lines = _load_source_lines()
    if _is_manifest(lines):
        fragments = [
            ROOT / "Golden_Standard" / "golden_standard_tokenomics.yaml",
            ROOT / "Golden_Standard" / "golden_standard_testing_vices.yaml",
            ROOT / "Golden_Standard" / "golden_standard_coding_vices.yaml",
            ROOT / "Golden_Standard" / "golden_standard_project_insights.yaml",
        ]
        missing = [str(path.relative_to(ROOT)) for path in fragments if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"Golden Standard manifest is split but missing fragments: {missing}")
        print("Golden Standard catalogs already split")
        return 0

    tokenomics_idx = _find_index(lines, "tokenomics:")
    testing_idx = _find_index(lines, "testing_vices:")
    coding_idx = _find_index(lines, "coding_vices:")
    project_insights_idx = _find_index(lines, "project_insights:")
    coding_details_idx = _find_index(lines, "coding_vices_details:")

    fragments = {
        "golden_standard_tokenomics.yaml": _slice(lines, tokenomics_idx, testing_idx),
        "golden_standard_testing_vices.yaml": _slice(lines, testing_idx, coding_idx),
        "golden_standard_coding_vices.yaml": _slice(lines, coding_idx, project_insights_idx)
        + _slice(lines, coding_details_idx, None),
        "golden_standard_project_insights.yaml": _slice(lines, project_insights_idx, coding_details_idx),
    }

    for filename, content in fragments.items():
        if not content.strip():
            raise ValueError(f"Generated fragment {filename} is empty")
        (ROOT / "Golden_Standard" / filename).write_text(content, encoding="utf-8")

    SOURCE.write_text(
        "format_version: 2\n"
        "description: Golden Standard canonical manifest. Data lives in split catalogs; this file indexes them.\n"
        "catalogs:\n"
        "  tokenomics: golden_standard_tokenomics.yaml\n"
        "  testing_vices: golden_standard_testing_vices.yaml\n"
        "  coding_vices: golden_standard_coding_vices.yaml\n"
        "  project_insights: golden_standard_project_insights.yaml\n",
        encoding="utf-8",
    )
    print("Golden Standard split complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
