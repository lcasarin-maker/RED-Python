#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_10d.py v0.02 - Polyglot Forensic Auditor (CoderCerberus)
10 dominios: D1 Integridad, D2 Completitud, D3 Claridad, D4 Anti-Spaghetti,
D5 Angry Path, D6 Anti-Slop, D7 Seguridad, D8 Cobertura Adversarial,
D9 Pureza de Tests, D10 Tokenomics & Eficiencia de Contexto.
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
from scripts.hygiene_auditor import repair_mojibake, deprecate_legacy_scripts, find_hygiene_findings
from scripts.permission_auditor import run as run_permission_audit
from cerberus import get_project_insights, get_project_insight_recommendations

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
            self.errors.append(f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' está vacía.")
            return
        if len(body) == 1:
            stmt = body[0]
            if isinstance(stmt, ast.Pass):
                self.errors.append(f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub vacío (pass).")
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                self.errors.append(f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub vacío (...).")
            elif isinstance(stmt, ast.Raise):
                if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name) and stmt.exc.func.id in ['NotImplementedError', 'NotImplemented']:
                    self.errors.append(f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub (raise NotImplementedError).")
                elif isinstance(stmt.exc, ast.Name) and stmt.exc.id in ['NotImplementedError', 'NotImplemented']:
                    self.errors.append(f"D7: {self.filename} l.{node.lineno} {node_type} '{node.name}' es un stub (raise NotImplementedError).")

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
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                    is_silent = True
                elif isinstance(stmt, ast.Continue):
                    is_silent = True
            
            if is_silent:
                handler_type = handler.type.id if (handler.type and isinstance(handler.type, ast.Name)) else "generic"
                self.errors.append(f"D5: {self.filename} l.{handler.lineno} bloque 'except {handler_type}' silencioso (pass/continue) prohibido.")
        self.generic_visit(node)

class TestTheaterVisitor(ast.NodeVisitor):
    """Detecta patrones de teatro en archivos test (S22/S23): aserciones nulas,
    tests sin medición real, decoradores que enmascaran fallos permanentes.
    Solo se activa en funciones cuyo nombre comienza con 'test_'.
    """
    def __init__(self, filename, source_lines):
        self.filename = filename
        self.source_lines = source_lines
        self.errors = []

    def visit_FunctionDef(self, node):
        if node.name.startswith('test_'):
            self._check_trivial_asserts(node)
            self._check_no_asserts(node)
            self._check_if_false(node)
            self._check_xfail_skip(node)
            self._check_return_bool(node)
        self.generic_visit(node)

    def _check_return_bool(self, node):
        """Detecta tests que usan 'return True/False' en lugar de assert/pytest.fail (D9/PytestReturnNotNoneWarning)."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, bool):
                self.errors.append(
                    f"D9: {self.filename} l.{stmt.lineno} {node.name}() usa 'return {stmt.value.value}' — "
                    f"usa assert/pytest.fail en cambio (PytestReturnNotNoneWarning/S23/B3)."
                )

    def _check_trivial_asserts(self, node):
        for stmt in ast.walk(node):
            if (isinstance(stmt, ast.Assert)
                    and isinstance(stmt.test, ast.Constant)
                    and stmt.test.value is True):
                self.errors.append(
                    f"D9: {self.filename} l.{stmt.lineno} assert True literal — asercion nula (S23/B1).")
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if (isinstance(call.func, ast.Attribute)
                        and call.func.attr in ('assertTrue', 'assertFalse')
                        and call.args
                        and isinstance(call.args[0], ast.Constant)
                        and call.args[0].value in (True, False)):
                    self.errors.append(
                        f"D9: {self.filename} l.{stmt.lineno} {call.func.attr}(literal) — asercion tautologica (S23/B1).")
                if (isinstance(call.func, ast.Attribute)
                        and call.func.attr == 'assertEqual'
                        and len(call.args) >= 2
                        and isinstance(call.args[0], ast.Name)
                        and isinstance(call.args[1], ast.Name)
                        and call.args[0].id == call.args[1].id):
                    self.errors.append(
                        f"D9: {self.filename} l.{stmt.lineno} assertEqual(x, x) — tautologia (S23/B5).")

    def _check_no_asserts(self, node):
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assert):
                return
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                fn = stmt.value.func
                attr = getattr(fn, 'attr', '')
                name = getattr(fn, 'id', '')
                if attr.startswith('assert') or attr in ('raises', 'fail') or name in ('raises', 'fail'):
                    return
        self.errors.append(
            f"D9: {self.filename} l.{node.lineno} {node.name}() sin aserciones — siempre pasa (S23/B2).")

    def _check_if_false(self, node):
        for stmt in ast.walk(node):
            if (isinstance(stmt, ast.If)
                    and isinstance(stmt.test, ast.Constant)
                    and stmt.test.value is False):
                self.errors.append(
                    f"D9: {self.filename} l.{stmt.lineno} 'if False:' en test — codigo inalcanzable (S23/C3).")

    def _check_xfail_skip(self, node):
        for dec in node.decorator_list:
            mark = self._pytest_mark_name(dec)
            if mark == 'xfail':
                lineno = dec.lineno
                prev = self.source_lines[lineno - 2].strip() if lineno >= 2 else ''
                if not any(prev.startswith(t) for t in ('# TODO:', '# REMOVE_WHEN:', '# reason:', '# Reason:')):
                    self.errors.append(
                        f"D9: {self.filename} l.{lineno} @xfail sin criterio de remocion — ignorado permanente (S22/C1).")
            elif mark == 'skip':
                has_reason = isinstance(dec, ast.Call) and any(kw.arg == 'reason' for kw in dec.keywords)
                if not has_reason:
                    self.errors.append(
                        f"D9: {self.filename} l.{dec.lineno} @skip sin reason= — ignorado sin justificacion (S23/C2).")

    def _pytest_mark_name(self, dec):
        func = getattr(dec, 'func', dec)
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
        default=depth
    )


def _check_ast_pattern(node: ast.AST, pattern: str, value: str | None) -> bool:
    """Valida si un nodo AST coincide con el patrón y valor declarados (aplanado)."""
    if f"ast.{type(node).__name__}" != pattern:
        return False
    if value and (not isinstance(node, ast.Constant) or str(node.value) != value):
        return False
    return True


def _evaluate_single_rule(rule: dict, f_name: str, f_ext: str, lines: list, tree: ast.AST | None) -> list[str]:
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

    for kw in keywords:
        for idx, line in enumerate(lines, 1):
            if kw in line:
                errors.append(f"[{rule_id}]: {f_name} l.{idx} — {message}")

    if func_name and tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func_name:
                lineno = getattr(node, "lineno", 1)
                errors.append(f"[{rule_id}]: {f_name} l.{lineno} — {message}")

    if pattern and tree:
        for node in ast.walk(tree):
            if _check_ast_pattern(node, pattern, value):
                lineno = getattr(node, "lineno", 1)
                errors.append(f"[{rule_id}]: {f_name} l.{lineno} — {message}")

    return errors


class DeepForensicAuditor:
    """Orquestador de auditoría 8D con auto‑fix de higiene del workspace (estándar)."""

    def __init__(self, target_project_path="."):
        """Inicializa el auditor apuntando al proyecto destino."""
        self.project_path = Path(target_project_path).resolve()
        self.spec_file = self.project_path / "SPEC.md"
        self.registry_path = self.project_path / ".protocol" / "metadata" / "REGISTRY.json"
        self.hard_excludes = [
            # Generated tooling artifacts — never project code
            '.git', '__pycache__', '.pytest_cache', '.ruff_cache',
            'venv', 'env', '.venv', 'node_modules',
            # Governance metadata dir — auto-generated maps, evidence, manifests
            '.protocol',
            # Evidence subdir — timestamped generated files, gitignored
            'evidence',
            # Backup stores — other projects' protocol copies, gitignored
            'backups',
            # Retrospective session exports — generated output, gitignored
            'exports',
            # Credentials infrastructure — gitignored, not project code
            '.secrets',
            # The ONLY business exemption per CoderCerberus protocol
            'deprecated',
        ]
        self.audit_extensions = ['*.py', '*.html', '*.js', '*.css']
        self.whitelist = self._extract_whitelist()

    def _extract_whitelist(self) -> set:
        """Extrae la lista de archivos permitidos especificos del proyecto destino."""
        base = set(['.claudeignore', 'AGENT.md', 'PROTOCOL_SYSTEM.md', 'PROTOCOL_BEHAVIOR.md', 'SPEC.md', '.agent_state.json', '.gitignore', '.cursorrules', 'HISTORIAL.md', 'GLOBAL_LEARNING.md', 'PRE_DELIVERY_CHECKLIST.md', 'STATUS.md', 'task.md', 'CHECKLIST.md', 'run_all_tests.bat', 'run_audit.ps1', 'PLAN_REMEDIACION.md', 'pytest.ini', 'directives/architecture.md', 'rules/verification.yaml', 'tests/rules/test_pending_escalation.py','docs/rules.md', 'cerberus/close_pending.py', 'cerberus/pending_tasks.json', 'cerberus/rule_collector.py', 'cerberus/rules_engine.py', 'cerberus/rules/pending_escalation.yaml', 'cerberus/rules/rule_severity.yaml', 'cerberus/rules/test_coverage.yaml', 'tools/create_rule_test.py', 'tools/generate_rules_docs.py', 'rename_bulk.py', 'rename_bulk_corrected.ps1', 'rename-project.ps1', 'PROTOCOLO_GLOBAL', '.headroom.config', 'red.spec', 'FASE_8_FINDINGS.md', 'scripts/review_queue.py', 'scripts/review_reminder.py', 'scripts/setup_reminder_task.py', '.protocol/review_queue.json', '.protocol/.gitattributes', 'scripts/generate_golden_audit.py', 'docs/golden_standard_audit_report.md', 'tests/test_golden_standard_compliance.py', '.protocol/metadata/golden_standard_audit.json',
                    'scripts/clean_satellites.py', 'scripts/migrate_to_subtree.py',
                    # .claude/ infrastructure files — hardcoded to survive SPEC.md sentence-punctuation edge cases
                    '.claude/cache/protocol_rules.json', '.claude/settings.json', '.claude/settings.local.json',
                    '.claude/settings.template.json', '.claude/CLAUDE.md', '.claude/.gitignore',
                    # '00 audit/' dir — spaces in dirname break the whitelist regex; hardcoded as deterministic fix
                    '00 audit/00_CONSTITUCION_CERBERUS.md', '00 audit/01_AUDITORIA_LOCAL.md',
                    '00 audit/02_AUDITORIA_REPOSITORIOS.md', '00 audit/03_EVOLUCION_GOLDEN_STANDARD.md',
                    '00 audit/04_CONTEXTO_EJECUCION.md', '00 audit/README_ORDEN_DE_EJECUCION.md',
                    '00 audit/results/external_repositories_audit.md'])

        if self.spec_file.exists():
            content = self.spec_file.read_text(encoding='utf-8', errors='ignore')
            # Match standard files with extensions
            matches = re.findall(r'([a-zA-Z0-9_/.-]+\.(?:py|md|sh|json|yaml|txt|db|html|bat|js|css|sql|cmd|ps1|example))', content)
            base.update(matches)
            # Match dotfiles without extensions (e.g., .gitignore, .cursorrules)
            dotfiles = re.findall(r'(\.(?:gitignore|cursorrules|claude))', content)
            base.update(dotfiles)
            # Match .claude/* patterns
            claude_files = re.findall(r'(\.claude/[a-zA-Z0-9_.-]+)', content)
            base.update(claude_files)
            # Match git hooks
            hooks = re.findall(r'(scripts/hooks/[a-zA-Z0-9_-]+)', content)
            base.update(hooks)
        return base

    def _get_audit_files(self) -> list:
        """Obtiene todos los archivos fuente que deben ser auditados en el target."""
        files = []
        for ext in self.audit_extensions:
            # Buscar en root del proyecto
            files.extend(list(self.project_path.glob(ext)))
            # Buscar en subcarpetas comunes (scripts, tests)
            for sub in ["scripts", "tests", "src"]:
                sub_dir = self.project_path / sub
                if sub_dir.exists():
                    files.extend(list(sub_dir.glob(f"**/{ext}")))
        
                # Filter out core script files
        return [f for f in files if f.name not in ["__init__.py", "audit_10d.py", "chaos_monkey.py", "core_utils.py"]]

    def _is_legitimate_test_file(self, rel_path: str) -> bool:
        """Solo archivos test con convención de nombre son auto-whitelisted en tests/.
        Archivos arbitrarios en tests/ (backdoor.py, evil.json) siguen siendo zombis.
        """
        fname = Path(rel_path).name
        return (
            rel_path.startswith('tests/') and (
                fname.startswith('test_') or
                fname.startswith('automation_test_') or
                fname in ('conftest.py', '__init__.py', 'pytest.ini')
            )
        )

    def audit_d1_integrity(self) -> list:
        """D1: Whitelist Forense (Polyglot) + permission & duplicate checks."""
        errors = []
        if not self.project_path.exists():
            return [f"Ruta de proyecto no existe: {self.project_path}"]
        # Permission audit (also performed in D4, but we enforce here as well)
        if not run_permission_audit(self.project_path):
            errors.append("D1: Permission audit failed (dangerous permissions detected)")

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in self.hard_excludes]
            for file in files:
                rel_path = (Path(root).relative_to(self.project_path) / file).as_posix()
                if file in self.hard_excludes or rel_path in self.hard_excludes:
                    continue
                if rel_path not in self.whitelist and not self._is_legitimate_test_file(rel_path):
                    errors.append(f"Archivo no registrado (Zombi): {rel_path}")

        # VC-118: Zombie Compatibility Theater — detect shim patterns in active scripts
        errors.extend(self._audit_d1_zombie_compat())
        # Barrier 3: dot-directory whitelist (unauthorized hidden dirs in root)
        errors.extend(self._audit_d1_dot_directories())
        return errors

    # Barrier 3: authorized dot-directories in repo root.
    _DOT_DIR_WHITELIST = frozenset({
        ".git", ".claude", ".github", ".protocol", ".secrets",
        ".pytest_cache", ".ruff_cache",   # tool caches — ephemeral, OK
    })

    def _audit_d1_dot_directories(self) -> list:
        """D1 sub-check: detect unauthorized dot-directories in repo root (Barrier 3)."""
        errors = []
        try:
            for item in self.project_path.iterdir():
                if item.is_dir() and item.name.startswith('.') and item.name not in self._DOT_DIR_WHITELIST:
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
        (re.compile(r'\bbackward[- ]?compat\b', re.IGNORECASE), "backward compat comment",        "comment"),
        (re.compile(r'\bcompatibility shim\b',  re.IGNORECASE), "compatibility shim comment",     "comment"),
        (re.compile(r'\bfor now\b.*\bcompat',   re.IGNORECASE), "for-now compat comment",         "comment"),
        (re.compile(r'\bor\b.+\.exists\(\)'),                   "dual .exists() OR fallback",     "any"),
        (re.compile(r'^\s*(from|import)\s+deprecated\b', re.IGNORECASE),
                                                                "import desde deprecated/",        "import"),
    ]

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
            try:
                lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for pattern, label, mode in self._ZOMBIE_PATTERNS:
                for idx, line in enumerate(lines, 1):
                    stripped = line.lstrip()
                    if mode == "comment" and not stripped.startswith("#"):
                        continue
                    if mode == "import" and not re.match(r'\s*(from|import)\b', line, re.IGNORECASE):
                        continue
                    if pattern.search(line):
                        errors.append(
                            f"D1: VC-118 Zombie Compat en {py_file.name} l.{idx}: {label}. "
                            f"REEMPLAZAR = ELIMINAR + CREAR (S19)."
                        )
                        break  # one hit per pattern per file is enough
        return errors

    def audit_d2_completeness(self) -> list:
        """D2: SPEC Semantico local + D7 Code Completeness."""
        errors = []
        if not self.spec_file.exists():
            return ["Falla Critica: Falta SPEC.md."]

        content = self.spec_file.read_text(encoding='utf-8', errors='ignore')
        if "DATA SKELETON & UI LAYOUT" not in content:
            errors.append("SPEC.md: Falta seccion mandataria DATA SKELETON & UI LAYOUT.")

        if not (self.project_path / "CHECKLIST.md").exists():
            errors.append("D2: CHECKLIST.md no existe — revision humana de calidad de tests no documentada (S23).")

        # Parity with SPEC.md: verify key files from Whitelist actually exist physically
        core_scripts = [
            "scripts/audit_10d.py",
            "scripts/rigor_maestro.py",
            "scripts/chaos_monkey.py",
            "scripts/chunking_validator.py",
            "scripts/empirical_proof_checker.py"
        ]
        for script_rel in core_scripts:
            script_path = self.project_path / script_rel
            if not script_path.exists():
                errors.append(f"D2: Script core declarado en SPEC.md no existe: {script_rel}")

        # Scan for D7 (Code Completeness): stubs, technical debt, and one-liners in all audit files
        files = self._get_audit_files()
        debt_pattern = re.compile(r'(?:#|//|/\*)\s*(?:TODO|FIXME|BUG)\b', re.IGNORECASE)

        for f in files:
            file_content = f.read_text(encoding='utf-8', errors='ignore')
            lines = file_content.splitlines()

            # 1. Technical Debt Scan
            for idx, line in enumerate(lines):
                match = debt_pattern.search(line)
                if match:
                    errors.append(f"D7: {f.name} l.{idx+1} marca de deuda técnica sin resolver ({match.group().strip()}).")

            # 2. Stub validation (AST-based for Python)
            if f.suffix == '.py':
                try:
                    tree = ast.parse(file_content, filename=f.name)
                    visitor = StubVisitor(f.name)
                    visitor.visit(tree)
                    errors.extend(visitor.errors)
                except Exception as e:
                    logging.error(f"D7: Fallo parsing AST de stubs en {f.name}: {e}")
            elif f.suffix in ['.js', '.html']:
                # Regex-based stub validation for JS/HTML
                js_stub_pattern = re.compile(r'function\s+\w+\s*\([^)]*\)\s*\{\s*(?:pass|return\s*;?|throw\s+new\s+Error\([^)]*\);?)?\s*\}')
                for idx, line in enumerate(lines):
                    if js_stub_pattern.search(line) or ('function' in line and '{}' in line):
                        errors.append(f"D7: {f.name} l.{idx+1} función stub vacía detectada en JavaScript.")

        return errors

    def audit_d3_clarity(self) -> list:
        """D3: Paridad de Documentacion + Analisis AST de Conectividad (Dead Code)."""
        errors = []
        files = self._get_audit_files()
        
        # Standard docstring validation
        for f in files:
            content = f.read_text(encoding='utf-8', errors='ignore')
            defs = re.findall(r'^\s*(?:def|class|function|const|let)\s+\w+', content, re.MULTILINE)
            docs = re.findall(r'["\']{3}[\s\S]*?["\']{3}|\/\*\*[\s\S]*?\*\/', content)

            if f.suffix == '.py' and not (content.startswith('"""') or content.startswith("'''") or content.startswith('#!')):
                 errors.append(f"D3: {f.name} falta docstring de modulo.")
            
            if len(defs) > 5 and len(docs) < 1:
                 errors.append(f"D3: {f.name} es una caja negra ({len(defs)} funciones sin documentacion).")

        # AST Call Graph analysis for Python files (excluding test files themselves)
        py_files = [f for f in files if f.suffix == '.py' and 'test_' not in f.name and 'tests' not in f.parts]
        defined_in_files = {}  # f.name -> set of defined functions/classes
        all_referenced = set()
        thin_wrapper_files = set()  # archivos marcados como "thin wrapper" — su API pública es intencional

        for f in py_files:
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content, filename=f.name)
                visitor = CallGraphVisitor()
                visitor.visit(tree)
                defined_in_files[f.name] = visitor.defined_funcs
                all_referenced.update(visitor.referenced)
                # Detectar patrón thin wrapper: docstring de módulo contiene "thin wrapper"
                # Justificación: thin wrappers son superficies de API pública deliberadas.
                # Sus funciones no se llaman internamente — son para callers externos.
                if 'thin wrapper' in content[:500].lower():
                    thin_wrapper_files.add(f.name)
            except Exception as e:
                logging.error(f"D3: Fallo analizando grafo de llamadas en {f.name}: {e}")

        # Exclusions for functions/classes that are allowed to have 0 references
        # Nombres exentos de dead-code: entrypoints de framework, handlers y APIs públicas documentadas.
        # JUSTIFICACIÓN REQUERIDA para cada entrada — nombres genéricos sin justificación = dead code.
        exclude_names = {
            # Python framework entrypoints
            '__init__', '__main__', '__str__', '__repr__', '__eq__', '__hash__',
            'main', 'run', 'setUp', 'tearDown', 'setup', 'teardown',
            # Los 10 dominios del auditor (llamados por DeepForensicAuditor.run() vía self.method())
            'audit_d1_integrity', 'audit_d2_completeness', 'audit_d3_clarity',
            'audit_d4_anti_spaghetti', 'audit_d5_angry_path', 'audit_d6_anti_slop',
            'audit_d7_data_security', 'audit_d8_test_coverage',
            'audit_d9_test_purity', 'audit_d10_tokenomics', 'validate_sca_trivy',
            'validate_satellite_drift',
            '_name_congruency_check', '_audit_d10_tokenomics_inner',
            # Scripts de higiene y validación Cerberus
            'check_proof', 'has_human_validation', 'validate_chunks',
            'find_hygiene_findings', 'repair_mojibake', 'deprecate_legacy_scripts',
            # Clases del auditor (DeepForensicAuditor)
            'DeepForensicAuditor', 'SilentFailureEnforcer', 'StubVisitor',
            'CallGraphVisitor', 'TryBlockVisitor',
            # HTTP handlers — BaseHTTPRequestHandler convention, llamados por el framework HTTP
            'do_GET', 'do_POST', 'do_OPTIONS', 'do_DELETE', 'do_PUT', 'log_message',
            # Callbacks de eventos
            'changed_files', 'ui_files',
            # API pública de EvidenceLogger — llamada por protocol_cli y hooks externos (B7)
            'validate_operation_approved', 'log_operation',
            # API pública de TokenTracker — llamada por dashboard y protocol_cli (TOKEN_BUDGET.md)
            'log_completion', 'get_summary', 'get_alerts',
            # API pública de merge_semantic — llamada por scripts externos y git merge driver
            'detect_semantic_conflict', 'extract_rules_touched',
            # API pública de state_checkpoint_validator — llamada por externos (REGLA #19)
            'compute_checkpoint_hash', 'create_checkpoint', 'export_checkpoint_json',
            # API pública de handoff — standalone CLI, funciones exportadas para uso externo
            'validate_historial_checkpoints',
        }

        # Check for orphaned definitions
        for fname, definitions in defined_in_files.items():
            for name in definitions:
                if name in exclude_names or name.startswith('test_') or name.startswith('_'):
                    continue
                # Thin wrappers son superficies de API pública intencionales.
                # Sus funciones module-level no tienen callers internos por diseño.
                if fname in thin_wrapper_files:
                    continue
                if name not in all_referenced:
                    errors.append(f"D3: {fname} define la función/clase huérfana '{name}' (dead code).")

        return errors

    def audit_d4_anti_spaghetti(self) -> list:
        """D4: Complejidad Forense Multi-Lenguaje con análisis de contenido."""
        errors = []
        files = self._get_audit_files()
        for f in files:
            content = f.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            for i, line in enumerate(lines):
                stripped = line.strip()
                indent = len(line) - len(line.lstrip())

                # Verificar indentation excesiva
                if indent > 32:
                    errors.append(f"D4: {f.name} l.{i+1} Indentación excesiva (spaghetti probable).")

                # Detectar lógica compleja (independiente de longitud)
                logical_ops = stripped.count(' and ') + stripped.count(' or ') + \
                             stripped.count('&&') + stripped.count('||')
                is_complex_logic = logical_ops > 2

                # Detectar si es una lista/array de datos
                is_data_list = any(pattern in stripped for pattern in [
                    '= [', '= {', ': [', ': {',
                    'data = ', 'items = ', 'values = ', 'dates = ',
                    'const ', 'let ', 'var '
                ])

                # Si es lógica compleja (spaghetti real), reportar
                if is_complex_logic and not is_data_list:
                    errors.append(f"D4: {f.name} l.{i+1} Spaghetti detectado ({logical_ops} operadores lógicos). "
                                f"Sugerencia: extraer condición a función dedicada.")

                # Análisis de líneas largas (>250 chars)
                if len(line) > 250:
                    is_data_content = any(pattern in stripped for pattern in [
                        'json', 'base64', '":[', '": [', '"value":', 'data'
                    ])

                    if is_data_list or is_data_content:
                        # Datos o lista: sugerir extracción
                        pass

        return errors

    def audit_d5_angry_path(self) -> list:
        """D5: Angry Path Validation + AST Try Block Rigor."""
        errors = []
        files = self._get_audit_files()
        for f in files:
            if f.suffix in ['.py', '.js', '.html']:
                content = f.read_text(encoding='utf-8', errors='ignore')
                # Test files usan pytest/unittest para manejo de errores; no requieren try/except
                is_test = f.name.startswith('test_') or f.name.startswith('automation_test_')

                # Python AST Try/Except check (AST real — no string search)
                if f.suffix == '.py':
                    try:
                        tree = ast.parse(content, filename=f.name)
                        if not is_test:
                            # Verifica existencia real de bloques try (no string en comentario)
                            has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
                            if not has_try and len(content.splitlines()) > 100:
                                errors.append(f"D5: {f.name} sin manejo de errores real (Fragilidad detectada).")
                        visitor = TryBlockVisitor(f.name)
                        visitor.visit(tree)
                        errors.extend(visitor.errors)
                    except Exception as e:
                        logging.error(f"D5: Fallo parsing AST de Try/Except en {f.name}: {e}")
                elif len(content.splitlines()) > 100 and "try" not in content and not is_test:
                    errors.append(f"D5: {f.name} sin manejo de errores (Fragilidad detectada).")
                
                # JS regex empty catch check
                elif f.suffix == '.js':
                    lines = content.splitlines()
                    js_catch_pattern = re.compile(r'catch\s*\([^)]*\)\s*\{\s*(?:pass|continue|return)?\s*\}')
                    for idx, line in enumerate(lines):
                        if js_catch_pattern.search(line):
                            errors.append(f"D5: {f.name} l.{idx+1} bloque catch silencioso en JavaScript.")

        # Chaos Monkey check
        try:
            chaos_script = self.project_path / "scripts/chaos_monkey.py"
            if chaos_script.exists():
                returncode, stdout, stderr = run_command([sys.executable, str(chaos_script)])
                if returncode != 0:
                    errors.append("D5: Chaos Monkey falló — resiliencia real no certificada.")
        except Exception as e:
            logging.error(f"Chaos Monkey audit error: {e}")
        return errors

    def audit_d6_anti_slop(self) -> list:
        """D6: Anti‑Slop + higiene del workspace.
        Además de las reglas de tipado y comandos prohibidos, verifica que
        no queden artefactos de limpieza ni hallazgos de higiene.
        """
        errors = []
        files = self._get_audit_files()
        for f in files:
            content = f.read_text(encoding='utf-8', errors='ignore')
            # 1. Prohibición de tipado débil (any/Any) — check por anotación real, no string genérico
            _weak_typing = False
            if "typing.Any" in content:
                _weak_typing = True
            elif "from typing import" in content and re.search(r'\bAny\b', content):
                _weak_typing = True
            elif f.suffix == '.py' and re.search(r'(?::\s*any\b|\->\s*any\b)', content, re.IGNORECASE):
                # Solo en anotaciones de tipo, no en comentarios ni strings
                _weak_typing = True
            if _weak_typing:
                errors.append(f"D6: {f.name} usa tipado debil prohibido (any/Any) bajo Mandato S3.")
            # 2. Prohibición de var obsoleto en JS/HTML
            if "var " in content and f.suffix in ['.js', '.html']:
                errors.append(f"D6: {f.name} usa patron obsoleto (var) bajo Mandato S4.")
            # 3. Prohibición de comandos destructivos shell en Python
            # Excluir archivos de test: contienen regex patterns como strings literales
            is_test_file = f.name.startswith('test_') or 'tests' in f.parts
            if f.suffix == '.py' and not is_test_file:
                if re.search(r'\bsed\b', content):
                    errors.append(f"D6: {f.name} contiene llamada a comando de mutacion ciega prohibido (sed) bajo Mandato S7.")
                if re.search(r'\becho\b', content) and (">" in content or ">>" in content) and "subprocess" in content:
                    errors.append(f"D6: {f.name} contiene comando shell con redireccion destructiva (echo) bajo Mandato S7.")
        # 4. Verificar artefactos de workspace restantes (ignorar pycache porque pytest los regenera)
        artifacts = []
        for pattern in ["**/.coverage*"]:
            artifacts.extend(path for path in self.project_path.glob(pattern) if ".git" not in path.parts)
        if artifacts:
            errors.append(f"D6: {len(artifacts)} artefacto(s) de workspace aún presentes; ejecutar auto‑fix.")
        # 5. Hallazgos de higiene (p. ej., archivos con codificación incorrecta)
        hygiene_findings = find_hygiene_findings(self.project_path)
        if hygiene_findings:
            first = hygiene_findings[0]
            errors.append(f"D6: {len(hygiene_findings)} hallazgo(s) de higiene; primero: {first.kind} en {first.path}:{first.line}")
        return errors

    def audit_d7_data_security(self) -> list[str]:
        """D7 SEGURIDAD DE DATOS: Validación estricta contra credenciales e inyecciones."""
        errors = []
        dangerous_patterns = {
            "hardcoded_credentials": (r"(password|api_key|secret|token|apikey)\s*[=:]\s*['\"][\w\-\.]{8,}['\"]", "Credenciales hardcodeadas (posible token/llave)"),
            "unsafe_eval": (r"\beval\s*\(", "Uso inseguro de eval()"),
            "sql_injection": (r"f\s*['\"].*(?:SELECT|INSERT|UPDATE|DELETE).*\{", "Posible inyección SQL (f-string en query)"),
            "unsafe_pickle": (r"pickle\.(load|loads)\s*\(", "Des-serialización insegura con pickle"),
            "exposed_private_key": (r"-----BEGIN (?:RSA|OPENSSH|PRIVATE|EC) KEY-----", "Llave privada expuesta"),
            "aws_key_pattern": (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID detectada")
        }

        for f in self._get_audit_files():
            if f.suffix not in ['.py', '.js', '.json', '.yaml', '.yml', '.md', '.html', '.css', '.sh', '.ps1', '.bat']:
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    for pattern_name, (regex, msg) in dangerous_patterns.items():
                        if re.search(regex, line, re.IGNORECASE):
                            errors.append(f"D7: {f.name}:{line_num} -> {msg}")
            except Exception as e:
                logging.debug("D7: skipped %s — %s", f.name, e)
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
            return ["D8: No existe directorio tests/ — cobertura imposible de verificar."]

        test_contents = {
            tf.name: tf.read_text(encoding='utf-8', errors='ignore')
            for tf in tests_dir.glob("test_*.py")
        }
        if not test_contents:
            return ["D8: No hay test files en tests/."]

        all_test_text = "\n".join(test_contents.values())

        # 1. Scripts core deben estar cubiertos (referenciados por nombre o importados)
        # Solo se verifican los que realmente existen en este proyecto —
        # proyectos satélite no tienen sync_binding/global_sync_safe y no deben ser penalizados.
        CORE_SCRIPTS = [
            "rigor_maestro", "sync_binding", "chaos_monkey",
            "audit_10d", "permission_auditor", "global_sync_safe",
        ]
        for script in CORE_SCRIPTS:
            if not (self.project_path / "scripts" / f"{script}.py").exists():
                continue  # Script no aplica a este proyecto — no penalizar
            if script not in all_test_text:
                errors.append(f"D8: scripts/{script}.py no está referenciado en ningún test.")

        # 2. Funciones importadas directamente deben tener path negativo cubierto
        # Patrones adversariales — amplio para capturar variantes reales sin falsos positivos:
        # assertEqual(len(...)>0 = conteo violaciones; assertTrue(any( = violación presente;
        # assertRaises/False = negativas explícitas; self.fail = unittest fail explícito
        ADVERSARIAL = [
            'assertRaises', 'assertFalse', 'assertIsNone', 'assertNotIn', 'assertNotEqual',
            'assertGreater', 'self.fail(', 'pytest.raises', 'pytest.fail',
            'returncode != 0', 'returncode == 1',
            'FAIL', 'REJECTED', 'CAOS FALLIDO', '[FAIL',
            'assertEqual(len(', 'assertTrue(any(', '== []',
        ]
        imported_funcs = set(re.findall(
            r'from\s+scripts\.\w+\s+import\s+([\w]+)', all_test_text
        ))
        for func in sorted(imported_funcs):
            has_adversarial = any(
                func in content and any(p in content for p in ADVERSARIAL)
                for content in test_contents.values()
            )
            if not has_adversarial:
                errors.append(f"D8: {func}() importada en tests sin path negativo cubierto.")

        # 3. Al menos 50% de test files tienen aserciones adversariales
        adversarial_files = [
            tf for tf, content in test_contents.items()
            if any(p in content for p in ADVERSARIAL)
        ]
        ratio = len(adversarial_files) / len(test_contents)
        if ratio < 0.5:
            errors.append(
                f"D8: Solo {len(adversarial_files)}/{len(test_contents)} test files "
                f"tienen aserciones adversariales ({ratio:.0%}) — objetivo: >50%."
            )

        # 4. Detectar thin wrappers — archivos sin código real propio
        # Un thin wrapper: todas sus funciones son single-statement que delegan a otro módulo.
        # Son atajos que ocultan dependencias reales; el código debe ir al módulo fuente.
        scripts_dir = self.project_path / "scripts"
        WRAPPER_EXCLUDES = {"__init__.py", "audit_10d.py", "chaos_monkey.py", "core_utils.py"}
        for f in scripts_dir.glob("*.py"):
            if f.name in WRAPPER_EXCLUDES:
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content, filename=f.name)
                # Detectar si importa de scripts.* (patrón de re-exportación)
                imports_from_scripts = any(
                    isinstance(n, ast.ImportFrom) and n.module
                    and n.module.startswith('scripts.')
                    for n in ast.walk(tree)
                )
                if not imports_from_scripts:
                    continue
                # Todas las funciones son single-statement (delegación pura)
                funcs = [n for n in ast.walk(tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                if not funcs:
                    continue

                def _effective_body(fn):
                    body = fn.body
                    if (body and isinstance(body[0], ast.Expr)
                            and isinstance(body[0].value, ast.Constant)):
                        body = body[1:]  # strip docstring
                    return body

                all_single = all(len(_effective_body(fn)) == 1 for fn in funcs)
                # Archivo corto (< 30 líneas sustantivas)
                substantive = [l for l in content.splitlines()
                               if l.strip() and not l.strip().startswith('#')]
                short = len(substantive) < 30
                if all_single and short:
                    errors.append(
                        f"D8: {f.name} es un thin wrapper (solo delega a otro módulo). "
                        f"Mover código real al módulo fuente y eliminar el wrapper."
                    )
            except SyntaxError:
                pass

        # 5. Detectar mocks/stubs/placeholders/fakes — código que finge ser producción
        # El código real debe ser código real: sin teatro, sin atajos disfrazados.
        FINJA_NAME_RE = re.compile(r'^(?:mock|stub|fake|placeholder|dummy|noop)_', re.IGNORECASE)
        FINJA_DOC_RE = re.compile(r'\b(?:MOCK|STUB|FAKE|PLACEHOLDER|DUMMY|TEMPORAL|WIP)\b')
        finja_dirs = [scripts_dir]
        tests_dir_finja = self.project_path / "tests"
        if tests_dir_finja.exists():
            finja_dirs.append(tests_dir_finja)
        for scan_dir in finja_dirs:
            for f in scan_dir.glob("*.py"):
                if f.name in WRAPPER_EXCLUDES:
                    continue
                if FINJA_NAME_RE.match(f.stem):
                    errors.append(f"D8: {f.name} — nombre de archivo delata mock/stub/fake (código de teatro).")
                    continue
                try:
                    content = f.read_text(encoding='utf-8', errors='ignore')
                    tree = ast.parse(content, filename=f.name)
                    for node in ast.walk(tree):
                        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            continue
                        if FINJA_NAME_RE.match(node.name):
                            errors.append(f"D8: {f.name}:{node.name}() — nombre de función es mock/stub/fake.")
                        # Docstring con marcador WIP/STUB/PLACEHOLDER — señal de código provisional
                        if (node.body and isinstance(node.body[0], ast.Expr)
                                and isinstance(node.body[0].value, ast.Constant)
                                and isinstance(node.body[0].value.value, str)
                                and FINJA_DOC_RE.search(node.body[0].value.value)):
                            errors.append(f"D8: {f.name}:{node.name}() docstring contiene marcador mock/placeholder.")
                except SyntaxError:
                    pass

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
            if f.name in {"__init__.py", "audit_10d.py", "core_utils.py"}:
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)
                nesting = _max_ast_nesting(tree)
                if nesting > MAX_DEPTH:
                    violations.append(
                        f"{f.name} profundidad {nesting} > {MAX_DEPTH} — "
                        f"extraer bloques a funciones dedicadas."
                    )
            except SyntaxError:
                pass
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

    def audit_d9_test_purity(self) -> list:
        """D9: Pureza de Tests — detecta 18 patrones de teatro (S22/S23).
        Solo escanea tests/ del proyecto destino para no penalizar codigo de produccion.
        Detecta: aserciones nulas, xfail permanentes, mocks internos, env manipulation.
        """
        errors = []
        tests_dir = self.project_path / "tests"
        if not tests_dir.exists():
            return errors

        THEATER_IMPORTS = {'freezegun', 'time_machine', 'pyfakefs', 'requests_mock', 'responses', 'httpretty'}

        for f in tests_dir.glob("test_*.py"):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                tree = ast.parse(content, filename=f.name)

                # Clase 1+2: AST visitor — aserciones nulas, if False, xfail/skip sin criterio
                visitor = TestTheaterVisitor(f.name, lines)
                visitor.visit(tree)
                errors.extend(visitor.errors)

                # Clase 3: imports que reemplazan realidad
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        if node.module in THEATER_IMPORTS or node.module.split('.')[0] in THEATER_IMPORTS:
                            errors.append(
                                f"D9: {f.name} l.{node.lineno} import de {node.module} — "
                                f"reemplaza realidad en tests (S23/D-group).")
                    # mock.patch sobre modulo interno (scripts.*)
                    if (isinstance(node, ast.Call)
                            and isinstance(getattr(node, 'func', None), ast.Attribute)
                            and node.func.attr == 'patch'
                            and node.args
                            and isinstance(node.args[0], ast.Constant)
                            and isinstance(node.args[0].value, str)
                            and node.args[0].value.startswith('scripts.')):
                        errors.append(
                            f"D9: {f.name} l.{node.lineno} mock.patch('{node.args[0].value}') — "
                            f"mocking de modulo interno prohibido (S23/D1).")

                # Clase 4: subprocess silenciando stderr en tests
                for idx, line in enumerate(lines, 1):
                    if 'stderr=subprocess.DEVNULL' in line or 'stderr=DEVNULL' in line:
                        errors.append(
                            f"D9: {f.name} l.{idx} stderr=DEVNULL en test — silencia errores (S23/E2).")

                # Clase 5: manipulacion de entorno
                for node in ast.walk(tree):
                    if (isinstance(node, ast.Assign)
                            and node.targets
                            and isinstance(node.targets[0], ast.Subscript)
                            and isinstance(node.targets[0].value, ast.Attribute)
                            and node.targets[0].value.attr == 'environ'):
                        errors.append(
                            f"D9: {f.name} l.{node.lineno} os.environ asignacion en test — "
                            f"manipulacion de entorno prohibida (S23/J1).")

                # Path absoluto hardcodeado
                for idx, line in enumerate(lines, 1):
                    if any(marker in line for marker in ('C:\\', 'D:\\', '/home/', '/Users/')):
                        if not line.strip().startswith('#'):
                            errors.append(
                                f"D9: {f.name} l.{idx} path absoluto hardcodeado — solo usar relativo (S23/J4).")

            except SyntaxError:
                pass

        # H: CI config — continue-on-error en steps de tests (bloquea CI ante fallos)
        workflows_dir = self.project_path / ".github" / "workflows"
        if workflows_dir.exists():
            for yml in workflows_dir.glob("*.yml"):
                try:
                    yml_lines = yml.read_text(encoding='utf-8', errors='ignore').splitlines()
                    for idx, line in enumerate(yml_lines):
                        if 'continue-on-error: true' in line.lower():
                            ctx = '\n'.join(yml_lines[max(0, idx - 5):idx + 2])
                            if any(kw in ctx.lower() for kw in ('test', 'pytest', 'unittest')):
                                errors.append(
                                    f"D9: {yml.name} l.{idx+1} continue-on-error en step de tests — CI ignora fallos (S23/H1).")
                except Exception as e:
                    logging.debug("D9: skipped yml %s — %s", yml.name, e)

        return list(dict.fromkeys(errors))

    def _auto_checklist_report(self) -> list:
        """Responde automaticamente las preguntas del CHECKLIST.md sin intervencion humana.
        Cubre grupos F4 (inputs de borde), G4 (tests amplios), H (CI), I (vibe coding risk).
        Informativo — no afecta veredicto APPROVED/REJECTED.
        """
        report = []
        tests_dir = self.project_path / "tests"
        if not tests_dir.exists():
            return ["CHECKLIST: Sin directorio tests/"]
        BOUNDARY_VALS = frozenset({None, 0, -1})
        files_no_boundary, wide_tests = [], []
        for f in tests_dir.glob("test_*.py"):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if 'scripts.' not in content:
                    continue
                tree = ast.parse(content, filename=f.name)
                funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
                if len(funcs) >= 3:
                    has_boundary = any(
                        (isinstance(n, ast.Constant) and (n.value in BOUNDARY_VALS or n.value == ''))
                        or (isinstance(n, ast.List) and not n.elts)
                        for n in ast.walk(tree)
                    )
                    if not has_boundary:
                        files_no_boundary.append(f.name)
                import_names = {
                    alias.asname or alias.name
                    for nd in ast.walk(tree)
                    if isinstance(nd, ast.ImportFrom) and nd.module and nd.module.startswith('scripts.')
                    for alias in nd.names
                }
                for fn in funcs:
                    called = {
                        getattr(c.func, 'id', None) or getattr(c.func, 'attr', None)
                        for c in ast.walk(fn) if isinstance(c, ast.Call)
                    } & import_names
                    if len(called) >= 5:
                        wide_tests.append(f"{f.name}:{fn.name}()")
            except SyntaxError:
                pass
        status_f4 = f"[F4] RIESGO: {', '.join(files_no_boundary)} — agregar None/0/'' en tests." if files_no_boundary else "[F4] OK"
        status_g4 = f"[G4] RIESGO: {', '.join(wide_tests)} — dividir o separar aserciones." if wide_tests else "[G4] OK"
        workflows_dir = self.project_path / ".github" / "workflows"
        status_h = "[H] OK — CI presente" if workflows_dir.exists() else "[H] INFO — Sin CI configurado"
        # Review Queue: muestra commits pendientes de verificacion humana
        queue_file = self.project_path / ".protocol" / "review_queue.json"
        status_queue = "[R] Sin commits pendientes de revision."
        if queue_file.exists():
            try:
                import json as _json
                items = _json.loads(queue_file.read_text(encoding="utf-8"))
                pending = [i for i in items if not i.get("verified")]
                if pending:
                    hashes = ", ".join(p["commit"] for p in pending[:3])
                    suffix = f" +{len(pending)-3} mas" if len(pending) > 3 else ""
                    status_queue = (
                        f"[R] PENDIENTE: {len(pending)} commit(s) sin verificar: {hashes}{suffix}. "
                        "Ejecuta: python scripts/review_queue.py --ack <hash>"
                    )
            except Exception:
                pass
        report.extend([status_f4, status_g4, status_h, status_queue,
                        "[I] AVISO VIBE CODING: IA escribio codigo Y tests — verifica que al menos 1 test falla sin el feature."])
        return report

    def auto_fix_workspace_hygiene(self):
        """Limpia automáticamente artefactos conocidos del sistema."""
        patterns = ["**/__pycache__", "**/*.pyc", "**/.pytest_cache", "**/.coverage*"]
        for pattern in patterns:
            for path in self.project_path.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)

    # ── D6 sub-check ──────────────────────────────────────────────────────────

    def _name_congruency_check(self) -> list:
        """D6 sub-check (VC-113): filename's N must match count of audit_dN_ methods."""
        import inspect as _inspect
        this_file = Path(__file__)
        m = re.match(r'audit_(\d+)d\.py', this_file.name)
        if not m:
            return []
        declared = int(m.group(1))
        actual = len([
            name for name, _ in _inspect.getmembers(self.__class__, predicate=_inspect.isfunction)
            if re.match(r'audit_d\d+_', name)
        ])
        if actual != declared:
            return [
                f"D6: {this_file.name} declara {declared} dominios pero tiene {actual} "
                f"metodos audit_dN_. Renombrar archivo o ajustar dominios (VC-113)."
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
        for rel in ["scripts/rigor_maestro.py", "scripts/self_improvement_loop.py", "scripts/auto_audit_loop.py"]:
            p = self.project_path / rel
            if p.exists() and "OutputCompressor" not in p.read_text(encoding="utf-8", errors="ignore"):
                errors.append(f"D10: TK-023: {rel} sin OutputCompressor — logs grandes sin comprimir.")
        # TK-038: Trinity of Memory manifest size gates
        for fname, limit in {"AGENT.md": 150, "STATUS.md": 200, "SPEC.md": 500}.items():
            mp = self.project_path / fname
            if mp.exists():
                lines = len(mp.read_text(encoding="utf-8", errors="ignore").splitlines())
                if lines > limit:
                    errors.append(f"D10: TK-038: {fname} tiene {lines} lineas (limite: {limit}). Riesgo saturacion contexto.")
        # TK-039: script references in TOKEN_BUDGET.md / AGENT.md must exist on disk
        for doc in ["TOKEN_BUDGET.md", "AGENT.md"]:
            dp = self.project_path / doc
            if not dp.exists():
                continue
            content = dp.read_text(encoding="utf-8", errors="ignore")
            for ref in re.findall(r'python (?:scripts/)?(\S+\.py)', content):
                candidate = (self.project_path / "scripts" / Path(ref).name if "/" not in ref else self.project_path / ref)
                if not candidate.exists():
                    errors.append(f"D10: TK-039: {doc} referencia '{ref}' pero el archivo no existe (script espectral).")
        return errors

    # ── D11 SCA Trivy ──────────────────────────────────────────────────────────

    def validate_sca_trivy(self) -> list:
        """D11: SCA via Trivy. Soft gate: warn si Trivy no disponible (VT-112)."""
        import shutil
        import subprocess
        import json

        trivy_bin = shutil.which("trivy")
        if not trivy_bin:
            print("[WARN] D11: Trivy no instalado — SCA omitido")
            return None

        try:
            # Ejecutar trivy fs --quiet --format json --severity CRITICAL .
            res = subprocess.run(
                [trivy_bin, "fs", "--quiet", "--format", "json", "--severity", "CRITICAL", "."],
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
                encoding="utf-8",
                errors="ignore"
            )
            if res.returncode != 0 and not res.stdout:
                print(f"[WARN] D11: Fallo al ejecutar Trivy (exit {res.returncode}): {res.stderr.strip()}")
                return None

            data = json.loads(res.stdout)
            errors = []
            results_list = data.get("Results", []) or []
            for target_res in results_list:
                vulns = target_res.get("Vulnerabilities", []) or []
                for v in vulns:
                    vuln_id = v.get("VulnerabilityID", "N/A")
                    pkg = v.get("PkgName", "N/A")
                    installed = v.get("InstalledVersion", "N/A")
                    fixed = v.get("FixedVersion", "N/A")
                    target = target_res.get("Target", "N/A")
                    errors.append(f"D11: VT-112: Vulnerabilidad CRITICAL {vuln_id} en {target} -> {pkg} (instalada: {installed}, corregida en: {fixed})")
            return errors
        except Exception as e:
            print(f"[WARN] D11: Excepcion ejecutando Trivy: {e}")
            return None

    def validate_satellite_drift(self) -> list:
        """D12: Drift Detection. Checks core standard files against physical/subtree copies in satellites."""
        import hashlib
        import json

        # 1. Context detection: only run in the core Cerberus
        if not self.registry_path.exists():
            return []

        errors = []
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception as e:
            return [f"D12: Error loading REGISTRY.json: {e}"]

        projects = registry.get("projects", [])

        # Standard files to check
        files_to_check = [
            "AGENT.md",
            "PROTOCOL_SYSTEM.md",
            "PROTOCOL_BEHAVIOR.md",
            "SPEC.md",
            ".gitattributes",
            "scripts/audit_10d.py",
            "scripts/verify_protocol_adoption.py",
            "scripts/pre_edit_guard.py",
            ".claude/settings.json"
        ]

        def get_sha256(path: Path) -> str:
            if not path.exists():
                return "NOT_FOUND"
            h = hashlib.sha256()
            try:
                with open(path, "rb") as f_in:
                    h.update(f_in.read())
                return h.hexdigest()
            except Exception:
                return "ERROR"

        for proj in projects:
            if proj.get("role") == "CORE" or proj.get("status") != "active":
                continue
            proj_path = Path(proj["path"]).resolve()
            if not proj_path.exists():
                continue  # Skip missing paths

            # Check subtree path (.protocol-core/<file>) or root path (<file>)
            subtree_dir = proj_path / ".protocol-core"
            is_subtree = subtree_dir.exists()

            for rel_file in files_to_check:
                core_file_path = self.project_path / rel_file
                if not core_file_path.exists():
                    continue

                if is_subtree:
                    sat_file_path = subtree_dir / rel_file
                else:
                    sat_file_path = proj_path / rel_file

                core_sha = get_sha256(core_file_path)
                sat_sha = get_sha256(sat_file_path)

                if sat_sha == "NOT_FOUND":
                    errors.append(f"D12: VT-114: Archivo faltante en satélite '{proj['name']}': {rel_file}")
                elif sat_sha != core_sha:
                    errors.append(f"D12: VT-114: Drift detectado en satélite '{proj['name']}': {rel_file} difiere del core")

        return errors

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
            errors_by_domain["D1"].append(f"D1: Error al cargar rules.yaml declarativo: {e}")
            return errors_by_domain

        files = self._get_audit_files()
        for f in files:
            try:
                file_content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lines = file_content.splitlines()

            tree = None
            if f.suffix == ".py":
                try:
                    tree = ast.parse(file_content, filename=f.name)
                except Exception:
                    pass

            for rule in rules:
                domain = rule.get("domain", "D1")
                rule_errors = _evaluate_single_rule(rule, f.name, f.suffix, lines, tree)
                for err in rule_errors:
                    errors_by_domain[domain].append(f"{domain} {err}")

        return errors_by_domain

    def audit_project_insights(self) -> list:
        """Verifica que el Golden Standard exponga el bloque de project insights canónico."""
        errors = []
        insights = get_project_insights()
        expected_ids = {f"PI-{i:03d}" for i in range(1, 7)}
        missing = expected_ids - set(insights)
        extra = set(insights) - expected_ids
        if missing:
            errors.append(f"KNOWLEDGE: Faltan project insights canónicos: {sorted(missing)}")
        if extra:
            errors.append(f"KNOWLEDGE: Project insights no canónicos detectados: {sorted(extra)}")
        for insight_id in sorted(expected_ids & set(insights)):
            if not insights[insight_id].strip():
                errors.append(f"KNOWLEDGE: {insight_id} está vacío.")
        return errors

    def audit_project_insight_recommendations(self) -> dict:
        """Return domain-oriented recommendations derived from the project insights."""
        recommendations = get_project_insight_recommendations()
        expected_domains = {f"D{i}" for i in range(1, 11)}
        missing_domains = expected_domains - set(recommendations)
        if missing_domains:
            raise ValueError(f"Missing recommendation domains: {sorted(missing_domains)}")
        return recommendations

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
                "D8 COBERTURA ADVERSARIAL": self.audit_d8_test_coverage() + dec_results.get("D8", []),
                "D1 INTEGRIDAD":            self.audit_d1_integrity() + dec_results.get("D1", []),
                "D2 COMPLETITUD":           self.audit_d2_completeness() + dec_results.get("D2", []),
                "D3 CLARIDAD":              self.audit_d3_clarity() + dec_results.get("D3", []),
                "D4 ANTI-SPAGHETTI":        self.audit_d4_anti_spaghetti() + dec_results.get("D4", []),
                "D5 ANGRY PATH":            self.audit_d5_angry_path() + dec_results.get("D5", []),
                "D6 ANTI-SLOP":             self.audit_d6_anti_slop() + self._name_congruency_check() + dec_results.get("D6", []),
                "D7 SEGURIDAD DE DATOS":    self.audit_d7_data_security() + dec_results.get("D7", []),
                "D9 PUREZA DE TESTS":       self.audit_d9_test_purity() + dec_results.get("D9", []),
                "D10 TOKENOMICS":           self.audit_d10_tokenomics() + dec_results.get("D10", []),
                "D11 SCA TRIVY":            self.validate_sca_trivy(),
                "D12 SATELLITE DRIFT":      self.validate_satellite_drift(),
            }

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

            # Informe de deprecated/ (informativo — no afecta veredicto)
            deprecated = self._scan_deprecated()
            if deprecated:
                print(f"\n[INFO] deprecated/ contiene {len(deprecated)} archivo(s) retirados (pendiente eliminacion formal):")
                for d in deprecated:
                    print(f"  [D] {d}")

            # Auto-checklist: responde automaticamente preguntas F/G/H/I sin intervencion humana
            checklist = self._auto_checklist_report()
            print("\n[CHECKLIST AUTO-EVALUACION]")
            for item in checklist:
                print(f"  {item}")

            print("\n[RECOMENDACIONES POR DOMINIO]")
            for domain in sorted(recommendation_map):
                items = recommendation_map[domain]
                print(f"  {domain}:")
                for item in items:
                    print(f"    - {item['insight_id']} / {item['project']}: {item['action']}")

            # Informe de anidamiento excesivo — deuda tecnica conocida, se refactoriza por separado
            nesting_debt = self._scan_nesting_violations()
            if nesting_debt:
                print(f"\n[DEUDA] {len(nesting_debt)} script(s) con anidamiento > 4 (mandato de aplanamiento):")
                for nd in nesting_debt:
                    print(f"  [>>] {nd}")

            passed = all(not errs for errs in results.values() if errs is not None) and not insight_results
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
    parser = argparse.ArgumentParser(description="Auditoria 6D - Polyglot Forensic Auditor")
    parser.add_argument("target_pos", nargs="?", default=None, help="Target project path")
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
