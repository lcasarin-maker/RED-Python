#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTK AUTO COMPRESS — Compresión quirúrgica de output verboso (v4.3)
Detecta output que supera el umbral de verbosidad y recorta líneas largas.
Caller: rigor_maestro.py, compact_automation_helper.py.
"""
import sys
from pathlib import Path

from scripts.core_utils import setup_windows_utf8
setup_windows_utf8()


class RTKAutoCompress:
    """Detecta y comprime output verboso automáticamente."""

    VERBOSITY_THRESHOLD = 500  # chars antes de comprimir
    LINE_LIMIT = 120           # chars máximos por línea

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estima tokens basado en longitud: len // 4."""
        return len(text) // 4

    @staticmethod
    def should_compress(output: str) -> bool:
        """True si el output supera el umbral de verbosidad."""
        return len(output) > RTKAutoCompress.VERBOSITY_THRESHOLD

    @staticmethod
    def process_output(output: str, command_type: str = "git") -> tuple:
        """
        Aplica compresión quirúrgica si necesario.

        Returns:
            Tuple[str, bool]: (texto procesado, True si se comprimió)
        """
        if not RTKAutoCompress.should_compress(output):
            return output, False

        compressed = []
        for line in output.split('\n'):
            if len(line) > RTKAutoCompress.LINE_LIMIT:
                compressed.append(line[:RTKAutoCompress.LINE_LIMIT - 3] + "...")
            else:
                compressed.append(line)

        final_output = '\n'.join(compressed)
        tokens_before = RTKAutoCompress.estimate_tokens(output)
        tokens_after = RTKAutoCompress.estimate_tokens(final_output)

        if tokens_before > tokens_after:
            savings = (tokens_before - tokens_after) / tokens_before * 100
            print(
                f"[RTK] Compressed: {tokens_before} -> {tokens_after} tokens "
                f"({savings:.0f}% saved)",
                file=sys.stderr
            )
            return final_output, True

        return output, False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-compress verbose output")
    parser.add_argument("--command", type=str, default="git")
    parser.add_argument("--input-file", type=str)
    args = parser.parse_args()

    if args.input_file:
        content = Path(args.input_file).read_text(encoding='utf-8', errors='ignore')
    else:
        content = sys.stdin.read()

    compressed, used = RTKAutoCompress.process_output(content, args.command)
    print(compressed)
