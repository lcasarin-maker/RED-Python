#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
record_validation_debt_historical.py — Record historical validation debts
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.satellite_validation_debt import register_validation_debt

# Control_Procesal false positive: Marked APPROVED but server/UI were broken
debt_id_1 = register_validation_debt(
    satellite="Control_Procesal",
    debt_type="functional",
    severity="critical",
    description="Server validation was ceremonial — only checked file structure, not endpoint functionality. /expedientes endpoint had timeout/hanging behavior.",
    evidence=[
        "00 audit/results/exterior/Control_Procesal/2026-06-05/phase2_ui_screenshot.png (shows 'Conectando...' status)",
        "00 audit/results/exterior/Control_Procesal/2026-06-05/phase2_remediation_result.md (documents initialization race condition)"
    ],
    remediation="Implemented async bootstrap chain: verificarServidor() → cargarData() → cargarInhabiles() → cargarClientes() → cargarValoraciones(). Added tests to block reintroduction.",
    falsely_approved_phase="PHASE_1_CONTRACT"
)

print(f"✅ Recorded debt: {debt_id_1}")
print("   Type: Functional validation gap (ceremonial audit)")
print("   Severity: CRITICAL")
print("   Phase: Control_Procesal server validation only checked structure, not real endpoints")
