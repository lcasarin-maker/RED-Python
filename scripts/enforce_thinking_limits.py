#!/usr/bin/env python3
"""
enforce_thinking_limits.py — TK-044: Control de Thinking Mode

Limita reasoning tokens en tareas simples. Evita que Opus gaste 10x por
trivialidades.

Hook: pre_model_selection (antes de seleccionar modelo)
"""

import json
import sys
from pathlib import Path
from typing import Dict


class ThinkingLimiter:
    """Controla activación de thinking mode según complejidad."""

    def __init__(self, config_path: str = "rules/thinking_limits.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Cargar configuración. Fallback completo si el archivo no existe."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as exc:
                import logging
                logging.getLogger("enforce_thinking_limits").warning(
                    "config ilegible %s: %s", self.config_path, exc
                )
        # Fallback completo con todas las claves requeridas
        return {
            "thinking_level": "low",
            "max_tokens": 8000,
            "rules": {
                "opus_simple_task": False,
                "opus_strategy_task": True,
                "sonnet": False,
                "haiku": False,
            },
            "detection_rules": {
                "simple_task_tokens": 10000,
                "keywords_simple": ["lista", "grep", "formato", "resume", "muestra", "busca"],
                "keywords_complex": ["diseña", "arquitectura", "debug", "analiza", "implementa"],
            },
        }

    def detect_simple_task(self, input_text: str, input_tokens: int) -> bool:
        """
        ¿Es una tarea simple?

        Simple si:
        - < 10K tokens entrada
        - Contiene palabras clave simples (lista, grep, formato)
        """
        if input_tokens > self.config["detection_rules"]["simple_task_tokens"]:
            return False

        keywords = self.config["detection_rules"]["keywords_simple"]
        text_lower = input_text.lower()

        return any(kw in text_lower for kw in keywords)

    def detect_complex_task(self, input_text: str) -> bool:
        """¿Es una tarea compleja que NECESITA thinking?"""
        keywords = self.config["detection_rules"]["keywords_complex"]
        text_lower = input_text.lower()

        return any(kw in text_lower for kw in keywords)

    def get_thinking_settings(
        self, model: str, input_text: str, input_tokens: int
    ) -> Dict[str, any]:
        """
        Obtener configuración de thinking para este modelo/tarea.

        Returns:
            {
              'thinking_enabled': bool,
              'thinking_level': str,
              'max_tokens': int,
              'reason': str
            }
        """
        is_simple = self.detect_simple_task(input_text, input_tokens)
        is_complex = self.detect_complex_task(input_text)

        if model == "opus":
            if is_simple:
                return {
                    "thinking_enabled": False,
                    "thinking_level": None,
                    "max_tokens": 0,
                    "reason": "Tarea simple: desactivar reasoning",
                }
            elif is_complex:
                return {
                    "thinking_enabled": True,
                    "thinking_level": "extended",
                    "max_tokens": self.config["max_tokens"],
                    "reason": "Tarea compleja: activar reasoning",
                }
            else:
                # Por defecto: thinking bajo
                return {
                    "thinking_enabled": True,
                    "thinking_level": "low",
                    "max_tokens": self.config["max_tokens"] // 2,
                    "reason": "Por defecto: thinking bajo",
                }

        elif model == "sonnet":
            return {
                "thinking_enabled": False,
                "thinking_level": None,
                "max_tokens": 0,
                "reason": "Sonnet: sin reasoning",
            }

        elif model == "haiku":
            return {
                "thinking_enabled": False,
                "thinking_level": None,
                "max_tokens": 0,
                "reason": "Haiku: sin reasoning",
            }

        return {
            "thinking_enabled": False,
            "thinking_level": None,
            "max_tokens": 0,
            "reason": f"Modelo desconocido: {model}",
        }


def main():
    """
    CLI: python enforce_thinking_limits.py <model> <input_text> <input_tokens>

    Retorna JSON con configuración de thinking.
    """
    if len(sys.argv) < 4:
        print(
            "[USAGE] python enforce_thinking_limits.py <model> <input_text> <input_tokens>"
        )
        sys.exit(1)

    model = sys.argv[1]
    input_text = sys.argv[2]
    try:
        input_tokens = int(sys.argv[3])
    except ValueError:
        input_tokens = len(input_text) // 4

    limiter = ThinkingLimiter()
    settings = limiter.get_thinking_settings(model, input_text, input_tokens)

    print(json.dumps(settings))


if __name__ == "__main__":
    main()
