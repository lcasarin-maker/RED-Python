"""
Utility to generate scaffold unit-test files for each rule defined in ``protocol_engine/rules/``.

Running this script creates ``tests/rules/test_<rule_id>.py`` with a minimal pytest
skeleton that registers the rule ID in ``test_rule_ids`` (used by the rule engine).

Usage:
    python -m scripts.generate_rule_test_scaffold
"""

import pathlib

import yaml

RULES_DIR = pathlib.Path(__file__).parents[1] / "protocol_engine" / "rules"
TESTS_DIR = pathlib.Path(__file__).parents[1] / "tests" / "rules"


def load_rule_ids():
    ids = []
    for yaml_path in RULES_DIR.glob("*.yaml"):
        with yaml_path.open() as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                ids.extend([r.get("id") for r in data if r.get("id")])
            elif isinstance(data, dict) and data.get("id"):
                ids.append(data["id"])
    return ids


def create_placeholder(rule_id: str):
    filename = TESTS_DIR / f"test_{rule_id.lower().replace('-', '_')}.py"
    if filename.exists():
        return  # don't overwrite existing tests
    content = f"""# tests/rules/test_{rule_id.lower().replace('-', '_')}.py\n\nScaffold test for rule {rule_id}.\n\nThe test registers the rule ID in ``test_rule_ids`` so that the ``R-TEST-COVERAGE``\nrule can verify the presence of a unit test. Replace this scaffold with real\nassertions that exercise the rule logic.\n\nimport pytest\n\n\n@pytest.fixture(scope=\"module\")\ndef test_rule_ids():\n    return [\"{rule_id}\"]\n\n\ndef test_placeholder():\n    pytest.fail(\"Scaffold only: implement real assertions for {rule_id}\")\n"""
    filename.write_text(content, encoding="utf-8")
    print(f"[generate_rule_test_scaffold] Created scaffold {filename.name}")


def main():
    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    for rule_id in load_rule_ids():
        create_placeholder(rule_id)


if __name__ == "__main__":
    main()
