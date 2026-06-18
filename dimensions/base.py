#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dimension contract (Sprint 28.5 Step 2).

Every dimension implements `audit(ctx) -> list[Finding]` over a shared
`AuditContext`. `UNAVAILABLE` exists so a missing input or binary is never
reported as a silent PASS (S5 anti-slop).
"""
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
        "UNAVAILABLE"  # missing input or binary: blocks with a reason, never passes
    )


@dataclass(frozen=True)
class Finding:
    """A finding produced by a dimension. status != PASS requires gate/hook action."""

    dimension: str  # "D7"
    message: str
    status: Status = Status.FAIL
    path: str = None
    line: int = None

    def is_blocking(self) -> bool:
        return self.status in (Status.FAIL, Status.UNAVAILABLE)


@runtime_checkable
class Dimension(Protocol):
    """Interface that every registered dimension must satisfy. No `main()`."""

    id: str  # "d7"
    name: str  # "Data Security"
    channel: str  # "gate" | "hook"

    def audit(self, ctx: AuditContext) -> list: ...
