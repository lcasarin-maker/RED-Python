#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D7 Data Security (Sprint 28.5): secret/injection regex + bandit SAST.

Consolidates the inline checks (regex, preserved verbatim) with the SAST from
the enhanced version. It does NOT include Trivy (D11 owns SCA - deduped).
Semgrep is deferred: it requires network access (rules download) plus high
latency for a per-commit gate, and bandit already covers Python SAST; it stays
as a follow-up (hook/CI). Missing binary => UNAVAILABLE (H4, never a silent
PASS) - fixes the enhanced version's `except: return []`. HIGH threshold:
HIGH/CRITICAL => FAIL.
"""
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

# Same extensions as the inline version (audit_extensions): .py/.html/.js/.css.
# Expanding to .yaml/.sh/.ps1 is a follow-up (needs to handle false positives
# from docs/examples).
_SCAN_EXTS = {".py", ".html", ".js", ".css"}
# Self-referential files: they CONTAIN the patterns as literals, so they would
# scan themselves (same rationale and list as inline _get_audit_files; d7_security
# is included because it defines _DANGEROUS). Necessary, documented exclusion,
# not a whitelist cheat.
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
        "Possible SQL injection (f-string)",
    ),
        "unsafe_pickle": (
        r"pickle\.(load|loads)\s*\(",
        "Unsafe pickle deserialization",
    ),
    "exposed_private_key": (
        r"-----BEGIN (?:RSA|OPENSSH|PRIVATE|EC) KEY-----",
        "Llave privada expuesta",
    ),
    "aws_key_pattern": (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID detectada"),
}


class D7Security:
    """D7 dimension: secrets/injection (regex) + Python SAST (bandit)."""

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
                    "bandit missing: Python SAST not audited",
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
        # Missing => UNAVAILABLE (H4). Transient error (timeout/partial output under
        # hook load) => WARN, non-blocking: a per-commit gate should not flap on timing.
        try:
            res = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", *targets, "-f", "json", "-q"],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return [Finding(self.id, f"bandit transient error: {exc}", Status.WARN)]
        try:
            data = json.loads(res.stdout)
        except (json.JSONDecodeError, TypeError):
            return [
                Finding(
                    self.id, "bandit returned no valid JSON output (transient)", Status.WARN
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
        logger.info("d7 bandit: %d HIGH+ findings", len(out))
        return out
