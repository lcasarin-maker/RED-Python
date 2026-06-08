#!/usr/bin/env python3
"""
model_router.py — TK-045: Cascada de modelos inteligente

Encamina tareas a Haiku/Sonnet/Opus basándose en complejidad + budget tokens.

Hook: pre_model_selection (antes de seleccionar modelo)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Tuple


class ModelRouter:
    """Encamina a modelo apropiado según complejidad y costo."""

    def __init__(self, config_path: str = "rules/model_routing_matrix.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Cargar matriz de routing (YAML simpleificado a dict)."""
        # Para este MVP, usar configuración por defecto
        return {
            "haiku": {
                "allocation": 0.80,
                "budget": 10000,
                "keywords": ["list", "grep", "format", "small", "simple"],
            },
            "sonnet": {
                "allocation": 0.15,
                "budget": 50000,
                "keywords": ["implement", "debug", "refactor", "moderate"],
            },
            "opus": {
                "allocation": 0.05,
                "budget": 200000,
                "keywords": ["architecture", "critical", "strategic", "design"],
            },
        }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimación: 1 token ≈ 4 caracteres."""
        return len(text) // 4

    def score_complexity(self, prompt: str) -> Tuple[float, str]:
        """
        Puntuar complejidad 0-10.

        Returns:
            (score, reasoning)
        """
        prompt_lower = prompt.lower()
        score = 5.0  # Default: medio

        # Palabras clave simples
        simple_keywords = [
            "list",
            "grep",
            "format",
            "small",
            "simple",
            "read",
            "search",
            "find",
            "grep",
            "básico",
            "simple",
        ]
        if any(kw in prompt_lower for kw in simple_keywords):
            score -= 3

        # Palabras clave complejas
        complex_keywords = [
            "architecture",
            "critical",
            "strategic",
            "design",
            "adversarial",
            "debugging",
            "architect",
            "crítica",
            "diseño",
            "decisión",
        ]
        if any(kw in prompt_lower for kw in complex_keywords):
            score += 4

        # Palabras clave moderadas
        moderate_keywords = [
            "implement",
            "debug",
            "refactor",
            "integrate",
            "moderate",
            "implementa",
            "refactor",
        ]
        if any(kw in prompt_lower for kw in moderate_keywords):
            score = 5

        # Limitar a 0-10
        score = max(0, min(10, score))

        if score < 3:
            reasoning = "Simple task (keywords)"
        elif score < 6:
            reasoning = "Moderate task (balanced)"
        else:
            reasoning = "Complex task (keywords)"

        return score, reasoning

    def recommend_model(
        self, prompt: str, input_tokens: int, force_model: str = None
    ) -> Dict:
        """
        Recomendar modelo.

        Args:
            prompt: Texto de la tarea
            input_tokens: Tokens de entrada estimados
            force_model: Forzar modelo específico (para override)

        Returns:
            {
              'recommended_model': str,
              'score': float,
              'reasoning': list,
              'cost_estimate': dict,
              'alternatives': dict
            }
        """
        if force_model:
            return {
                "recommended_model": force_model,
                "score": None,
                "reasoning": ["Modelo forzado por usuario"],
                "cost_estimate": {"model": force_model},
                "alternatives": {},
            }

        complexity_score, complexity_reason = self.score_complexity(prompt)

        # Lógica de routing
        if input_tokens < 10000 and complexity_score < 3:
            model = "haiku"
            reasoning = [
                f"Tokens entrada: {input_tokens} < 10K (Haiku budget)",
                f"Complejidad: {complexity_score}/10 (simple)",
                complexity_reason,
            ]
        elif input_tokens < 50000 and complexity_score < 6:
            model = "sonnet"
            reasoning = [
                f"Tokens entrada: {input_tokens} < 50K (Sonnet budget)",
                f"Complejidad: {complexity_score}/10 (moderate)",
                complexity_reason,
            ]
        else:
            model = "opus"
            reasoning = [
                f"Tokens entrada: {input_tokens} (Opus para este scope)",
                f"Complejidad: {complexity_score}/10 (complex)",
                complexity_reason,
            ]

        # Si es muy simple pero fuerza Opus, advertir
        if model != "opus" and input_tokens > 100000:
            model = "opus"
            reasoning.append("Contexto muy grande: usar Opus para mejor rendimiento")

        return {
            "recommended_model": model,
            "score": round(complexity_score, 1),
            "reasoning": reasoning,
            "cost_estimate": {
                "model": model,
                "estimated_input_tokens": input_tokens,
                "allocation_percent": int(self.config[model]["allocation"] * 100),
            },
            "alternatives": {
                "haiku": "Más barato, para tareas simples",
                "sonnet": "Equilibrio costo-calidad",
                "opus": "Mejor calidad, más caro",
            },
        }


def main():
    """
    CLI: python model_router.py <prompt> <input_tokens> [--force <model>]

    Retorna JSON con recomendación.
    """
    if len(sys.argv) < 3:
        print(
            "[USAGE] python model_router.py <prompt> <input_tokens> [--force <model>]"
        )
        sys.exit(1)

    prompt = sys.argv[1]
    try:
        input_tokens = int(sys.argv[2])
    except ValueError:
        input_tokens = ModelRouter.estimate_tokens(prompt)

    force_model = None
    if len(sys.argv) > 4 and sys.argv[3] == "--force":
        force_model = sys.argv[4]

    router = ModelRouter()
    recommendation = router.recommend_model(prompt, input_tokens, force_model)

    print(json.dumps(recommendation, indent=2))


if __name__ == "__main__":
    main()
