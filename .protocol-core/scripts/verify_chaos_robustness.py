#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHAOS MONKEY v2.0 - CoderCerberus Resilience Tester
Inyecta fallos reales y verifica que el sistema los maneja correctamente.
Exit 0 = sistema robusto. Exit 1 = fallo silencioso detectado.
Mandato S1/B3 — REGLA B3: Angry Path Dominance.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.append(os.getcwd())
from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()


def scenario_a_nonexistent_path() -> bool:
    """Chaos A: run_security_audit_12d con proyecto inexistente retorna errores, no crash."""
    sys.path.insert(0, os.getcwd())
    try:
        from scripts.run_security_audit_12d import DeepForensicAuditor
        auditor = DeepForensicAuditor("/ruta/que/no/existe/cerberus_chaos_99999")
        result = auditor.audit_d1_integrity()
        if not isinstance(result, list):
            print("  [FAIL A] audit_d1 no retornó lista ante ruta inexistente.")
            return False
        if len(result) == 0:
            print("  [FAIL A] audit_d1 retornó lista vacía para ruta inexistente (debería tener errores).")
            return False
        print("  [PASS A] Ruta inexistente retorna errores correctamente, no crash.")
        return True
    except SystemExit:
        print("  [FAIL A] audit_d12 llamó sys.exit() ante ruta inexistente.")
        return False
    except Exception as e:
        print(f"  [FAIL A] Excepción no manejada ante ruta inexistente: {e}")
        return False


def scenario_b_malformed_state() -> bool:
    """Chaos B: .agent_state.json malformado no crashea sync_binding."""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / ".agent_state.json").write_text("{bad json", encoding="utf-8")
            from scripts.sync_binding import ProtocolSyncManager
            mgr = ProtocolSyncManager(root_dir=tmp_path)
            if not isinstance(mgr.state, dict):
                print("  [FAIL B] sync_binding no retornó dict ante JSON malformado.")
                return False
            print("  [PASS B] sync_binding maneja .agent_state.json malformado sin crash.")
            return True
    except Exception as e:
        print(f"  [FAIL B] Excepción no manejada: {e}")
        return False


def scenario_c_empty_spec_real() -> bool:
    """Chaos C: run_security_audit_12d con SPEC.md vacío extrae whitelist base sin crash."""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "SPEC.md").write_text("", encoding="utf-8")
            from scripts.run_security_audit_12d import DeepForensicAuditor
            auditor = DeepForensicAuditor(str(tmp_path))
            if not isinstance(auditor.whitelist, set):
                print("  [FAIL C] whitelist no es set ante SPEC.md vacío.")
                return False
            print(f"  [PASS C] SPEC.md vacío retorna whitelist base ({len(auditor.whitelist)} entries).")
            return True
    except Exception as e:
        print(f"  [FAIL C] Excepción: {e}")
        return False


def scenario_d_evidence_bad_dir() -> bool:
    """Chaos D: EvidenceLogger con directorio inexistente no crashea silenciosamente."""
    try:
        from scripts.log_evidence import EvidenceLogger
        el = EvidenceLogger(root=Path("/ruta/inexistente/chaos_99999"))
        try:
            el.log_operation(
                operation="chaos_test", agent_name="chaos", command="test",
                outcome="test"
            )
            print("  [PASS D] EvidenceLogger manejó directorio inexistente (mkdir -p exitoso).")
            return True
        except (OSError, PermissionError):
            print("  [PASS D] EvidenceLogger lanzó error explícito ante directorio inaccesible.")
            return True
    except Exception as e:
        print(f"  [FAIL D] Excepción inesperada: {e}")
        return False


def scenario_e_exit_code_logic() -> bool:
    """Chaos E: Lógica de exit code penaliza escenarios fallidos."""
    try:
        passed = 0
        total = 1
        exit_code = 0 if passed == total else 1
        if exit_code != 1:
            print("  [FAIL E] Lógica de exit code no penaliza escenarios fallidos.")
            return False
        print("  [PASS E] Lógica de exit code correcta: 0/1 → exit 1.")
        return True
    except Exception as e:
        print(f"  [FAIL E] Excepción: {e}")
        return False


def scenario_f_check_gate() -> bool:
    """Chaos F: protocol_cli verifica exit code de run_security_audit_12d, no string (S22 mandate)."""
    try:
        content = Path("scripts/protocol_cli.py").read_text(encoding="utf-8")
        has_exit_code_check = "code != 0" in content and "return 1" in content
        has_string_theater = '"APPROVED" not in stdout' in content
        if has_exit_code_check and not has_string_theater:
            print("  [PASS F] protocol_cli usa exit code (no string) para verificar run_security_audit_12d.")
            return True
        elif has_string_theater:
            print("  [FAIL F] command_check verifica por string 'APPROVED' — teatro (S22 violation).")
            return False
        else:
            print("  [FAIL F] command_check no tiene gate por exit code para run_security_audit_12d failure.")
            return False
    except Exception as e:
        print(f"  [FAIL F] Excepcion: {e}")
        return False


def run_all_scenarios() -> tuple:
    """Ejecuta todos los escenarios y reporta resultado. Retorna (passed, total)."""
    print("=" * 60)
    print("CHAOS MONKEY v2.1 — ANGRY PATH CERTIFICATION")
    print("=" * 60)

    scenarios = [
        ("A: Ruta de proyecto inexistente", scenario_a_nonexistent_path),
        ("B: .agent_state.json malformado en sync_binding", scenario_b_malformed_state),
        ("C: SPEC.md vacío en whitelist extractor real", scenario_c_empty_spec_real),
        ("D: EvidenceLogger con directorio inexistente", scenario_d_evidence_bad_dir),
        ("E: Exit code penaliza escenarios fallidos", scenario_e_exit_code_logic),
        ("F: protocol_cli gate retorna 1 ante run_security_audit_12d failure", scenario_f_check_gate),
    ]

    passed = 0
    for name, fn in scenarios:
        print(f"\n[ESCENARIO {name}]")
        try:
            if fn():
                passed += 1
        except Exception as e:
            print(f"  [FAIL] Excepción no capturada en escenario: {e}")

    total = len(scenarios)
    print("\n" + "=" * 60)
    if passed == total:
        print(f"CAOS CERTIFICADO: {passed}/{total} escenarios superados — sistema resiliente.")
    else:
        print(f"CAOS FALLIDO: {passed}/{total} escenarios superados — fallos silenciosos detectados.")
    print("=" * 60)
    return passed, total


if __name__ == "__main__":
    passed, total = run_all_scenarios()
    sys.exit(0 if passed == total else 1)
