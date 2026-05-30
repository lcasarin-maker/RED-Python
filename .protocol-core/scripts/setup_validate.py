#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SETUP VALIDATOR (MINIMAL) — CoderCerberus Stack Bootstrap
Fast validation for pre-commit hook. Checks ONLY essential items (<1sec).
"""

import json
import shutil
import sys
from pathlib import Path

_TOTAL_CHECKS = 6



class MinimalValidator:
    def __init__(self):
        self.root = Path(".")
        self.errors = []
        self.ok = 0
        self.is_satellite = (self.root / ".protocol-core").is_dir()
        self.protocol_base = self.root / ".protocol-core" if self.is_satellite else self.root


    def check_python_version(self):
        """Python 3.10+"""
        if sys.version_info < (3, 10):
            self.errors.append(f"Python 3.10+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        else:
            self.ok += 1

    def check_essential_files(self):
        """Only files that block execution"""
        essential = ["PROTOCOL_SYSTEM.md", "PROTOCOL_BEHAVIOR.md", "AGENT.md"]
        missing = [f for f in essential if not (self.protocol_base / f).exists()]
        
        # Check for .agent_state.json in either root or protocol_base
        state_in_root = (self.root / ".agent_state.json").exists()
        state_in_base = (self.protocol_base / ".agent_state.json").exists()
        if not (state_in_root or state_in_base):
            missing.append(".agent_state.json")
            
        if missing:
            self.errors.append(f"Missing: {', '.join(missing)}")
        else:
            self.ok += 1

    def check_git_in_path(self):
        """git must be available on PATH (VT-107)"""
        if shutil.which("git") is None:
            self.errors.append("git not found on PATH — 3-tier governance requires git")
        else:
            self.ok += 1

    def check_pre_commit_hook(self):
        """Pre-commit hook must exist and be executable (VT-105)"""
        hook = self.root / ".git" / "hooks" / "pre-commit"
        import os
        if not hook.exists():
            self.errors.append(
                "Missing .git/hooks/pre-commit — install with: "
                "cp scripts/hooks/pre-commit .git/hooks/ && chmod +x .git/hooks/pre-commit"
            )
        elif not os.access(hook, os.X_OK):
            self.errors.append(".git/hooks/pre-commit exists but is not executable")
        else:
            self.ok += 1

    def check_registry_parseable(self):
        """.protocol/metadata/REGISTRY.json must be valid JSON"""
        registry = self.protocol_base / ".protocol" / "metadata" / "REGISTRY.json"
        if not registry.exists():
            path_str = f".protocol-core/.protocol/metadata/REGISTRY.json" if self.is_satellite else ".protocol/metadata/REGISTRY.json"
            self.errors.append(f"{path_str} missing — project registry required")
            return
        try:
            json.loads(registry.read_text(encoding='utf-8'))
            self.ok += 1
        except Exception as e:
            self.errors.append(f"REGISTRY.json is not valid JSON: {e}")

    def check_protocol_write_access(self):
        """Write access to .protocol/ must be available"""
        protocol_dir = self.protocol_base / ".protocol"
        if not protocol_dir.exists():
            path_str = f".protocol-core/.protocol/" if self.is_satellite else ".protocol/"
            self.errors.append(f"{path_str} directory missing — evidence storage unavailable")
            return
        probe = protocol_dir / ".write_test"
        try:
            probe.write_text("ok", encoding='utf-8')
            probe.unlink()
            self.ok += 1
        except OSError as e:
            self.errors.append(f".protocol/ not writable: {e}")

    def _heal_satellite_config(self):
        """Automatic healing of satellite .claude directory (P5.1 self-healing)"""
        if not self.is_satellite:
            return
        src_claude = self.root / ".protocol-core" / ".claude"
        dst_claude = self.root / ".claude"
        if not src_claude.is_dir():
            return
        dst_claude.mkdir(parents=True, exist_ok=True)
        for f in ["settings.json", "settings.template.json", "CLAUDE.md", ".gitignore"]:
            src_file = src_claude / f
            dst_file = dst_claude / f
            if not src_file.exists():
                continue
            if dst_file.exists():
                continue
            try:
                shutil.copy2(src_file, dst_file)
                print(f"      [HEAL] Copied missing satellite config: {f}")
            except Exception as e:
                print(f"      [WARN] Could not copy {f}: {e}")

    def run(self):
        """Execute validations"""
        self._heal_satellite_config()

        self.check_python_version()
        self.check_essential_files()
        self.check_git_in_path()
        self.check_pre_commit_hook()
        self.check_registry_parseable()
        self.check_protocol_write_access()

        if self.errors:
            print(f"[BOOTSTRAP FAIL] {len(self.errors)} error(s):", file=sys.stderr)
            for err in self.errors:
                print(f"  x {err}", file=sys.stderr)
            return 1

        print(f"[BOOTSTRAP OK] Stack ready ({self.ok}/{_TOTAL_CHECKS} checks)", file=sys.stdout)
        return 0

if __name__ == "__main__":
    sys.exit(MinimalValidator().run())
