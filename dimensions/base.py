#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrato de dimensión (Sprint 28.5 Paso 2).

Toda dimensión implementa `audit(ctx) -> list[Finding]` sobre un `AuditContext`
compartido. `UNAVAILABLE` existe para que un insumo/binario ausente NUNCA se
reporte como PASS silencioso (S5 anti-slop)."""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from dimensions.context import AuditContext

logger = logging.getLogger("dimensions.base")


class Status(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNAVAILABLE = (
        "UNAVAILABLE"  # insumo/binario ausente: bloquea con motivo, no aprueba
    )


@dataclass(frozen=True)
class Finding:
    """Un hallazgo de una dimensión. status != PASS implica acción del gate/hook."""

    dimension: str  # "D7"
    message: str
    status: Status = Status.FAIL
    path: str = None
    line: int = None

    def is_blocking(self) -> bool:
        return self.status in (Status.FAIL, Status.UNAVAILABLE)


@runtime_checkable
class Dimension(Protocol):
    """Interfaz que toda dimensión registrada debe cumplir. Sin `main()`."""

    id: str  # "d7"
    name: str  # "Seguridad de Datos"
    channel: str  # "gate" | "hook"

    def audit(self, ctx: AuditContext) -> list: ...
