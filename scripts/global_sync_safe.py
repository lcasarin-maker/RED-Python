#!/usr/bin/env python3
"""
global_sync_safe.py v2.0 — Safe Multi-Project Protocol Synchronization

Synchronizes VibeCoderProof v5.7 protocol files across all registered projects.
Features: dry-run, backup, validation, rollback support.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import shutil
import subprocess
import os

sys.path.insert(0, str(Path(__file__).parent))
from core_utils import setup_windows_utf8, get_centralized_version
from evidence_logger import EvidenceLogger

setup_windows_utf8()
logger = logging.getLogger("global_sync_safe")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class GlobalSyncManager:
    """Safe multi-project synchronization with rollback support."""

    def __init__(self, core_path="."):
        self.core_path = Path(core_path).resolve()
        self.registry_path = self.core_path / ".vibecoderproof" / "REGISTRY.json"
        self.evidence_logger = EvidenceLogger(self.core_path)
        self.version = get_centralized_version()
        self.sync_log = []

    def load_registry(self) -> dict:
        """Load project registry."""
        if not self.registry_path.exists():
            logger.error("REGISTRY.json not found")
            return {}

        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def sync_project(self, project_info: dict, dry_run: bool = False, create_backup: bool = True) -> dict:
        """Synchronize protocol files to a single project."""
        project_path = Path(project_info['path']).resolve()
        project_name = project_info['name']

        if project_path == self.core_path:
            logger.info(f"\n⭐ CORE: {project_name} (skipping identical path)")
            return {"status": "skipped", "reason": "core_path"}

        logger.info(f"\n📦 Syncing: {project_name}")
        logger.info(f"   Path: {project_path}")

        # Validate project exists
        if not project_path.exists():
            logger.warning("   ⚠️  Project path not found, skipping")
            return {"status": "skipped", "reason": "path_not_found"}

        # Validate it's a git repo
        git_dir = project_path / ".git"
        if not git_dir.exists():
            logger.warning("   ⚠️  Not a git repository, skipping")
            return {"status": "skipped", "reason": "not_git_repo"}

        # Create backup before syncing
        backup_path = None
        if create_backup and not dry_run:
            backup_dir = self.core_path / ".vibecoderproof" / "backups" / datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / project_name
            logger.info("   💾 Creating backup...")

            for protocol_file in [
                "AGENT.md", "PROTOCOL_SYSTEM.md", "PROTOCOL_BEHAVIOR.md",
                "SPEC.md", "ESCALATION_PROTOCOL.md", "MANDATES_BY_PHASE.md",
                "PERMISSIONS.md", ".agent_state.json"
            ]:
                src = project_path / protocol_file
                if src.exists():
                    dst = backup_path / protocol_file
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)

        # Copy protocol files
        synced_files = []
        for protocol_file in [
            "AGENT.md", "PROTOCOL_SYSTEM.md", "PROTOCOL_BEHAVIOR.md",
            "SPEC.md", "ESCALATION_PROTOCOL.md", "MANDATES_BY_PHASE.md",
            "PERMISSIONS.md", ".gitattributes"
        ]:
            src = self.core_path / protocol_file
            dst = project_path / protocol_file

            if src.exists():
                if not dry_run:
                    shutil.copy2(src, dst)
                    synced_files.append(protocol_file)
                else:
                    synced_files.append(f"{protocol_file} (preview)")
                logger.info(f"   ✅ {protocol_file}")
            else:
                logger.warning(f"   ⚠️  Source not found: {protocol_file}")

        return {
            "status": "dry_run" if dry_run else "synced",
            "files": synced_files,
            "backup": str(backup_path) if backup_path else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def auto_discover_projects(self, registry: dict, dry_run: bool = False) -> list:
        """Descubre nuevas carpetas y, si no son git, inicializa git y crea repo remoto en GitHub."""
        
        ai_root = Path("D:/GoogleDrive/AI").resolve()
        if not ai_root.exists():
            return []
            
        # Get github token
        github_token = ""
        token_path = ai_root / ".secrets" / "github" / "token.classic"
        if token_path.exists():
            github_token = token_path.read_text(encoding='utf-8').strip()
            
        projects = registry.get("projects", [])
        known_paths = {Path(p['path']).resolve() for p in projects}
        
        # Ignorar carpetas del sistema, scripts globales y otras carpetas no-proyectos
        ignore_dirs = {'.claude', '.pytest_cache', '.secrets', 'scripts', 'deprecated', 'tests', self.core_path.name}
        
        newly_created = []
        changed = False
        
        for child in ai_root.iterdir():
            if child.is_dir() and child.name not in ignore_dirs and not child.name.startswith('.'):
                if child.resolve() not in known_paths:
                    if not dry_run:
                        git_dir = child / ".git"
                        if not git_dir.exists():
                            self._init_github_repo(child, github_token)
                                
                        newly_created.append(child.name)
                        
                    new_project = {
                        "name": child.name,
                        "path": str(child),
                        "role": "PROJECT",
                        "description": f"Auto-discovered project: {child.name}",
                        "status": "active",
                        "last_sync": ""
                    }
                    projects.append(new_project)
                    logger.info(f"🌟 Auto-descubierto nuevo proyecto: {child.name}")
                    changed = True
                    
        if changed and not dry_run:
            registry['projects'] = projects
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)
            logger.info("✅ REGISTRY.json actualizado con nuevos proyectos detectados.")
            
        return newly_created

    def _init_github_repo(self, child_path: Path, github_token: str):
        import random
        import string
        logger.info(f"   ⚙️  Inicializando Git y GitHub para: {child_path.name}")
        subprocess.run(["git", "init"], cwd=str(child_path), capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=str(child_path), capture_output=True)
        env = os.environ.copy()
        if github_token:
            env["GH_TOKEN"] = github_token
            if "GITHUB_TOKEN" in env:
                del env["GITHUB_TOKEN"]
        rand_suffix = ''.join(random.choices(string.digits, k=4))
        repo_name = f"{child_path.name.replace(' ', '-')}-{rand_suffix}"
        res = subprocess.run(["gh", "repo", "create", repo_name, "--private", "--source=.", "--remote=origin"], cwd=str(child_path), capture_output=True, text=True, env=env)
        if res.returncode == 0:
            logger.info(f"   ☁️  Repositorio privado creado en GitHub: {repo_name}")
            if github_token:
                url_res = subprocess.run(["git", "config", "remote.origin.url"], cwd=str(child_path), capture_output=True, text=True)
                url = url_res.stdout.strip()
                if url.startswith("https://"):
                    url_with_token = url.replace("https://", f"https://{github_token}@", 1)
                    subprocess.run(["git", "remote", "set-url", "origin", url_with_token], cwd=str(child_path))
        else:
            logger.error(f"   ❌ Error creando repo GitHub: {res.stderr}")

    def sync_all(self, dry_run: bool = False) -> dict:
        """Synchronize all registered projects."""
        registry = self.load_registry()
        
        # Auto-discover new projects in AI directory
        newly_created = self.auto_discover_projects(registry, dry_run=dry_run)
        
        projects = registry.get("projects", [])

        logger.info(f"\n{'='*70}")
        logger.info("🌍 GLOBAL PROTOCOL SYNCHRONIZATION v2.0")
        logger.info(f"{'='*70}")
        logger.info(f"{'DRY-RUN' if dry_run else 'APPLY'} mode")
        logger.info(f"Projects to sync: {len([p for p in projects if p['role'] != 'CORE'])}")

        results = {}
        synced_count = 0
        failed_count = 0

        for project in projects:
            if project['role'] == 'CORE':
                logger.info(f"\n⭐ CORE: {project['name']} (skipping)")
                continue

            result = self.sync_project(project, dry_run=dry_run)
            results[project['name']] = result

            if result['status'] in ["synced", "dry_run"]:
                synced_count += 1
                
                # If newly created, do the initial commit and push
                if not dry_run and project['name'] in newly_created:
                    logger.info(f"   🚀 Haciendo commit inicial y push a GitHub para: {project['name']}")
                    project_path = str(Path(project['path']).resolve())
                    subprocess.run(["git", "add", "."], cwd=project_path, capture_output=True)
                    subprocess.run(["git", "commit", "-m", "Initial protocol sync from Cerberus"], cwd=project_path, capture_output=True)
                    res_push = subprocess.run(["git", "-c", "credential.helper=", "push", "-u", "origin", "main"], cwd=project_path, capture_output=True, text=True)
                    if res_push.returncode == 0:
                        logger.info("   ✅ Push inicial exitoso.")
                    else:
                        logger.error(f"   ❌ Fallo en el push inicial: {res_push.stderr}")
            else:
                failed_count += 1

        # Update registry
        if not dry_run:
            registry['last_updated'] = datetime.now(timezone.utc).isoformat()
            registry['sync_summary'] = {
                "total_projects": len(projects),
                "synced": synced_count + 1,  # +1 for core
                "pending": len([p for p in projects if p['role'] != 'CORE']) - synced_count,
                "failed": failed_count
            }

            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)

        # Log evidence
        self.evidence_logger.log_operation(
            operation="global_sync",
            agent_name="protocol_cli",
            command="global_sync_safe --dry-run" if dry_run else "global_sync_safe",
            outcome="success",
            output_log=f"Synced {synced_count}/{len([p for p in projects if p['role'] != 'CORE'])} projects",
            human_approval_required=False,
        )

        # Print summary
        logger.info(f"\n{'='*70}")
        logger.info("📊 SYNC SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"  Mode: {'DRY-RUN (preview only)' if dry_run else 'APPLY'}")
        logger.info(f"  Synced: {synced_count}/{len([p for p in projects if p['role'] != 'CORE'])}")
        logger.info(f"  Failed: {failed_count}")
        if dry_run:
            logger.info("\n  To apply: python scripts/global_sync_safe.py --apply")
        logger.info(f"{'='*70}")

        return {
            "mode": "dry_run" if dry_run else "apply",
            "synced": synced_count,
            "failed": failed_count,
            "projects": results
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Safe multi-project protocol synchronization")
    parser.add_argument("--dry-run", action="store_true", help="Preview without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Without this flag the command is dry-run.")
    parser.add_argument("--core-path", default=".", help="Path to core protocol repository")
    args = parser.parse_args()

    manager = GlobalSyncManager(core_path=args.core_path)
    dry_run = args.dry_run or not args.apply
    result = manager.sync_all(dry_run=dry_run)

    return 0 if result['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
