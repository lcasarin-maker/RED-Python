#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AuditContext (Sprint 28.5 Paso 2): pasada única compartida.

Calcula la lista de archivos UNA vez y cachea el AST por archivo, para que las
N dimensiones no re-caminen el árbol ni re-parseen (conserva la virtud del
monolito sin su inextensibilidad)."""
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
    """Contexto inmutable-por-construcción de una corrida de auditoría."""

    def __init__(self, project_path):
        self.project_path = Path(project_path).resolve()
        self._py_files = None
        self._ast_cache = {}

    def py_files(self) -> list:
        """Lista de .py del proyecto, calculada una sola vez."""
        if self._py_files is None:
            files = []
            for p in self.project_path.rglob("*.py"):
                if any(part in _HARD_EXCLUDES for part in p.parts):
                    continue
                files.append(p)
            self._py_files = sorted(files)
            logger.info(
                "py_files: %d archivos bajo %s", len(self._py_files), self.project_path
            )
        return self._py_files

    def ast_of(self, path: Path | str) -> ast.AST | None:
        """AST cacheado de un archivo. Devuelve None si no parsea (lo registra)."""
        key = str(path)
        if key not in self._ast_cache:
            try:
                self._ast_cache[key] = ast.parse(
                    Path(path).read_text(encoding="utf-8", errors="replace")
                )
            except SyntaxError as exc:
                logger.warning("ast_of: %s no parsea: %s", key, exc)
                self._ast_cache[key] = None
        return self._ast_cache[key]
