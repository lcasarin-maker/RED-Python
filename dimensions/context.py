#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AuditContext (Sprint 28.5 Step 2): shared single pass.

Computes the file list once and caches the AST per file so the N dimensions do
not re-walk the tree or re-parse it (keeping the monolith's virtue without its
inflexibility).
"""
import ast
import logging
from pathlib import Path

logger = logging.getLogger("dimensions.context")

_HARD_EXCLUDES = {
    "__pycache__",
    ".git",
    "deprecated",
    ".ruff_cache",
    ".pytest_cache",
    ".protocol",
    "node_modules",
}


class AuditContext:
    """Immutable-by-construction context for an audit run."""

    def __init__(self, project_path):
        self.project_path = Path(project_path).resolve()
        self._py_files = None
        self._ast_cache = {}

    def py_files(self) -> list:
        """Project .py file list, computed only once."""
        if self._py_files is None:
            files = []
            for p in self.project_path.rglob("*.py"):
                if any(part in _HARD_EXCLUDES for part in p.parts):
                    continue
                files.append(p)
            self._py_files = sorted(files)
            logger.info(
                "py_files: %d files under %s", len(self._py_files), self.project_path
            )
        return self._py_files

    def ast_of(self, path: Path | str) -> ast.AST | None:
        """Cached AST for a file. Returns None if parsing fails and logs it."""
        key = str(path)
        if key not in self._ast_cache:
            try:
                self._ast_cache[key] = ast.parse(
                    Path(path).read_text(encoding="utf-8", errors="replace")
                )
            except SyntaxError as exc:
                logger.warning("ast_of: %s does not parse: %s", key, exc)
                self._ast_cache[key] = None
        return self._ast_cache[key]
