#!/usr/bin/env python3
"""
bump_version.py – Increment the project's semantic version.
Usage:
  python scripts/bump_version.py [major|minor|patch]
It updates VERSION.txt and optionally creates a git tag.
"""
import argparse
from pathlib import Path
import subprocess
import re

VERSION_FILE = Path(__file__).parent.parent / "VERSION.txt"

def read_version() -> str:
    if not VERSION_FILE.exists():
        raise FileNotFoundError(f"VERSION.txt not found at {VERSION_FILE}")
    return VERSION_FILE.read_text(encoding="utf-8").strip()

def write_version(new_version: str):
    VERSION_FILE.write_text(new_version + "\n", encoding="utf-8")

def bump(version: str, part: str) -> str:
    if part not in ("major", "minor", "patch"):
        raise ValueError(f"Invalid part '{part}'. Must be 'major', 'minor', or 'patch'.")
    # Expect semver like X.Y or X.Y.Z
    parts = version.split('.')
    # Pad to three parts
    while len(parts) < 3:
        parts.append('0')
    major, minor, patch = map(int, parts[:3])
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    return f"{major}.{minor}.{patch}" if len(version.split('.')) == 3 else f"{major}.{minor}"

def propagate_version(old_version: str, new_version: str, root_dir: Path = None):
    root = root_dir if root_dir is not None else Path(__file__).parent.parent
    files_to_update = [
        (root / ".agent_state.json", f'"version": "{old_version}"', f'"version": "{new_version}"'),
        (root / "scripts/hooks/pre-commit", f"v{old_version}", f"v{new_version}"),
        (root / ".git/hooks/pre-commit", f"v{old_version}", f"v{new_version}"),
        (root / "AGENT.md", f"v{old_version}", f"v{new_version}"),
        (root / "PROTOCOL_SYSTEM.md", f"v{old_version}", f"v{new_version}"),
        (root / "PROTOCOL_BEHAVIOR.md", f"v{old_version}", f"v{new_version}"),
        (root / "MANDATES_BY_PHASE.md", f"V{old_version}", f"V{new_version}"),
        (root / "MANDATES_BY_PHASE.md", f"v{old_version}", f"v{new_version}"),
        (root / "SPEC.md", f"v{old_version}", f"v{new_version}"),
        (root / "SPEC.md", f"V{old_version}", f"V{new_version}"),
        (root / ".claude/CLAUDE.md", f"v{old_version}", f"v{new_version}"),
    ]
    for filepath, target, replacement in files_to_update:
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            if target in content:
                content = content.replace(target, replacement)
                filepath.write_text(content, encoding="utf-8")
                print(f"Propagated to {filepath.name} (exact match): {target} -> {replacement}")
            else:
                # Fallback: regex replacement
                # Replace v{old_version}(\.\d+)? with v{new_version}
                pattern = re.compile(rf"[vV]{re.escape(old_version)}(?:\.\d+)?")
                if pattern.search(content):
                    content = pattern.sub(f"v{new_version}", content)
                    filepath.write_text(content, encoding="utf-8")
                    print(f"Propagated to {filepath.name} (regex): v{old_version} -> v{new_version}")

def create_git_tag(version: str):
    tag_name = f"v{version}"
    subprocess.run(["git", "tag", tag_name], check=False)
    subprocess.run(["git", "push", "origin", tag_name], check=False)

def main():
    parser = argparse.ArgumentParser(description="Bump project version.")
    parser.add_argument("part", choices=["major", "minor", "patch"], help="Which part to bump")
    parser.add_argument("--tag", action="store_true", help="Create a git tag after bump")
    args = parser.parse_args()
    current = read_version()
    new_version = bump(current, args.part)
    write_version(new_version)
    print(f"Version bumped: {current} -> {new_version}")
    propagate_version(current, new_version)
    if args.tag:
        create_git_tag(new_version)
        print(f"Git tag v{new_version} created (if git is configured).")

if __name__ == "__main__":
    main()
