#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cobertura adversarial (D8) — paths negativos REALES de D13.

Sprint 28.5 Paso 3: salda deuda preexistente — las funciones enhanced de los
Sprints 24-28 estaban importadas en tests sin path negativo, dejando el gate 12D
en RED. Cada test ejerce un modo de fallo concreto (no token-stuffing).
(Los paths negativos de d11 migraron a test_d11_dependency.py al consolidar D11.)"""
import pytest

from dimensions.d13_observable import (
    count_tokens,
    DecisionLogger,
    DivergenceDetector,
    D13Report,
)


def test_count_tokens_missing_file_returns_zero(tmp_path):
    """Archivo inexistente => 0, no excepción que tumbe al medidor."""
    assert count_tokens(str(tmp_path / "no_such.md")) == 0


def test_divergence_detector_without_agent_md_denies_action(tmp_path):
    """Sin AGENT.md no hay reglas => acción desconocida cae a no-permitida (fail-closed)."""
    det = DivergenceDetector(agent_md_path=str(tmp_path / "missing_AGENT.md"))
    assert det.can_do == set()
    assert det.cannot_do == set()
    verdict = det.check("delete")
    assert verdict["allowed"] is False
    assert verdict["severity"] == "WARNING"


def test_decision_logger_rejects_file_as_parent_dir(tmp_path):
    """log_dir cuyo padre es un archivo => mkdir falla ruidoso, no silencioso."""
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    with pytest.raises((OSError, NotADirectoryError, FileExistsError)):
        DecisionLogger(log_dir=str(blocker / "sub"))
    assert (
        blocker.is_file()
    )  # discriminante: el bloqueador sigue siendo archivo, no se creó dir


def test_d13_report_recent_decisions_empty_when_no_log(tmp_path):
    """Reporte sin decisiones logueadas => recent_decisions == []."""
    report = D13Report()
    report.decision_logger.log_file = tmp_path / "absent.jsonl"
    assert report.generate_json()["recent_decisions"] == []
