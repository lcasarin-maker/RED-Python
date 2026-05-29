# tools/generate_rules_docs.py
"""
Genera documentación Markdown para todas las reglas definidas en ``cerberus/rules/``.

Ejecutar:
    python -m tools.generate_rules_docs
"""

import pathlib
import yaml

RULES_DIR = pathlib.Path(__file__).parents[2] / "cerberus" / "rules"
OUTPUT_MD = pathlib.Path(__file__).parents[2] / "docs" / "rules.md"

def load_rules():
    rules = []
    for yaml_path in RULES_DIR.glob("*.yaml"):
        with yaml_path.open() as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                rules.extend(data)
            else:
                rules.append(data)
    return rules

def main():
    rules = load_rules()
    lines = ["# Regla de documentación", ""]
    for rule in rules:
        lines.append(f"## {rule.get('id', 'UNKNOWN')}")
        lines.append(f"- **Descripción**: {rule.get('description', '')}")
        lines.append(f"- **Severidad**: {rule.get('severity', 'medium')}")
        lines.append(f"- **Enforcement**: {rule.get('enforcement', '')}\n")
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"[generate_rules_docs] Documentación escrita en {OUTPUT_MD}")

if __name__ == "__main__":
    main()
