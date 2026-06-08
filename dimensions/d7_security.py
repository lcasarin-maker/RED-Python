#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D7 Data Security (Sprint 28.5): regex secretos/inyección + SAST bandit.

Consolida el inline (regex, preservado verbatim) con el SAST del enhanced. NO
incluye trivy (d11 posee la SCA — dedupe). semgrep se DIFIERE: requiere red
(descarga de reglas) + latencia alta en un gate por-commit, y bandit ya cubre el
SAST Python; va como follow-up (hook/CI). Binario ausente => UNAVAILABLE (H4,
nunca PASS silencioso) — corrige el `except: return []` del enhanced. Umbral HIGH:
HIGH/CRITICAL => FAIL."""
import importlib.util
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

from dimensions.base import Finding, Status
from dimensions.context import AuditContext, _HARD_EXCLUDES

logger = logging.getLogger("dimensions.d7")

# Mismas extensiones que el inline (audit_extensions): .py/.html/.js/.css. Ampliar a
# .yaml/.sh/.ps1 es follow-up (requiere manejar falsos positivos de docs/ejemplos).
_SCAN_EXTS = {".py", ".html", ".js", ".css"}
# Auto-referenciales: CONTIENEN los patrones como literales => se escanearían a sí
# mismos (mismo motivo y lista que el inline _get_audit_files; d7_security se suma
# porque define _DANGEROUS). Exclusión necesaria y documentada, no whitelist-cheat.
_SELF_REF = {
    "__init__.py",
    "run_security_audit_12d.py",
    "verify_chaos_robustness.py",
    "core_utils.py",
    "d7_security.py",
    "test_portability.py",
}
_SCAN_SUBDIRS = ("scripts", "tests", "src", "protocol_engine", "dimensions")
_HIGH = {"HIGH", "CRITICAL"}

_DANGEROUS = {
    "hardcoded_credentials": (
        r"(password|api_key|secret|token|apikey)\s*[=:]\s*['\"][\w\-\.]{8,}['\"]",
        "Credenciales hardcodeadas",
    ),
    "unsafe_eval": (r"\beval\s*\(", "Uso inseguro de eval()"),
    "sql_injection": (
        r"f\s*['\"].*(?:SELECT|INSERT|UPDATE|DELETE).*\{",
        "Posible inyección SQL (f-string)",
    ),
    "unsafe_pickle": (
        r"pickle\.(load|loads)\s*\(",
        "Des-serialización insegura con pickle",
    ),
    "exposed_private_key": (
        r"-----BEGIN (?:RSA|OPENSSH|PRIVATE|EC) KEY-----",
        "Llave privada expuesta",
    ),
    "aws_key_pattern": (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID detectada"),
}


class D7Security:
    """Dimensión D7: secretos/inyección (regex) + SAST Python (bandit)."""

    id = "d7"
    name = "DATA SECURITY"
    channel = "gate"

    def audit(self, ctx: AuditContext) -> list:
        return self._regex(ctx) + self._bandit(ctx)

    def _scan_files(self, ctx) -> list:
        roots = [(ctx.project_path, "*")]
        for sub in _SCAN_SUBDIRS:
            d = ctx.project_path / sub
            if d.exists():
                roots.append((d, "**/*"))
        seen, out = set(), []
        for root, pat in roots:
            for f in root.glob(pat):
                if (
                    not f.is_file()
                    or f.suffix not in _SCAN_EXTS
                    or f.name in _SELF_REF
                    or any(p in _HARD_EXCLUDES for p in f.parts)
                    or f in seen
                ):
                    continue
                seen.add(f)
                out.append(f)
        return out

    def _regex(self, ctx) -> list:
        out = []
        for f in self._scan_files(ctx):
            try:
                lines = f.read_text(encoding="utf-8", errors="ignore").split("\n")
            except OSError as exc:
                logger.debug("d7 regex: skip %s — %s", f.name, exc)
                continue
            for num, line in enumerate(lines, 1):
                for regex, msg in _DANGEROUS.values():
                    if re.search(regex, line, re.IGNORECASE):
                        out.append(
                            Finding(
                                self.id,
                                f"{f.name}:{num} -> {msg}",
                                Status.FAIL,
                                str(f),
                                num,
                            )
                        )
        logger.info("d7 regex: %d hallazgos", len(out))
        return out

    def _bandit(self, ctx) -> list:
        if importlib.util.find_spec("bandit") is None:
            return [
                Finding(
                    self.id,
                    "bandit ausente: SAST Python no auditado",
                    Status.UNAVAILABLE,
                )
            ]
        targets = [
            str(ctx.project_path / d)
            for d in ("scripts", "dimensions")
            if (ctx.project_path / d).exists()
        ]
        if not targets:
            return []
        # Ausente => UNAVAILABLE (H4). Error transitorio (timeout/salida parcial bajo
        # carga del hook) => WARN, no bloquea: un gate por-commit no debe flaquear por timing.
        try:
            res = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", *targets, "-f", "json", "-q"],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return [Finding(self.id, f"bandit error transitorio: {exc}", Status.WARN)]
        try:
            data = json.loads(res.stdout)
        except (json.JSONDecodeError, TypeError):
            return [
                Finding(
                    self.id, "bandit sin salida JSON válida (transitorio)", Status.WARN
                )
            ]
        out = []
        for issue in data.get("results", []):
            if issue.get("issue_severity", "").upper() in _HIGH:
                out.append(
                    Finding(
                        self.id,
                        f"bandit {issue.get('test_id')} {issue.get('issue_severity')} "
                        f"{Path(issue.get('filename', '')).name}:{issue.get('line_number')} "
                        f"{issue.get('issue_text', '')[:60]}",
                        Status.FAIL,
                        issue.get("filename"),
                        issue.get("line_number"),
                    )
                )
        logger.info("d7 bandit: %d HIGH+", len(out))
        return out
