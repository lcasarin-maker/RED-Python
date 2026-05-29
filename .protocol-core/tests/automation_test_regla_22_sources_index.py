"""
TEST: test_regla_22_sources_index.py
Parte de la suite de validacion de Coder Cerberus V0.1.
"""

import re
from pathlib import Path

def test_sources_of_truth_exists():
    """REGLA #22: SOURCES_OF_TRUTH.md must exist"""
    sources_path = Path("SOURCES_OF_TRUTH.md")

    assert sources_path.exists(), "SOURCES_OF_TRUTH.md not found"
    assert sources_path.stat().st_size > 100, "SOURCES_OF_TRUTH.md is empty or too small"

    print("✓ REGLA #22 check 1: SOURCES_OF_TRUTH.md exists")


def test_sources_table_format():
    """REGLA #22: SOURCES_OF_TRUTH must have valid table format"""
    sources_path = Path("SOURCES_OF_TRUTH.md")

    with open(sources_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for table header
    assert "| Concepto | Archivo Autorizado | Tipo |" in content, (
        "SOURCES_OF_TRUTH missing table header"
    )

    # Extract table rows (skip header separator)
    table_pattern = r"\| [^\|]+ \| [^\|]+ \| (SPEC|POLICY) \|"
    matches = re.findall(table_pattern, content)

    assert len(matches) >= 20, f"Table has too few entries ({len(matches)}, need ≥20)"

    print(f"✓ REGLA #22 check 2: Table format valid ({len(matches)} entries)")


def test_sources_spec_policy_valid():
    """REGLA #22: Every entry must be SPEC or POLICY"""
    sources_path = Path("SOURCES_OF_TRUTH.md")

    with open(sources_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract all table rows
    table_pattern = r"\| ([^\|]+) \| ([^\|]+) \| ([A-Z]+) \|"
    matches = re.findall(table_pattern, content)

    invalid_types = []
    for concepto, archivo, tipo in matches:
        if tipo not in ["SPEC", "POLICY"]:
            invalid_types.append((concepto.strip(), tipo))

    assert not invalid_types, f"Invalid types found: {invalid_types}"

    print("✓ REGLA #22 check 3: All entries have valid SPEC/POLICY type")


def test_sources_references_all_reglas():
    """REGLA #22: All REGLAS #0-22 must be referenced"""
    sources_path = Path("SOURCES_OF_TRUTH.md")

    with open(sources_path, "r", encoding="utf-8") as f:
        content = f.read()

    missing_reglas = []
    for i in range(0, 23):
        regla_ref = f"REGLA #{i}"
        # Allow variations: "REGLA #13", "REGLAS #0-20", etc.
        if not re.search(rf"REGLA\s*#\s*{i}(?:\D|$)", content):
            missing_reglas.append(i)

    assert not missing_reglas, (
        f"Missing REGLA references: {missing_reglas}. All REGLAS #0-22 must be in index."
    )

    print("✓ REGLA #22 check 4: All REGLAS #0-22 referenced")


def test_sources_matches_regla_files():
    """REGLA #22: Index should match actual REGLA files"""
    protocolo_dir = Path(".")

    # Find all REGLA files
    regla_files = list(protocolo_dir.glob("N?_REGLA_*.md"))
    regla_numbers = [
        int(re.search(r"REGLA_(\d+)", f.name).group(1))
        for f in regla_files
        if re.search(r"REGLA_(\d+)", f.name)
    ]

    sources_path = Path("SOURCES_OF_TRUTH.md")
    with open(sources_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check each REGLA file is mentioned
    missing_in_index = []
    for num in sorted(set(regla_numbers)):
        if num > 10:  # Only check REGLA #11+ (multi-digit)
            pattern = f"REGLA.*#{num}(?:,|\\D|$)"
        else:
            pattern = f"REGLA.*#{num}(?:,|\\D|$)"

        if not re.search(pattern, content):
            missing_in_index.append(num)

    assert not missing_in_index, (
        f"REGLAS in SOURCES_OF_TRUTH missing references: {missing_in_index}"
    )

    print(f"✓ REGLA #22 check 5: Index references {len(regla_numbers)} actual REGLA files")


def test_sources_governance_section():
    """REGLA #22: SOURCES_OF_TRUTH must explain SPEC vs POLICY governance"""
    sources_path = Path("SOURCES_OF_TRUTH.md")

    with open(sources_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "## SPEC vs POLICY" in content, "Missing SPEC vs POLICY explanation"
    assert "### SPEC" in content, "Missing SPEC section"
    assert "### POLICY" in content, "Missing POLICY section"
    assert "GOVERNANCE" in content.upper(), "Missing governance section"

    print("✓ REGLA #22 check 6: Governance section present")


if __name__ == "__main__":
    test_sources_of_truth_exists()
    test_sources_table_format()
    test_sources_spec_policy_valid()
    test_sources_references_all_reglas()
    test_sources_matches_regla_files()
    test_sources_governance_section()
    print("\n✅ All REGLA #22 tests PASSED")
