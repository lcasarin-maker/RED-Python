"""
test_portability.py — Comportamiento real, no existencia.
Cada test verifica que la detección ocurre, no que el objeto existe.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dimensions.context import AuditContext
from dimensions.d7_security import D7Security
from run_security_audit_12d import DeepForensicAuditor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _d7_messages(tmp_path: Path) -> list[str]:
    """Run D7 regex (no bandit) y retorna mensajes de hallazgos."""
    ctx = AuditContext(tmp_path)
    findings = D7Security()._regex(ctx)
    return [f.message for f in findings]


# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------

class TestExternalProjectAudit:
    def test_audit_init_external_project(self, tmp_path):
        auditor = DeepForensicAuditor(str(tmp_path))
        assert str(auditor.project_path) == str(tmp_path)
        assert auditor.is_cerberus is False

    def test_audit_init_cerberus_flag_is_bool(self):
        """is_cerberus debe ser bool, nunca None ni truthy-string."""
        cerberus_path = Path(__file__).parent.parent.parent
        auditor = DeepForensicAuditor(str(cerberus_path))
        assert isinstance(auditor.is_cerberus, bool)

    def test_audit_no_crash_without_protocol_engine(self, tmp_path):
        """Audit no debe fallar con ImportError al correr en proyecto externo."""
        (tmp_path / "main.py").write_text("print('hello')\n")
        auditor = DeepForensicAuditor(str(tmp_path))
        try:
            auditor.run()
        except ImportError as exc:
            if "protocol_engine" in str(exc):
                pytest.fail(f"Sigue requiriendo import interno: {exc}")
            raise

    def test_run_returns_bool(self, tmp_path):
        """run() debe retornar bool — no dict ni None."""
        (tmp_path / "clean.py").write_text("x: int = 1\n")
        auditor = DeepForensicAuditor(str(tmp_path))
        result = auditor.run()
        assert isinstance(result, bool), f"run() retornó {type(result)}, esperado bool"

    def test_external_project_requires_purge_evidence(self, tmp_path):
        """Si es proyecto externo, D2 debe exigir purge_plan.md y phase_0_purge_result.md."""
        # Generar SPEC.md básico para pasar _check_spec_completeness
        spec_content = "# SPEC.md\n1. Descripción Operacional\n2. Interfaz Pública\n3. Restricciones\n4. Arquitectura\n5. Mandatos Aplicables\n6. Próximos Sprints\n7. Regla de Cierre\n8. Contacto/DRI\n"
        (tmp_path / "SPEC.md").write_text(spec_content, encoding="utf-8")
        
        auditor = DeepForensicAuditor(str(tmp_path))
        errors = auditor.audit_d2_completeness()
        
        # Deben faltar ambos archivos de evidencia de purga
        assert any("purge_plan.md" in err for err in errors)
        assert any("phase_0_purge_result.md" in err for err in errors)
        
        # Crear los archivos de evidencia
        (tmp_path / "purge_plan.md").write_text("plan", encoding="utf-8")
        (tmp_path / "phase_0_purge_result.md").write_text("result", encoding="utf-8")
        
        errors_fixed = auditor.audit_d2_completeness()
        assert not any("purge_plan.md" in err for err in errors_fixed)
        assert not any("phase_0_purge_result.md" in err for err in errors_fixed)

    def test_gitignore_comments(self, tmp_path):
        """Verifica que las exclusiones en .gitignore sin comentarios de justificación
        fallen la auditoría D2 (VC-111).
        """
        spec_content = "# SPEC.md\n1. Descripción Operacional\n2. Interfaz Pública\n3. Restricciones\n4. Arquitectura\n5. Mandatos Aplicables\n6. Próximos Sprints\n7. Regla de Cierre\n8. Contacto/DRI\n"
        (tmp_path / "SPEC.md").write_text(spec_content, encoding="utf-8")
        (tmp_path / "purge_plan.md").write_text("plan", encoding="utf-8")
        (tmp_path / "phase_0_purge_result.md").write_text("result", encoding="utf-8")
        
        # 1. Caso .gitignore sin comentarios
        (tmp_path / ".gitignore").write_text("secret_dir/\ntemp_file.txt\n", encoding="utf-8")
        auditor = DeepForensicAuditor(str(tmp_path))
        errors = auditor.audit_d2_completeness()
        assert any("VC-111" in err and "secret_dir/" in err for err in errors), f"No se detectó secret_dir/ sin comentario: {errors}"
        assert any("VC-111" in err and "temp_file.txt" in err for err in errors), f"No se detectó temp_file.txt sin comentario: {errors}"

        # 2. Caso .gitignore con comentarios válidos
        gitignore_valid = (
            "# Justificación de exclusiones\n"
            "secret_dir/\n"
            "\n"
            "# Archivos temporales de build\n"
            "temp_file.txt\n"
        )
        (tmp_path / ".gitignore").write_text(gitignore_valid, encoding="utf-8")
        errors_valid = auditor.audit_d2_completeness()
        assert not any("VC-111" in err for err in errors_valid), f"Falso positivo en gitignore comentado: {errors_valid}"

    def test_declarative_rule_validation(self, tmp_path):
        """Debe validar la presencia y el formato de golden_standard_ref en rules.yaml."""
        auditor = DeepForensicAuditor(str(tmp_path))
        errors_by_domain = {"D2": []}
        
        # 1. Regla sin golden_standard_ref
        rules_missing = [{"id": "D6_test", "domain": "D6"}]
        auditor._validate_declarative_rule_references(rules_missing, errors_by_domain)
        assert any("no contiene el campo 'golden_standard_ref'" in err for err in errors_by_domain["D2"])
        
        # 2. Regla con golden_standard_ref con formato inválido
        errors_by_domain["D2"] = []
        rules_invalid = [{"id": "D6_test", "domain": "D6", "golden_standard_ref": "INVALID-123"}]
        auditor._validate_declarative_rule_references(rules_invalid, errors_by_domain)
        assert any("golden_standard_ref' inválido o mal formateado" in err for err in errors_by_domain["D2"])
        
        # 3. Reglas válidas (con y sin PENDING:)
        errors_by_domain["D2"] = []
        rules_valid = [
            {"id": "D6_test1", "domain": "D6", "golden_standard_ref": "VC-067"},
            {"id": "D6_test2", "domain": "D6", "golden_standard_ref": "PENDING:VC-115"},
            {"id": "D6_test3", "domain": "D6", "golden_standard_ref": "PI-012"}
        ]
        auditor._validate_declarative_rule_references(rules_valid, errors_by_domain)
        assert len(errors_by_domain["D2"]) == 0


# ---------------------------------------------------------------------------
# D7 Detección de seguridad — comportamiento real
# ---------------------------------------------------------------------------

class TestSecurityDetectionBehavior:
    def test_detects_hardcoded_password(self, tmp_path):
        """D7 debe detectar credenciales hardcodeadas (password = 'secret')."""
        (tmp_path / "config.py").write_text(
            "DB_PASSWORD = 'MySuperSecret123'\n"
        )
        msgs = _d7_messages(tmp_path)
        assert any("Credenciales" in m for m in msgs), (
            f"D7 no detectó credenciales. Hallazgos: {msgs}"
        )

    def test_detects_hardcoded_api_key(self, tmp_path):
        """D7 debe detectar API keys hardcodeadas."""
        (tmp_path / "config.py").write_text(
            "API_KEY = 'sk-proj-abcdefghij'\n"
        )
        msgs = _d7_messages(tmp_path)
        assert any("Credenciales" in m for m in msgs), (
            f"D7 no detectó API key. Hallazgos: {msgs}"
        )

    def test_detects_eval(self, tmp_path):
        """D7 debe detectar eval() inseguro."""
        (tmp_path / "dangerous.py").write_text(
            "result = eval(user_input)\n"
        )
        msgs = _d7_messages(tmp_path)
        assert any("eval" in m.lower() for m in msgs), (
            f"D7 no detectó eval(). Hallazgos: {msgs}"
        )

    def test_detects_pickle_loads(self, tmp_path):
        """D7 debe detectar pickle.loads() inseguro."""
        (tmp_path / "loader.py").write_text(
            "import pickle\ndata = pickle.loads(raw_bytes)\n"
        )
        msgs = _d7_messages(tmp_path)
        assert any("pickle" in m.lower() for m in msgs), (
            f"D7 no detectó pickle.loads(). Hallazgos: {msgs}"
        )

    def test_detects_sql_fstring_injection(self, tmp_path):
        """D7 debe detectar inyección SQL via f-string."""
        (tmp_path / "db.py").write_text(
            'query = f"SELECT * FROM users WHERE id={uid}"\n'
        )
        msgs = _d7_messages(tmp_path)
        assert any("SQL" in m or "inyecci" in m.lower() for m in msgs), (
            f"D7 no detectó SQL f-string. Hallazgos: {msgs}"
        )

    def test_clean_file_has_no_findings(self, tmp_path):
        """Archivo limpio no debe producir hallazgos D7."""
        (tmp_path / "clean.py").write_text(
            "def greet(name: str) -> str:\n    return f'Hello {name}'\n"
        )
        msgs = _d7_messages(tmp_path)
        assert msgs == [], f"D7 produjo falsos positivos: {msgs}"

    def test_deterministic_across_two_runs(self, tmp_path):
        """Misma entrada → mismo número de hallazgos."""
        (tmp_path / "config.py").write_text("SECRET = 'hardcoded_val'\n")
        msgs1 = _d7_messages(tmp_path)
        msgs2 = _d7_messages(tmp_path)
        assert len(msgs1) == len(msgs2), "D7 no es determinístico"

    def test_declarative_insecure_defaults(self, tmp_path):
        """La regla declarativa D7_prevent_insecure_defaults debe detectar patrones inseguros."""
        rules_dir = tmp_path / ".protocol" / "rules"
        rules_dir.mkdir(parents=True)
        
        import yaml
        rules_yaml_content = {
            "rules": [
                {
                    "id": "D7_prevent_insecure_defaults",
                    "domain": "D7",
                    "keywords": ["verify=False", "host='0.0.0.0'", 'host="0.0.0.0"', "CORS origins='*'", 'CORS origins="*"', "origins='*'", 'origins="*"', "hashlib.md5(", "debug=True"],
                    "message": "Se detectó un valor predeterminado inseguro por defecto.",
                    "golden_standard_ref": "VC-138"
                }
            ]
        }
        with open(rules_dir / "rules.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(rules_yaml_content, f)

        # 1. Caso verify=False
        (tmp_path / "insecure.py").write_text("requests.get(url, verify=False)\n")
        auditor = DeepForensicAuditor(str(tmp_path))
        errors = auditor.audit_declarative_rules()
        assert any("D7_prevent_insecure_defaults" in err for err in errors["D7"]), f"No se detectó verify=False. Errores: {errors}"

        # 2. Caso debug=True
        (tmp_path / "insecure.py").write_text("app.run(debug=True)\n")
        errors = auditor.audit_declarative_rules()
        assert any("D7_prevent_insecure_defaults" in err for err in errors["D7"]), f"No se detectó debug=True. Errores: {errors}"

        # 3. Caso host='0.0.0.0'
        (tmp_path / "insecure.py").write_text("app.run(host='0.0.0.0')\n")
        errors = auditor.audit_declarative_rules()
        assert any("D7_prevent_insecure_defaults" in err for err in errors["D7"]), f"No se detectó host='0.0.0.0'. Errores: {errors}"

        # 4. Caso limpio
        (tmp_path / "insecure.py").write_text("requests.get(url, verify=True)\n")
        errors = auditor.audit_declarative_rules()
        assert len(errors["D7"]) == 0, f"Se reportó error falso en archivo limpio. Errores: {errors}"


# ---------------------------------------------------------------------------
# Edge cases de portabilidad
# ---------------------------------------------------------------------------

class TestPortabilityEdgeCases:
    def test_empty_directory_no_crash(self, tmp_path):
        """Directorio vacío no debe lanzar excepción."""
        msgs = _d7_messages(tmp_path)
        assert isinstance(msgs, list)

    def test_binary_file_skipped(self, tmp_path):
        """Archivo binario no debe romper el escaneo."""
        (tmp_path / "script.py").write_text("x = 1\n")
        (tmp_path / "data.pkl").write_bytes(b'\x80\x04\x95')
        msgs = _d7_messages(tmp_path)
        assert isinstance(msgs, list)

    def test_incremental_detection(self, tmp_path):
        """Segunda instancia detecta archivo nuevo agregado después."""
        (tmp_path / "clean.py").write_text("x = 1\n")
        msgs1 = _d7_messages(tmp_path)
        (tmp_path / "secret.py").write_text("password = 'supersecret123'\n")
        msgs2 = _d7_messages(tmp_path)
        assert len(msgs2) > len(msgs1), (
            "Segunda corrida no detectó el archivo agregado"
        )

    def test_strict_type_annotations(self, tmp_path):
        """Verifica que el comprobador detecte firmas sin anotaciones en protocol_engine y dimensions, y acepte las anotadas."""
        pe_dir = tmp_path / "protocol_engine"
        pe_dir.mkdir()
        
        # 1. Caso sin anotación de retorno
        (pe_dir / "bad_ret.py").write_text("def do_something(x: int):\n    pass\n", encoding="utf-8")
        auditor = DeepForensicAuditor(str(tmp_path))
        errors = auditor.audit_d6_anti_slop()
        assert any("bad_ret.py" in err and "no tiene anotación de tipo de retorno" in err for err in errors), f"No se detectó falta de retorno. Errores: {errors}"
        
        # 2. Caso sin anotación de argumento
        (pe_dir / "bad_arg.py").write_text("def do_something(x) -> None:\n    pass\n", encoding="utf-8")
        errors = auditor.audit_d6_anti_slop()
        assert any("bad_arg.py" in err and "argumento 'x'" in err and "no tiene anotación de tipo" in err for err in errors), f"No se detectó falta de argumento. Errores: {errors}"

        # 3. Ignorar funciones privadas
        (pe_dir / "private_func.py").write_text("def _do_something(x):\n    pass\n", encoding="utf-8")
        errors = auditor.audit_d6_anti_slop()
        assert not any("private_func.py" in err for err in errors), f"Se reportó error en función privada. Errores: {errors}"

        # 4. Caso limpio
        (pe_dir / "clean.py").write_text("def do_something(x: int) -> None:\n    pass\n", encoding="utf-8")
        errors = auditor.audit_d6_anti_slop()
        clean_errors = [err for err in errors if "clean.py" in err]
        assert len(clean_errors) == 0, f"Falso positivo en archivo limpio: {clean_errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
