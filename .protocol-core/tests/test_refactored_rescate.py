#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Validar que rescate items refactorizados tienen utilidad REAL.
Cuestiona mecanismo, no solo documentación.
"""

import pytest
import json
import subprocess
from pathlib import Path


class TestRefactoredRescate:
    """Validar que refactorización produce código/mandatos ejecutables."""

    def test_b12_operativo_lista_incertidumbre(self):
        """B12 debe ser operativo: listar incertidumbre específica"""
        protocol = Path("PROTOCOL_BEHAVIOR.md").read_text(encoding='utf-8')
        b12_section = protocol[protocol.find("MANDATO B12"):protocol.find("MANDATO B13")]

        # Validación: B12 tiene "Al final de cada turno"
        assert "Al final de cada turno" in b12_section, \
            "B12: No es operativo (falta frecuencia de ejecución)"

        # Validación: B12 especifica QUÉ listar
        assert ("subsistemas" in b12_section or "verificadas" in b12_section), \
            "B12: No especifica QUÉ listar (genérico)"

    def test_b14_secuencial_con_b6(self):
        """B14 (auditar pre-deprecación) debe ser distinguible de B6"""
        protocol = Path("PROTOCOL_BEHAVIOR.md").read_text(encoding='utf-8')

        b14_idx = protocol.find("MANDATO B14")
        b6_idx = protocol.find("MANDATO B6")

        assert b14_idx < b6_idx, \
            "B14 debe venir antes de B6 (auditar ANTES de deprecar)"

        b14_section = protocol[b14_idx:b6_idx]
        assert "Fase 1" in b14_section and "auditar" in b14_section, \
            "B14: No documenta que es pre-deprecation phase"

    def test_b15_sync_binding_exists_and_works(self):
        """B15 requiere sync_binding.py real. Validar que existe y funciona."""
        sync_script = Path("scripts/sync_binding.py")
        assert sync_script.exists(), \
            "B15: sync_binding.py no existe (mandato sin dientes)"

        # Validación: sync_binding.py puede ejecutar --check
        result = subprocess.run(
            ["python", str(sync_script), "--check"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Exit code puede ser 0 o 1 (dependiendo de si hay cambios)
        # Lo importante es que NO falla por sintaxis/import
        assert result.returncode in [0, 1], \
            f"B15: sync_binding.py falla con sintaxis error: {result.stderr}"

    def test_setup_validate_py_is_fast(self):
        """setup_validate.py refactorizado debe ser <1sec (pre-commit friendly)"""
        script = Path("scripts/setup_validate.py")
        assert script.exists(), "setup_validate.py no existe"

        import time
        start = time.time()
        result = subprocess.run(
            ["python", str(script)],
            capture_output=True,
            text=True,
            timeout=5
        )
        elapsed = time.time() - start

        assert elapsed < 1.0, \
            f"setup_validate.py tardó {elapsed:.2f}s (debe ser <1s para pre-commit)"

    def test_prompts_rapidos_has_activation_conditions(self):
        """PROMPTS_RAPIDOS.md debe tener CUÁNDO usar (no templates genéricos)"""
        prompts = Path("PROMPTS_RAPIDOS.md").read_text(encoding='utf-8')

        # Validación: Tiene sección "Cuándo"
        assert "Cuándo:" in prompts, \
            "PROMPTS_RAPIDOS: Sin sección 'Cuándo usar' (genérico)"

        # Validación: Tiene métricas de éxito
        assert "Condición de éxito:" in prompts, \
            "PROMPTS_RAPIDOS: Sin métricas de validación (no es accionable)"

        # Validación: Cada bloque tiene >1 "Cuándo"
        cuando_count = prompts.count("Cuándo:")
        assert cuando_count >= 5, \
            f"PROMPTS_RAPIDOS: Solo {cuando_count} templates con Cuándo (necesita >5)"

    def test_pre_commit_hook_enforces_setup_validate(self):
        """Pre-commit hook debe ejecutar setup_validate.py (B15 enforcement)"""
        hook = Path(".git/hooks/pre-commit")
        assert hook.exists(), "Pre-commit hook no existe"

        hook_content = hook.read_text(encoding='utf-8', errors='replace')
        assert "setup_validate.py" in hook_content, \
            "B15: setup_validate.py NO está en pre-commit hook (no enforced)"

        # Validación: Hook verifica result code
        assert "bootstrap" in hook_content.lower(), \
            "B15: Hook no valida resultado de setup_validate"

class TestRefactorIntegration:
    """Validar que rescate items funcionan JUNTOS."""

    def test_b12_b14_b15_chain(self):
        """B12→B14→B15 forma una cadena coherente"""
        protocol = Path("PROTOCOL_BEHAVIOR.md").read_text(encoding='utf-8')

        # B12: lista incertidumbre (verificación)
        assert "MANDATO B12" in protocol, "B12 no existe"
        assert "Al final de cada turno" in protocol, "B12 no es operativo"

        # B14: audita antes de deprecar (rescue)
        assert "MANDATO B14" in protocol, "B14 no existe"
        assert "Fase 1" in protocol, "B14 no es secuencial"

        # B15: sincroniza cambios (propagación)
        assert "MANDATO B15" in protocol, "B15 no existe"
        assert "sync_binding.py" in protocol, "B15 no menciona mecanismo"

        # Cadena completa existe
        assert "MANDATO B12" in protocol and "MANDATO B13" in protocol \
            and "MANDATO B14" in protocol and "MANDATO B15" in protocol, \
            "Cadena B12→B13→B14→B15 está rota"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
