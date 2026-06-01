"""Collect rule definitions from markdown sources and generate unified YAML files.

The collector scans a predefined list of markdown files (agents, gems, plugins) for
rule headings of the form ``### <ID> – <Description>`` and optional `````yaml```
code blocks that contain a ``check`` expression.  For each unique rule ID it
produces a YAML file under ``cerberus/rules/<id>.yaml``.

Duplicate rule IDs are merged – the first occurrence wins and later duplicates
are ignored (deduplication).
"""

import logging
import pathlib
import re
import yaml
from typing import Dict, List

# ---------------------------------------------------------------------------
# Configuration – markdown files to scan (add more paths if needed)
# ---------------------------------------------------------------------------
MARKDOWN_PATHS = [
    pathlib.Path("AGENT.md"),
    pathlib.Path("GEMINI.md"),
    pathlib.Path("AGENT_SAFETY.md"),
]

RULES_DIR = pathlib.Path(__file__).parent / "rules"
RULES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helper: parse a single markdown file and extract rule definitions
# ---------------------------------------------------------------------------
RULE_HEADER_RE = re.compile(r"^###\s+(?P<id>R-[A-Z0-9_-]+)\s*[–-]\s*(?P<desc>.+)$")

def extract_rules_from_md(md_path: pathlib.Path) -> List[Dict]:
    rules = []
    if not md_path.exists():
        return rules
    with md_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = RULE_HEADER_RE.match(line)
        if m:
            rule_id = m.group("id").strip()
            description = m.group("desc").strip()
            # Look ahead for a yaml code block containing a `check` field
            check_expr = "True"  # default safe check
            # advance to possible code block
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```yaml"):
                j += 1
            if j < len(lines) and lines[j].strip().startswith("```yaml"):
                # capture until closing backticks
                yaml_lines = []
                j += 1
                while j < len(lines) and not lines[j].strip().startswith("```"):
                    yaml_lines.append(lines[j])
                    j += 1
                try:
                    yaml_content = yaml.safe_load("".join(yaml_lines))
                    if isinstance(yaml_content, dict) and "check" in yaml_content:
                        check_expr = yaml_content["check"]
                except yaml.YAMLError as e:
                    logging.debug("rule_collector: bloque YAML invalido ignorado: %s", e)
                i = j  # skip processed block
            # Build rule dict
            rules.append({
                "id": rule_id,
                "description": description,
                "check": check_expr,
                "enforcement": "error_if_true",
            })
        i += 1
    return rules

# ---------------------------------------------------------------------------
# Main collector logic – deduplicate and write yaml files
# ---------------------------------------------------------------------------
def main():
    seen_ids = set()
    for md_path in MARKDOWN_PATHS:
        for rule in extract_rules_from_md(md_path):
            rid = rule["id"]
            if rid in seen_ids:
                # Duplicate – skip (first definition wins)
                continue
            seen_ids.add(rid)
            yaml_path = RULES_DIR / f"{rid.lower()}.yaml"
            with yaml_path.open("w", encoding="utf-8") as out:
                yaml.safe_dump([rule], out, sort_keys=False)
    print(f"[rule_collector] Collected {len(seen_ids)} unique rules into {RULES_DIR}")

if __name__ == "__main__":
    main()
