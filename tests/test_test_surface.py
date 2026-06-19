from __future__ import annotations

from pathlib import Path

from scripts.satellite_governance import evaluate_test_surface, format_test_surface_report


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_test_surface_detects_covered_and_missing_areas(tmp_path):
    root = tmp_path
    _write(root / "red.py")
    _write(root / "core.py")
    _write(root / "filters.py")
    _write(root / "scripts" / "satellite_governance.py")

    _write(
        root / "tests" / "test_main_cli.py",
        "\n".join(
            [
                "_run_cli",
                "--dry-run",
                "--export",
                "--quiet",
                "--permanent",
            ]
        ),
    )
    _write(
        root / "tests" / "test_gui_smoke.py",
        "\n".join(["_run_gui", "mainloop"]),
    )
    _write(
        root / "tests" / "test_red_core_behaviour.py",
        "\n".join(
            [
                "Scanner",
                "scan_hidden",
                "follow_symlinks",
                "max_depth",
                "min_age_hours",
                "protected_dirs",
                "never_empty",
                "Cleaner",
                "simulate",
                "recycle",
                "permanent",
                "on_error",
                "pause_ms",
                "max_warnings",
            ]
        ),
    )
    _write(
        root / "tests" / "test_satellite_governance.py",
        "\n".join(
            [
                "validate_satellite_layout",
                "validate_agent_entrypoint",
                "validate_github_home_record",
                "build_learning_event",
                "collect_worktree_changes",
            ]
        ),
    )

    findings = evaluate_test_surface(root)
    by_name = {finding.name: finding for finding in findings}

    assert by_name["CLI behavior"].status == "covered"
    assert by_name["GUI entrypoint"].status == "covered"
    assert by_name["Scanner contract"].status == "covered"
    assert by_name["Cleaner contract"].status == "covered"
    assert by_name["Governance helpers"].status == "covered"
    assert by_name["Rule matching helpers"].status == "missing"

    report = format_test_surface_report(findings)
    assert report[0] == "Test surface report:"
    assert report[-1].startswith("Summary:")
