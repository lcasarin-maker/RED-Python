#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_satellites.py v1.0 — Satellite Projects Sanitation Script
Purges deprecated files from satellite project folders before Subtree migration.
"""

import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()

_DEPRECATED_FILES_MANIFEST = _ROOT / "deprecated" / "metadata" / "deprecated_cleanup_targets.json"


def _load_deprecated_files() -> list[str]:
    try:
        with _DEPRECATED_FILES_MANIFEST.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Deprecated cleanup manifest not found: {_DEPRECATED_FILES_MANIFEST}"
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to load deprecated cleanup manifest: {exc}") from exc

    files = payload.get("files", [])
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        raise ValueError("Deprecated cleanup manifest must contain a string list at 'files'")
    return files


def _clean_project_files(proj_path: Path) -> int:
    deleted = 0
    for rel_file in _load_deprecated_files():
        target_file = proj_path / rel_file
        if target_file.exists() and target_file.is_file():
            try:
                target_file.unlink()
                print(f"   🗑️  Removed deprecated: {rel_file}")
                deleted += 1
            except Exception as e:
                print(f"   ❌ Error deleting {rel_file}: {e}")
    return deleted


def clean_satellites():
    registry_path = _ROOT / ".protocol" / "metadata" / "REGISTRY.json"
    if not registry_path.exists():
        print(f"❌ REGISTRY.json not found at {registry_path}")
        sys.exit(1)

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ Error loading REGISTRY.json: {e}")
        sys.exit(1)

    projects = registry.get("projects", [])
    cleaned_count = 0
    file_deleted_count = 0

    print("\n" + "=" * 70)
    print("🧹 SATELLITE SANITATION & DEPRECATION PURGE")
    print("=" * 70)

    for proj in projects:
        if proj.get("role") == "CORE":
            continue

        proj_name = proj.get("name")
        proj_path = Path(proj.get("path")).resolve()

        if not proj_path.exists():
            print(f"⚠️  Project '{proj_name}' path does not exist: {proj_path}")
            continue

        print(f"\n📁 Cleaning Project: {proj_name}")
        print(f"   Path: {proj_path}")

        deleted_in_project = _clean_project_files(proj_path)
        file_deleted_count += deleted_in_project

        # Remove empty scripts/ directory when cleanup leaves it unused.
        scripts_dir = proj_path / "scripts"
        if (
            scripts_dir.exists()
            and scripts_dir.is_dir()
            and not os.listdir(scripts_dir)
        ):
            try:
                scripts_dir.rmdir()
                print("   🗑️  Removed empty scripts/ directory")
            except Exception as e:
                print(f"   ❌ Error removing scripts directory: {e}")

        if deleted_in_project > 0:
            cleaned_count += 1

    print("\n" + "=" * 70)
    print("📊 SANITATION SUMMARY")
    print("=" * 70)
    print(
        f"  Total projects scanned: {len([p for p in projects if p.get('role') != 'CORE'])}"
    )
    print(f"  Projects cleaned:       {cleaned_count}")
    print(f"  Total files removed:    {file_deleted_count}")
    print("=" * 70)


if __name__ == "__main__":
    clean_satellites()
