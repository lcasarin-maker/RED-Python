#!/usr/bin/env python3
"""
image_cost_detector.py — TK-050: Evitar imágenes innecesarias

Detecta screenshots y sugiere alternativas textuales.

Hook: pre_screenshot (antes de tomar screenshot)
"""

import json
import sys
from pathlib import Path
from typing import Dict


class ImageCostDetector:
    """Detecta screenshots innecesarias y sugiere alternativas."""

    BASE_COST = 1000  # tokens por imagen base
    COST_PER_KB = 2  # tokens adicionales por KB

    CRITICAL_CONTEXTS = {"ui_layout", "design_mockup", "browser_inspector"}

    DISCOURGED_CONTEXTS = {
        "terminal_error": "Usa `cat error.log` en texto",
        "json_output": "Formatea como bloque de código markdown",
        "small_file": "Archivo < 200 líneas: copia directamente",
        "log_output": "Usa `cat logfile.txt`",
        "code_snippet": "Formatea con syntax highlighting",
    }

    def __init__(self, config_path: str = "rules/image_policy.yaml"):
        self.config_path = Path(config_path)
        self.context = None

    def detect_context(self, intention: str) -> str:
        """
        Detectar contexto de la screenshot.

        Args:
            intention: Razón/descripción de por qué quiere screenshot

        Returns:
            'critical' | 'allowed' | 'discouraged'
        """
        intention_lower = intention.lower()

        # Contextos críticos que permiten screenshot
        if any(ctx in intention_lower for ctx in self.CRITICAL_CONTEXTS):
            return "critical"

        # Contextos desaconsejados
        for ctx, reason in self.DISCOURGED_CONTEXTS.items():
            if ctx in intention_lower:
                return "discouraged"

        # Default: desaconsejado
        return "discouraged"

    def estimate_cost(self, file_size_kb: float = 100) -> Dict:
        """
        Estimar costo de screenshot.

        Args:
            file_size_kb: Tamaño estimado en KB

        Returns:
            {
              'base_tokens': int,
              'size_tokens': int,
              'total_tokens': int,
              'cost_usd': float
            }
        """
        base_tokens = self.BASE_COST
        size_tokens = int(file_size_kb * self.COST_PER_KB)
        total_tokens = base_tokens + size_tokens

        # Estimación USD (Claude 3.5 Sonnet: $3 per 1M input tokens)
        cost_usd = (total_tokens / 1_000_000) * 3

        return {
            "base_tokens": base_tokens,
            "size_tokens": size_tokens,
            "total_tokens": total_tokens,
            "cost_usd": round(cost_usd, 6),
            "estimated_file_size_kb": file_size_kb,
        }

    def evaluate_screenshot(self, intention: str, file_size_kb: float = 100) -> Dict:
        """
        Evaluar si la screenshot es apropiada.

        Returns:
            {
              'allowed': bool,
              'context': str,
              'cost': dict,
              'recommendation': str,
              'alternative': str (si discouraged)
            }
        """
        context = self.detect_context(intention)
        cost = self.estimate_cost(file_size_kb)

        if context == "critical":
            return {
                "allowed": True,
                "context": context,
                "cost": cost,
                "recommendation": f'✅ Screenshot crítica (costo: {cost["total_tokens"]} tokens)',
                "alternative": None,
            }

        elif context == "discouraged":
            # Buscar alternativa
            alternative = None
            for ctx, alt in self.DISCOURGED_CONTEXTS.items():
                if ctx in intention.lower():
                    alternative = alt
                    break

            return {
                "allowed": False,
                "context": context,
                "cost": cost,
                "recommendation": f'⚠️ Desconsejada (ahorraría {cost["total_tokens"]} tokens)',
                "alternative": alternative or "Describe el problema en texto",
            }

        return {
            "allowed": False,
            "context": "unknown",
            "cost": cost,
            "recommendation": f'⚠️ Sin contexto claro (costo: {cost["total_tokens"]} tokens)',
            "alternative": "Describe en texto si es posible",
        }


def main():
    """
    CLI: python image_cost_detector.py <intention> [--size <kb>]

    Retorna JSON con evaluación.
    """
    if len(sys.argv) < 2:
        print("[USAGE] python image_cost_detector.py <intention> [--size <kb>]")
        sys.exit(1)

    intention = sys.argv[1]
    file_size = 100

    if len(sys.argv) > 3 and sys.argv[2] == "--size":
        try:
            file_size = float(sys.argv[3])
        except ValueError:
            print(
                f"[WARN] File size no es número: {sys.argv[3]}, usando default 100KB",
                file=sys.stderr,
            )

    detector = ImageCostDetector()
    evaluation = detector.evaluate_screenshot(intention, file_size)

    print(json.dumps(evaluation, indent=2))


if __name__ == "__main__":
    main()
