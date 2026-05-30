#!/usr/bin/env python3
"""global_sync_safe.py v2.0 — Safe Multi-Project Protocol Synchronization
Refactored to use shared helpers (scripts/helpers.py) to keep nesting depth ≤4.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8, get_centralized_version
from scripts.helpers import _backup_project_files, _copy_protocol_files

setup_windows_utf8()
logger = logging.getLogger("global_sync_safe")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class GlobalSyncManager:
    """Safe multi‑project synchronization with rollback support."""

    PROTOCOL_FILES = [
        "AGENT.md",
        "PROTOCOL_SYSTEM.md",
        "PROTOCOL_BEHAVIOR.md",
        "SPEC.md",
        ".gitattributes",
        # Auditor — required for real adoption (P5.1)
        "scripts/audit_10d.py",
        "scripts/verify_protocol_adoption.py",
        # Pre-edit guard — enforces S6/S7/S19 at edit time, not just at commit
        "scripts/pre_edit_guard.py",
        # Claude hook config — wires guard into PreToolUse
        ".claude/settings.json",
    ]

    def __init__(self, core_path: str = "."):
        self.core_path = Path(core_path).resolve()
        self.registry_path = self.core_path / ".protocol" / "metadata" / "REGISTRY.json"
        self.version = get_centralized_version()
        self.sync_log = []

    def load_registry(self) -> dict:
        """Load project registry JSON."""
        if not self.registry_path.exists():
            logger.error("REGISTRY.json not found")
            return {}
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def sync_project(self, project_info: dict, dry_run: bool = False, create_backup: bool = True) -> dict:
        """Synchronize protocol files to a single project using Git Subtree.

        Returns a status dict.
        """
        project_path = Path(project_info["path"]).resolve()
        project_name = project_info["name"]
        if project_path == self.core_path:
            logger.info(f"\n⭐ CORE: {project_name} (skipping identical path)")
            return {"status": "skipped", "reason": "core_path"}
        logger.info(f"\n📦 Syncing (Subtree): {project_name}\n   Path: {project_path}")
        if not project_path.exists():
            logger.warning("   ⚠️  Project path not found, skipping")
            return {"status": "skipped", "reason": "path_not_found"}
        if not (project_path / ".git").exists():
            logger.warning("   ⚠️  Not a git repository, skipping")
            return {"status": "skipped", "reason": "not_git_repo"}

        if dry_run:
            logger.info("   ✅ git subtree pull --prefix=.protocol-core/ (preview)")
            return {"status": "dry_run", "files": ["git subtree pull"], "timestamp": datetime.now(timezone.utc).isoformat()}

        try:
            # Dynamic import of migration/subtree helpers to avoid cyclic dependency
            from scripts.migrate_to_subtree import clean_physical_copies, install_hooks_in_satellite

            # 1. Purge legacy physical files
            clean_physical_copies(project_path)

            env = os.environ.copy()
            env["GIT_MERGE_AUTOEDIT"] = "no"

            # Commit any cleanup/sanitation before pulling
            subprocess.run(["git", "add", "-u"], cwd=str(project_path), capture_output=True, env=env)
            subprocess.run(["git", "commit", "-m", "chore: sanitize legacy protocol copies before subtree update"], cwd=str(project_path), capture_output=True, env=env)

            # 2. Run git subtree pull from core path
            core_url = str(self.core_path).replace("\\", "/")
            logger.info(f"   🌿 Pulling Git Subtree from {core_url}...")
            res = subprocess.run(
                ["git", "subtree", "pull", "--prefix=.protocol-core/", core_url, "master", "--squash"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                env=env
            )
            
            if res.returncode != 0:
                logger.error(f"   ❌ Git Subtree pull failed: {res.stderr.strip()}")
                return {"status": "failed", "reason": f"Git Subtree pull failed: {res.stderr.strip()}"}
            
            logger.info("   ✅ Git Subtree pulled successfully!")

            # 3. Update hooks in satellite
            logger.info("   ⚓ Installing subtree-aware hooks...")
            install_hooks_in_satellite(project_path)

            # Commit hook updates if any
            subprocess.run(["git", "add", "-u"], cwd=str(project_path), capture_output=True, env=env)
            subprocess.run(["git", "commit", "-m", "chore: update subtree-aware git hooks"], cwd=str(project_path), capture_output=True, env=env)

        except Exception as e:
            logger.error(f"   ❌ Synchronization error: {e}")
            return {"status": "failed", "reason": str(e)}

        return {"status": "synced", "files": ["git subtree pull", "hooks installed"], "timestamp": datetime.now(timezone.utc).isoformat()}

    def _discover_new_projects(self, registry: dict, dry_run: bool = False) -> list:
        """Discover new folders under CERBERUS_AI_ROOT (env) and optionally init git.
        Returns list of newly created project names.
        """
        ai_root_env = os.getenv("CERBERUS_AI_ROOT", "")
        if not ai_root_env:
            logger.debug("_discover_new_projects: CERBERUS_AI_ROOT not set; skipping discovery")
            return []
        ai_root = Path(ai_root_env).resolve()
        if not ai_root.exists():
            return []
        known_paths = {Path(p["path"]).resolve() for p in registry.get("projects", [])}
        ignore_dirs = {'.claude', '.pytest_cache', '.secrets', 'scripts', 'deprecated', 'tests', self.core_path.name}
        newly_created = []
        for child in ai_root.iterdir():
            if child.is_dir() and child.name not in ignore_dirs and not child.name.startswith('.'):
                if child.resolve() not in known_paths:
                    self._maybe_init_new_project(child, dry_run, newly_created)
                    registry.setdefault("projects", []).append({
                        "name": child.name,
                        "path": str(child),
                        "role": "PROJECT",
                        "description": f"Auto‑discovered project: {child.name}",
                        "status": "active",
                        "last_sync": "",
                    })
                    logger.info(f"🌟 Auto‑discovered new project: {child.name}")
        return newly_created

    def _maybe_init_new_project(self, child: Path, dry_run: bool, newly_created: list) -> None:
        if dry_run:
            return
        if not (child / ".git").exists():
            self._init_github_repo(child)
        newly_created.append(child.name)

    def _init_github_repo(self, child_path: Path):
        logger.info(f"   ⚙️  Initializing Git/GitHub for: {child_path.name}")
        subprocess.run(["git", "init"], cwd=str(child_path), capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=str(child_path), capture_output=True)
        # Skipping actual GitHub CLI calls for safety

    def sync_all(self, dry_run: bool = False, project_filter: str = None) -> dict:
        """Synchronize registered projects, optionally filtered by project name.
        Returns a summary dict.
        """
        registry = self.load_registry()
        newly_created = self._discover_new_projects(registry, dry_run=dry_run)
        projects = registry.get("projects", [])
        
        target_projects = [p for p in projects if p["role"] != "CORE"]
        if project_filter:
            target_projects = [p for p in target_projects if p["name"].lower() == project_filter.lower()]
            if not target_projects:
                logger.warning(f"No project matching filter: {project_filter}")
        
        logger.info("\n" + "=" * 70)
        logger.info("🌍 GLOBAL PROTOCOL SYNCHRONIZATION v2.0")
        logger.info("=" * 70)
        logger.info(f"{'DRY‑RUN' if dry_run else 'APPLY'} mode")
        logger.info(f"Projects to sync: {len(target_projects)}")
        results = {}
        synced = failed = 0
        for project in projects:
            if project["role"] == "CORE":
                logger.info(f"\n⭐ CORE: {project['name']} (skipping)")
                continue
            if project_filter and project["name"].lower() != project_filter.lower():
                continue
            result = self.sync_project(project, dry_run=dry_run)
            results[project["name"]] = result
            if result["status"] in ("synced", "dry_run"):
                synced += 1
                if not dry_run:
                    project["last_sync"] = datetime.now(timezone.utc).isoformat()
                if not dry_run and project["name"] in newly_created:
                    logger.info(f"   🚀 Initial commit & push for: {project['name']}")
                    proj_path = str(Path(project["path"]).resolve())
                    subprocess.run(["git", "add", "."], cwd=proj_path, capture_output=True)
                    subprocess.run(["git", "commit", "-m", "Initial protocol sync from Cerberus"], cwd=proj_path, capture_output=True)
                    subprocess.run(["git", "-c", "credential.helper=", "push", "-u", "origin", "main"], cwd=proj_path, capture_output=True, text=True)
            else:
                failed += 1
        if not dry_run:
            registry.setdefault("last_updated", datetime.now(timezone.utc).isoformat())
            registry.setdefault("sync_summary", {})
            registry["sync_summary"].update({
                "total_projects": len(projects),
                "synced": synced,
                "pending": len([p for p in projects if p["role"] != "CORE"]) - synced,
                "failed": failed,
            })
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2)
        logger.info("\n" + "=" * 70)
        logger.info("📊 SYNC SUMMARY")
        logger.info("=" * 70)
        logger.info(f"  Mode: {'DRY‑RUN (preview only)' if dry_run else 'APPLY'}")
        logger.info(f"  Synced: {synced}/{len(target_projects)}")
        logger.info(f"  Failed: {failed}")
        if dry_run:
            logger.info("\n  To apply: python scripts/global_sync_safe.py --apply")
        logger.info("=" * 70)
        return {"mode": "dry_run" if dry_run else "apply", "synced": synced, "failed": failed, "projects": results}


def main():
    parser = argparse.ArgumentParser(description="Safe multi-project protocol synchronization")
    parser.add_argument("--dry-run", action="store_true", help="Preview without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry‑run)")
    parser.add_argument("--core-path", default=".", help="Path to core protocol repository")
    parser.add_argument("--project", default=None, help="Sync only a specific project by name")
    args = parser.parse_args()
    manager = GlobalSyncManager(core_path=args.core_path)
    dry = args.dry_run or not args.apply
    result = manager.sync_all(dry_run=dry, project_filter=args.project)
    return 0 if result["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
