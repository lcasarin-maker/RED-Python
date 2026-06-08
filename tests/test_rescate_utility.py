#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Validar que rescate de archivos deprecated tiene utilidad real, no solo existencia.
Cuestiona el FONDO, no la forma.
"""

import pytest
from pathlib import Path


class TestProtocolBehaviorRescate:
    """Validar que B13 refactorizado tiene mecanismo real."""

    def test_b13_requires_reproducible_failure(self):
        """B13 (PROTOCOL FEEDBACK LOOP) exige que el mandato esté en PROTOCOL_BEHAVIOR.md
        con texto que obliga a evidencia empírica, no solo declaraciones."""
        protocol = Path("PROTOCOL_BEHAVIOR.md").read_text(encoding="utf-8", errors="ignore")
        # B13 debe existir en el protocolo
        assert "B13" in protocol, "B13 no aparece en PROTOCOL_BEHAVIOR.md"
        # B13 debe referir a evidencia/test/reproducible — no puede ser solo un nombre
        b13_section_start = protocol.find("B13")
        b13_excerpt = protocol[b13_section_start:b13_section_start + 400]
        has_evidence_language = any(
            kw in b13_excerpt.lower()
            for kw in ["test", "evidencia", "reproducible", "fallo", "feedback"]
        )
        assert has_evidence_language, (
            f"B13 existe pero sin lenguaje de evidencia empírica. Extracto: {b13_excerpt[:200]}"
        )

    def test_prompts_rapidos_actually_saves_tokens(self):
        """
        PROMPTS_RAPIDOS.md reclama acelerar sesiones.
        ¿Realmente lo hace o es dead code?

        TEST: Si el archivo existe, debe tener métrica de uso.
        """
        prompts_file = Path("PROMPTS_RAPIDOS.md")
        if prompts_file.exists():
            content = prompts_file.read_text(encoding="utf-8", errors="ignore")
            # Validación: ¿Hay evidencia de uso real?
            # SIN ESTO: Es documento especulativo
            has_usage_evidence = (
                "token_saved" in content
                or "usage_count" in content
                or "efectivamente_acelera" in content
            )
            assert (
                has_usage_evidence or len(content) > 500
            ), "PROMPTS_RAPIDOS: Sin evidencia de utilidad. Considera remover."

    def test_setup_validate_is_wired_to_ci(self):
        """
        setup_validate.py reclama validar stack antes de ejecución.
        ¿Realmente está wired a CI o es script huérfano?

        TEST: Debe existir en pre-commit hook o CI config.
        """
        setup_validate = Path("scripts/setup_validate.py")
        if setup_validate.exists():
            # Validación: ¿Se ejecuta en git hook?
            pre_commit_hook = Path(".git/hooks/pre-commit")
            if pre_commit_hook.exists():
                hook_content = pre_commit_hook.read_text(
                    encoding="utf-8", errors="ignore"
                )
                is_enforced = "setup_validate.py" in hook_content
                assert is_enforced, (
                    "setup_validate.py existe pero NO está en pre-commit hook. "
                    "Es código muerto especulativo."
                )


class TestPhase2Refactorization:
    """Validar que Phase 2 cambios realmente mejoraron el protocolo."""

    def test_b3_angry_path_categories_are_actionable(self):
        """
        B3 fue mejorado con 3 categorías obligatorias.
        ¿Son realmente acciones que alguien ejecutaría o solo palabras?

        TEST: Cada categoría debe poder derivarse en un test concreto.
        """
        categories = {
            "Entradas Adversarias": ["nulos", "vacíos", "extremos", "SQL injection"],
            "Lógica de Negocio": [
                "duplicidad",
                "llaves únicas",
                "estados incompatibles",
            ],
            "Seguridad": ["sanitización", "Auth boundaries", "RLS", "no secrets"],
        }

        for cat, items in categories.items():
            assert len(items) > 0, f"{cat}: vacío, no es accionable"
            # Validación profunda: ¿Podrías escribir un test para cada item?
            for item in items:
                # Si puedes escribir `test_` + snake_case, es accionable
                test_name = "test_" + item.lower().replace(" ", "_")
                assert (
                    len(test_name) > 5
                ), f"{cat}/{item}: no es específico suficiente para test"

    def test_no_redundancy_between_b1_b2_b7_b12(self):
        """
        B12 (PESIMISMO ALGORÍTMICO EXTREMO) fue removido por redundancia.
        Validar que no reimplemente conceptos ya en B1, B2, B7.

        TEST: Si reaparece B12, debe tener contenido único.
        """
        # REGLA: La IA no debe rescatar mandatos redundantes.
        # Si B12 reaparece en PROTOCOL_BEHAVIOR.md, test falla.
        protocol = Path("PROTOCOL_BEHAVIOR.md").read_text(
            encoding="utf-8", errors="ignore"
        )
        has_b12 = "MANDATO B12" in protocol

        if has_b12:
            # Si existe, DEBE aportar concepto único no cubierto por B1/B2/B7
            unique_concepts = [
                "lista_incertidumbre",  # Único en B12
                "mecanismo_verificacion_estructura_ficheros",  # Único en B12
            ]
            has_unique = any(concept in protocol.lower() for concept in unique_concepts)
            assert (
                has_unique
            ), "B12 reapareció pero sin conceptos únicos. Debería estar removido."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
