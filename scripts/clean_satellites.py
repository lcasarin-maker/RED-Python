#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_satellites.py v1.0 — Satellite Projects Sanitation Script
Surgically purges legacy/deprecated files from satellite project folders before Subtree migration.
"""

import json
import os
import shutil
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()

DEPRECATED_FILES = [
    # Legacy audit scripts
    "audit_6d.py",
    "audit_8d.py",
    "scripts/audit_6d.py",
    "scripts/audit_8d.py",
    # Legacy hooks and setups at root/scripts
    "install_hooks.ps1",
    "scripts/install_hooks.ps1",
    "install_hooks.sh",
    "scripts/install_hooks.sh",
    # Legacy manifests
    "MANDATES_BY_PHASE.md",
    "ESCALATION_PROTOCOL.md",
]

def _clean_project_files(proj_path: Path) -> int:
    deleted = 0
    for rel_file in DEPRECATED_FILES:
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

        # Clean empty scripts directory in satellite if it only had deprecated files
        scripts_dir = proj_path / "scripts"
        if scripts_dir.exists() and scripts_dir.is_dir() and not os.listdir(scripts_dir):
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
    print(f"  Total projects scanned: {len([p for p in projects if p.get('role') != 'CORE'])}")
    print(f"  Projects cleaned:       {cleaned_count}")
    print(f"  Total files removed:    {file_deleted_count}")
    print("=" * 70)

if __name__ == "__main__":
    clean_satellites()
