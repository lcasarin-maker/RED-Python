#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests falsables del mecanismo de continuidad VC-140.

Ejercen la función PURA `check_handoff_freshness`: dado el changeset staged, el texto
del HANDOFF y el mensaje, decide si el commit puede proceder."""
import sys

import scripts.check_handoff_freshness as chf
from scripts.check_handoff_freshness import check_handoff_freshness

_FRESH = "## ESTADO\nlisto\n## SIGUIENTE\n1. x\n## VERIFICAR\npytest -q\n"


def test_substantive_change_without_handoff_blocks():
    ok, reason = check_handoff_freshness(["scripts/foo.py"], "", "fix: foo")
    assert ok is False and "no actualizado" in reason


def test_substantive_change_with_fresh_handoff_passes():
    ok, reason = check_handoff_freshness(
        ["scripts/foo.py", "HANDOFF.md"], _FRESH, "feat: foo"
    )
    assert ok is True and reason == "handoff fresco"


def test_handoff_staged_but_missing_sections_blocks():
    ok, reason = check_handoff_freshness(
        ["scripts/foo.py", "HANDOFF.md"], "## ESTADO\nsolo esto\n", "feat: foo"
    )
    assert ok is False and "sin secciones" in reason and "## VERIFICAR" in reason


def test_only_trivial_files_passes():
    # Editar solo HISTORIAL/STATUS/HANDOFF no exige relevo nuevo.
    ok, reason = check_handoff_freshness(["HISTORIAL.md", "STATUS.md"], "", "docs")
    assert ok is True and "sin cambios sustantivos" in reason


def test_skip_token_in_message_escapes():
    ok, reason = check_handoff_freshness(["scripts/foo.py"], "", "fix: typo [skip-handoff]")
    assert ok is True and "escape" in reason


def test_skip_env_var_escapes(monkeypatch):
    monkeypatch.setenv("CERBERUS_SKIP_HANDOFF", "1")
    ok, reason = check_handoff_freshness(["scripts/foo.py"], "", "fix: typo")
    assert ok is True and "escape" in reason


def test_skip_token_only_in_body_does_not_escape():
    """Regresión: mencionar [skip-handoff] en el CUERPO (prosa) NO debe escapar;
    solo la línea de asunto cuenta como flag intencional."""
    msg = "feat: documenta el escape\n\nMenciona [skip-handoff] en prosa, no debe escapar."
    ok, reason = check_handoff_freshness(["scripts/foo.py"], "", msg)
    assert ok is False and "no actualizado" in reason


def test_main_blocks_with_nonzero_returncode(monkeypatch, tmp_path):
    """Path negativo del CLI: con cambio sustantivo y sin HANDOFF.md, main() bloquea."""
    msgfile = tmp_path / "COMMIT_EDITMSG"
    msgfile.write_text("feat: cambio sin relevo", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["check_handoff_freshness", str(msgfile)])
    monkeypatch.setattr(chf, "_staged_files", lambda: ["scripts/foo.py"])
    monkeypatch.setattr(chf, "_ROOT", tmp_path)  # tmp_path no contiene HANDOFF.md
    returncode = chf.main()
    assert returncode == 1


def test_main_no_args_is_informational(monkeypatch):
    """Fuera del hook (sin argv) NO bloquea: smoke test de scripts pasa."""
    monkeypatch.setattr(sys, "argv", ["check_handoff_freshness"])
    assert chf.main() == 0
