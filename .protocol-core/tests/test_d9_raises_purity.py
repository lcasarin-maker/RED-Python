#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_d9_raises_purity.py
P0.2: D9 test-purity AST checks around pytest.raises.
Locks two behaviors so they cannot regress:
  1. `with pytest.raises(X): foo()` without any assert -> "siempre pasa" (pre-existing).
  2. `assert exc` / `assert exc.value` after pytest.raises -> non-discriminating (new).
A discriminating assert (`exc.type is X`, `X in str(exc.value)`) must NOT be flagged.
"""

import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.run_security_audit_12d import TestTheaterVisitor


def _flags(src: str) -> list:
    """Return D9 errors the theater visitor raises for a test source snippet."""
    visitor = TestTheaterVisitor("snippet.py", src.splitlines())
    visitor.visit(ast.parse(src))
    return visitor.errors


def test_raises_without_assert_is_flagged():
    """P0.2: pytest.raises with no assert in the body must be flagged as 'siempre pasa'."""
    src = (
        "def test_x():\n"
        "    import pytest\n"
        "    with pytest.raises(TypeError):\n"
        "        foo()\n"
    )
    errors = _flags(src)
    assert any("siempre pasa" in e for e in errors), f"Expected siempre-pasa flag, got: {errors}"


def test_nondiscriminating_assert_exc_is_flagged():
    """P0.2: `assert exc` (always truthy ExceptionInfo) must be flagged as non-discriminating."""
    src = (
        "def test_x():\n"
        "    import pytest\n"
        "    with pytest.raises(TypeError) as exc:\n"
        "        foo()\n"
        "    assert exc\n"
    )
    errors = _flags(src)
    assert any("no discrimina" in e for e in errors), f"Expected non-discriminating flag, got: {errors}"


def test_nondiscriminating_assert_exc_value_is_flagged():
    """P0.2: `assert exc.value` (always truthy) must be flagged as non-discriminating."""
    src = (
        "def test_x():\n"
        "    import pytest\n"
        "    with pytest.raises(TypeError) as exc:\n"
        "        foo()\n"
        "    assert exc.value\n"
    )
    errors = _flags(src)
    assert any("no discrimina" in e for e in errors), f"Expected non-discriminating flag, got: {errors}"


def test_discriminating_assert_passes():
    """P0.2: a real comparison on the exception must NOT be flagged."""
    src = (
        "def test_x():\n"
        "    import pytest\n"
        "    with pytest.raises(ValueError) as ei:\n"
        "        foo()\n"
        "    assert 'bad' in str(ei.value)\n"
    )
    errors = _flags(src)
    assert not errors, f"Discriminating assert must not be flagged, got: {errors}"
