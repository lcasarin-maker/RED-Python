#!/usr/bin/env python3
"""Tests falsables del contrato de auditoría exterior por fases."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_external_audit_phases import validate_external_audit


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_common_phase_artifacts(results_dir: Path) -> None:
    _write(
        results_dir / "repo_profile.json",
        json.dumps({"git": {"branch": "main", "remote": "origin"}, "clean": True}, indent=2),
    )
    _write(
        results_dir / "legacy_controls_inventory.json",
        json.dumps({"controls": ["scripts/old_cerberus.py"]}, indent=2),
    )
    _write(results_dir / "privacy_check.md", "# Privacy\nprivate by default\n")
    _write(results_dir / "purge_plan.md", "Purge scripts/old_cerberus.py from active tree.\n")
    _write(
        results_dir / "phase_0_purge_result.md",
        "Removed and neutralized legacy Cerberus controls into deprecated/.\n",
    )

    _write(
        results_dir / "claims.json",
        json.dumps([{"id": "C1", "claim": "README describes install"}], indent=2),
    )
    _write(
        results_dir / "commands_detected.json",
        json.dumps({"commands": ["python -m pytest -q"]}, indent=2),
    )
    _write(
        results_dir / "CONTRATO_INFERIDO.md",
        "# Hechos\n- README present\n\n# Inferencias\n- install command exists\n\n# Supuestos\n- app has no UI\n",
    )
    _write(results_dir / "github_surface_check.md", "GitHub surface aligned with README.\n")

    _write(results_dir / "execution_log.txt", "1. python -m pytest -q\n2. exit 0\n3. artifacts saved\n")
    _write(results_dir / "ui_backend_trace.md", "No UI in this target; backend trace verified.\nline2\nline3\n")
    _write(results_dir / "human_flow_evidence.md", "Happy path and angry path documented.\nline2\nline3\n")

    _write(
        results_dir / "claim_matrix.csv",
        "claim,status,evidence\nC1,VERIFIED,README.md\nC2,PARTIAL,commands_detected.json\n",
    )
    _write(results_dir / "evidence_index.json", json.dumps({"C1": ["README.md"]}, indent=2))

    _write(
        results_dir / "gs_mapping.json",
        json.dumps(
            {
                "D1": [{"rule": "GS-001", "status": "covered_by_guard"}],
                "D2": [{"rule": "GS-002", "status": "missing_required_guard"}],
            },
            indent=2,
        ),
    )
    _write(
        results_dir / "gs_gaps.md",
        "missing_required_guard: consumer guard required for stale purge.\ncovered_by_guard: phase 0 purge gate.\n",
    )

    _write(
        results_dir / "adversarial_findings.md",
        "Malformed inputs, incomplete states, dependency gaps, config issues,\npermissions problems, inconsistent data and false positives were tested.\n",
    )
    _write(
        results_dir / "theater_findings.md",
        "No theater detected beyond expected false positive checks.\n",
    )

    _write(
        results_dir / "verdict.md",
        "REJECTED until purge gate is satisfied; risk is medium and blocking; requires post-remediation recheck.\n",
    )
    _write(
        results_dir / "repair_plan.md",
        "1. Fix purge evidence.\n2. Validate claims.\n3. Rerun adversarial phase.\n",
    )


def test_validator_blocks_active_legacy_controls(tmp_path):
    target = tmp_path / "target"
    results = tmp_path / "results"
    active = target / "scripts" / "old_cerberus.py"
    active.parent.mkdir(parents=True, exist_ok=True)
    active.write_text("print('legacy cerberus')\n", encoding="utf-8")
    _write(target / "deprecated" / "old_cerberus.py", "print('deprecated')\n")
    _write_common_phase_artifacts(results)

    errors = validate_external_audit(target, results)
    assert any("controles heredados siguen vivos" in err for err in errors)

    active.unlink()
    clean_errors = validate_external_audit(target, results)
    assert not any("controles heredados siguen vivos" in err for err in clean_errors)


def test_validator_accepts_complete_contract(tmp_path):
    target = tmp_path / "target"
    results = tmp_path / "results"
    _write(target / "deprecated" / "old_cerberus.py", "print('deprecated')\n")
    _write_common_phase_artifacts(results)

    errors = validate_external_audit(target, results)
    assert errors == [], f"Unexpected contract errors: {errors}"
