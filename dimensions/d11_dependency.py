#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D11 Dependency (Sprint 28.5): Trivy SCA + PyPI freshness (outdated/yanked).

Consolidates everything into a single D11 (resolving the label collision): the
inline Trivy SCA moved here (S19/VC-118, copied without a bridge) and a REAL
freshness check was added via the PyPI JSON API. It does NOT duplicate vulns
(Trivy already covers them). No cache/TTL: the dependency surface is small.
Trivy missing => UNAVAILABLE (H4, never a silent PASS). Network missing => WARN
(user choice: offline informs, does not block). yanked => FAIL (package removed
from PyPI); outdated => WARN (informational).
"""
import json
import logging
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from dimensions.base import Finding, Status
from dimensions.context import AuditContext

logger = logging.getLogger("dimensions.d11")

_PYPI_URL = "https://pypi.org/pypi/{}/json"
_SKIP_DIRS = (
    "node_modules,.git,playwright-report,test-results,.next,dist,"
    "build,out,__pycache__,.pytest_cache"
)


def _find_trivy() -> str:
    """Resolve Trivy via PATH or a local WinGet install (PATH not refreshed)."""
    found = shutil.which("trivy")
    if found:
        return found
    roots = []
    local = os.environ.get("LOCALAPPDATA")
    if local:
        roots.append(Path(local))
    home = Path.home() / "AppData" / "Local"
    if home not in roots:
        roots.append(home)
    for base in roots:
        wg = base / "Microsoft" / "WinGet"
        link = wg / "Links" / "trivy.exe"
        if link.exists():
            return str(link)
        if wg.exists():
            hits = sorted(wg.rglob("trivy.exe"))
            if hits:
                return str(hits[0])
    return ""


class D11Dependency:
    """D11 dimension: dependency security and freshness."""

    id = "d11"
    name = "DEPENDENCY"
    channel = "gate"

    def audit(self, ctx: AuditContext) -> list:
        return self._trivy(ctx) + self._pypi(ctx)

    def _trivy(self, ctx) -> list:
        trivy = _find_trivy()
        if not trivy:
            return [
                Finding(self.id, "Trivy missing: SCA not audited", Status.UNAVAILABLE)
            ]
        try:
            res = subprocess.run(
                [
                    trivy,
                    "fs",
                    "--quiet",
                    "--format",
                    "json",
                    "--severity",
                    "CRITICAL",
                    "--timeout",
                    "30s",
                    "--skip-dirs",
                    _SKIP_DIRS,
                    ".",
                ],
                capture_output=True,
                text=True,
                cwd=str(ctx.project_path),
                encoding="utf-8",
                errors="ignore",
                timeout=45,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            # Transient error (timeout under hook load) => WARN, non-blocking.
            return [Finding(self.id, f"Trivy transient error: {exc}", Status.WARN)]
        if res.returncode != 0 and not res.stdout:
            return [
                Finding(
                    self.id,
                    f"Trivy transient failure (exit {res.returncode}): {res.stderr.strip()}",
                    Status.WARN,
                )
            ]
        try:
            results = json.loads(res.stdout).get("Results") or []
        except (json.JSONDecodeError, TypeError):
            return [
                Finding(self.id, "Trivy returned partial JSON output (transient)", Status.WARN)
            ]
        out = []
        for tr in results:
            for v in tr.get("Vulnerabilities") or []:
                out.append(
                    Finding(
                        self.id,
                        f"VT-112 CRITICAL {v.get('VulnerabilityID', 'N/A')} en {tr.get('Target', 'N/A')} -> "
                        f"{v.get('PkgName', 'N/A')} (instalada {v.get('InstalledVersion', 'N/A')}, "
                        f"fix {v.get('FixedVersion', 'N/A')})",
                        Status.FAIL,
                    )
                )
        logger.info("d11 trivy: %d CRITICAL vulns", len(out))
        return out

    def _pypi(self, ctx) -> list:
        req = ctx.project_path / "requirements.txt"
        if not req.exists():
            return []
        deps = []
        for line in req.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "==" in line:
                name, ver = line.split("==", 1)
                deps.append((name.strip(), ver.strip()))
        out = []
        for name, pinned in deps:
            try:
                with urllib.request.urlopen(_PYPI_URL.format(name), timeout=5) as resp:
                    data = json.loads(resp.read())
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    out.append(
                        Finding(
                            self.id,
                            f"VC-129 hallucinated dependency detected: '{name}' does not exist on PyPI",
                            Status.FAIL,
                        )
                    )
                else:
                    out.append(
                        Finding(
                            self.id,
                            f"PyPI error for {name}: ({exc})",
                            Status.WARN,
                        )
                    )
                continue
            except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
                out.append(
                    Finding(
                        self.id,
                        f"PyPI unreachable for {name}: outdated/yanked not verified ({exc})",
                        Status.WARN,
                    )
                )
                continue
            latest = data.get("info", {}).get("version")
            files = data.get("releases", {}).get(pinned) or []
            if files and all(f.get("yanked") for f in files):
                out.append(
                    Finding(
                        self.id,
                        f"{name}=={pinned} is YANKED on PyPI (removed)",
                        Status.FAIL,
                    )
                )
            elif latest and latest != pinned:
                out.append(
                    Finding(
                        self.id,
                        f"{name}=={pinned} is outdated (latest {latest})",
                        Status.WARN,
                    )
                )
        logger.info("d11 pypi: %d deps revisadas", len(deps))
        return out
