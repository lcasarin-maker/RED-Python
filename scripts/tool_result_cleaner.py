#!/usr/bin/env python3
"""
tool_result_cleaner.py — TK-047: Tool-Result Clearing

Limpia/resume resultados de herramientas gigantes.

Hook: post_tool_result (después de cualquier tool execution)
"""

import json
import sys
from typing import Tuple, Dict


class ToolResultCleaner:
    """Detecta y resume resultados de herramientas grandes."""

    VERBOSITY_THRESHOLD = 5000  # tokens
    CRITICAL_THRESHOLD = 10000  # truncar si supera esto

    # Estrategias por tipo de herramienta
    TOOL_STRATEGIES = {
        "grep": {
            "max_lines": 20,
            "summary": True,
            "example": "Mostrar líneas coincidentes + cuenta",
        },
        "find": {
            "max_items": 10,
            "summary": True,
            "example": 'Mostrar 10 primeros + "...N más archivos"',
        },
        "git log": {
            "max_commits": 3,
            "summary": True,
            "example": "Últimos 3 commits + resumen",
        },
        "git diff": {
            "max_lines": 50,
            "summary": True,
            "example": 'Primeras 50 líneas + "...truncado"',
        },
        "ls": {"max_items": 50, "summary": True, "example": "Listar máximo 50 items"},
        "cat": {"max_lines": 100, "summary": True, "example": "Primeras 100 líneas"},
    }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimación rápida de tokens (1 token ≈ 4 caracteres)."""
        return len(text) // 4

    # Orden importa: git log/diff antes que tokens sueltos
    _TOOL_KEYWORDS = [
        ("git log", "git log"),
        ("git diff", "git diff"),
        ("grep", "grep"),
        ("find", "find"),
        ("ls", "ls"),
        ("cat", "cat"),
    ]

    @classmethod
    def get_tool_type(cls, command: str) -> str:
        """Detectar tipo de herramienta por keyword (dict-driven, sin elif chains)."""
        command_lower = command.lower()
        for keyword, tool_type in cls._TOOL_KEYWORDS:
            if keyword in command_lower:
                return tool_type
        return "unknown"

    @staticmethod
    def truncate_output(output: str, max_lines: int) -> Tuple[str, int]:
        """
        Trunca a máximo N líneas.

        Returns:
            (output_truncado, líneas_removidas)
        """
        lines = output.split("\n")
        if len(lines) <= max_lines:
            return output, 0

        removed = len(lines) - max_lines
        truncated = "\n".join(lines[:max_lines])
        truncated += f"\n... ({removed} líneas más omitidas)"

        return truncated, removed

    def _get_limit(self, strategy: dict) -> int:
        """Extrae el límite de líneas/items de una estrategia."""
        return strategy.get("max_lines", strategy.get("max_items", 50))

    def _make_result(self, tokens: int, result: str) -> Dict:
        """Resultado sin cambios (bajo umbral)."""
        return {
            "original_tokens": tokens,
            "cleaned_tokens": tokens,
            "tokens_saved": 0,
            "output": result,
            "action": "none",
            "summary": f"Resultado pequeño ({tokens} tokens)",
        }

    def clean_result(self, tool_command: str, result: str) -> Dict:
        """Limpiar resultado de herramienta si supera el umbral de tokens."""
        original_tokens = self.estimate_tokens(result)
        if original_tokens < self.VERBOSITY_THRESHOLD:
            return self._make_result(original_tokens, result)

        tool_type = self.get_tool_type(tool_command)
        strategy = self.TOOL_STRATEGIES.get(tool_type, self.TOOL_STRATEGIES["cat"])
        limit = self._get_limit(strategy)
        cleaned, removed = self.truncate_output(result, limit)
        cleaned_tokens = self.estimate_tokens(cleaned)

        return {
            "original_tokens": original_tokens,
            "cleaned_tokens": cleaned_tokens,
            "tokens_saved": original_tokens - cleaned_tokens,
            "output": cleaned,
            "action": "truncated",
            "summary": f"{tool_type}: {original_tokens}→{cleaned_tokens} tokens ({removed} líneas removidas)",
        }


def main():
    """
    CLI: python tool_result_cleaner.py <tool_command> <result_output>

    Retorna JSON con resultado limpiado.
    """
    if len(sys.argv) < 3:
        print("[USAGE] python tool_result_cleaner.py <tool_command> <result_output>")
        sys.exit(1)

    try:
        tool_command = sys.argv[1]
        result_output = sys.argv[2]

        cleaner = ToolResultCleaner()
        cleaned = cleaner.clean_result(tool_command, result_output)

        print(json.dumps(cleaned))
    except Exception as e:
        error_output = {
            "error": str(e),
            "original_tokens": 0,
            "cleaned_tokens": 0,
            "tokens_saved": 0,
            "output": result_output,
            "action": "error",
        }
        print(json.dumps(error_output), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
