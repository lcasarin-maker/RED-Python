#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_catalog_circularity_ratchet.py
Sprint 3.3 (flip total) — RATCHET de circularidad del verificador de cobertura.

Contexto (root cause): `test_physical_validation_exists` acepta que el
`validating_mechanism` exista como string LITERAL en cualquier .py de scripts/ o
tests/. Como `generate_golden_audit.py` (el generador que ESCRIBE esos strings) es
uno de los archivos escaneados, la verificación es circular (juez == sujeto). Esto
es exactamente VT-014 (test circular) / VT-103 (expected codificado en el evaluador)
del propio catálogo, ocurriendo dentro del gate de gobernanza de salida.

Regla estricta (no circular): un mecanismo está REALMENTE cubierto solo si existe
como `def <mech>(` en tests/ o scripts/ EXCLUYENDO el generador, o como atributo de
`DeepForensicAuditor`. Bajo esa regla hoy hay 170 IDs / 8 mecanismos que son puro
string-literal (teatro) — congelados en circularity_baseline.json.

Este test NO voltea el gate a duro de golpe (rompería con 170 fallos). Implementa un
ratchet: el set circular ACTUAL debe ser ⊆ baseline. Efecto:
  - Vicio NUEVO mapeado a un fallback (sin def real) → circular y NO en baseline → FALLA.
    => failing-first inmediato para todo lo que se agregue de aquí en adelante.
  - Drenar un vicio (escribir su test real) → sale del set circular, sigue ⊆ baseline → PASA.
    => al drenar, se REMUEVE el ID del baseline para apretar el ratchet (nunca agregar).
"""

import json
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.run_security_audit_12d import DeepForensicAuditor

_GENERATOR = "generate_golden_audit.py"
_AUDIT_JSON = _ROOT / ".protocol" / "metadata" / "golden_standard_audit.json"
_BASELINE = _ROOT / ".protocol" / "metadata" / "circularity_baseline.json"


def _scan_real_defs() -> str:
    """Texto de todos los .py de tests/ y scripts/ MENOS el generador (rompe circularidad)."""
    py_files = [
        p for p in list((_ROOT / "tests").glob("**/*.py"))
        + list((_ROOT / "scripts").glob("**/*.py"))
        if p.name != _GENERATOR
    ]
    return "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in py_files)


def _current_circular() -> set:
    """IDs cuyo validating_mechanism NO resuelve a un def real ni a atributo del auditor.

    IDs con validating_mechanism == "DOC_ONLY" son EXCLUIDOS: declaran honestamente que
    el vicio es conductual/doctrinal y no tiene test estático genérico discriminante.
    DOC_ONLY != circular; DOC_ONLY = honesto (Sprint 3.4: reclasificación de catch-alls).
    """
    db = json.loads(_AUDIT_JSON.read_text(encoding="utf-8"))
    text = _scan_real_defs()
    circular = set()
    for fid, entry in db.items():
        mech = entry["validating_mechanism"]
        # DOC_ONLY es honesto: declara que no hay test estático, no es teatro
        if mech == "DOC_ONLY":
            continue
        if hasattr(DeepForensicAuditor, mech):
            continue
        if f"def {mech}" in text:
            continue
        circular.add(fid)
    return circular


class TestCircularityRatchet(unittest.TestCase):
    def test_no_new_circular_ids_beyond_baseline(self):
        """RATCHET: ningún vicio NUEVO puede mapear a un mecanismo-fallback (string-literal).
        El set circular actual debe ser subconjunto del baseline congelado."""
        baseline = set(json.loads(_BASELINE.read_text(encoding="utf-8"))["all_ids"])
        current = _current_circular()
        new_circular = sorted(current - baseline)
        self.assertEqual(
            new_circular, [],
            "Circularidad NUEVA detectada (vicios mapeados a un mecanismo que no existe como "
            f"def de test real, solo string-literal en {_GENERATOR}): {new_circular}. "
            "Escribe un test failing-first real para estos IDs o corrige su validating_mechanism.",
        )

    def test_baseline_only_lists_genuinely_circular_ids(self):
        """Higiene del ratchet: el baseline no debe listar IDs YA drenados (que sí tienen def real).
        Si este test falla, drenaste un vicio pero olvidaste removerlo del baseline → aprieta el ratchet."""
        baseline = set(json.loads(_BASELINE.read_text(encoding="utf-8"))["all_ids"])
        current = _current_circular()
        stale = sorted(baseline - current)
        self.assertEqual(
            stale, [],
            "El baseline lista IDs que ya NO son circulares (tienen def real). Remuévelos de "
            f"circularity_baseline.json para apretar el ratchet: {stale}",
        )


if __name__ == "__main__":
    unittest.main()
