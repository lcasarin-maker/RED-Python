#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Satellite governance helpers for onboarding, supervision, and learning.

This module stays stdlib-only so it can be used early in the onboarding flow.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REQUIRED_LAYOUT = (
    "README.md",
    "AGENT.md",
    "STATUS.md",
    "docs/onboarding/SATELLITE_ONBOARDING.md",
    "docs/supervision/SATELLITE_SUPERVISION.md",
    "docs/supervision/GITHUB_HOME.md",
    "docs/learning/SATELLITE_LEARNING_FLOW.md",
    "docs/DEBT_LEDGER.md",
    "docs/learning/LEARNING_EVENT_SCHEMA.json",
    "docs/learning/LEARNING_EVENT_TEMPLATE.json",
    "Wiki/Index.md",
    "Wiki/Home.md",
    "Wiki/Onboarding.md",
    "Wiki/Supervision.md",
    "Wiki/Learning.md",
    "Wiki/Graph.md",
)

AGENT_ENTRYPOINT_HINTS = (
    "docs/onboarding/SATELLITE_ONBOARDING.md",
    "docs/supervision/SATELLITE_SUPERVISION.md",
    "docs/learning/SATELLITE_LEARNING_FLOW.md",
)

GITHUB_HOME_HINTS = (
    "remote:",
    "branch:",
    "visibility:",
    "confirmed_by:",
    "confirmed_at_utc:",
)


@dataclass(frozen=True)
class LearningSignal:
    source: str
    category: str
    summary: str
    root_cause: str
    fix: str
    evidence: tuple[str, ...]
    scope: str = "local"
    recommendation: str = "keep-local"
    impact: str = ""
    token_savings: str = ""
    notes: str = ""

    def to_event(self, repo: str, timestamp_utc: str | None = None) -> dict:
        return {
            "schema_version": "1.0",
            "repo": repo,
            "source": self.source,
            "timestamp_utc": timestamp_utc
            or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "category": self.category,
            "summary": self.summary,
            "root_cause": self.root_cause,
            "fix": self.fix,
            "evidence": list(self.evidence),
            "scope": classify_scope(self),
            "recommendation": self.recommendation,
            "impact": self.impact,
            "token_savings": self.token_savings,
            "notes": self.notes,
        }


def classify_scope(signal: LearningSignal) -> str:
    scope = signal.scope.strip().lower()
    if scope in {"local", "cc", "gs"}:
        return scope
    if signal.recommendation == "promote-gs":
        return "gs"
    if signal.recommendation == "promote-cc":
        return "cc"
    return "local"


def validate_satellite_layout(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    missing = []
    for rel in REQUIRED_LAYOUT:
        if not (root_path / rel).is_file():
            missing.append(rel)
    return missing


def validate_agent_entrypoint(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    agent_path = root_path / "AGENT.md"
    if not agent_path.is_file():
        return ["AGENT.md"]

    content = agent_path.read_text(encoding="utf-8")
    missing = [hint for hint in AGENT_ENTRYPOINT_HINTS if hint not in content]
    return missing


def validate_github_home_record(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    record_path = root_path / "docs" / "supervision" / "GITHUB_HOME.md"
    if not record_path.is_file():
        return ["docs/supervision/GITHUB_HOME.md"]

    content = record_path.read_text(encoding="utf-8").lower()
    missing = [hint for hint in GITHUB_HOME_HINTS if hint not in content]
    return missing


def load_learning_event(path: Path | str) -> dict:
    event_path = Path(path)
    data = json.loads(event_path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "repo",
        "source",
        "timestamp_utc",
        "category",
        "summary",
        "root_cause",
        "fix",
        "evidence",
        "scope",
        "recommendation",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if not isinstance(data["evidence"], list) or not data["evidence"]:
        raise ValueError("evidence must be a non-empty list")
    return data


def build_learning_event(signal: LearningSignal, repo: str) -> dict:
    return signal.to_event(repo=repo)


def git_remote_present(root: Path | str) -> bool:
    root_path = Path(root).resolve()
    result = subprocess.run(
        ["git", "remote", "-v"],
        cwd=str(root_path),
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def collect_worktree_changes(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    result = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=str(root_path),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("unable to inspect git status")
    entries = []
    for line in result.stdout.splitlines():
        line = line.rstrip()
        if line:
            entries.append(line)
    return entries


def _cmd_validate(args: argparse.Namespace) -> int:
    missing = validate_satellite_layout(args.root)
    if missing:
        print("Missing satellite artifacts:")
        for item in missing:
            print(f"- {item}")
        return 1

    entrypoint_missing = validate_agent_entrypoint(args.root)
    if entrypoint_missing:
        print("AGENT.md must point to the onboarding, supervision, and learning docs.")
        for item in entrypoint_missing:
            print(f"- {item}")
        return 1

    if not git_remote_present(args.root):
        print("Missing Git remote configuration.")
        return 1

    github_home_missing = validate_github_home_record(args.root)
    if github_home_missing:
        print("GitHub home record is missing or incomplete.")
        for item in github_home_missing:
            print(f"- {item}")
        return 1

    print("Satellite layout is complete, Git remote is configured, and GitHub home is recorded.")
    return 0


def _cmd_review_changes(args: argparse.Namespace) -> int:
    entries = collect_worktree_changes(args.root)
    if not entries:
        print("Worktree is clean.")
        return 0

    print("Worktree changes must be reviewed, absorbed, validated, discarded, or quarantined.")
    for entry in entries:
        print(entry)
    print(f"Total changed paths: {len(entries)}")
    return 0


def _cmd_emit_template(args: argparse.Namespace) -> int:
    signal = LearningSignal(
        source=args.source,
        category=args.category,
        summary=args.summary,
        root_cause=args.root_cause,
        fix=args.fix,
        evidence=tuple(args.evidence),
        scope=args.scope,
        recommendation=args.recommendation,
        impact=args.impact or "",
        token_savings=args.token_savings or "",
        notes=args.notes or "",
    )
    event = build_learning_event(signal, repo=args.repo)
    print(json.dumps(event, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Satellite governance helper")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate the satellite layout")
    validate.add_argument("--root", type=Path, default=Path("."))
    validate.set_defaults(func=_cmd_validate)

    review = sub.add_parser(
        "review-changes",
        help="List worktree changes so foreign edits cannot be skipped",
    )
    review.add_argument("--root", type=Path, default=Path("."))
    review.set_defaults(func=_cmd_review_changes)

    emit = sub.add_parser("emit-template", help="Emit a learning event packet")
    emit.add_argument("--repo", required=True)
    emit.add_argument("--source", required=True)
    emit.add_argument("--category", required=True)
    emit.add_argument("--summary", required=True)
    emit.add_argument("--root-cause", required=True)
    emit.add_argument("--fix", required=True)
    emit.add_argument("--evidence", nargs="+", required=True)
    emit.add_argument("--scope", default="local")
    emit.add_argument("--recommendation", default="keep-local")
    emit.add_argument("--impact", default="")
    emit.add_argument("--token-savings", default="")
    emit.add_argument("--notes", default="")
    emit.set_defaults(func=_cmd_emit_template)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
