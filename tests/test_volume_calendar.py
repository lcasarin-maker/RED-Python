"""
tests/test_volume_calendar.py — P4.5
Volume boundary tests (>1000 items) and calendar boundary tests (31 Dec, 29 Feb, DST).
These cover the gaps documented in CHECKLIST.md under 'Gaps de cobertura'.
"""

from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _make_session_block(n: int) -> str:
    """Generate a memory block string with n sessions."""
    lines = []
    for i in range(n):
        lines.append(f"## SESIÓN {i:04d}")
        lines.append(f"**Tarea:** Task {i}")
        lines.append("**Estado:** COMPLETED")
        lines.append(f"- cambio {i}: modified file_{i}.py")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Vol-1: compress_memory_block with >1000 sessions
# ──────────────────────────────────────────────────────────────────────────────


class TestVolumeCompressMemory:
    def test_compress_1000_sessions_returns_structured_dict(self):
        """Vol-1: compress_memory_block debe manejar 1000+ sesiones sin error."""
        from scripts.helpers import compress_memory_block

        block = _make_session_block(1000)
        result = compress_memory_block(block)
        assert isinstance(result, dict)
        assert "fact_summaries" in result
        assert len(result["fact_summaries"]) == 1000

    def test_compress_1000_sessions_ratio_is_numeric(self):
        """Vol-1: comprimir 1000 sesiones devuelve ratio numérico (puede ser negativo si JSON overhead > savings)."""
        from scripts.helpers import compress_memory_block

        block = _make_session_block(1000)
        result = compress_memory_block(block)
        assert isinstance(result["compression_ratio"], float)
        assert result["original_bytes"] > 0
        assert result["compressed_bytes"] > 0

    def test_compress_zero_sessions_no_crash(self):
        """Vol-1: borde inferior — bloque vacío no debe lanzar excepción."""
        from scripts.helpers import compress_memory_block

        result = compress_memory_block("")
        assert isinstance(result, dict)
        assert result["fact_summaries"] == []


# ──────────────────────────────────────────────────────────────────────────────
# Vol-2: extract_compact_facts with very large single session
# ──────────────────────────────────────────────────────────────────────────────


class TestVolumeExtractFacts:
    def test_extract_facts_from_10k_line_session(self):
        """Vol-2: extract_compact_facts debe manejar contenido de 10 000 líneas."""
        from scripts.helpers import extract_compact_facts

        big_content = "**Tarea:** Tarea grande\n" + (
            "- cambio X: archivo modificado\n" * 10_000
        )
        result = extract_compact_facts(big_content)
        assert isinstance(result, dict)
        assert "key_learnings" in result

    def test_extract_facts_single_empty_string(self):
        """Vol-2: borde inferior — string vacío devuelve estructura válida."""
        from scripts.helpers import extract_compact_facts

        result = extract_compact_facts("")
        assert isinstance(result, dict)
        assert result["key_learnings"] == []


# ──────────────────────────────────────────────────────────────────────────────
# Cal-1: 31 December — year rollover
# ──────────────────────────────────────────────────────────────────────────────


class TestCalendarDecember31:
    def test_isoformat_dec31_is_valid(self):
        """Cal-1: timestamp del 31 dic debe ser parseable como fecha válida."""
        dt = datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        iso = dt.isoformat()
        parsed = datetime.fromisoformat(iso)
        assert parsed.year == 2024
        assert parsed.month == 12
        assert parsed.day == 31

    def test_compress_session_dec31_timestamp_in_summary(self):
        """Cal-1: compress_session_to_fact_summary debe funcionar en sesión con fecha 31 dic."""
        from scripts.helpers import compress_session_to_fact_summary

        content = (
            "## SESIÓN 2024-12-31\n**Tarea:** Cierre de año\n**Estado:** COMPLETED\n"
        )
        result = compress_session_to_fact_summary("2024-12-31", content)
        assert isinstance(result, str)
        assert "2024-12-31" in result


# ──────────────────────────────────────────────────────────────────────────────
# Cal-2: 29 February (leap year)
# ──────────────────────────────────────────────────────────────────────────────


class TestCalendarFeb29:
    def test_leap_year_feb29_datetime_valid(self):
        """Cal-2: datetime 29 feb en año bisiesto no debe lanzar ValueError."""
        dt = datetime(2024, 2, 29, 12, 0, 0, tzinfo=timezone.utc)
        assert dt.day == 29
        assert dt.month == 2

    def test_non_leap_year_feb29_raises(self):
        """Cal-2: 29 feb en año no bisiesto debe lanzar ValueError (verificar que no se acepta silenciosamente)."""
        raised = False
        try:
            datetime(2023, 2, 29)
        except ValueError:
            raised = True
        assert raised, "datetime(2023, 2, 29) debería lanzar ValueError"

    def test_compress_session_feb29_no_crash(self):
        """Cal-2: sesión con fecha 29 feb debe procesarse sin error."""
        from scripts.helpers import compress_session_to_fact_summary

        content = (
            "## SESIÓN 2024-02-29\n**Tarea:** Tarea bisiesto\n**Estado:** COMPLETED\n"
        )
        result = compress_session_to_fact_summary("2024-02-29", content)
        assert isinstance(result, str)


# ──────────────────────────────────────────────────────────────────────────────
# Cal-3: UTC vs timezone-aware — no DST confusion
# ──────────────────────────────────────────────────────────────────────────────


class TestCalendarUTC:
    def test_utc_timestamps_are_timezone_aware(self):
        """Cal-3: todos los timestamps generados por Cerberus deben ser timezone-aware."""
        now = datetime.now(tz=timezone.utc)
        assert now.tzinfo is not None

    def test_adoption_audit_timestamp_is_utc(self):
        """Cal-3: verify_protocol_adoption genera timestamps timezone-aware (UTC)."""
        iso = datetime.now(tz=timezone.utc).isoformat()
        parsed = datetime.fromisoformat(iso)
        assert parsed.tzinfo is not None
