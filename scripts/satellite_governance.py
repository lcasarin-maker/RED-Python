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
    ".github/workflows/audit.yml",
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
    "authorization:",
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


@dataclass(frozen=True)
class TestSurfaceRule:
    name: str
    source: str
    suggested_test_file: str
    markers: tuple[str, ...]
    notes: str = ""


@dataclass(frozen=True)
class TestSurfaceFinding:
    name: str
    source: str
    suggested_test_file: str
    status: str
    present_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    notes: str = ""


TEST_SURFACE_RULES = (
    TestSurfaceRule(
        name="CLI behavior",
        source="red.py",
        suggested_test_file="tests/test_main_cli.py",
        markers=(
            "_run_cli",
            "--dry-run",
            "--export",
            "--quiet",
            "--permanent",
        ),
        notes="Covers CLI entrypoint flags and export branches.",
    ),
    TestSurfaceRule(
        name="GUI entrypoint",
        source="red.py",
        suggested_test_file="tests/test_gui_smoke.py",
        markers=("_run_gui", "mainloop"),
        notes="Covers the GUI boot path.",
    ),
    TestSurfaceRule(
        name="Scanner contract",
        source="core.py",
        suggested_test_file="tests/test_red_core_behaviour.py",
        markers=(
            "Scanner",
            "scan_hidden",
            "follow_symlinks",
            "max_depth",
            "min_age_hours",
            "protected_dirs",
            "never_empty",
        ),
        notes="Covers the scanner's selection and filtering branches.",
    ),
    TestSurfaceRule(
        name="Cleaner contract",
        source="core.py",
        suggested_test_file="tests/test_red_core_behaviour.py",
        markers=(
            "Cleaner",
            "simulate",
            "recycle",
            "permanent",
            "on_error",
            "pause_ms",
            "max_warnings",
        ),
        notes="Covers the cleaner's deletion modes and error handling.",
    ),
    TestSurfaceRule(
        name="Rule matching helpers",
        source="filters.py",
        suggested_test_file="tests/test_filters.py",
        markers=(
            "match_rule",
            "is_file_ignored",
            "is_dir_ignored",
            "is_never_empty",
            "long_path",
            "strip_long_prefix",
            "is_hidden",
            "is_system",
            "has_only_ignorable_files",
            "collect_ignorable_files",
        ),
        notes="Dedicated tests should exist for the rule engine and file helpers.",
    ),
    TestSurfaceRule(
        name="Governance helpers",
        source="scripts/satellite_governance.py",
        suggested_test_file="tests/test_satellite_governance.py",
        markers=(
            "validate_satellite_layout",
            "validate_agent_entrypoint",
            "validate_github_home_record",
            "build_learning_event",
            "collect_worktree_changes",
        ),
        notes="Covers the onboarding and learning governance helpers.",
    ),
)


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


def _load_test_texts(root: Path | str) -> dict[str, str]:
    root_path = Path(root).resolve()
    tests_dir = root_path / "tests"
    texts: dict[str, str] = {}
    if not tests_dir.is_dir():
        return texts
    for path in sorted(tests_dir.glob("test_*.py")):
        if path.is_file():
            texts[path.name] = path.read_text(encoding="utf-8")
    return texts


def evaluate_test_surface(root: Path | str) -> list[TestSurfaceFinding]:
    root_path = Path(root).resolve()
    test_texts = _load_test_texts(root_path)
    findings: list[TestSurfaceFinding] = []

    for rule in TEST_SURFACE_RULES:
        source_present = (root_path / rule.source).is_file()
        if not source_present:
            findings.append(
                TestSurfaceFinding(
                    name=rule.name,
                    source=rule.source,
                    suggested_test_file=rule.suggested_test_file,
                    status="missing-source",
                    present_markers=(),
                    missing_markers=rule.markers,
                    notes=rule.notes,
                )
            )
            continue

        present = tuple(
            marker
            for marker in rule.markers
            if any(marker in text for text in test_texts.values())
        )
        missing = tuple(marker for marker in rule.markers if marker not in present)
        if len(present) == len(rule.markers):
            status = "covered"
        elif present:
            status = "partial"
        else:
            status = "missing"

        findings.append(
            TestSurfaceFinding(
                name=rule.name,
                source=rule.source,
                suggested_test_file=rule.suggested_test_file,
                status=status,
                present_markers=present,
                missing_markers=missing,
                notes=rule.notes,
            )
        )

    return findings


def format_test_surface_report(findings: list[TestSurfaceFinding]) -> list[str]:
    lines = ["Test surface report:"]
    covered = partial = missing = source_missing = 0

    for finding in findings:
        if finding.status == "covered":
            covered += 1
        elif finding.status == "partial":
            partial += 1
        elif finding.status == "missing":
            missing += 1
        else:
            source_missing += 1

        lines.append(
            f"- {finding.name} ({finding.source}) -> {finding.status}"
        )
        if finding.present_markers:
            lines.append(f"  present: {', '.join(finding.present_markers)}")
        if finding.missing_markers:
            lines.append(f"  missing: {', '.join(finding.missing_markers)}")
            lines.append(f"  suggested test file: {finding.suggested_test_file}")
        if finding.notes:
            lines.append(f"  note: {finding.notes}")

    lines.append(
        f"Summary: {covered} covered, {partial} partial, {missing} missing, {source_missing} missing-source."
    )
    return lines


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
    print()
    for line in format_test_surface_report(evaluate_test_surface(args.root)):
        print(line)
    return 0


def _cmd_test_surface(args: argparse.Namespace) -> int:
    findings = evaluate_test_surface(args.root)
    for line in format_test_surface_report(findings):
        print(line)
    if args.strict and any(f.status != "covered" for f in findings):
        return 1
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

    surface = sub.add_parser(
        "test-surface",
        help="Report the ideal test surface inferred from the repo",
    )
    surface.add_argument("--root", type=Path, default=Path("."))
    surface.add_argument("--strict", action="store_true")
    surface.set_defaults(func=_cmd_test_surface)

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
