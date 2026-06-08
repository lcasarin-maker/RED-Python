#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests del contrato de dimensiones (Sprint 28.5 Paso 2).

Falsables: ejercen paths negativos reales (AST que no parsea, dir vacío,
status no-bloqueante) para que el contrato no pueda mentir."""
import pytest

from dimensions import REGISTRY, AuditContext, Finding, Status


def test_registry_is_list():
    assert isinstance(REGISTRY, list)


def test_py_files_excludes_noise_and_caches(tmp_path):
    (tmp_path / "real.py").write_text("x = 1\n")
    junk = tmp_path / "deprecated"
    junk.mkdir()
    (junk / "old.py").write_text("y = 2\n")
    ctx = AuditContext(tmp_path)
    files = ctx.py_files()
    names = [f.name for f in files]
    assert "real.py" in names
    assert "old.py" not in names  # deprecated/ excluido
    assert ctx.py_files() is files  # pasada única: mismo objeto cacheado


def test_ast_of_returns_none_on_syntax_error(tmp_path):
    bad = tmp_path / "broken.py"
    bad.write_text("def (:\n")  # sintaxis inválida
    ctx = AuditContext(tmp_path)
    assert ctx.ast_of(bad) is None  # path negativo: no parsea => None, no crash


def test_empty_project_has_no_py_files(tmp_path):
    assert AuditContext(tmp_path).py_files() == []


def test_finding_blocking_semantics():
    assert Finding("D7", "fuga", Status.FAIL).is_blocking() is True
    assert Finding("D7", "scanner ausente", Status.UNAVAILABLE).is_blocking() is True
    assert Finding("D7", "ok", Status.PASS).is_blocking() is False
    assert Finding("D7", "aviso", Status.WARN).is_blocking() is False


def test_unavailable_status_exists_and_is_not_pass():
    assert Status.UNAVAILABLE != Status.PASS
    with pytest.raises(KeyError):
        _ = Status["NONEXISTENT"]
