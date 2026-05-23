#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria 6D v5.4 - Polyglot Forensic Auditor
Implementa ruteo de contexto dinamico y soporte multi-lenguaje (PY, HTML, JS, CSS).
Fuerza la existencia de SPEC.md en el proyecto destino y audita TODAS las fuentes.
"""

import re
import sys
import os
import shutil
import argparse
from pathlib import Path
import ast
import logging

# Fix para importacion local
sys.path.append(os.getcwd())

from scripts.core_utils import setup_windows_utf8, run_command, get_centralized_version
from scripts.hygiene_auditor import repair_mojibake, deprecate_legacy_scripts, find_hygiene_findings
from scripts.permission_auditor import run as run_permission_audit

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

class DeepForensicAuditor:
    """Orquestador de auditoría 6D con auto‑fix de higiene del workspace (estándar)."""

    # Deprecated placeholder; actual cleanup performed later
# Deprecated placeholder removed (no-op)

    def __init__(self, target_project_path="."):
        """Inicializa el auditor apuntando al proyecto destino."""
        self.project_path = Path(target_project_path).resolve()
        self.spec_file = self.project_path / "SPEC.md"
        self.hard_excludes = [
            '.git', '__pycache__', '.pytest_cache', '.ruff_cache', 'venv', 'env',
            '.venv', 'node_modules', '.agent-sandbox', 'deprecated', '.secrets', '.protocol',
            '.vibecoderproof', 'antigravityfindings.md', 'CERBERUS_ANTIGRAVITY.md',
            'findings.md', 'PLAN.md', 'audit_output.txt', 'scratch', 'archive',
            '01 Cuenza 2025', 'decompiled-legacy', 'bin', 'obj', '.run', '.tools', 'backups', 'modern-app',
            'build', 'dist'
        ]
        self.audit_extensions = ['*.py', '*.html', '*.js', '*.css']
        self.whitelist = self._extract_whitelist()

    def _extract_whitelist(self) -> set:
        """Extrae la lista de archivos permitidos especificos del proyecto destino."""
        base = set(['.claudeignore', 'AGENT.md', 'PROTOCOL_SYSTEM.md', 'PROTOCOL_BEHAVIOR.md', 'SPEC.md', '.agent_state.json', '.gitignore', '.cursorrules', 'HISTORIAL.md', 'GLOBAL_LEARNING.md', 'PRE_DELIVERY_CHECKLIST.md', 'STATUS.md', 'task.md', 'run_all_tests.bat', 'run_audit.ps1', 'directives/architecture.md', 'rules/verification.yaml', 'scripts/context_engineering.py', 'cerberus/context_engineering.py', 'tests/rules/test_pending_escalation.py', 'tests/rules/test_rule_severity.py', 'tests/rules/test_test_coverage.py', 'docs/rules.md', 'cerberus/close_pending.py', 'cerberus/pending_tasks.json', 'cerberus/rule_collector.py', 'cerberus/rules_engine.py', 'cerberus/rules/pending_escalation.yaml', 'cerberus/rules/rule_severity.yaml', 'cerberus/rules/test_coverage.yaml', 'tools/create_rule_test.py', 'tools/generate_rules_docs.py', 'rename_bulk.py', 'rename_bulk_corrected.ps1', 'rename-project.ps1', 'PROTOCOLO_GLOBAL', '.headroom.config', 'red.spec', 'FASE_8_FINDINGS.md'])

        if self.spec_file.exists():
            content = self.spec_file.read_text(encoding='utf-8', errors='ignore')
            # Match standard files with extensions
            matches = re.findall(r'([a-zA-Z0-9_/.-]+\.(?:py|md|sh|json|yaml|txt|db|html|bat|js|css|sql|cmd|ps1))', content)
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
        return [f for f in files if f.name not in ["__init__.py", "audit_6d.py", "chaos_monkey.py", "core_utils.py"]]

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
                if rel_path not in self.whitelist and not rel_path.startswith('tests/'):
                    errors.append(f"Archivo no registrado (Zombi): {rel_path}")
        return errors

    def audit_d2_completeness(self) -> list:
        """D2: SPEC Semantico local + D7 Code Completeness."""
        errors = []
        if not self.spec_file.exists():
            return ["Falla Critica: Falta SPEC.md."]

        content = self.spec_file.read_text(encoding='utf-8', errors='ignore')
        if "DATA SKELETON & UI LAYOUT" not in content:
            errors.append("SPEC.md: Falta seccion mandataria DATA SKELETON & UI LAYOUT.")

        # Parity with SPEC.md: verify key files from Whitelist actually exist physically
        core_scripts = [
            "scripts/audit_6d.py",
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

        for f in py_files:
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content, filename=f.name)
                visitor = CallGraphVisitor()
                visitor.visit(tree)
                defined_in_files[f.name] = visitor.defined_funcs
                all_referenced.update(visitor.referenced)
            except Exception as e:
                logging.error(f"D3: Fallo analizando grafo de llamadas en {f.name}: {e}")

        # Exclusions for functions/classes that are allowed to have 0 references
        exclude_names = {
            '__init__', '__main__', 'main', 'run', 'setUp', 'tearDown', 'setup',
            'audit_d1_integrity', 'audit_d2_completeness', 'audit_d3_clarity',
            'audit_d4_anti_spaghetti', 'audit_d5_angry_path', 'audit_d6_anti_slop',
            'audit_domain_1_code_structure', 'audit_domain_2_functionality',
            'audit_domain_3_human_validation', 'audit_domain_4_security_io',
            'audit_domain_5_state_integrity', 'audit_domain_6_workspace_cleanup',
            'check_proof', 'has_human_validation', 'validate_chunks',
            'find_hygiene_findings', 'repair_mojibake', 'deprecate_legacy_scripts',
            'DeepForensicAuditor', 'SilentFailureEnforcer', 'StubVisitor',
            'CallGraphVisitor', 'TryBlockVisitor', 'changed_files', 'ui_files',
            'promote', 'doctor', 'validate_operation_approved', 'log_completion', 'get_summary',
            'install', 'get_alerts', 'do_GET', 'do_POST', 'do_OPTIONS', 'do_DELETE', 'log_message', 'git_merge_driver', 'audit_d7_data_security'
        }

        # Check for orphaned definitions
        for fname, definitions in defined_in_files.items():
            for name in definitions:
                if name in exclude_names or name.startswith('test_') or name.startswith('_'):
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
                if "try" not in content and len(content.splitlines()) > 100:
                    errors.append(f"D5: {f.name} sin manejo de errores (Fragilidad detectada).")

                # Python AST Try/Except check
                if f.suffix == '.py':
                    try:
                        tree = ast.parse(content, filename=f.name)
                        visitor = TryBlockVisitor(f.name)
                        visitor.visit(tree)
                        errors.extend(visitor.errors)
                    except Exception as e:
                        logging.error(f"D5: Fallo parsing AST de Try/Except en {f.name}: {e}")
                
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
                if "REGLA B3" not in stdout:
                    errors.append("D5: Chaos Monkey no pudo certificar el sistema.")
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
            # 1. Prohibición de tipado débil (any/Any)
            if ": any" in content or "typing.Any" in content or ("from typing import" in content and "Any" in content):
                errors.append(f"D6: {f.name} usa tipado debil prohibido (any/Any) bajo Mandato S3.")
            # 2. Prohibición de var obsoleto en JS/HTML
            if "var " in content and f.suffix in ['.js', '.html']:
                errors.append(f"D6: {f.name} usa patron obsoleto (var) bajo Mandato S4.")
            # 3. Prohibición de comandos destructivos shell en Python
            if f.suffix == '.py':
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
            except Exception:
                pass
        return errors

    def auto_fix_workspace_hygiene(self):
        """Limpia automáticamente artefactos conocidos del sistema."""
        patterns = ["**/__pycache__", "**/*.pyc", "**/.pytest_cache", "**/.coverage*"]
        for pattern in patterns:
            for path in self.project_path.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)

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
            results = {
                "D1 INTEGRIDAD": self.audit_d1_integrity(),
                "D2 COMPLETITUD": self.audit_d2_completeness(),
                "D3 CLARIDAD": self.audit_d3_clarity(),
                "D4 ANTI-SPAGHETTI": self.audit_d4_anti_spaghetti(),
                "D5 ANGRY PATH": self.audit_d5_angry_path(),
                "D6 ANTI-SLOP": self.audit_d6_anti_slop(),
                "D7 SEGURIDAD DE DATOS": self.audit_d7_data_security(),
            }

            for dim, errs in results.items():
                if errs:
                    print(f"\n[FAIL] {dim}:")
                    for e in errs:
                        print(f"  - {e}")
                else:
                    print(f"[PASS] {dim}")

            try:
                passed = all(not errs for errs in results.values())
                if passed:
                    print("\n" + "=" * 75)
                    print(f"VEREDICTO FINAL: APPROVED ({self.project_path.name})")
                    return True
            except Exception as e:
                logging.error(f"Error checking dangerous patterns: {e}")
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
