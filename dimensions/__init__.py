#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paquete de dimensiones (Sprint 28.5 Paso 2).

`REGISTRY` es la única fuente de verdad de qué dimensiones existen y se ejecutan.
Añadir una dimensión = crear su módulo e inscribirla aquí; el gate la corre por
el loop sobre REGISTRY y `dimension_registry.json` la audita. Imposible orfanar.
"""
from dimensions.base import Dimension, Finding, Status
from dimensions.context import AuditContext
from dimensions.d3_dead_code import D3DeadCode
from dimensions.d7_security import D7Security
from dimensions.d11_dependency import D11Dependency
from dimensions.d13_observable import D13Observable
from dimensions.d14_discourse_rigor import D14DiscourseRigor

# Única fuente de verdad. run() recorre las de canal gate; las hook (d13/d14) las
# salta — su entrada la invoca el Stop hook (discourse_hook.py).
REGISTRY: list = [
    D3DeadCode(),
    D7Security(),
    D11Dependency(),
    D13Observable(),
    D14DiscourseRigor(),
]

__all__ = ["Dimension", "Finding", "Status", "AuditContext", "REGISTRY"]
