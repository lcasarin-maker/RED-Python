#!/usr/bin/env python3
"""
block_auto_docs.py — TK-049: Prohibir generación automática de documentación

Previene que Claude genere archivos .md, .json, .yaml sin solicitud explícita.
Hook: pre_write (antes de cualquier Write/Create)

Excepciones permitidas:
  - SPEC.md, PLAN.md, HISTORIAL.md (archivos permitidos)
  - Si usuario dice "crea..." explícitamente
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class DocBlocker:
    """Bloquea creación automática de documentación."""

    FORBIDDEN_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".txt", ".xml"}
    ALLOWED_FILES = {
        "SPEC.md",
        "PLAN.md",
        "HISTORIAL.md",
        ".agent_state.json",
        "VERSION.txt",
    }

    def __init__(self, state_file: str = ".agent_state.json"):
        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Cargar estado actual."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {}

    def _save_state(self):
        """Guardar estado."""
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def should_block(self, file_path: str, context: dict = None) -> bool:
        """
        ¿Debería bloquear este archivo?

        Args:
            file_path: Ruta del archivo a crear
            context: Contexto (contiene user_input, user_asked_explicit, etc.)

        Returns:
            True si debería bloquearse
        """
        path = Path(file_path)

        # Permitir archivos explícitamente permitidos
        if path.name in self.ALLOWED_FILES:
            return False

        # Permitir si tiene extensión segura
        if path.suffix not in self.FORBIDDEN_EXTENSIONS:
            return False

        # Permitir si usuario pidió explícitamente
        if context and context.get("user_asked_explicit"):
            return False

        # BLOQUEAR
        return True

    def block_attempt(self, file_path: str, reason: str = "auto-generated"):
        """Registrar intento bloqueado."""
        if "blocked_docs" not in self.state:
            self.state["blocked_docs"] = []

        self.state["blocked_docs"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "file": str(file_path),
                "reason": reason,
            }
        )
        self._save_state()

    def suggest_alternative(self, file_path: str) -> str:
        """Sugerir alternativa textual."""
        return f"""
[BLOCKED] No genero archivos {Path(file_path).suffix} automáticamente.

Puedo describir el contenido aquí en el chat. Si lo necesitas como archivo,
pídeme explícitamente: "crea el archivo {Path(file_path).name}"
"""


def main():
    """CLI: python block_auto_docs.py <file_path> [--context <json>]"""
    if len(sys.argv) < 2:
        print("[USAGE] python block_auto_docs.py <file_path> [--context <json>]")
        sys.exit(1)

    file_path = sys.argv[1]

    # Parsear contexto si existe
    context = {}
    if len(sys.argv) > 3 and sys.argv[2] == "--context":
        try:
            context = json.loads(sys.argv[3])
        except json.JSONDecodeError as e:
            print(f"[WARN] Contexto JSON inválido: {e}", file=sys.stderr)

    blocker = DocBlocker()

    if blocker.should_block(file_path, context):
        blocker.block_attempt(file_path)
        suggestion = blocker.suggest_alternative(file_path)
        print(suggestion, file=sys.stderr)
        sys.exit(1)  # Bloquear

    sys.exit(0)  # Permitir


if __name__ == "__main__":
    main()
