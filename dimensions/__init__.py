#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dimension package (Sprint 28.5 Step 2).

`REGISTRY` is the single source of truth for which dimensions exist and run.
Adding a dimension means creating its module and registering it here; the gate
iterates over REGISTRY and `dimension_registry.json` audits it. Orphans are
impossible by design.
"""
from dimensions.base import Dimension, Finding, Status
from dimensions.context import AuditContext
from dimensions.d3_dead_code import D3DeadCode
from dimensions.d7_security import D7Security
from dimensions.d11_dependency import D11Dependency
from dimensions.d13_observable import D13Observable
from dimensions.d14_discourse_rigor import D14DiscourseRigor

# Single source of truth. `run()` iterates over gate-channel dimensions; hook
# dimensions (d13/d14) are skipped because their entry point is invoked by the
# Stop hook (`discourse_hook.py`).
REGISTRY: list = [
    D3DeadCode(),
    D7Security(),
    D11Dependency(),
    D13Observable(),
    D14DiscourseRigor(),
]

__all__ = ["Dimension", "Finding", "Status", "AuditContext", "REGISTRY"]
