#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_external_audit_phases.py — endurece el contrato de 00 audit.

Valida los artefactos de una auditoría exterior por fases 0-6 y, en Fase 0,
cruza el inventario de controles heredados contra el árbol vivo del target.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


PHASE0_REQUIRED = (
    "repo_profile.json",
    "legacy_controls_inventory.json",
    "privacy_check.md",
    "purge_plan.md",
    "phase_0_purge_result.md",
)
PHASE1_REQUIRED = (
    "claims.json",
    "commands_detected.json",
    "CONTRATO_INFERIDO.md",
    "github_surface_check.md",
)
PHASE2_REQUIRED = (
    "execution_log.txt",
    "ui_backend_trace.md",
    "human_flow_evidence.md",
)
PHASE3_REQUIRED = ("claim_matrix.csv", "evidence_index.json")
PHASE4_REQUIRED = ("gs_mapping.json", "gs_gaps.md")
PHASE5_REQUIRED = ("adversarial_findings.md", "theater_findings.md")
PHASE6_REQUIRED = ("verdict.md", "repair_plan.md")

CLAIM_STATUSES = {
    "VERIFIED",
    "PARTIAL",
    "UNTESTED",
    "FALSE",
    "UNKNOWN",
    "NOT_APPLICABLE",
}
GS_MAPPING_STATUSES = {
    "covered_by_test",
    "covered_by_guard",
    "advisory_only",
    "missing_required_guard",
    "not_applicable_with_reason",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_json(path: Path):
    return json.loads(_read_text(path))


def _looks_like_path(text: str) -> bool:
    lowered = text.strip().replace("\\", "/")
    return bool(
        lowered
        and (
            "/" in lowered
            or re.search(r"\.(py|sh|ps1|md|json|ya?ml|txt|csv|html|bat|js|css)$", lowered, re.I)
            or "cerberus" in lowered.lower()
            or "legacy" in lowered.lower()
        )
    )


def _collect_path_strings(payload) -> list[str]:
    found: set[str] = set()

    def walk(value) -> None:
        if isinstance(value, str):
            if _looks_like_path(value):
                found.add(value.replace("\\", "/").strip().lstrip("./"))
            return
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
            return
        if isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return sorted(found)


def _missing_files(results_dir: Path, names: tuple[str, ...]) -> list[str]:
    return [name for name in names if not (results_dir / name).is_file()]


def _check_non_empty(path: Path, errors: list[str], label: str) -> None:
    if not _read_text(path).strip():
        errors.append(f"{label}: {path.name} está vacío.")


def _active_legacy_controls(target_root: Path, controls: list[str]) -> list[str]:
    active: list[str] = []
    for rel in controls:
        candidate = Path(rel)
        candidate = candidate if candidate.is_absolute() else (target_root / candidate)
        candidate = candidate.resolve()
        if not candidate.exists() or not candidate.is_relative_to(target_root):
            continue
        rel_parts = candidate.relative_to(target_root).parts
        if "deprecated" not in rel_parts and "archive" not in rel_parts:
            active.append(candidate.relative_to(target_root).as_posix())
    return sorted(set(active))


def _purge_plan_mentions_inventory(purge_plan: str, controls: list[str]) -> bool:
    return any(rel in purge_plan for rel in controls[: min(len(controls), 20)])


def _purge_result_is_real(purge_result: str) -> bool:
    return any(
        token in purge_result
        for token in ("deprecated", "moved", "removed", "purged", "neutralized")
    )


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(_read_text(path).splitlines()))


def _collect_statuses(value) -> set[str]:
    found: set[str] = set()

    def walk(item) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if key == "status" and isinstance(child, str):
                    found.add(child)
                walk(child)
            return
        if isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return found


def _gs_gaps_mentions_guard(text: str) -> bool:
    return "missing_required_guard" in text or "covered_by_guard" in text


def _phase5_keyword_coverage(text: str) -> int:
    keywords = {
        "malformed": ("malform", "mal formado", "malformado"),
        "incomplete": ("incomplet", "incompleto"),
        "dependency": ("dependenc", "dependen"),
        "config": ("configur", "configuración", "configuracion"),
        "permissions": ("permiso", "permission"),
        "inconsistent": ("inconsist",),
        "false_positive": ("falso positivo", "false positive", "teatro"),
    }
    return sum(1 for patterns in keywords.values() if any(p in text for p in patterns))


def validate_phase_0(target_root: Path, results_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = _missing_files(results_dir, PHASE0_REQUIRED)
    if missing:
        errors.append(f"Fase 0: faltan artefactos requeridos: {', '.join(missing)}.")
        return errors

    for name in PHASE0_REQUIRED:
        _check_non_empty(results_dir / name, errors, "Fase 0")

    inventory = _load_json(results_dir / "legacy_controls_inventory.json")
    controls = _collect_path_strings(inventory)
    if not controls:
        errors.append("Fase 0: legacy_controls_inventory.json no contiene rutas detectables.")

    active_legacy = _active_legacy_controls(target_root, controls)

    if active_legacy:
        errors.append(
            "Fase 0: controles heredados siguen vivos en el árbol activo: "
            + ", ".join(sorted(set(active_legacy)))
        )

    purge_plan = _read_text(results_dir / "purge_plan.md")
    if controls and not _purge_plan_mentions_inventory(purge_plan, controls):
        errors.append(
            "Fase 0: purge_plan.md no referencia el inventario de controles heredados."
        )

    purge_result = _read_text(results_dir / "phase_0_purge_result.md").lower()
    if not _purge_result_is_real(purge_result):
        errors.append(
            "Fase 0: phase_0_purge_result.md no describe una purga/neutralización real."
        )

    return errors


def validate_phase_1(results_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = _missing_files(results_dir, PHASE1_REQUIRED)
    if missing:
        errors.append(f"Fase 1: faltan artefactos requeridos: {', '.join(missing)}.")
        return errors

    for name in PHASE1_REQUIRED:
        _check_non_empty(results_dir / name, errors, "Fase 1")

    inferred = _read_text(results_dir / "CONTRATO_INFERIDO.md").lower()
    for token in ("hecho", "infer", "supuesto"):
        if token not in inferred:
            errors.append(
                f"Fase 1: CONTRATO_INFERIDO.md no separa claramente hechos/inferencias/supuestos ({token})."
            )

    claims = _load_json(results_dir / "claims.json")
    if not _collect_path_strings(claims) and not claims:
        errors.append("Fase 1: claims.json está vacío o no contiene claims detectables.")

    commands = _load_json(results_dir / "commands_detected.json")
    if not _collect_path_strings(commands) and not commands:
        errors.append("Fase 1: commands_detected.json está vacío o no contiene comandos detectables.")

    if "github" not in _read_text(results_dir / "github_surface_check.md").lower():
        errors.append("Fase 1: github_surface_check.md no menciona la superficie GitHub.")

    return errors


def validate_phase_2(results_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = _missing_files(results_dir, PHASE2_REQUIRED)
    if missing:
        errors.append(f"Fase 2: faltan artefactos requeridos: {', '.join(missing)}.")
        return errors

    for name in PHASE2_REQUIRED:
        path = results_dir / name
        _check_non_empty(path, errors, "Fase 2")
        if len(_read_text(path).splitlines()) < 3:
            errors.append(f"Fase 2: {path.name} tiene muy pocas líneas para ser evidencia real.")

    return errors


def validate_phase_3(results_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = _missing_files(results_dir, PHASE3_REQUIRED)
    if missing:
        errors.append(f"Fase 3: faltan artefactos requeridos: {', '.join(missing)}.")
        return errors

    matrix_path = results_dir / "claim_matrix.csv"
    rows = _load_csv_rows(matrix_path)
    if not rows:
        errors.append("Fase 3: claim_matrix.csv no contiene filas.")
        return errors
    if "status" not in (rows[0].keys() if rows else []):
        errors.append("Fase 3: claim_matrix.csv no contiene columna 'status'.")
    for row in rows:
        status = str(row.get("status", "")).strip().upper()
        if status not in CLAIM_STATUSES:
            errors.append(f"Fase 3: status inválido en claim_matrix.csv: {status or '<vacío>'}.")

    evidence_index = _load_json(results_dir / "evidence_index.json")
    if not evidence_index:
        errors.append("Fase 3: evidence_index.json está vacío.")
    return errors


def validate_phase_4(results_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = _missing_files(results_dir, PHASE4_REQUIRED)
    if missing:
        errors.append(f"Fase 4: faltan artefactos requeridos: {', '.join(missing)}.")
        return errors

    mapping = _load_json(results_dir / "gs_mapping.json")
    found_statuses = _collect_statuses(mapping)
    if not found_statuses:
        errors.append("Fase 4: gs_mapping.json no expone estados de cobertura.")
    else:
        invalid = sorted(s for s in found_statuses if s not in GS_MAPPING_STATUSES)
        if invalid:
            errors.append("Fase 4: gs_mapping.json contiene estados inválidos: " + ", ".join(invalid))

    gaps = _read_text(results_dir / "gs_gaps.md").lower()
    if not gaps.strip():
        errors.append("Fase 4: gs_gaps.md está vacío.")
    if not _gs_gaps_mentions_guard(gaps):
        errors.append("Fase 4: gs_gaps.md no refleja mapeo de consumer guards.")
    return errors


def validate_phase_5(results_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = _missing_files(results_dir, PHASE5_REQUIRED)
    if missing:
        errors.append(f"Fase 5: faltan artefactos requeridos: {', '.join(missing)}.")
        return errors

    combined = "\n".join(_read_text(results_dir / name).lower() for name in PHASE5_REQUIRED)
    covered_count = _phase5_keyword_coverage(combined)
    if covered_count < 5:
        errors.append(
            "Fase 5: findings adversariales demasiado pobres; faltan categorías clave: "
            + "malformed, incomplete, dependency, config, permissions, inconsistent, false_positive"
        )
    return errors


def validate_phase_6(results_dir: Path) -> list[str]:
    errors: list[str] = []
    missing = _missing_files(results_dir, PHASE6_REQUIRED)
    if missing:
        errors.append(f"Fase 6: faltan artefactos requeridos: {', '.join(missing)}.")
        return errors

    verdict = _read_text(results_dir / "verdict.md").lower()
    if not any(token in verdict for token in ("approved", "rejected", "partial")):
        errors.append("Fase 6: verdict.md no contiene veredicto operativo.")
    if not any(token in verdict for token in ("risk", "riesg", "block", "bloque")):
        errors.append("Fase 6: verdict.md no enumera riesgos o bloqueos.")
    if not any(token in verdict for token in ("revalid", "recheck", "rerun", "post-fix", "post remediation", "post-remediation")):
        errors.append("Fase 6: verdict.md no confirma revalidacion post-remediacion.")

    repair_plan = _read_text(results_dir / "repair_plan.md").lower()
    if len([ln for ln in repair_plan.splitlines() if ln.strip().startswith(("-", "*", "1.", "2.", "3."))]) < 3:
        errors.append("Fase 6: repair_plan.md no parece un plan por fases accionable.")
    if not any(token in repair_plan for token in ("revalid", "recheck", "rerun", "post-fix", "post remediation", "post-remediation", "verification", "verificacion")):
        errors.append("Fase 6: repair_plan.md no incluye verificacion posterior a la remediacion.")
    return errors


def validate_external_audit(target_root: Path, results_dir: Path) -> list[str]:
    errors: list[str] = []
    phases = (
        ("Fase 0", lambda: validate_phase_0(target_root, results_dir)),
        ("Fase 1", lambda: validate_phase_1(results_dir)),
        ("Fase 2", lambda: validate_phase_2(results_dir)),
        ("Fase 3", lambda: validate_phase_3(results_dir)),
        ("Fase 4", lambda: validate_phase_4(results_dir)),
        ("Fase 5", lambda: validate_phase_5(results_dir)),
        ("Fase 6", lambda: validate_phase_6(results_dir)),
    )
    for phase_name, phase_fn in phases:
        try:
            errors.extend(phase_fn())
        except Exception as exc:
            errors.append(
                f"{phase_name}: excepción no controlada en validate_external_audit_phases.py: "
                f"{exc.__class__.__name__}: {exc}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate 00 audit exterior artifacts and phase 0-6 contract."
    )
    parser.add_argument("--target-root", required=True, help="Path to the audited repo root.")
    parser.add_argument(
        "--results-dir",
        required=True,
        help="Path to the audit results directory (e.g. 00 audit/results/exterior/<repo>/<date>).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON errors only.")
    args = parser.parse_args(argv)

    target_root = Path(args.target_root).resolve()
    results_dir = Path(args.results_dir).resolve()
    errors = validate_external_audit(target_root, results_dir)
    if args.json:
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
    else:
        if errors:
            print("[AUDIT-CONTRACT] REJECTED")
            for err in errors:
                print(f"  - {err}")
        else:
            print("[AUDIT-CONTRACT] APPROVED")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

