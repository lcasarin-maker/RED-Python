#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_security_audit_12d.py v0.02 - Polyglot Forensic Auditor (CoderCerberus)
12 dominios: D1 Integridad, D2 Completitud, D3 Claridad, D4 Anti-Spaghetti,
D5 Angry Path, D6 Anti-Slop, D7 Seguridad, D8 Cobertura Adversarial,
D9 Pureza de Tests, D10 Tokenomics & Eficiencia de Contexto, D11 SCA Trivy,
D12 Satellite Drift.
Entrypoint primario desde P7.1 (VC-113). Soporte multi-lenguaje (PY, HTML, JS, CSS).
"""

import re
import sys
import os
import shutil
import argparse
from pathlib import Path
import ast
import logging

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8, run_command, get_centralized_version
from scripts.audit_hygiene import (
    repair_mojibake,
    deprecate_legacy_scripts,
    find_hygiene_findings,
)
from scripts.audit_permissions import run as run_permission_audit

# Optional import for Cerberus-specific audits (not available in external projects)
try:
    from protocol_engine import (
        get_project_insights,
        get_project_insight_recommendations,
        load_golden_standard_audit,
    )
    _PROTOCOL_ENGINE_AVAILABLE = True
except ImportError:
    _PROTOCOL_ENGINE_AVAILABLE = False
    def get_project_insights(): return {}
    def get_project_insight_recommendations(): return {}
    def load_golden_standard_audit(): return {}

setup_windows_utf8()
VERSION = get_centralized_version()


class StubVisitor(ast.NodeVisitor):
    """AST visitor to find empty stubs or NotImplementedError raises."""

    def __init__(self, filename):
        self.filename = filename
        self.errors = []

    def visit_FunctionDef(self, node):
        self.check_body(node, "Función")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.check_body(node, "Función asíncrona")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.check_body(node, "Clase")
        self.generic_visit(node)

    def check_body(self, node, node_type):
        body = node.body
        if not body:
            self.errors.append(
                f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' está vacía."
            )
            return
        if len(body) == 1:
            stmt = body[0]
            if isinstance(stmt, ast.Pass):
                self.errors.append(
                    f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub vacío (pass)."
                )
            elif (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is Ellipsis
            ):
                self.errors.append(
                    f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub vacío (...)."
                )
            elif isinstance(stmt, ast.Raise):
                if (
                    isinstance(stmt.exc, ast.Call)
                    and isinstance(stmt.exc.func, ast.Name)
                    and stmt.exc.func.id in ["NotImplementedError", "NotImplemented"]
                ):
                    self.errors.append(
                        f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub (raise NotImplementedError)."
                    )
                elif isinstance(stmt.exc, ast.Name) and stmt.exc.id in [
                    "NotImplementedError",
                    "NotImplemented",
                ]:
                    self.errors.append(
                        f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub (raise NotImplementedError)."
                    )


class CallGraphVisitor(ast.NodeVisitor):
    """AST visitor to map definitions and references to detect orphaned code."""

    def __init__(self):
        self.defined_funcs = set()
        self.referenced = set()

    def visit_FunctionDef(self, node):
        self.defined_funcs.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.defined_funcs.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.defined_funcs.add(node.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Registra el nombre ORIGINAL de cada import, incluyendo cuando hay alias.
        Sin esto, 'from X import Foo as bar' solo registra 'bar', nunca 'Foo'.
        Esto evita falsos positivos cuando thin wrappers usan aliases de importación.
        """
        for alias in node.names:
            self.referenced.add(alias.name)  # nombre original, no el alias local
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.referenced.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.referenced.add(node.attr)
        self.generic_visit(node)


class TryBlockVisitor(ast.NodeVisitor):
    """AST visitor to find empty/silent exception handlers."""

    def __init__(self, filename):
        self.filename = filename
        self.errors = []

    def visit_Try(self, node):
        for handler in node.handlers:
            body = handler.body
            is_silent = False
            if not body:
                is_silent = True
            elif len(body) == 1:
                stmt = body[0]
                if isinstance(stmt, ast.Pass):
                    is_silent = True
                elif (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Constant)
                    and stmt.value.value is Ellipsis
                ):
                    is_silent = True
                elif isinstance(stmt, ast.Continue):
                    is_silent = True

            if is_silent:
                handler_type = (
                    handler.type.id
                    if (handler.type and isinstance(handler.type, ast.Name))
                    else "generic"
                )
                self.errors.append(
                    f"D5: {self.filename} l.{handler.lineno} bloque 'except {handler_type}' silencioso (pass/continue) prohibido."
                )
        self.generic_visit(node)


class TestTheaterVisitor(ast.NodeVisitor):
    """Detecta patrones de teatro en archivos test (S22/S23): aserciones nulas,
    tests sin medición real, decoradores que enmascaran fallos permanentes.
    Solo se activa en funciones cuyo nombre comienza con 'test_'.
    """

    __test__ = (
        False  # No es una clase de test pese al prefijo 'Test' — pytest no la colecta.
    )

    def __init__(self, filename, source_lines):
        self.filename = filename
        self.source_lines = source_lines
        self.errors = []

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            self._check_trivial_asserts(node)
            self._check_no_asserts(node)
            self._check_nondiscriminating_raises_assert(node)
            self._check_if_false(node)
            self._check_xfail_skip(node)
            self._check_return_bool(node)
        self.generic_visit(node)

    def _check_return_bool(self, node):
        """Detecta tests que usan 'return True/False' en lugar de assert/pytest.fail (D9/PytestReturnNotNoneWarning)."""
        for stmt in ast.walk(node):
            if (
                isinstance(stmt, ast.Return)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, bool)
            ):
                self.errors.append(
                    f"D9: {self.filename} l.{stmt.lineno} {node.name}() usa 'return {stmt.value.value}' — "
                    f"usa assert/pytest.fail en cambio (PytestReturnNotNoneWarning/S23/B3)."
                )

    def _check_nondiscriminating_raises_assert(self, node):
        """P0.2: assert sobre la variable de pytest.raises sin comparación (assert exc /
        assert exc.value) — siempre truthy, no discrimina. El discriminante es un Compare
        (exc.type is X, X in str(exc.value)). Atado a la var del 'as' para no sobre-acusar.
        """
        exc_vars = set()
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.With):
                for item in stmt.items:
                    ce = item.context_expr
                    if (
                        isinstance(ce, ast.Call)
                        and isinstance(ce.func, ast.Attribute)
                        and ce.func.attr == "raises"
                        and isinstance(item.optional_vars, ast.Name)
                    ):
                        exc_vars.add(item.optional_vars.id)
        if not exc_vars:
            return
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Assert):
                continue
            t = stmt.test
            base = (
                t.id
                if isinstance(t, ast.Name)
                else (
                    t.value.id
                    if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                    else None
                )
            )
            if base in exc_vars:
                self.errors.append(
                    f"D9: {self.filename} l.{stmt.lineno} assert sobre '{base}' de pytest.raises "
                    f"sin comparación — siempre truthy, no discrimina (S23/B1). "
                    f"Usa exc.type/exc.value con ==/is/in."
                )

    def _check_trivial_asserts(self, node):
        for stmt in ast.walk(node):
            if (
                isinstance(stmt, ast.Assert)
                and isinstance(stmt.test, ast.Constant)
                and stmt.test.value is True
            ):
                self.errors.append(
                    f"D9: {self.filename} l.{stmt.lineno} assert True literal — asercion nula (S23/B1)."
                )
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if (
                    isinstance(call.func, ast.Attribute)
                    and call.func.attr in ("assertTrue", "assertFalse")
                    and call.args
                    and isinstance(call.args[0], ast.Constant)
                    and call.args[0].value in (True, False)
                ):
                    self.errors.append(
                        f"D9: {self.filename} l.{stmt.lineno} {call.func.attr}(literal) — asercion tautologica (S23/B1)."
                    )
                if (
                    isinstance(call.func, ast.Attribute)
                    and call.func.attr == "assertEqual"
                    and len(call.args) >= 2
                    and isinstance(call.args[0], ast.Name)
                    and isinstance(call.args[1], ast.Name)
                    and call.args[0].id == call.args[1].id
                ):
                    self.errors.append(
                        f"D9: {self.filename} l.{stmt.lineno} assertEqual(x, x) — tautologia (S23/B5)."
                    )

    def _check_no_asserts(self, node):
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assert):
                return
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                fn = stmt.value.func
                attr = getattr(fn, "attr", "")
                name = getattr(fn, "id", "")
                if (
                    attr.startswith("assert")
                    or attr in ("raises", "fail")
                    or name in ("raises", "fail")
                ):
                    return
        self.errors.append(
            f"D9: {self.filename} l.{node.lineno} {node.name}() sin aserciones — siempre pasa (S23/B2)."
        )

    def _check_if_false(self, node):
        for stmt in ast.walk(node):
            if (
                isinstance(stmt, ast.If)
                and isinstance(stmt.test, ast.Constant)
                and stmt.test.value is False
            ):
                self.errors.append(
                    f"D9: {self.filename} l.{stmt.lineno} 'if False:' en test — codigo inalcanzable (S23/C3)."
                )

    def _check_xfail_skip(self, node):
        for dec in node.decorator_list:
            mark = self._pytest_mark_name(dec)
            if mark == "xfail":
                lineno = dec.lineno
                prev = self.source_lines[lineno - 2].strip() if lineno >= 2 else ""
                if not any(
                    prev.startswith(t)
                    for t in ("# TODO:", "# REMOVE_WHEN:", "# reason:", "# Reason:")
                ):
                    self.errors.append(
                        f"D9: {self.filename} l.{lineno} @xfail sin criterio de remocion — ignorado permanente (S22/C1)."
                    )
            elif mark == "skip":
                has_reason = isinstance(dec, ast.Call) and any(
                    kw.arg == "reason" for kw in dec.keywords
                )
                if not has_reason:
                    self.errors.append(
                        f"D9: {self.filename} l.{dec.lineno} @skip sin reason= — ignorado sin justificacion (S23/C2)."
                    )

    def _pytest_mark_name(self, dec):
        func = getattr(dec, "func", dec)
        if isinstance(func, ast.Attribute):
            return func.attr
        return None


def _max_ast_nesting(node: ast.AST, depth: int = 0) -> int:
    """Mide profundidad máxima de anidamiento de control flow.
    Mandato de aplanamiento: código real no debe superar 4 niveles de anidamiento.
    Cada nivel adicional indica que la lógica debe extraerse a una función dedicada.
    """
    NEST_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)
    if isinstance(node, NEST_NODES):
        depth += 1
    return max(
        (_max_ast_nesting(child, depth) for child in ast.iter_child_nodes(node)),
        default=depth,
    )


def _check_ast_pattern(node: ast.AST, pattern: str, value: str | None) -> bool:
    """Valida si un nodo AST coincide con el patrón y valor declarados (aplanado)."""
    if f"ast.{type(node).__name__}" != pattern:
        return False
    if value and (not isinstance(node, ast.Constant) or str(node.value) != value):
        return False
    return True


def _evaluate_keywords(
    rule_id: str, message: str, keywords: list, lines: list, f_name: str
) -> list[str]:
    """Helper to evaluate list of keywords against file lines."""
    errors = []
    for kw in keywords:
        for idx, line in enumerate(lines, 1):
            if kw in line:
                errors.append(f"[{rule_id}]: {f_name} l.{idx} — {message}")
    return errors


def _evaluate_func(
    rule_id: str, message: str, func_name: str, tree: ast.AST, f_name: str
) -> list[str]:
    """Helper to evaluate function calls against AST."""
    errors = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == func_name
        ):
            lineno = getattr(node, "lineno", 1)
            errors.append(f"[{rule_id}]: {f_name} l.{lineno} — {message}")
    return errors


def _evaluate_pattern(
    rule_id: str, message: str, pattern: str, value: str, tree: ast.AST, f_name: str
) -> list[str]:
    """Helper to evaluate structural patterns against AST."""
    errors = []
    for node in ast.walk(tree):
        if _check_ast_pattern(node, pattern, value):
            lineno = getattr(node, "lineno", 1)
            errors.append(f"[{rule_id}]: {f_name} l.{lineno} — {message}")
    return errors


def _evaluate_single_rule(
    rule: dict, f_name: str, f_ext: str, lines: list, tree: ast.AST | None
) -> list[str]:
    """Evalúa una sola regla declarativa sobre un archivo y su AST (aplanado)."""
    errors = []
    rule_id = rule.get("id")
    extensions = rule.get("extensions", [])
    if extensions and f_ext not in extensions:
        return errors

    pattern = rule.get("pattern")
    value = rule.get("value")
    keywords = rule.get("keywords", [])
    func_name = rule.get("func")
    message = rule.get("message", f"Regla {rule_id} fallida.")

    if keywords:
        errors.extend(_evaluate_keywords(rule_id, message, keywords, lines, f_name))

    if func_name and tree:
        errors.extend(_evaluate_func(rule_id, message, func_name, tree, f_name))

    if pattern and tree:
        errors.extend(_evaluate_pattern(rule_id, message, pattern, value, tree, f_name))

    return errors


class DeepForensicAuditor:
    """Orquestador de auditoría 8D con auto‑fix de higiene del workspace (estándar)."""

    def __init__(self, target_project_path="."):
        """Inicializa el auditor apuntando al proyecto destino."""
        self.project_path = Path(target_project_path).resolve()
        # Detect if this is Cerberus (has protocol_engine available)
        self.is_cerberus = (
            _PROTOCOL_ENGINE_AVAILABLE
            and (self.project_path / "protocol_engine").exists()
        ) or self.project_path.name == "Cerberus"
        self.registry_path = (
            self.project_path / ".protocol" / "metadata" / "REGISTRY.json"
        )

        # Detect if we are running in a subtree satellite
        self.is_satellite = (
            not self.registry_path.exists()
            and (self.project_path / ".protocol-core").exists()
        )

        if self.is_satellite:
            self.spec_file = self.project_path / ".protocol-core" / "SPEC.md"
        else:
            self.spec_file = self.project_path / "SPEC.md"

        self.hard_excludes = [
            # Generated tooling artifacts — never project code
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            "venv",
            "env",
            ".venv",
            "node_modules",
            ".next",
            "dist",
            "build",
            "out",
            "playwright-report",
            "test-results",
            "cfdi_downloads_sat",
            # Governance metadata dir — auto-generated maps, evidence, manifests
            ".protocol",
            # Evidence subdir — timestamped generated files, gitignored
            "evidence",
            # Backup stores — other projects' protocol copies, gitignored
            "backups",
            # Retrospective session exports — generated output, gitignored
            "exports",
            # Credentials infrastructure — gitignored, not project code
            ".secrets",
            # The ONLY business exemption per CoderCerberus protocol
            "deprecated",
            # Symlink/junction to external directory — must not be traversed (causes infinite scan)
            "PROTOCOLO_GLOBAL",
            # Golden Standard — repo independiente en D:\AI\VibeCoding_GoldenStandard. Directorio local eliminado.
            # Entrada mantenida por si el dir reaparece como subtree/symlink; el scan lo excluye en ese caso.
            "Golden_Standard",
        ]
        self.audit_extensions = ["*.py", "*.html", "*.js", "*.css"]
        self.whitelist = self._extract_whitelist()

        self.authorized_dot_dirs = set(self._DOT_DIR_WHITELIST)
        if self.is_satellite:
            self.authorized_dot_dirs.add(".protocol-core")

    def _extract_whitelist(self) -> set:
        """Extrae la lista de archivos permitidos especificos del proyecto destino."""
        base = set(
            [
                ".claudeignore",
                "AGENT.md",
                "PROTOCOL_SYSTEM.md",
                "PROTOCOL_BEHAVIOR.md",
                "SPEC.md",
                ".agent_state.json",
                ".gitignore",
                ".cursorrules",
                "HISTORIAL.md",
                "GLOBAL_LEARNING.md",
                "PRE_DELIVERY_CHECKLIST.md",
                "STATUS.md",
                "CHECKLIST.md",
                "pytest.ini",
                "docs/architecture.md",
                "protocol_engine/rules/verification.yaml",
                "tests/rules/test_pending_escalation.py",
                "docs/rules.md",
                "protocol_engine/close_pending.py",
                "protocol_engine/pending_tasks.json",
                "protocol_engine/rule_collector.py",
                "protocol_engine/rules_engine.py",
                "protocol_engine/rules/pending_escalation.yaml",
                "protocol_engine/rules/rule_severity.yaml",
                "protocol_engine/rules/test_coverage.yaml",
                "scripts/generate_rule_test_scaffold.py",
                "scripts/generate_rules_docs.py",
                "scripts/blast_radius.py",
                "scripts/validate_external_audit_phases.py",
                "scripts/manage_review_queue.py",
                "scripts/send_review_reminder.py",
                "scripts/setup_reminder_task.py",
                ".compact_needed",  # compact sentinel — operational, not zombie
                ".protocol/review_queue.json",
                ".protocol/.gitattributes",
                "scripts/split_golden_standard_catalogs.py",
                "scripts/normalize_golden_audit_consumer_contract.py",
                "docs/golden_standard_audit_report.md",
                "tests/test_golden_standard_compliance.py",
                ".protocol/metadata/golden_standard_audit.json",
                ".protocol/metadata/satellite_learnings.json",
                "scripts/clean_satellites.py",
                "scripts/migrate_to_subtree.py",
                "scripts/generate_rule_test_scaffold.py",
                "scripts/repair_failing_tests.py",
                # .claude/ infrastructure files — hardcoded to survive SPEC.md sentence-punctuation edge cases
                ".claude/cache/protocol_rules.json",
                ".claude/settings.json",
                ".claude/settings.local.json",
                ".claude/settings.template.json",
                ".claude/CLAUDE.md",
                ".claude/.gitignore",
                ".claude/ACTIVE_HOOKS.json",
                # 00 audit/ is a distinct audit topology. Keep these paths centralized here so any
                # doc-name or ordering change forces an explicit runner update during preflight.
                "00 audit/00_CONSTITUCION_CERBERUS.md",
                "00 audit/01_AUDITORIA_LOCAL.md",
                "00 audit/02_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md",
            ]
        )

        if self.spec_file.exists():
            content = self.spec_file.read_text(encoding="utf-8", errors="ignore")
            # Match standard files with extensions
            matches = re.findall(
                r"([a-zA-Z0-9_/.-]+\.(?:py|md|sh|json|yaml|txt|db|html|bat|js|css|sql|cmd|ps1|example))",
                content,
            )
            base.update(matches)
            # Match dotfiles without extensions (e.g., .gitignore, .cursorrules)
            dotfiles = re.findall(r"(\.(?:gitignore|cursorrules|claude))", content)
            base.update(dotfiles)
            # Match .claude/* patterns
            claude_files = re.findall(r"(\.claude/[a-zA-Z0-9_.-]+)", content)
            base.update(claude_files)
            # Match git hooks
            hooks = re.findall(r"(scripts/hooks/[a-zA-Z0-9_-]+)", content)
            base.update(hooks)

        if self.is_satellite:
            # Prefix all core files with .protocol-core/
            core_whitelist = set(base)
            for f in core_whitelist:
                base.add(f".protocol-core/{f}")

            # Whitelist tracked files in satellite
            try:
                import subprocess

                res = subprocess.run(
                    ["git", "ls-files"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_path),
                    encoding="utf-8",
                    errors="ignore",
                )
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        line = line.strip().replace("\\", "/")
                        if line and not line.startswith(".protocol-core/"):
                            base.add(line)
            except Exception as exc:
                logging.warning("Failed to run git ls-files: %s", exc)

        return base

    def _get_audit_files(self) -> list:
        """Obtiene todos los archivos fuente que deben ser auditados en el target."""
        files = []
        for ext in self.audit_extensions:
            # Buscar en root del proyecto
            files.extend(list(self.project_path.glob(ext)))
            # Buscar en subcarpetas comunes (scripts, tests, src, protocol_engine)
            for sub in ["scripts", "tests", "src", "protocol_engine"]:
                sub_dir = self.project_path / sub
                if sub_dir.exists():
                    files.extend(list(sub_dir.glob(f"**/{ext}")))

        # Exención mínima y real (Sprint 6): estos 4 core se auto-eximen de la D-suite porque
        # CONTIENEN los patrones de detección como literales (eval(/exec(/shell=True/except…) y
        # escanearse a sí mismos daría falsos positivos en D6/D7. La pureza D5 (except mudos) de
        # estos archivos NO queda sin cubrir: se re-arma en tests/test_core_self_audit.py.
        return [
            f
            for f in files
            if f.name
            not in [
                "__init__.py",
                "run_security_audit_12d.py",
                "verify_chaos_robustness.py",
                "core_utils.py",
                "test_portability.py",
            ]
        ]

    def _is_legitimate_test_file(self, rel_path: str) -> bool:
        """Solo archivos test con convención de nombre son auto-whitelisted en tests/.
        Archivos arbitrarios en tests/ (backdoor.py, evil.json) siguen siendo zombis.
        """
        fname = Path(rel_path).name
        return (
            rel_path.startswith("tests/")
            or rel_path.startswith(".protocol-core/tests/")
        ) and (
            fname.startswith("test_")
            or fname.startswith("automation_test_")
            or fname in ("conftest.py", "__init__.py", "pytest.ini")
        )

    def audit_d1_integrity(self) -> list:
        """D1: Whitelist Forense (Polyglot) + permission & duplicate checks."""
        errors = []
        if not self.project_path.exists():
            return [f"Ruta de proyecto no existe: {self.project_path}"]
        # Permission audit (also performed in D4, but we enforce here as well)
        if not run_permission_audit(self.project_path):
            errors.append(
                "D1: Permission audit failed (dangerous permissions detected)"
            )

        for root, dirs, files in os.walk(self.project_path, followlinks=False):
            # Exclude hard-excluded dirs AND symlinks/junctions (prevent infinite traversal)
            # Use os.path.islink for junction detection on Windows (more reliable than Path.is_symlink)
            dirs[:] = [
                d
                for d in dirs
                if d not in self.hard_excludes
                and not os.path.islink(os.path.join(root, d))
            ]
            for file in files:
                rel_path = (Path(root).relative_to(self.project_path) / file).as_posix()
                if file in self.hard_excludes or rel_path in self.hard_excludes:
                    continue
                # VC-114/VC-118: "desconfia de documentos confianza en codigo"
                # Exclude non-code documents, data, and assets from being flagged as zombie files.
                ext = Path(file).suffix.lower()
                if (
                    ext
                    in (
                        ".xml",
                        ".xlsx",
                        ".xls",
                        ".csv",
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".gif",
                        ".ico",
                        ".pdf",
                        ".db",
                        ".sqlite",
                        ".zip",
                        ".tar",
                        ".gz",
                        ".md",
                        ".tsbuildinfo",
                        ".docx",
                        ".log",
                        ".env",
                        ".txt",
                        ".yaml",   # data/config — no es código ejecutable
                        ".yml",    # idem
                        ".json",   # idem
                        ".toml",   # idem
                    )
                    or rel_path.endswith(".d.ts")
                    or Path(file).name.startswith(".env")
                ):
                    continue
                if (
                    rel_path not in self.whitelist
                    and not self._is_legitimate_test_file(rel_path)
                ):
                    errors.append(f"Archivo no registrado (Zombi): {rel_path}")

        # VC-118: Zombie Compatibility Theater — detect shim patterns in active scripts
        errors.extend(self._audit_d1_zombie_compat())
        # Barrier 3: dot-directory whitelist (unauthorized hidden dirs in root)
        errors.extend(self._audit_d1_dot_directories())
        return errors

    # Barrier 3: authorized dot-directories in repo root.
    _DOT_DIR_WHITELIST = frozenset(
        {
            ".git",
            ".claude",
            ".codex",  # local Codex session config/hooks
            ".github",
            ".protocol",
            ".secrets",
            ".pytest_cache",
            ".ruff_cache",  # tool caches — ephemeral, OK
        }
    )

    def _audit_d1_dot_directories(self) -> list:
        """D1 sub-check: detect unauthorized dot-directories in repo root (Barrier 3)."""
        errors = []
        try:
            for item in self.project_path.iterdir():
                if (
                    item.is_dir()
                    and item.name.startswith(".")
                    and item.name not in self.authorized_dot_dirs
                ):
                    errors.append(
                        f"D1 [ZOMBIE-DIR]: '{item.name}/' no autorizado — "
                        f"agregar a _DOT_DIR_WHITELIST con justificación o eliminar"
                    )
        except Exception as exc:
            errors.append(f"D1: no se pudo escanear directorio raíz: {exc}")
        return errors

    # VC-118 shim patterns (AGENT.md S19 enforcement).
    # Each tuple: (compiled_regex, label, match_mode)
    # match_mode "comment" = only check lines where stripped line starts with '#'
    # match_mode "import"  = only check lines where stripped line starts with 'from'/'import'
    # match_mode "any"     = check all lines
    _ZOMBIE_PATTERNS = [
        (
            re.compile(r"\bbackward[- ]?compat\b", re.IGNORECASE),
            "backward compat comment",
            "comment",
        ),
        (
            re.compile(r"\bcompatibility shim\b", re.IGNORECASE),
            "compatibility shim comment",
            "comment",
        ),
        (
            re.compile(r"\bfor now\b.*\bcompat", re.IGNORECASE),
            "for-now compat comment",
            "comment",
        ),
        (re.compile(r"\bor\b.+\.exists\(\)"), "dual .exists() OR fallback", "any"),
        (
            re.compile(r"^\s*(from|import)\s+deprecated\b", re.IGNORECASE),
            "import desde deprecated/",
            "import",
        ),
    ]

    def _is_zombie_line(self, line: str, mode: str, pattern: re.Pattern) -> bool:
        """Determines if a given line contains a zombie pattern match based on mode."""
        stripped = line.lstrip()
        if mode == "comment" and not stripped.startswith("#"):
            return False
        if mode == "import" and not re.match(
            r"\s*(from|import)\b", line, re.IGNORECASE
        ):
            return False
        return bool(pattern.search(line))

    def _audit_single_file_zombies(self, py_file: Path) -> list[str]:
        """Scans a single python file for any zombie compatibility markers."""
        errors = []
        try:
            lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            return errors

        for pattern, label, mode in self._ZOMBIE_PATTERNS:
            for idx, line in enumerate(lines, 1):
                if self._is_zombie_line(line, mode, pattern):
                    errors.append(
                        f"D1: VC-118 Zombie Compat en {py_file.name} l.{idx}: {label}. "
                        f"REEMPLAZAR = ELIMINAR + CREAR (S19)."
                    )
                    break  # one hit per pattern per file is enough
        return errors

    def _audit_d1_zombie_compat(self) -> list:
        """D1 sub-check (VC-118): detect Zombie Compatibility Theater in active scripts."""
        errors = []
        scripts_dir = self.project_path / "scripts"
        if not scripts_dir.exists():
            return errors
        for py_file in scripts_dir.glob("*.py"):
            if "deprecated" in py_file.parts:
                continue
            if py_file.name == Path(__file__).name:
                continue  # auditor itself contains pattern definitions by necessity
            errors.extend(self._audit_single_file_zombies(py_file))
        return errors

    def _check_spec_completeness(self) -> list[str]:
        """Validates SPEC.md structure, CHECKLIST.md, and key core scripts existence."""
        errors = []
        if not self.spec_file.exists():
            return ["Falla Critica: Falta SPEC.md."]

        content = self.spec_file.read_text(encoding="utf-8", errors="ignore")
        if "DATA SKELETON & UI LAYOUT" not in content:
            errors.append(
                "SPEC.md: Falta seccion mandataria DATA SKELETON & UI LAYOUT."
            )

        if not (self.project_path / "CHECKLIST.md").exists():
            errors.append(
                "D2: CHECKLIST.md no existe — revision humana de calidad de tests no documentada (S23)."
            )

        core_scripts = [
            "scripts/run_security_audit_12d.py",
            "scripts/run_compliance_tests.py",
            "scripts/verify_chaos_robustness.py",
            "scripts/validate_chunking.py",
            "scripts/check_empirical_proof.py",
        ]
        for script_rel in core_scripts:
            script_path = self.project_path / script_rel
            subtree_path = self.project_path / ".protocol-core" / script_rel
            if not script_path.exists() and not subtree_path.exists():
                errors.append(
                    f"D2: Script core declarado en SPEC.md no existe: {script_rel}"
                )
        return errors

    def _check_file_technical_debt(
        self, f: Path, lines: list, debt_pattern: re.Pattern
    ) -> list[str]:
        """Scans a file for unresolved technical debt comments (TODO/FIXME/BUG)."""
        errors = []
        for idx, line in enumerate(lines):
            match = debt_pattern.search(line)
            if match:
                errors.append(
                    f"D7: {f.name} l.{idx+1} marca de deuda técnica sin resolver ({match.group().strip()})."
                )
        return errors

    def _check_file_stubs(self, f: Path, file_content: str, lines: list) -> list[str]:
        """Validates that no empty stubs or mock functions are present in the file."""
        errors = []
        if f.suffix == ".py":
            try:
                tree = ast.parse(file_content, filename=f.name)
                visitor = StubVisitor(f.name)
                visitor.visit(tree)
                errors.extend(visitor.errors)
            except Exception as e:
                logging.error(f"D7: Fallo parsing AST de stubs en {f.name}: {e}")
        elif f.suffix in [".js", ".html"]:
            js_stub_pattern = re.compile(
                r"function\s+\w+\s*\([^)]*\)\s*\{\s*(?:pass|return\s*;?|throw\s+new\s+Error\([^)]*\);?)?\s*\}"
            )
            for idx, line in enumerate(lines):
                if js_stub_pattern.search(line) or (
                    "function" in line and "{}" in line
                ):
                    errors.append(
                        f"D7: {f.name} l.{idx+1} función stub vacía detectada en JavaScript."
                    )
        return errors

    def _validate_gitignore_comments(self) -> list[str]:
        """D2: Exclusión sin auditoría previa (VC-111).
        Verifica que todas las exclusiones en el archivo .gitignore estén antecedidas por
        un comentario descriptivo en el mismo bloque para evitar ignorar carpetas sin auditar.
        """
        errors = []
        gitignore_path = self.project_path / ".gitignore"
        if not gitignore_path.exists():
            return errors

        try:
            content = gitignore_path.read_text(encoding="utf-8")
        except OSError:
            return errors

        lines = content.splitlines()
        has_comment = False
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                has_comment = False
                continue
            if stripped.startswith("#"):
                has_comment = True
                continue
            
            # Si no es comentario ni línea en blanco, es una regla de exclusión.
            # Verificamos si se ha visto un comentario en el bloque activo.
            if not has_comment:
                errors.append(
                    f"D2: VC-111: .gitignore l.{idx} — Regla de exclusión '{stripped}' sin comentario justificativo previo."
                )
        return errors

    def audit_d2_completeness(self) -> list:
        """D2: SPEC Semantico local + D7 Code Completeness."""
        errors = self._check_spec_completeness()
        if errors and "Falla Critica: Falta SPEC.md." in errors:
            return errors

        # Validar comentarios en gitignore (VC-111)
        errors.extend(self._validate_gitignore_comments())


        # Verify Phase 0 purge evidence files for external projects (VC-092 & VC-108 checks)
        if not self.is_cerberus:
            has_purge_plan = False
            has_purge_result = False
            for p in self.project_path.rglob("*.md"):
                # Ignore deprecated, .git, node_modules, and virtual environments
                parts = p.relative_to(self.project_path).parts
                if any(x in parts for x in ["deprecated", ".git", "node_modules", "venv", ".venv"]):
                    continue
                if p.name == "purge_plan.md":
                    has_purge_plan = True
                elif p.name == "phase_0_purge_result.md":
                    has_purge_result = True
            if not has_purge_plan:
                errors.append("D2: Falta el archivo de evidencia de purga 'purge_plan.md' para auditoría externa.")
            if not has_purge_result:
                errors.append("D2: Falta el archivo de evidencia de purga 'phase_0_purge_result.md' para auditoría externa.")

        files = self._get_audit_files()
        debt_pattern = re.compile(r"(?:#|//|/\*)\s*(?:TODO|FIXME|BUG)\b", re.IGNORECASE)

        for f in files:
            file_content = f.read_text(encoding="utf-8", errors="ignore")
            lines = file_content.splitlines()

            errors.extend(self._check_file_technical_debt(f, lines, debt_pattern))
            errors.extend(self._check_file_stubs(f, file_content, lines))

        return errors

    def _check_file_docstrings(self, files: list) -> list[str]:
        """Validates standard module docstrings and documentation density ratio."""
        errors = []
        for f in files:
            content = f.read_text(encoding="utf-8", errors="ignore")
            defs = re.findall(
                r"^\s*(?:def|class|function|const|let)\s+\w+", content, re.MULTILINE
            )
            docs = re.findall(r'["\']{3}[\s\S]*?["\']{3}|\/\*\*[\s\S]*?\*\/', content)

            if f.suffix == ".py" and not (
                content.startswith('"""')
                or content.startswith("'''")
                or content.startswith("#!")
            ):
                errors.append(f"D3: {f.name} falta docstring de modulo.")

            if len(defs) > 5 and len(docs) < 1:
                errors.append(
                    f"D3: {f.name} es una caja negra ({len(defs)} funciones sin documentacion)."
                )
        return errors

    def _parse_call_graphs(self, py_files: list) -> tuple[dict, set, set]:
        """Generates AST call graph definitions and references for list of Python files."""
        defined_in_files = {}
        all_referenced = set()
        thin_wrapper_files = set()
        for f in py_files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=f.name)
                visitor = CallGraphVisitor()
                visitor.visit(tree)
                defined_in_files[f.name] = visitor.defined_funcs
                all_referenced.update(visitor.referenced)
                if "thin wrapper" in content[:500].lower():
                    thin_wrapper_files.add(f.name)
            except Exception as e:
                logging.error(
                    f"D3: Fallo analizando grafo de llamadas en {f.name}: {e}"
                )
        return defined_in_files, all_referenced, thin_wrapper_files

    def _check_orphaned_definitions(
        self,
        defined_in_files: dict,
        all_referenced: set,
        thin_wrapper_files: set,
        exclude_names: set,
    ) -> list[str]:
        """Identifies any defined functions that are never called internally (dead code)."""
        errors = []
        for fname, definitions in defined_in_files.items():
            for name in definitions:
                if (
                    name in exclude_names
                    or name.startswith("test_")
                    or name.startswith("_")
                ):
                    continue
                if fname in thin_wrapper_files:
                    continue
                if name not in all_referenced:
                    errors.append(
                        f"D3: {fname} define la función/clase huérfana '{name}' (dead code)."
                    )
        return errors

    def audit_d3_clarity(self) -> list:
        """D3: Paridad de Documentacion + Analisis AST de Conectividad (Dead Code)."""
        files = self._get_audit_files()
        errors = self._check_file_docstrings(files)

        py_files = [
            f
            for f in files
            if f.suffix == ".py" and "test_" not in f.name and "tests" not in f.parts
        ]
        defined_in_files, all_referenced, thin_wrapper_files = self._parse_call_graphs(
            py_files
        )

        exclude_names = {
            "__init__",
            "__main__",
            "__str__",
            "__repr__",
            "__eq__",
            "__hash__",
            "main",
            "run",
            "setUp",
            "tearDown",
            "setup",
            "teardown",
            "audit_d1_integrity",
            "audit_d2_completeness",
            "audit_d3_clarity",
            "audit_d4_anti_spaghetti",
            "audit_d5_angry_path",
            "audit_d6_anti_slop",
            "audit_d8_test_coverage",
            "audit_d9_test_purity",
            "audit_d10_tokenomics",
            "audit_d12_validate_satellite_drift",
            "_name_congruency_check",
            "_audit_d10_tokenomics_inner",
            "check_proof",
            "has_human_validation",
            "validate_chunks",
            "find_hygiene_findings",
            "repair_mojibake",
            "deprecate_legacy_scripts",
            "DeepForensicAuditor",
            "SilentFailureEnforcer",
            "StubVisitor",
            "CallGraphVisitor",
            "TryBlockVisitor",
            "do_GET",
            "do_POST",
            "do_OPTIONS",
            "do_DELETE",
            "do_PUT",
            "log_message",
            "changed_files",
            "ui_files",
            "validate_operation_approved",
            "log_operation",
            "log_completion",
            "get_summary",
            "get_alerts",
            "detect_semantic_conflict",
            "extract_rules_touched",
            "compute_checkpoint_hash",
            "create_checkpoint",
            "export_checkpoint_json",
            "validate_historial_checkpoints",
            # protocol_engine exports — called cross-file via __init__.py
            "get_project_insights",
            "get_project_insight_recommendations",
        }

        errors.extend(
            self._check_orphaned_definitions(
                defined_in_files, all_referenced, thin_wrapper_files, exclude_names
            )
        )
        return errors

    def _compute_module_fan_in(self, py_files: list) -> list[str]:
        """Graphify-inspired: detecta módulos con demasiadas dependencias entrantes (god nodes).

        Un módulo importado por >8 módulos distintos es un god node — acoplamiento excesivo
        que rompe la modularidad. Lógica agnóstica de graphify/Leiden clustering.
        """
        import_counts: dict[str, int] = {}
        for f in py_files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=f.name)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        names = (
                            [alias.name for alias in node.names]
                            if isinstance(node, ast.Import)
                            else ([node.module] if node.module else [])
                        )
                        for name in names:
                            base = name.split(".")[0] if name else ""
                            if base:
                                import_counts[base] = import_counts.get(base, 0) + 1
            except Exception as exc:
                logging.debug("_compute_module_fan_in: skip %s: %s", f.name, exc)
                continue
        # Excluir stdlib — son universales por diseño, no son god nodes arquitectónicos
        _STDLIB = {
            "os", "sys", "re", "json", "logging", "pathlib", "argparse",
            "subprocess", "datetime", "typing", "shutil", "io", "ast",
            "collections", "itertools", "functools", "hashlib", "time",
            "tempfile", "copy", "math", "enum", "abc", "contextlib",
            "unittest", "threading", "queue", "signal", "struct", "uuid",
            # stdlib adicional y frameworks de test/infra — universales por diseño
            "sqlite3", "pytest", "dataclasses", "traceback", "warnings",
            "inspect", "importlib", "types", "weakref", "gc",
        }
        # Excluir paquetes raíz del propio proyecto (son "god" por diseño estructural)
        root = Path(__file__).resolve().parent.parent
        _PROJECT_ROOTS = {
            p.name for p in root.iterdir()
            if p.is_dir() and not p.name.startswith(".") and (p / "__init__.py").exists()
        }
        _EXCLUDED = _STDLIB | _PROJECT_ROOTS
        threshold = 8
        return [
            f"D4 VC-069 god-node: '{mod}' importado por {count} módulos — "
            f"acoplamiento excesivo (umbral: {threshold}). Extraer interfaz estable."
            for mod, count in import_counts.items()
            if count >= threshold and not mod.startswith("_") and mod not in _EXCLUDED
        ]

    def audit_d4_anti_spaghetti(self) -> list:
        """D4: Complejidad Forense Multi-Lenguaje con análisis de contenido."""
        errors = []
        files = self._get_audit_files()
        py_files = [f for f in files if f.suffix == ".py"]
        errors.extend(self._compute_module_fan_in(py_files))
        for f in files:
            content = f.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                stripped = line.strip()
                indent = len(line) - len(line.lstrip())

                # Verificar indentation excesiva
                if indent > 32:
                    errors.append(
                        f"D4: {f.name} l.{i+1} Indentación excesiva (spaghetti probable)."
                    )

                # Detectar lógica compleja (independiente de longitud)
                logical_ops = (
                    stripped.count(" and ")
                    + stripped.count(" or ")
                    + stripped.count("&&")
                    + stripped.count("||")
                )
                is_complex_logic = logical_ops > 2

                # Detectar si es una lista/array de datos
                is_data_list = any(
                    pattern in stripped
                    for pattern in [
                        "= [",
                        "= {",
                        ": [",
                        ": {",
                        "data = ",
                        "items = ",
                        "values = ",
                        "dates = ",
                        "const ",
                        "let ",
                        "var ",
                    ]
                )

                # Si es lógica compleja (spaghetti real), reportar
                if is_complex_logic and not is_data_list:
                    errors.append(
                        f"D4: {f.name} l.{i+1} Spaghetti detectado ({logical_ops} operadores lógicos). "
                        f"Sugerencia: extraer condición a función dedicada."
                    )

                # Análisis de líneas largas (>250 chars)
                if len(line) > 250:
                    is_data_content = any(
                        pattern in stripped
                        for pattern in [
                            "json",
                            "base64",
                            '":[',
                            '": [',
                            '"value":',
                            "data",
                        ]
                    )

                    if is_data_list or is_data_content:
                        # Datos o lista: sugerir extracción
                        pass

        return errors

    def _check_python_try_catch(
        self, f: Path, content: str, is_test: bool
    ) -> list[str]:
        errors = []
        try:
            tree = ast.parse(content, filename=f.name)
            if not is_test:
                # Verifica existencia real de bloques try (no string en comentario)
                has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
                if not has_try and len(content.splitlines()) > 100:
                    errors.append(
                        f"D5: {f.name} sin manejo de errores real (Fragilidad detectada)."
                    )
            visitor = TryBlockVisitor(f.name)
            visitor.visit(tree)
            errors.extend(visitor.errors)
        except Exception as e:
            logging.error(f"D5: Fallo parsing AST de Try/Except en {f.name}: {e}")
        return errors

    def _check_javascript_catch(self, f: Path, content: str) -> list[str]:
        errors = []
        lines = content.splitlines()
        js_catch_pattern = re.compile(
            r"catch\s*\([^)]*\)\s*\{\s*(?:pass|continue|return)?\s*\}"
        )
        for idx, line in enumerate(lines):
            if js_catch_pattern.search(line):
                errors.append(
                    f"D5: {f.name} l.{idx+1} bloque catch silencioso en JavaScript."
                )
        return errors

    def _run_chaos_robustness_check(self) -> list[str]:
        errors = []
        try:
            chaos_script = self.project_path / "scripts/verify_chaos_robustness.py"
            if chaos_script.exists():
                returncode, stdout, stderr = run_command(
                    [sys.executable, "-m", "scripts.verify_chaos_robustness"],
                    cwd=str(self.project_path),
                )
                if returncode != 0:
                    errors.append(
                        "D5: Verify Chaos Robustness falló — resiliencia real no certificada."
                    )
        except Exception as e:
            logging.error(f"Chaos Monkey audit error: {e}")
        return errors

    def audit_d5_angry_path(self) -> list:
        """D5: Angry Path Validation + AST Try Block Rigor."""
        errors = []
        files = self._get_audit_files()
        for f in files:
            if f.suffix in [".py", ".js", ".html"]:
                content = f.read_text(encoding="utf-8", errors="ignore")
                # Test files usan pytest/unittest para manejo de errores; no requieren try/except
                is_test = f.name.startswith("test_") or f.name.startswith(
                    "automation_test_"
                )

                # Python AST Try/Except check (AST real — no string search)
                if f.suffix == ".py":
                    errors.extend(self._check_python_try_catch(f, content, is_test))
                elif (
                    len(content.splitlines()) > 100
                    and "try" not in content
                    and not is_test
                ):
                    errors.append(
                        f"D5: {f.name} sin manejo de errores (Fragilidad detectada)."
                    )

                # JS regex empty catch check
                elif f.suffix == ".js":
                    errors.extend(self._check_javascript_catch(f, content))

        # Chaos robustness check
        errors.extend(self._run_chaos_robustness_check())
        return errors

    def _check_weak_typing(self, f: Path, content: str) -> bool:
        if "typing.Any" in content:
            return True
        if "from typing import" in content and re.search(r"\bAny\b", content):
            return True
        if f.suffix == ".py" and re.search(
            r"(?::\s*any\b|\->\s*any\b)", content, re.IGNORECASE
        ):
            return True
        return False

    def _check_file_anti_slop(self, f: Path, content: str) -> list[str]:
        errors = []
        if self._check_weak_typing(f, content):
            errors.append(
                f"D6: {f.name} usa tipado debil prohibido (any/Any) bajo Mandato S3."
            )

        if "var " in content and f.suffix in [".js", ".html"]:
            errors.append(f"D6: {f.name} usa patron obsoleto (var) bajo Mandato S4.")

        is_test_file = f.name.startswith("test_") or "tests" in f.parts
        if f.suffix == ".py" and not is_test_file:
            if re.search(r"\bsed\b", content):
                errors.append(
                    f"D6: {f.name} contiene llamada a comando de mutacion ciega prohibido (sed) bajo Mandato S7."
                )
            if (
                re.search(r"\becho\b", content)
                and (">" in content or ">>" in content)
                and "subprocess" in content
            ):
                errors.append(
                    f"D6: {f.name} contiene comando shell con redireccion destructiva (echo) bajo Mandato S7."
                )
            # VC-087: Warning normalizado — bloquear supresión global de warnings sin justificación.
            # filterwarnings("ignore") sin comentario justificativo en la misma línea es anti-slop.
            for lineno, line in enumerate(content.splitlines(), 1):
                if re.search(r'filterwarnings\s*\(\s*["\']ignore["\']', line):
                    if not re.search(r"#\s*\S", line):  # sin comentario justificativo
                        errors.append(
                            f"D6 VC-087: {f.name}:{lineno} suprime warnings sin justificación "
                            f"(filterwarnings ignore sin comentario). Añade # VC-087-OK: <razón>."
                        )
        return errors

    def _scan_coverage_artifacts(self) -> list[str]:
        errors = []
        artifacts = []
        for _root, _dirs, _files in os.walk(self.project_path, followlinks=False):
            _dirs[:] = [
                d
                for d in _dirs
                if d not in self.hard_excludes
                and not os.path.islink(os.path.join(_root, d))
            ]
            for _f in _files:
                if _f.startswith(".coverage"):
                    fp = Path(_root) / _f
                    if ".git" not in fp.parts:
                        artifacts.append(fp)
        if artifacts:
            errors.append(
                f"D6: {len(artifacts)} artefacto(s) de workspace aún presentes; ejecutar auto‑fix."
            )
        return errors

    def _lint_file_lax_typing(self, f: Path) -> list[str]:
        """Check a single file for missing type annotations on public functions."""
        errors = []
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=f.name)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("_"):
                        continue
                    errors.extend(self._check_function_return_annotation(f, node))
                    errors.extend(self._check_function_arg_annotations(f, node))
        except Exception as e:
            logging.debug("lax-typing: %s: %s", f.name, e)
        return errors

    def _check_function_return_annotation(self, f: Path, node: ast.AST) -> list[str]:
        """Return annotation check for a function node."""
        errs = []
        if getattr(node, "returns", None) is None:
            errs.append(
                f"D6 VC-076: {f.name} l.{node.lineno} la función pública '{node.name}' no tiene anotación de tipo de retorno."
            )
        return errs

    def _check_function_arg_annotations(self, f: Path, node: ast.AST) -> list[str]:
        """Argument annotation check for a function node."""
        errs = []
        for arg in getattr(node, "args", []).args:
            if arg.arg in ("self", "cls"):
                continue
            if getattr(arg, "annotation", None) is None:
                errs.append(
                    f"D6 VC-076: {f.name} l.{node.lineno} el argumento '{arg.arg}' en la función pública '{node.name}' no tiene anotación de tipo."
                )
        return errs

    def _check_lax_typing(self, files: list) -> list[str]:
        """Enforce strict type annotations for public functions in protocol_engine and dimensions."""
        errors = []
        for f in files:
            parts = f.relative_to(self.project_path).parts
            if not any(x in parts for x in ("protocol_engine", "dimensions")):
                continue
            if "tests" in parts or f.name.startswith("test_"):
                continue
            errors.extend(self._lint_file_lax_typing(f))
        return errors

    def audit_d6_anti_slop(self) -> list:
        """D6: Anti‑Slop + higiene del workspace.
        Además de las reglas de tipado y comandos prohibidos, verifica que
        no queden artefactos de limpieza ni hallazgos de higiene.
        """
        errors = []
        files = self._get_audit_files()
        for f in files:
            content = f.read_text(encoding="utf-8", errors="ignore")
            errors.extend(self._check_file_anti_slop(f, content))

        errors.extend(self._check_lax_typing(files))
        errors.extend(self._scan_coverage_artifacts())

        hygiene_findings = find_hygiene_findings(self.project_path)
        if hygiene_findings:
            first = hygiene_findings[0]
            errors.append(
                f"D6: {len(hygiene_findings)} hallazgo(s) de higiene; primero: {first.kind} en {first.path}:{first.line}"
            )
        return errors

    def _check_core_scripts_test_references(self, all_test_text: str) -> list[str]:
        """Verifies that core scripts are referenced in at least one test."""
        errors = []
        # Nombres post-rename (Sprint 1): el guard de existencia (línea ~920) saltaba los nombres
        # viejos porque sus archivos ya no existen → el check D8 quedaba desdentado. Restaurado.
        CORE_SCRIPTS = [
            "run_compliance_tests",
            "sync_binding",
            "verify_chaos_robustness",
            "run_security_audit_12d",
            "permission_auditor",
            "global_sync_safe",
        ]
        for script in CORE_SCRIPTS:
            if not (self.project_path / "scripts" / f"{script}.py").exists():
                continue  # Script no aplica to this project — don't penalize
            if script not in all_test_text:
                errors.append(
                    f"D8: scripts/{script}.py no está referenciado en ningún test."
                )
        return errors

    def _check_imported_functions_adversarial(
        self, all_test_text: str, test_contents: dict[str, str]
    ) -> list[str]:
        """Verifies that imported functions have adversarial path coverage."""
        errors = []
        ADVERSARIAL = [
            "assertRaises",
            "assertFalse",
            "assertIsNone",
            "assertNotIn",
            "assertNotEqual",
            "assertGreater",
            "self.fail(",
            "pytest.raises",
            "pytest.fail",
            "returncode != 0",
            "returncode == 1",
            "FAIL",
            "REJECTED",
            "CAOS FALLIDO",
            "[FAIL",
            "assertEqual(len(",
            "assertTrue(any(",
            "== []",
            '== ""',
            "== ''",
        ]
        imported_funcs = set(
            re.findall(r"from\s+scripts\.\w+\s+import\s+([\w]+)", all_test_text)
        )
        for func in sorted(imported_funcs):
            has_adversarial = any(
                func in content and any(p in content for p in ADVERSARIAL)
                for content in test_contents.values()
            )
            if not has_adversarial:
                errors.append(
                    f"D8: {func}() importada en tests sin path negativo cubierto."
                )
        return errors

    def _check_adversarial_ratio(self, test_contents: dict[str, str]) -> list[str]:
        """Ensures that at least 50% of test files have adversarial assertions."""
        errors = []
        ADVERSARIAL = [
            "assertRaises",
            "assertFalse",
            "assertIsNone",
            "assertNotIn",
            "assertNotEqual",
            "assertGreater",
            "self.fail(",
            "pytest.raises",
            "pytest.fail",
            "returncode != 0",
            "returncode == 1",
            "FAIL",
            "REJECTED",
            "CAOS FALLIDO",
            "[FAIL",
            "assertEqual(len(",
            "assertTrue(any(",
            "== []",
            '== ""',
            "== ''",
        ]
        adversarial_files = [
            tf
            for tf, content in test_contents.items()
            if any(p in content for p in ADVERSARIAL)
        ]
        ratio = len(adversarial_files) / len(test_contents)
        if ratio < 0.5:
            errors.append(
                f"D8: Solo {len(adversarial_files)}/{len(test_contents)} test files "
                f"tienen aserciones adversariales ({ratio:.0%}) — objetivo: >50%."
            )
        return errors

    def _check_thin_wrappers(self) -> list[str]:
        """Detects thin wrappers that do not have their own logic and only delegate."""
        errors = []
        scripts_dir = self.project_path / "scripts"
        WRAPPER_EXCLUDES = {
            "__init__.py",
            "run_security_audit_12d.py",
            "verify_chaos_robustness.py",
            "core_utils.py",
        }
        for f in scripts_dir.glob("*.py"):
            if f.name in WRAPPER_EXCLUDES:
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=f.name)
                imports_from_scripts = any(
                    isinstance(n, ast.ImportFrom)
                    and n.module
                    and n.module.startswith("scripts.")
                    for n in ast.walk(tree)
                )
                if not imports_from_scripts:
                    continue
                funcs = [
                    n
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                if not funcs:
                    continue

                def _effective_body(fn):
                    body = fn.body
                    if (
                        body
                        and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                    ):
                        body = body[1:]  # strip docstring
                    return body

                all_single = all(len(_effective_body(fn)) == 1 for fn in funcs)
                substantive = [
                    l
                    for l in content.splitlines()
                    if l.strip() and not l.strip().startswith("#")
                ]
                short = len(substantive) < 30
                if all_single and short:
                    errors.append(
                        f"D8: {f.name} es un thin wrapper (solo delega a otro módulo). "
                        f"Mover código real al módulo fuente y eliminar el wrapper."
                    )
            except SyntaxError as e:
                logging.debug(
                    "D8 thin-wrapper: se omitio %s por SyntaxError: %s", f.name, e
                )
        return errors

    def audit_d8_test_coverage(self) -> list:
        """D8: Cobertura adversarial — tests existen y desafían paths negativos.

        Verifica tres propiedades:
        1. Scripts core están referenciados en al menos un test.
        2. Funciones importadas directamente tienen al menos un test con aserción adversarial.
        3. Al menos 50% de los test files tienen aserciones negativas (no solo happy-path).
        """
        errors = []
        tests_dir = self.project_path / "tests"
        if not tests_dir.exists():
            return [
                "D8: No existe directorio tests/ — cobertura imposible de verificar."
            ]

        test_contents = {
            tf.name: tf.read_text(encoding="utf-8", errors="ignore")
            for tf in tests_dir.glob("test_*.py")
        }
        if not test_contents:
            return ["D8: No hay test files en tests/."]

        all_test_text = "\n".join(test_contents.values())

        # 1. Scripts core deben estar cubiertos
        errors.extend(self._check_core_scripts_test_references(all_test_text))

        # 2. Funciones importadas directamente deben tener path negativo cubierto
        errors.extend(
            self._check_imported_functions_adversarial(all_test_text, test_contents)
        )

        # 3. Al menos 50% de test files tienen aserciones adversariales
        errors.extend(self._check_adversarial_ratio(test_contents))

        # 4. Detectar thin wrappers
        errors.extend(self._check_thin_wrappers())

        # 5. Detectar mocks/stubs/placeholders/fakes
        errors.extend(self._check_teatro_code_stubs())

        return list(dict.fromkeys(errors))

    def _check_ast_node_teatro(
        self,
        f_name: str,
        node: ast.AST,
        FINJA_NAME_RE: re.Pattern,
        FINJA_DOC_RE: re.Pattern,
    ) -> list[str]:
        """Validates a single AST node for fake/mock/stub patterns."""
        errors = []
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return errors
        if FINJA_NAME_RE.match(node.name):
            errors.append(
                f"D8: {f_name}:{node.name}() — nombre de función es mock/stub/fake."
            )
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
            and FINJA_DOC_RE.search(node.body[0].value.value)
        ):
            errors.append(
                f"D8: {f_name}:{node.name}() docstring contiene marcador mock/placeholder."
            )
        return errors

    def _scan_single_file_teatro(
        self, f: Path, FINJA_NAME_RE: re.Pattern, FINJA_DOC_RE: re.Pattern
    ) -> list[str]:
        """Scans a single file for mocks/stubs/placeholders/fakes."""
        errors = []
        if FINJA_NAME_RE.match(f.stem):
            return [
                f"D8: {f.name} — nombre de archivo delata mock/stub/fake (código de teatro)."
            ]
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=f.name)
            for node in ast.walk(tree):
                errors.extend(
                    self._check_ast_node_teatro(
                        f.name, node, FINJA_NAME_RE, FINJA_DOC_RE
                    )
                )
        except SyntaxError as e:
            logging.debug("D6 teatro: se omitio %s por SyntaxError: %s", f.name, e)
        return errors

    def _check_teatro_code_stubs(self) -> list[str]:
        """Detects mocks/stubs/placeholders/fakes inside production files or tests."""
        errors = []
        WRAPPER_EXCLUDES = {
            "__init__.py",
            "run_security_audit_12d.py",
            "verify_chaos_robustness.py",
            "core_utils.py",
        }
        FINJA_NAME_RE = re.compile(
            r"^(?:mock|stub|fake|placeholder|dummy|noop)_", re.IGNORECASE
        )
        FINJA_DOC_RE = re.compile(
            r"\b(?:MOCK|STUB|FAKE|PLACEHOLDER|DUMMY|TEMPORAL|WIP)\b"
        )

        finja_dirs = [self.project_path / "scripts"]
        tests_dir_finja = self.project_path / "tests"
        if tests_dir_finja.exists():
            finja_dirs.append(tests_dir_finja)

        for scan_dir in finja_dirs:
            for f in scan_dir.glob("*.py"):
                if f.name in WRAPPER_EXCLUDES:
                    continue
                errors.extend(
                    self._scan_single_file_teatro(f, FINJA_NAME_RE, FINJA_DOC_RE)
                )
        return list(dict.fromkeys(errors))

    def _scan_nesting_violations(self) -> list:
        """Rastrea scripts con anidamiento > 4 niveles — INFO, no FAIL.
        Mandato de aplanamiento: código nuevo debe ser plano (≤4 niveles).
        Las violaciones existentes son deuda técnica — se refactorizan por separado,
        no se bloquean commits, pero se registran para planificación de refactoring.
        Los tests quedan excluidos: su estructura de aserciones es intencionalmente verbosa.
        """
        violations = []
        MAX_DEPTH = 4
        scripts_dir = self.project_path / "scripts"
        if not scripts_dir.exists():
            return violations
        for f in scripts_dir.glob("*.py"):
            if f.name in {"__init__.py", "run_security_audit_12d.py", "core_utils.py"}:
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)
                nesting = _max_ast_nesting(tree)
                if nesting > MAX_DEPTH:
                    violations.append(
                        f"{f.name} profundidad {nesting} > {MAX_DEPTH} — "
                        f"extraer bloques a funciones dedicadas."
                    )
            except SyntaxError as e:
                logging.debug("D3 nesting: se omitio %s por SyntaxError: %s", f.name, e)
        return violations

    def _scan_deprecated(self) -> list:
        """Lista el contenido de deprecated/ — informa sin fallar (no agrega a errors).
        Regla S10: el código retirado se MUEVE a deprecated/ (no se elimina, no se etiqueta en sitio).
        El directorio deprecated/ es el contenedor real; D1 lo excluye de auditoría de zombis.
        La eliminación definitiva de deprecated/ requiere aprobación humana en sesión dedicada.
        Filtra subdirectorios de backup de sync (ej: .protocol/metadata/backups/) para reducir ruido.
        """
        dep_dir = self.project_path / "deprecated"
        if not dep_dir.exists():
            return []
        found = []
        backup_count = 0
        for f in sorted(dep_dir.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(dep_dir)
            if "backups" in rel.parts or ".bak." in f.name or f.suffix == ".bak":
                backup_count += 1
            else:
                found.append(f"deprecated/{rel.as_posix()}")
        if backup_count > 0:
            found.append(f"(+ {backup_count} archivos de backup/sync omitidos)")
        return found

    def _check_test_theater_imports_and_mocks(
        self, f: Path, tree: ast.AST, theater_imports: set
    ) -> list[str]:
        errors = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if (
                    node.module in theater_imports
                    or node.module.split(".")[0] in theater_imports
                ):
                    errors.append(
                        f"D9: {f.name} l.{node.lineno} import de {node.module} — "
                        f"reemplaza realidad en tests (S23/D-group)."
                    )
            if (
                isinstance(node, ast.Call)
                and isinstance(getattr(node, "func", None), ast.Attribute)
                and node.func.attr == "patch"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.startswith("scripts.")
            ):
                errors.append(
                    f"D9: {f.name} l.{node.lineno} mock.patch('{node.args[0].value}') — "
                    f"mocking de modulo interno prohibido (S23/D1)."
                )
        return errors

    def _check_test_env_manipulation(self, f: Path, tree: ast.AST) -> list[str]:
        errors = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and node.targets
                and isinstance(node.targets[0], ast.Subscript)
                and isinstance(node.targets[0].value, ast.Attribute)
                and node.targets[0].value.attr == "environ"
            ):
                errors.append(
                    f"D9: {f.name} l.{node.lineno} os.environ asignacion en test — "
                    f"manipulacion de entorno prohibida (S23/J1)."
                )
        return errors

    def _check_test_devnull_and_paths(self, f: Path, lines: list[str]) -> list[str]:
        errors = []
        for idx, line in enumerate(lines, 1):
            if "stderr=subprocess.DEVNULL" in line or "stderr=DEVNULL" in line:
                errors.append(
                    f"D9: {f.name} l.{idx} stderr=DEVNULL en test — silencia errores (S23/E2)."
                )
            if any(marker in line for marker in ("C:\\", "D:\\", "/home/", "/Users/")):
                if not line.strip().startswith("#"):
                    errors.append(
                        f"D9: {f.name} l.{idx} path absoluto hardcodeado — solo usar relativo (S23/J4)."
                    )
        return errors

    def _check_test_file_purity(self, f: Path) -> list[str]:
        """Scans a single test file for purity violations (theater patterns, env manipulation, etc)."""
        errors = []
        THEATER_IMPORTS = {
            "freezegun",
            "time_machine",
            "pyfakefs",
            "requests_mock",
            "responses",
            "httpretty",
        }
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            tree = ast.parse(content, filename=f.name)

            # Clase 1+2: AST visitor — aserciones nulas, if False, xfail/skip sin criterio
            visitor = TestTheaterVisitor(f.name, lines)
            visitor.visit(tree)
            errors.extend(visitor.errors)

            # Clase 3: imports y patch mocks
            errors.extend(
                self._check_test_theater_imports_and_mocks(f, tree, THEATER_IMPORTS)
            )

            # Clase 4 + Path absoluto
            errors.extend(self._check_test_devnull_and_paths(f, lines))

            # Clase 5: manipulacion de entorno
            errors.extend(self._check_test_env_manipulation(f, tree))

        except SyntaxError as e:
            logging.debug(
                "D9 test-theater: se omitio %s por SyntaxError: %s", f.name, e
            )
        return errors

    def _check_workflow_continue_on_error(self, yml: Path) -> list[str]:
        """Scans a GitHub workflow file for forbidden continue-on-error statements on test steps."""
        errors = []
        try:
            yml_lines = yml.read_text(encoding="utf-8", errors="ignore").splitlines()
            for idx, line in enumerate(yml_lines):
                if "continue-on-error: true" in line.lower():
                    ctx = "\n".join(yml_lines[max(0, idx - 5) : idx + 2])
                    if any(kw in ctx.lower() for kw in ("test", "pytest", "unittest")):
                        errors.append(
                            f"D9: {yml.name} l.{idx+1} continue-on-error en step de tests — CI ignora fallos (S23/H1)."
                        )
        except Exception as e:
            logging.debug("D9: skipped yml %s — %s", yml.name, e)
        return errors

    def audit_d9_test_purity(self) -> list:
        """D9: Pureza de Tests — detecta 18 patrones de teatro (S22/S23).
        Solo escanea tests/ del proyecto destino para no penalizar codigo de produccion.
        Detecta: aserciones nulas, xfail permanentes, mocks internos, env manipulation.
        """
        errors = []
        tests_dir = self.project_path / "tests"
        if not tests_dir.exists():
            return errors

        for f in tests_dir.glob("test_*.py"):
            errors.extend(self._check_test_file_purity(f))

        workflows_dir = self.project_path / ".github" / "workflows"
        if workflows_dir.exists():
            for yml in workflows_dir.glob("*.yml"):
                errors.extend(self._check_workflow_continue_on_error(yml))

        return list(dict.fromkeys(errors))

    def _analyze_test_files_checklist(
        self, BOUNDARY_VALS: frozenset
    ) -> tuple[list[str], list[str]]:
        """Analyzes test files to identify boundary values coverage and wide tests."""
        tests_dir = self.project_path / "tests"
        files_no_boundary, wide_tests = [], []
        for f in tests_dir.glob("test_*.py"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if "scripts." not in content:
                    continue
                tree = ast.parse(content, filename=f.name)
                funcs = [
                    n
                    for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
                ]
                if len(funcs) >= 3:
                    has_boundary = any(
                        (
                            isinstance(n, ast.Constant)
                            and (n.value in BOUNDARY_VALS or n.value == "")
                        )
                        or (isinstance(n, ast.List) and not n.elts)
                        for n in ast.walk(tree)
                    )
                    if not has_boundary:
                        files_no_boundary.append(f.name)
                import_names = {
                    alias.asname or alias.name
                    for nd in ast.walk(tree)
                    if isinstance(nd, ast.ImportFrom)
                    and nd.module
                    and nd.module.startswith("scripts.")
                    for alias in nd.names
                }
                for fn in funcs:
                    called = {
                        getattr(c.func, "id", None) or getattr(c.func, "attr", None)
                        for c in ast.walk(fn)
                        if isinstance(c, ast.Call)
                    } & import_names
                    if len(called) >= 5:
                        wide_tests.append(f"{f.name}:{fn.name}()")
            except SyntaxError as e:
                logging.debug("F4/G4: se omitio %s por SyntaxError: %s", f.name, e)
        return files_no_boundary, wide_tests

    def _check_review_queue_status(self) -> str:
        """Parses the review queue and returns a formatted status string."""
        queue_file = self.project_path / ".protocol" / "review_queue.json"
        if not queue_file.exists():
            return "[R] Sin commits pendientes de revision."
        try:
            import json as _json

            items = _json.loads(queue_file.read_text(encoding="utf-8"))
            pending = [i for i in items if not i.get("verified")]
            if pending:
                hashes = ", ".join(p["commit"] for p in pending[:3])
                suffix = f" +{len(pending)-3} mas" if len(pending) > 3 else ""
                return (
                    f"[R] PENDIENTE: {len(pending)} commit(s) sin verificar: {hashes}{suffix}. "
                    "Ejecuta: python scripts/manage_review_queue.py --ack <hash>"
                )
        except (ValueError, OSError, KeyError) as e:
            logging.debug("review-queue: no se pudo leer cola pendiente: %s", e)
        return "[R] Sin commits pendientes de revision."

    def _auto_checklist_report(self) -> list:
        """Responde automaticamente las preguntas del CHECKLIST.md sin intervencion humana.
        Cubre grupos F4 (inputs de borde), G4 (tests amplios), H (CI), I (vibe coding risk).
        Informativo — no afecta veredicto APPROVED/REJECTED.
        """
        tests_dir = self.project_path / "tests"
        if not tests_dir.exists():
            return ["CHECKLIST: Sin directorio tests/"]

        BOUNDARY_VALS = frozenset({None, 0, -1})
        files_no_boundary, wide_tests = self._analyze_test_files_checklist(
            BOUNDARY_VALS
        )

        status_f4 = (
            f"[F4] RIESGO: {', '.join(files_no_boundary)} — agregar None/0/'' en tests."
            if files_no_boundary
            else "[F4] OK"
        )
        status_g4 = (
            f"[G4] RIESGO: {', '.join(wide_tests)} — dividir o separar aserciones."
            if wide_tests
            else "[G4] OK"
        )

        workflows_dir = self.project_path / ".github" / "workflows"
        status_h = (
            "[H] OK — CI presente"
            if workflows_dir.exists()
            else "[H] INFO — Sin CI configurado"
        )

        status_queue = self._check_review_queue_status()

        return [
            status_f4,
            status_g4,
            status_h,
            status_queue,
        ]

    def auto_fix_workspace_hygiene(self):
        """Limpia automáticamente artefactos conocidos del sistema."""
        # Use os.walk with followlinks=False to avoid traversing Windows junctions/symlinks
        cleanup_dirs = {"__pycache__", ".pytest_cache"}
        cleanup_exts = {".pyc"}
        cleanup_prefixes = {".coverage"}
        for root, dirs, files in os.walk(
            self.project_path, topdown=True, followlinks=False
        ):
            # Skip symlinks/junctions and hard-excluded dirs
            dirs[:] = [
                d
                for d in dirs
                if d not in self.hard_excludes
                and not os.path.islink(os.path.join(root, d))
            ]
            # Remove cleanup dirs
            for d in list(dirs):
                if d in cleanup_dirs:
                    dp = Path(root) / d
                    shutil.rmtree(dp, ignore_errors=True)
                    dirs.remove(d)
            # Remove cleanup files
            for f in files:
                if Path(f).suffix in cleanup_exts or any(
                    f.startswith(p) for p in cleanup_prefixes
                ):
                    try:
                        (Path(root) / f).unlink(missing_ok=True)
                    except OSError as e:
                        logging.debug("cleanup: no se pudo borrar %s: %s", f, e)

    # ── D6 sub-check ──────────────────────────────────────────────────────────

    def _name_congruency_check(self) -> list:
        """D6 sub-check (VC-113): el N del filename debe igualar el número de
        dimensiones DISTINTAS que el gate enforce. Tras Sprint 28.5 las dimensiones
        viven en 2 lugares: métodos inline `audit_dN_` + módulos de `dimensions/`
        (canal gate) que run() recorre vía REGISTRY. Se cuentan IDs únicos de ambos."""
        import inspect as _inspect

        this_file = Path(__file__)
        m = re.match(r"run_security_audit_(\d+)d\.py", this_file.name)
        if not m:
            return []
        declared = int(m.group(1))
        ids = {
            int(re.match(r"audit_d(\d+)_", name).group(1))
            for name, _ in _inspect.getmembers(
                self.__class__, predicate=_inspect.isfunction
            )
            if re.match(r"audit_d\d+_", name)
        }
        try:
            from dimensions import REGISTRY

            ids |= {int(d.id[1:]) for d in REGISTRY if d.channel == "gate"}
        except ImportError as exc:
            logging.getLogger("audit_12d").warning(
                "congruency: REGISTRY no importable: %s", exc
            )
        actual = len(ids)
        if actual != declared:
            return [
                f"D6: {this_file.name} declara {declared} dominios pero el gate enforce "
                f"{actual} dimensiones distintas (inline + paquete). Ajustar (VC-113)."
            ]
        return []

    # ── D10 Tokenomics ────────────────────────────────────────────────────────

    def audit_d10_tokenomics(self) -> list:
        """D10 — Tokenomics & Context Efficiency (TK-023 / TK-038 / TK-039)."""
        errors = []
        try:
            return self._audit_d10_tokenomics_inner()
        except Exception as e:
            errors.append(f"D10: Error inesperado en tokenomics audit: {e}")
        return errors

    def _audit_d10_tokenomics_inner(self) -> list:
        """Inner implementation — separated for D5 angry-path compliance."""
        errors = []
        # TK-023: critical orchestrators must import OutputCompressor
        for rel in [
            "scripts/run_compliance_tests.py",
            "scripts/run_self_improvement.py",
            "scripts/auto_audit_loop.py",
        ]:
            p = self.project_path / rel
            if p.exists() and "OutputCompressor" not in p.read_text(
                encoding="utf-8", errors="ignore"
            ):
                errors.append(
                    f"D10: TK-023: {rel} sin OutputCompressor — logs grandes sin comprimir."
                )
        # TK-038: Trinity of Memory manifest size gates
        for fname, limit in {"AGENT.md": 150, "STATUS.md": 200, "SPEC.md": 500}.items():
            mp = self.project_path / fname
            if mp.exists():
                lines = len(
                    mp.read_text(encoding="utf-8", errors="ignore").splitlines()
                )
                if lines > limit:
                    errors.append(
                        f"D10: TK-038: {fname} tiene {lines} lineas (limite: {limit}). Riesgo saturacion contexto."
                    )
        # TK-039: script references in TOKEN_BUDGET.md / AGENT.md must exist on disk
        for doc in ["TOKEN_BUDGET.md", "AGENT.md"]:
            dp = self.project_path / doc
            if not dp.exists():
                continue
            content = dp.read_text(encoding="utf-8", errors="ignore")
            for ref in re.findall(r"python (?:scripts/)?(\S+\.py)", content):
                candidate = (
                    self.project_path / "scripts" / Path(ref).name
                    if "/" not in ref
                    else self.project_path / ref
                )
                if not candidate.exists():
                    errors.append(
                        f"D10: TK-039: {doc} referencia '{ref}' pero el archivo no existe (script espectral)."
                    )
        return errors

    # ── D11 SCA Trivy ──────────────────────────────────────────────────────────

    def audit_d12_validate_satellite_drift(self) -> list:
        """D12: Adopción de release (P3). Verifica que cada satélite adoptado esté en la
        versión de protocolo del core (VERSION.txt), NO byte-a-byte. Las micro-ediciones
        dentro de una versión no disparan drift: el core itera libre y la propagación
        ocurre por release (bump de VERSION.txt + sync). Reemplaza la comparación SHA256
        de archivos (acoplamiento que bloqueaba cada commit core con resync de 17 repos).
        """
        import json

        # Context: solo corre en el core (que tiene el registro de satélites).
        if not self.registry_path.exists():
            return []

        errors = []
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception as e:
            return [f"D12: Error loading REGISTRY.json: {e}"]

        core_vfile = self.project_path / "VERSION.txt"
        core_version = (
            core_vfile.read_text(encoding="utf-8").strip()
            if core_vfile.exists()
            else "UNKNOWN"
        )

        for proj in registry.get("projects", []):
            if (
                proj.get("role") == "CORE"
                or proj.get("status") != "active"
                or not proj.get("adoption_verified", False)
            ):
                continue
            proj_path = Path(proj["path"]).resolve()
            if not proj_path.exists():
                continue  # Skip missing paths

            subtree_dir = proj_path / ".protocol-core"
            sat_vfile = (
                (subtree_dir / "VERSION.txt")
                if subtree_dir.exists()
                else (proj_path / "VERSION.txt")
            )

            if not sat_vfile.exists():
                errors.append(
                    f"D12: satélite '{proj['name']}' sin VERSION.txt — no adoptó el protocolo (sync)."
                )
                continue
            sat_version = sat_vfile.read_text(encoding="utf-8").strip()
            if sat_version != core_version:
                errors.append(
                    f"D12: satélite '{proj['name']}' en v{sat_version}; release del core v{core_version}. "
                    f"Adopta con: python scripts/global_sync_safe.py --apply --project '{proj['name']}'."
                )

        return errors

    def _validate_declarative_rule_references(self, rules: list, errors_by_domain: dict) -> None:
        """Verifica el formato del campo golden_standard_ref de las reglas (VC-067)."""
        import re
        ref_pattern = re.compile(r"^(?:PENDING:)?(?:VC|VT|TK|PI)-\d+$")
        for rule in rules:
            rule_id = rule.get("id", "unnamed")
            ref = rule.get("golden_standard_ref")
            if not ref:
                errors_by_domain["D2"].append(
                    f"D2: La regla '{rule_id}' no contiene el campo 'golden_standard_ref'."
                )
            elif not isinstance(ref, str) or not ref_pattern.match(ref):
                errors_by_domain["D2"].append(
                    f"D2: La regla '{rule_id}' tiene un 'golden_standard_ref' inválido o mal formateado: '{ref}'."
                )

    def audit_declarative_rules(self) -> dict:
        """Carga y evalúa las reglas declarativas en YAML para los 10 dominios."""
        errors_by_domain = {f"D{i}": [] for i in range(1, 13)}
        rules_path = self.project_path / ".protocol" / "rules" / "rules.yaml"
        if not rules_path.exists():
            return errors_by_domain

        try:
            import yaml

            with open(rules_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            rules = config.get("rules", []) or []
        except Exception as e:
            errors_by_domain["D1"].append(
                f"D1: Error al cargar rules.yaml declarativo: {e}"
            )
            return errors_by_domain

        self._validate_declarative_rule_references(rules, errors_by_domain)

        files = self._get_audit_files()
        for f in files:
            try:
                file_content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError as e:
                logging.debug("rules-scan: no se pudo leer %s: %s", f.name, e)
                continue
            lines = file_content.splitlines()

            tree = None
            if f.suffix == ".py":
                try:
                    tree = ast.parse(file_content, filename=f.name)
                except (SyntaxError, ValueError) as e:
                    logging.debug("rules-scan: AST parse fallo en %s: %s", f.name, e)

            for rule in rules:
                domain = rule.get("domain", "D1")
                rule_errors = _evaluate_single_rule(rule, f.name, f.suffix, lines, tree)
                for err in rule_errors:
                    errors_by_domain[domain].append(f"{domain} {err}")

        return errors_by_domain

    def audit_project_insights(self) -> list:
        """Verifica que el Golden Standard exponga el bloque de project insights canónico."""
        # Skip if not Cerberus (protocol_engine not available)
        if not self.is_cerberus:
            return []
        errors = []
        audit_db = load_golden_standard_audit()
        insights = get_project_insights()
        canonical_ids = {k for k in insights if k.startswith("PI-")}
        bad_format = {k for k in insights if not k.startswith("PI-")}
        if bad_format:
            errors.append(
                f"KNOWLEDGE: Project insights con formato incorrecto: {sorted(bad_format)}"
            )
        if not canonical_ids:
            errors.append("KNOWLEDGE: GS no expone ningún project insight (PI-NNN).")
        for insight_id in sorted(canonical_ids):
            if not insights[insight_id].strip():
                errors.append(f"KNOWLEDGE: {insight_id} está vacío.")
        for flaw_id, entry in audit_db.items():
            if entry.get("validating_mechanism") != "DOC_ONLY":
                continue
            if entry.get("downstream_verification") not in {"none", "required"}:
                errors.append(
                    f"KNOWLEDGE: {flaw_id} perdió downstream_verification al normalizar la auditoría."
                )
        return errors

    def audit_project_insight_recommendations(self) -> dict:
        """Return domain-oriented recommendations derived from the project insights."""
        # Skip if not Cerberus (protocol_engine not available)
        if not self.is_cerberus:
            return {}
        recommendations = get_project_insight_recommendations()
        expected_domains = {f"D{i}" for i in range(1, 11)}
        missing_domains = expected_domains - set(recommendations)
        if missing_domains:
            raise ValueError(
                f"Missing recommendation domains: {sorted(missing_domains)}"
            )
        return recommendations

    def _collect_orphan_candidates(self, code_roots: list[str]) -> list[Path]:
        """Collects candidate python files for orphan scanning, excluding tests and deprecated."""

        def _excluded(p: Path) -> bool:
            sp = p.as_posix()
            return (
                "__pycache__" in sp
                or "/deprecated/" in sp
                or p.name == "__init__.py"
                or "/tests/" in sp
                or p.name.startswith("test_")
            )

        candidates = []
        for cr in code_roots:
            d = self.project_path / cr
            if d.exists():
                candidates += [p for p in d.rglob("*.py") if not _excluded(p)]
        return candidates

    def _collect_corpus_contents(
        self, code_roots: list[str], scripts_dir: Path
    ) -> list[tuple[Path, str]]:
        """Collects the full codebase and doc corpus as pairs of (Path, content) for reference matching."""
        corpus = []
        for cr in code_roots + ["tests"]:
            d = self.project_path / cr
            if d.exists():
                corpus += [
                    (p, p.read_text(encoding="utf-8", errors="ignore"))
                    for p in d.rglob("*.py")
                    if "__pycache__" not in p.as_posix()
                ]
        for sub in [scripts_dir / "hooks", self.project_path / ".claude" / "commands"]:
            if sub.exists():
                corpus += [
                    (f, f.read_text(encoding="utf-8", errors="ignore"))
                    for f in sub.rglob("*")
                    if f.is_file()
                ]
        for extra in [
            "AGENT.md",
            "TOKEN_BUDGET.md",
            "STATUS.md",
            "SPEC.md",
            "PROTOCOL_SYSTEM.md",
            "PROTOCOL_BEHAVIOR.md",
            ".claude/settings.json",
        ]:
            dp = self.project_path / extra
            if dp.exists():
                corpus.append((dp, dp.read_text(encoding="utf-8", errors="ignore")))
        return corpus

    def audit_script_orphans(self) -> list:
        """TK-039/TK-043 (gobernanza de salida): todo módulo .py del árbol de código debe
        estar en ruta activa — referenciado por otro módulo, hook, settings, cron o doc core
        — o vivir en deprecated/. Caza código espectral en TODO el árbol (scripts/ recursivo,
        cerberus/, tools/, dashboard/), no solo scripts/ top-level (P6). Excluye tests/ de los
        candidatos (pytest los descubre por path, no por nombre) pero los incluye en el corpus.
        Match conservador (substring) para no sobre-acusar (PI-007)."""
        scripts_dir = self.project_path / "scripts"
        if not scripts_dir.exists():
            return []  # satélites no tienen el árbol de código del core en root
        code_roots = ["scripts", "protocol_engine", "dashboard"]

        candidates = self._collect_orphan_candidates(code_roots)
        corpus = self._collect_corpus_contents(code_roots, scripts_dir)

        errors = []
        for c in candidates:
            stem = c.stem
            if any(stem in t for q, t in corpus if q != c):
                continue
            errors.append(
                f"D10: TK-039: {c.relative_to(self.project_path).as_posix()} es espectral — "
                f"sin referencia en módulo/hook/CLI/cron/doc activo. Cablea o mueve a deprecated/."
            )
        return errors

    def _scan_complexity_debt(self) -> list:
        """Complejidad ciclomática > 10 (ruff C901). Sprint 4.4: GATE DURO — bloquea el commit
        (ya no es solo deuda visible). El Simplicity Pass dejó C901=0; una función nueva > 10
        debe refactorizarse antes de commitear. Soft solo si ruff ausente (devuelve []).
        """
        import shutil
        import subprocess

        scripts_dir = self.project_path / "scripts"
        if not scripts_dir.exists():
            return []
        ruff = shutil.which("ruff")
        if not ruff:
            return []
        try:
            res = subprocess.run(
                [
                    ruff,
                    "check",
                    "--select",
                    "C901",
                    "--output-format=concise",
                    str(scripts_dir),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        except Exception:
            return []
        return [ln.strip() for ln in res.stdout.splitlines() if "C901" in ln]

    def _print_audit_results(self, results: dict, insight_results: list) -> None:
        """Prints the main results of the declarative and insight audits."""
        for dim, errs in results.items():
            if errs is None:
                continue
            if errs:
                print(f"\n[FAIL] {dim}:")
                for e in errs:
                    print(f"  - {e}")
            else:
                print(f"[PASS] {dim}")

        if insight_results:
            print("\n[FAIL] KNOWLEDGE:")
            for e in insight_results:
                print(f"  - {e}")
        else:
            print("\n[PASS] KNOWLEDGE")

    def _print_recommendations(self, recommendation_map: dict) -> None:
        """Sprint 5 — WARN→BLOCK: imprime recomendaciones solo cuando hay errores activos."""
        print("\n[RECOMENDACIONES POR DOMINIO]")
        for domain in sorted(recommendation_map):
            for item in recommendation_map[domain]:
                print(
                    f"  {domain}: {item['insight_id']} / {item['project']}: {item['action']}"
                )

    def _print_ancillary_reports(
        self,
        deprecated: list,
        checklist: list,
        recommendation_map: dict,
        nesting_debt: list,
        complexity_debt: list,
        has_errors: bool = False,
    ) -> None:
        """Prints deprecated file info, auto-checklist, debt reports, and (only on failure) recommendations."""
        if deprecated:
            print(
                f"\n[NOTE] deprecated/ contiene {len(deprecated)} archivo(s) retirados; se conserva solo como referencia histórica:"
            )
            for d in deprecated:
                print(f"  [D] {d}")

        print("\n[CHECKLIST AUTO-EVALUACION]")
        for item in checklist:
            print(f"  {item}")

        if has_errors:
            self._print_recommendations(recommendation_map)

        if nesting_debt:
            print(
                f"\n[DEUDA] {len(nesting_debt)} script(s) con anidamiento > 4 (mandato de aplanamiento):"
            )
            for nd in nesting_debt:
                print(f"  [>>] {nd}")

        if complexity_debt:
            print(
                f"\n[BLOQUEANTE] {len(complexity_debt)} función(es) con complejidad > 10 (C901 gate-duro, Sprint 4.4 — refactoriza antes de commitear):"
            )
            for cd in complexity_debt:
                print(f"  [X] {cd}")

    def run(self) -> bool:
        """Ejecuta la auditoría completa con auto‑fix y bucle de corrección hasta aprobar."""
        # Correcciones de higiene previas (mojibake y scripts legacy)
        repair_mojibake(self.project_path)
        deprecate_legacy_scripts(self.project_path)
        # Auto‑fix workspace al inicio
        self.auto_fix_workspace_hygiene()

        max_iterations = 5
        for iteration in range(1, max_iterations + 1):
            print(f"\n=== ITERACIÓN {iteration} ===")
            dec_results = self.audit_declarative_rules()
            insight_results = self.audit_project_insights()
            recommendation_map = self.audit_project_insight_recommendations()
            results = {
                "D8 COBERTURA ADVERSARIAL": self.audit_d8_test_coverage()
                + dec_results.get("D8", []),
                "D1 INTEGRIDAD": self.audit_d1_integrity() + dec_results.get("D1", []),
                "D2 COMPLETITUD": self.audit_d2_completeness()
                + dec_results.get("D2", []),
                "D3 CLARIDAD": self.audit_d3_clarity() + dec_results.get("D3", []),
                "D4 ANTI-SPAGHETTI": self.audit_d4_anti_spaghetti()
                + dec_results.get("D4", []),
                "D5 ANGRY PATH": self.audit_d5_angry_path() + dec_results.get("D5", []),
                "D6 ANTI-SLOP": self.audit_d6_anti_slop()
                + self._name_congruency_check()
                + dec_results.get("D6", []),
                "D7 DECLARATIVO": dec_results.get(
                    "D7", []
                ),  # regex+SAST migrados a dimensions/d7_security.py (REGISTRY)
                "D9 PUREZA DE TESTS": self.audit_d9_test_purity()
                + dec_results.get("D9", []),
                "D10 TOKENOMICS": self.audit_d10_tokenomics()
                + self.audit_script_orphans()
                + dec_results.get("D10", []),
                "D12 SATELLITE DRIFT": self.audit_d12_validate_satellite_drift(),
            }

            # Sprint 28.5: dimensiones migradas al paquete dimensions/ (canal gate).
            # _ROOT está en sys.path (línea 21) => `dimensions` importable al auditar
            # cualquier proyecto. Cada Dimension audita el repo TARGET vía AuditContext.
            try:
                from dimensions import REGISTRY as _DIM_REGISTRY, AuditContext as _DimCtx

                _dim_ctx = _DimCtx(self.project_path)
                for _dim in _DIM_REGISTRY:
                    if _dim.channel != "gate":
                        continue
                    _findings = _dim.audit(_dim_ctx)
                    results[f"{_dim.id.upper()} {_dim.name}"] = [
                        f.message for f in _findings if f.is_blocking()
                    ]
            except ImportError:
                # dimensions not available (external projects only run core audits)
                logging.getLogger("audit_12d").debug(
                    "Dimensions unavailable (external project mode)"
                )

            self._print_audit_results(results, insight_results)

            deprecated = self._scan_deprecated()
            checklist = self._auto_checklist_report()
            nesting_debt = self._scan_nesting_violations()
            complexity_debt = self._scan_complexity_debt()

            # Sprint 5: recomendaciones solo cuando hay errores bloqueantes activos
            has_domain_errors = (
                any(bool(errs) for errs in results.values())
                or bool(insight_results)
                or bool(complexity_debt)
            )
            self._print_ancillary_reports(
                deprecated,
                checklist,
                recommendation_map,
                nesting_debt,
                complexity_debt,
                has_errors=has_domain_errors,
            )

            # Sprint 4.4: C901 > 10 es GATE DURO (ya no solo deuda visible). Ahora que el
            # Simplicity Pass dejó C901=0, una función nueva con complejidad > 10 bloquea el commit.
            # Soft solo si ruff está ausente (_scan_complexity_debt devuelve []).
            passed = (
                all(not errs for errs in results.values() if errs is not None)
                and not insight_results
                and not complexity_debt
            )
            if passed:
                print("\n" + "=" * 75)
                print(f"VEREDICTO FINAL: APPROVED ({self.project_path.name})")
                return True

            # Intentar corregir nuevamente
            self.auto_fix_workspace_hygiene()
            repair_mojibake(self.project_path)
            deprecate_legacy_scripts(self.project_path)

        print("\n" + "=" * 75)
        print("💀 VEREDICTO FINAL: REJECTED (INSUFFICIENT RIGOR)")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auditoria 6D - Polyglot Forensic Auditor"
    )
    parser.add_argument(
        "target_pos", nargs="?", default=None, help="Target project path"
    )
    parser.add_argument("--project-path", default=".", help="Target project path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    target_path = args.project_path
    if args.target_pos:
        target_path = args.target_pos
    if DeepForensicAuditor(target_path).run():
        sys.exit(0)
    else:
        sys.exit(1)

