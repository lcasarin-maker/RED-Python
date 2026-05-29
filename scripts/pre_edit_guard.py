#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pre_edit_guard.py v1.0 — CoderCerberus V0.02 Pre-Edit Protocol Guard
Agent-agnostic enforcement gate. Runs BEFORE any file edit or write.

Checks enforced at edit time (not just at commit):
  S6  — Write >200 lines blocked.
  S7  — Shell mutation patterns in new content blocked.
  S19 — Edits to deprecated/ blocked.
  S19 — Zombie-compat strings in new content blocked.

Exit codes (Claude Code hook contract):
  0 = ALLOW
  2 = BLOCK — hard stop, operation does not proceed

Usage (Claude Code PreToolUse hook): reads JSON from stdin.
Usage (CLI / other agents): --file PATH --tool Edit|Write [--new-string TEXT | --content TEXT]
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger("pre_edit_guard")

# ---------------------------------------------------------------------------
# S19 Anti-Zombie-Compat: strings that signal shim/compat patterns
# ---------------------------------------------------------------------------
_S19_ZOMBIE_PATTERNS: list[tuple[str, str]] = [
    ("backward compat",          "S19: 'backward compat' — shim prohibido (VC-118)"),
    ("compatibility shim",       "S19: shim explícito prohibido (VC-118)"),
    ("# for now",                "S19: placeholder '# for now' prohibido (VC-118)"),
    ("# backward",               "S19: comentario de compatibilidad prohibido (VC-118)"),
    ("new.exists() or old",      "S19: ruta alternativa de adopción prohibida (VC-118)"),
    ("fallback to old",          "S19: fallback al archivo viejo prohibido (VC-118)"),
    ("from old import",          "S19: importar del módulo viejo prohibido (VC-118)"),
]

# ---------------------------------------------------------------------------
# S7 Anti-Shell: shell commands that mutate files
# ---------------------------------------------------------------------------
_S7_SHELL_RE: list[re.Pattern] = [
    re.compile(r'\becho\b.*(>>|>[^>])', re.IGNORECASE),
    re.compile(r'\bsed\b.*-i', re.IGNORECASE),
    re.compile(r'\bAdd-Content\b', re.IGNORECASE),
    re.compile(r'\bSet-Content\b', re.IGNORECASE),
    re.compile(r'\bOut-File\b', re.IGNORECASE),
]

_S6_WRITE_LINE_LIMIT = 200


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_deprecated_path(file_path: str) -> str | None:
    """S19: Edits to deprecated/ are forbidden — use git rm instead."""
    if "deprecated" in Path(file_path).parts:
        return (
            f"S19: '{file_path}' está en deprecated/ — edición prohibida. "
            "Usa git rm si debes eliminarlo."
        )
    return None


def _check_s19_zombie(content: str, file_path: str) -> list[str]:
    """S19: Detect zombie-compat strings being introduced."""
    lower = content.lower()
    return [
        f"{msg} — en {file_path}"
        for pattern, msg in _S19_ZOMBIE_PATTERNS
        if pattern in lower
    ]


def _check_s7_shell(content: str, file_path: str) -> list[str]:
    """S7: Detect shell file-mutation commands in new content."""
    return [
        f"S7: Comando shell con escritura detectado en {file_path} — usar Edit/Write atómico"
        for pat in _S7_SHELL_RE
        if pat.search(content)
    ]


def _check_s6_write_size(content: str, file_path: str, is_write: bool) -> str | None:
    """S6: Full-file Write >200 lines is blocked."""
    if not is_write:
        return None
    lines = content.count("\n") + 1
    if lines > _S6_WRITE_LINE_LIMIT:
        return (
            f"S6: Write de {lines} líneas a '{file_path}' prohibido "
            f"(máx {_S6_WRITE_LINE_LIMIT}). Usar Edit atómico <50 líneas."
        )
    return None


def _check_reasoning_lock() -> str | None:
    """Detect if the agent is locked due to repetitive reasoning deadlocks."""
    state_file = Path(__file__).resolve().parent.parent / ".agent_state.json"
    if state_file.exists():
        try:
            import json
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            if state.get("reasoning_lock", False):
                return (
                    "CPI reasoning_lock activo — El agente tiene prohibido realizar modificaciones en la base de código debido a fallos repetitivos (consecutive_failures >= 3).\n"
                    "  Revisa STATUS.md y ejecuta 'python scripts/protocol_cli.py unlock' en la terminal tras corregir el problema."
                )
        except Exception as e:
            logger.warning("Error checking reasoning lock state: %s", e)
    return None


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------

def evaluate(tool_name: str, file_path: str, content: str) -> list[str]:
    """Run all checks. Returns list of violation strings (empty = clean)."""
    violations: list[str] = []
    is_write = tool_name.lower() == "write"

    lock = _check_reasoning_lock()
    if lock:
        violations.append(lock)

    dep = _check_deprecated_path(file_path)
    if dep:
        violations.append(dep)

    s6 = _check_s6_write_size(content, file_path, is_write)
    if s6:
        violations.append(s6)

    violations.extend(_check_s19_zombie(content, file_path))
    violations.extend(_check_s7_shell(content, file_path))

    return violations


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def _run_hook_mode() -> None:
    """Claude Code PreToolUse hook: read JSON from stdin."""
    try:
        data = json.load(sys.stdin)
        tool_name: str = data.get("tool_name", "Edit")
        tool_input: dict = data.get("tool_input", {})
        file_path: str = tool_input.get("file_path", "")
        content: str = tool_input.get("new_string") or tool_input.get("content") or ""
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.warning("pre_edit_guard: stdin parse error — allowing (safe): %s", exc)
        sys.exit(0)

    _apply(tool_name, file_path, content)


def _run_cli_mode() -> None:
    """CLI mode for Gemini, ChatGPT, Codex, and manual invocation."""
    parser = argparse.ArgumentParser(description="CoderCerberus pre-edit protocol guard")
    parser.add_argument("--file", required=True, help="Target file path")
    parser.add_argument("--tool", default="Edit", choices=["Edit", "Write"])
    parser.add_argument("--new-string", default="", dest="new_string")
    parser.add_argument("--content", default="")
    args = parser.parse_args()
    _apply(args.tool, args.file, args.new_string or args.content)


def _apply(tool_name: str, file_path: str, content: str) -> None:
    violations = evaluate(tool_name, file_path, content)
    if violations:
        print("\n\U0001f6a8 PRE-EDIT GUARD — OPERACIÓN BLOQUEADA", file=sys.stderr)
        for v in violations:
            print(f"  ✗ {v}", file=sys.stderr)
        print(
            "\nCorrige la violación de protocolo antes de continuar.\n"
            "Referencia: PROTOCOL_SYSTEM.md — Mandatos S6, S7, S19",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(0)


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")
    if not sys.stdin.isatty():
        _run_hook_mode()
    else:
        _run_cli_mode()


if __name__ == "__main__":
    main()
