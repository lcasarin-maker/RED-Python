#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D3 Dead Code (Sprint 28.5): ruff F + vulture (solo defs muertas).

Real, no simulado. Ejecuta ruff (imports/locals F401/F841) y vulture
(funciones/métodos/clases/inalcanzable — el hueco de symbol-table que el
monolito inline no cubría). Excluye a propósito vulture "unused variable"/
"import": los locals reales ya los toma ruff F841 y el subconjunto de
*parámetros* da falsos positivos estructurales (firmas de callback obligatorias,
p.ej. shutil.rmtree onerror). Eso es scoping, no whitelist.

Binario ausente => Finding UNAVAILABLE (H4: nunca PASS silencioso), no []."""
import logging
import shutil
import subprocess

from dimensions.base import Finding, Status
from dimensions.context import AuditContext

logger = logging.getLogger("dimensions.d3")

_VULTURE_DEF_TYPES = (
    "unused function",
    "unused method",
    "unused class",
    "unused property",
    "unreachable code",
)


class D3DeadCode:
    """Dimensión D3: residuo de refactor (lo que sobra DENTRO y ENTRE archivos)."""

    id = "d3"
    name = "DEAD CODE"
    channel = "gate"

    def audit(self, ctx: AuditContext) -> list:
        scripts_dir = ctx.project_path / "scripts"
        if not scripts_dir.exists():
            return []
        return self._ruff(scripts_dir) + self._vulture(scripts_dir)

    def _ruff(self, scripts_dir) -> list:
        ruff = shutil.which("ruff")
        if not ruff:
            return [
                Finding(
                    self.id, "ruff ausente: dead-code F no auditado", Status.UNAVAILABLE
                )
            ]
        try:
            res = subprocess.run(
                [
                    ruff,
                    "check",
                    "--select",
                    "F",
                    "--output-format=concise",
                    str(scripts_dir),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return [Finding(self.id, f"ruff error: {exc}", Status.UNAVAILABLE)]
        out = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if ".py:" in line and ": F" in line:
                out.append(Finding(self.id, f"dead code (ruff): {line}", Status.FAIL))
        logger.info("d3 ruff: %d hallazgos", len(out))
        return out

    def _vulture(self, scripts_dir) -> list:
        vulture = shutil.which("vulture")
        if not vulture:
            return [
                Finding(
                    self.id,
                    "vulture ausente: defs muertas no auditadas",
                    Status.UNAVAILABLE,
                )
            ]
        try:
            res = subprocess.run(
                [vulture, str(scripts_dir), "--min-confidence", "80"],
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return [Finding(self.id, f"vulture error: {exc}", Status.UNAVAILABLE)]
        out = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if any(t in line for t in _VULTURE_DEF_TYPES):
                out.append(Finding(self.id, f"dead def (vulture): {line}", Status.FAIL))
        logger.info("d3 vulture: %d defs muertas", len(out))
        return out
