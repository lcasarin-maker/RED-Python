#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_to_subtree.py v1.0 — Satellite Projects Git Subtree Migration
Migrates all active satellite projects from physical copies to Git Subtree.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()

PROTOCOL_PHYSICAL_FILES = [
    "AGENT.md",
    "PROTOCOL_SYSTEM.md",
    "PROTOCOL_BEHAVIOR.md",
    "SPEC.md",
    ".gitattributes",
    "scripts/audit_10d.py",
    "scripts/verify_protocol_adoption.py",
    "scripts/pre_edit_guard.py",
    ".claude/settings.json"
]

def run_git_cmd(args: list, cwd: Path) -> tuple[int, str, str]:
    """Runs a git command and returns exit code, stdout, stderr."""
    env = os.environ.copy()
    env["GIT_MERGE_AUTOEDIT"] = "no"
    res = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        encoding="utf-8",
        errors="ignore"
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def clean_physical_copies(proj_path: Path):
    """Purges physical copies from project root to avoid git subtree merge collisions."""
    for rel_file in PROTOCOL_PHYSICAL_FILES:
        path = proj_path / rel_file
        if not path.exists():
            continue
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            print(f"      🗑️  Removed physical: {rel_file}")
        except Exception as e:
            print(f"      ❌ Failed to remove physical {rel_file}: {e}")

def _install_single_hook(src_hook: Path, dst_hook: Path, hook_name: str):
    if src_hook.exists():
        try:
            shutil.copy2(src_hook, dst_hook)
            # Make executable (primarily for Unix-like environments inside Git Bash)
            try:
                dst_hook.chmod(dst_hook.stat().st_mode | 0o111)
            except Exception as exc:
                print(f"      ⚠️  Could not make hook executable: {exc}")
            print(f"      ✅ Hook configured: {hook_name}")
        except Exception as e:
            print(f"      ❌ Failed to install hook {hook_name}: {e}")

def install_hooks_in_satellite(proj_path: Path):
    """Copies subtree git hooks into the satellite's .git/hooks directory."""
    git_hooks_dir = proj_path / ".git" / "hooks"
    git_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Source hook paths under subtree
    subtree_hooks_dir = proj_path / ".protocol-core" / "scripts" / "hooks"
    
    if not subtree_hooks_dir.exists():
        print("      ⚠️  Subtree hooks directory not found, skipping hooks copy")
        return
        
    for hook_name in ["pre-commit", "post-commit", "pre-push"]:
        src_hook = subtree_hooks_dir / hook_name
        dst_hook = git_hooks_dir / hook_name
        _install_single_hook(src_hook, dst_hook, hook_name)

def migrate_satellites():
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
    migrated_count = 0
    failed_count = 0

    print("\n" + "=" * 70)
    print("🚀 SATELLITE PROJECTS GIT SUBTREE MIGRATION")
    print("=" * 70)
    print(f"Core path: {_ROOT}")

    for proj in projects:
        if proj.get("role") == "CORE":
            continue

        proj_name = proj.get("name")
        proj_path = Path(proj.get("path")).resolve()

        if not proj_path.exists():
            print(f"\n⚠️  Project '{proj_name}' path does not exist, skipping: {proj_path}")
            continue

        print(f"\n📁 Processing: {proj_name}")
        print(f"   Path: {proj_path}")

        # 1. Clean physical copies
        print("   🧹 Cleaning legacy files to avoid subtree merge conflicts...")
        clean_physical_copies(proj_path)

        # 2. Check if git repository is clean or if we need to commit cleanup
        code, out, err = run_git_cmd(["git", "status", "--porcelain"], proj_path)
        if code != 0:
            print(f"   ❌ Git status check failed: {err}")
            failed_count += 1
            continue

        if out:
            print("   📝 Committing sanitation/cleanup in satellite...")
            run_git_cmd(["git", "add", "-A"], proj_path)
            run_git_cmd(["git", "commit", "--no-verify", "-m", "chore: sanitize legacy protocol copies before subtree migration"], proj_path)

        # 3. Add or pull Git Subtree
        subtree_dir = proj_path / ".protocol-core"
        if not subtree_dir.exists():
            print("   🌿 Adding Git Subtree (.protocol-core/)...")
            # git subtree add --prefix=.protocol-core/ D:/GoogleDrive/AI/Cerberus master --squash
            code, out, err = run_git_cmd(
                ["git", "subtree", "add", "--prefix=.protocol-core/", str(_ROOT).replace("\\", "/"), "master", "--squash"],
                proj_path
            )
            if code == 0:
                print("   ✅ Git Subtree added successfully!")
                migrated_count += 1
            else:
                print(f"   ❌ Failed to add Git Subtree: {err}")
                failed_count += 1
                continue
        else:
            print("   🌿 Git Subtree already exists, pulling updates...")
            # git subtree pull --prefix=.protocol-core/ D:/GoogleDrive/AI/Cerberus master --squash
            code, out, err = run_git_cmd(
                ["git", "subtree", "pull", "--prefix=.protocol-core/", str(_ROOT).replace("\\", "/"), "master", "--squash"],
                proj_path
            )
            if code == 0:
                print("   ✅ Git Subtree pulled successfully!")
                migrated_count += 1
            else:
                print(f"   ❌ Failed to pull Git Subtree changes: {err}")
                failed_count += 1
                continue

        # 4. Install updated hooks from subtree
        print("   ⚓ Installing subtree-aware hooks...")
        install_hooks_in_satellite(proj_path)

        # 5. Commit any hook updates or changes in satellite
        code, out, err = run_git_cmd(["git", "status", "--porcelain"], proj_path)
        if out:
            run_git_cmd(["git", "add", "-A"], proj_path)
            run_git_cmd(["git", "commit", "--no-verify", "-m", "chore: configure subtree-aware git hooks"], proj_path)

    print("\n" + "=" * 70)
    print("📊 MIGRATION SUMMARY")
    print("=" * 70)
    print(f"  Total projects scanned:   {len([p for p in projects if p.get('role') != 'CORE'])}")
    print(f"  Successfully processed:  {migrated_count}")
    print(f"  Failed migrations:        {failed_count}")
    print("=" * 70)

if __name__ == "__main__":
    migrate_satellites()
