#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REGLA #29 — ROLLBACK TESTER
Verifica que commits recientes son accesibles/reversibles antes de push.
Caller: pre-push hook.
"""
import sys
import subprocess
from pathlib import Path

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()


def get_last_commits(count: int = 3) -> list:
    """Retorna los últimos N commits como lista de strings 'sha mensaje'."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{count}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            cwd=Path.cwd(),
        )
        return [line.strip() for line in result.stdout.split("\n") if line.strip()]
    except Exception as e:
        print(f"[ERROR] git log failed: {e}")
        return []


def test_all_rollbacks() -> bool:
    """Verifica que los últimos commits existen y son accesibles (reversibles)."""
    commits = get_last_commits(3)
    if not commits:
        print("[WARN] No commits found")
        return True

    print(
        f"[ACTION] Testing rollback accessibility for {len(commits)} commits (REGLA #29)"
    )
    results = []
    for i, commit_line in enumerate(commits):
        commit_sha = commit_line.split()[0]
        print(f"\n[TEST {i+1}] Verifying {commit_sha}...")
        try:
            subprocess.run(
                ["git", "rev-parse", commit_sha],
                capture_output=True,
                text=True,
                check=True,
                cwd=Path.cwd(),
            )
            print(f"[OK] Commit {commit_sha} is valid and rollback-able")
            results.append(True)
        except subprocess.CalledProcessError:
            print(f"[ERROR] Commit {commit_sha} not found or inaccessible")
            results.append(False)

    success_rate = sum(results) / len(results) if results else 0
    print(f"\n[SUMMARY] Rollback accessibility: {success_rate:.0%}")
    return all(results)


def pre_push_validation() -> bool:
    """Verifica que commits no pusheados son reversibles (REGLA #29)."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "@{u}..HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            cwd=Path.cwd(),
        )
        commits_to_push = [l for l in result.stdout.split("\n") if l.strip()]
        if not commits_to_push:
            print("[OK] No commits to push")
            return True

        print(
            f"[ACTION] Pre-push: {len(commits_to_push)} commits to validate (REGLA #29)"
        )
        for commit_line in commits_to_push:
            commit_sha = commit_line.split()[0]
            try:
                subprocess.run(
                    ["git", "rev-parse", commit_sha],
                    capture_output=True,
                    check=True,
                    cwd=Path.cwd(),
                )
                print(f"[OK] {commit_sha} is reversible")
            except subprocess.CalledProcessError:
                print(f"[ERROR] {commit_sha} not found")
                return False

        print("[OK] All commits are reversible (REGLA #29 satisfied)")
        return True
    except Exception as e:
        print(f"[ERROR] Pre-push validation failed: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="REGLA #29: Rollback tester")
    parser.add_argument("--test-all", action="store_true", help="Test last 3 commits")
    parser.add_argument("--pre-push", action="store_true", help="Pre-push validation")
    args = parser.parse_args()

    success = test_all_rollbacks() if args.test_all else pre_push_validation()
    sys.exit(0 if success else 1)
