#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki & Knowledge Linter (Karpathy-style)
- Validates internal Obsidian links [[Note Name]] and relative markdown links.
- Identifies orphaned notes (notes with no incoming links, excluding index pages).
- Validates the Golden Standard YAML files for duplicate IDs, format compliance, and schema completeness.
"""

import sys
import re
import yaml
from pathlib import Path
import logging
import argparse

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Resolve directories dynamically
CORE_DIR = Path(__file__).resolve().parents[1]
GS_DIR = CORE_DIR.parent / "VibeCoding_GoldenStandard"
WIKI_DIR = GS_DIR / "Wiki"

# ID Regex patterns
ID_PATTERNS = {
    "coding_vices": re.compile(r"^VC-\d{3}$"),
    "testing_vices": re.compile(r"^VT-\d{3}$"),
    "tokenomics": re.compile(r"^TK-[F\d]\d{2}$"),
    "project_insights": re.compile(r"^PI-\d{3}$")
}

# Link patterns
OBSIDIAN_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

def load_yaml_safe(path):
    """Safely loads a YAML file."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error reading YAML {path}: {e}")
        return None

def _extract_items_from_yaml(data, domain):
    """Extracts the list of items from YAML data dynamically."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ["vices", "insights", "items", domain]:
            if key in data and isinstance(data[key], list):
                return data[key]
        for val in data.values():
            if isinstance(val, list):
                return val
    return []

def _validate_single_item(item, idx, filename, pattern, all_ids):
    """Validates a single item's ID, format, duplicates, and required fields."""
    errors = []
    if not isinstance(item, dict):
        errors.append(f"YAML {filename} item at index {idx} is not a dictionary.")
        return errors

    item_id = item.get("id")
    if not item_id:
        errors.append(f"YAML {filename} item at index {idx} is missing 'id'.")
        return errors

    # Format check
    if pattern and not pattern.match(item_id):
        errors.append(f"YAML {filename} has invalid ID format: '{item_id}' (expected pattern like {pattern.pattern})")

    # Duplicate check
    if item_id in all_ids:
        errors.append(f"Duplicate ID found across Golden Standard: '{item_id}'")
    all_ids.add(item_id)

    # Required fields check
    for field in ["title", "symptom", "cause", "solution"]:
        if not item.get(field):
            errors.append(f"Item '{item_id}' in {filename} is missing required field: '{field}'")
            
    return errors

def _validate_project_insights_yaml(data, y_file, pattern, all_ids):
    """Helper to validate project insights YAML structure."""
    errors = []
    raw = data.get("project_insights", {})
    if not isinstance(raw, dict):
        errors.append(f"YAML {y_file.name} does not contain a dictionary under 'project_insights' key.")
        return errors
    for key, val in raw.items():
        insight_id = str(key)
        if pattern and not pattern.match(insight_id):
            errors.append(f"YAML {y_file.name} has invalid ID format: '{insight_id}' (expected pattern like {pattern.pattern})")
        if insight_id in all_ids:
            errors.append(f"Duplicate ID found across Golden Standard: '{insight_id}'")
        all_ids.add(insight_id)
        if not val or not isinstance(val, str):
            errors.append(f"Insight '{insight_id}' in {y_file.name} must be a non-empty string.")
    return errors


def validate_yaml_integrity():
    """Validates duplicate IDs, schema compliance, and format in YAML files."""
    errors = []
    if not GS_DIR.exists():
        logging.warning("Golden Standard directory not found. Skipping YAML validations.")
        return errors

    all_ids = set()
    for y_file in GS_DIR.glob("golden_standard_*.yaml"):
        domain = y_file.stem.replace("golden_standard_", "")
        pattern = ID_PATTERNS.get(domain)
        
        data = load_yaml_safe(y_file)
        if not data:
            continue
            
        if domain == "project_insights":
            errors.extend(_validate_project_insights_yaml(data, y_file, pattern, all_ids))
            continue

        items = _extract_items_from_yaml(data, domain)
        if not items:
            errors.append(f"YAML {y_file.name} does not contain an parseable list of items.")
            continue

        for idx, item in enumerate(items):
            errors.extend(_validate_single_item(item, idx, y_file.name, pattern, all_ids))

    return errors


def _check_obsidian_links(content, md_file, source_stem_lower, note_map, incoming_links):
    """Validates Obsidian [[Links]] and updates incoming links."""
    errors = []
    for match in OBSIDIAN_LINK_RE.finditer(content):
        target_name = match.group(1).strip()
        target_no_anchor = target_name.split("#")[0]
        if not target_no_anchor:
            continue
        target_stem = Path(target_no_anchor).stem.lower()
        
        # Check if target exists in Wiki (note_map) or in GS_DIR (external markdown file)
        exists_in_wiki = target_stem in note_map
        exists_in_gs = False
        if not exists_in_wiki:
            path_candidates = [
                GS_DIR / f"{target_no_anchor}.md",
                GS_DIR / target_no_anchor
            ]
            if any(p.exists() for p in path_candidates):
                exists_in_gs = True
                
        if not exists_in_wiki and not exists_in_gs:
            errors.append(f"Broken Obsidian link in '{md_file.name}': [[{target_name}]] does not exist.")
        elif exists_in_wiki and target_stem != source_stem_lower:
            incoming_links[target_stem].add(source_stem_lower)
    return errors


def _check_markdown_links(content, md_file):
    """Validates standard Markdown [Links](path)."""
    errors = []
    for match in MARKDOWN_LINK_RE.finditer(content):
        path_str = match.group(1).strip()
        if path_str.startswith(("http://", "https://", "file://", "mailto:", "#")):
            continue
        
        path_no_anchor = path_str.split("#")[0]
        if not path_no_anchor:
            continue
            
        link_path = md_file.parent / path_no_anchor
        if not link_path.exists():
            # Check relative to GS_DIR as well
            if (GS_DIR / path_no_anchor).exists():
                continue
            errors.append(f"Broken markdown link in '{md_file.name}': '{path_str}' does not exist.")
    return errors


def _process_single_md_file(md_file, note_map, incoming_links):
    """Parses a single markdown file, finds links, and populates incoming_links."""
    content = md_file.read_text(encoding="utf-8", errors="ignore")
    source_stem_lower = md_file.stem.lower()

    obsidian_errors = _check_obsidian_links(content, md_file, source_stem_lower, note_map, incoming_links)
    markdown_errors = _check_markdown_links(content, md_file)

    return obsidian_errors + markdown_errors

def _find_orphans(incoming_links, note_map, indexes):
    """Identifies orphaned files (0 incoming links, not index pages)."""
    errors = []
    orphans = []
    for note_lower, sources in incoming_links.items():
        if note_lower in indexes:
            continue
        if not sources:
            actual_file = note_map[note_lower]
            orphans.append(actual_file.name)
            errors.append(f"Orphaned note found: '{actual_file.name}' has no incoming links.")
    return errors, orphans

def check_wiki_links():
    """Checks for broken links and orphaned notes in the Obsidian Wiki."""
    errors = []
    if not WIKI_DIR.exists():
        logging.warning("Obsidian Wiki directory not found. Skipping Wiki validations.")
        return errors, []

    all_md_files = list(WIKI_DIR.rglob("*.md"))
    note_map = {f.stem.lower(): f for f in all_md_files}
    incoming_links = {f.stem.lower(): set() for f in all_md_files}
    indexes = {
        "home", "index", "graph",
        "vices_index", "project_insights_index",
        "tokenomics_index", "tokenomics_map",
        "coding_vices", "testing_vices", "tokenomics", "project_insights"
    }

    for md_file in all_md_files:
        errors.extend(_process_single_md_file(md_file, note_map, incoming_links))

    orphan_errors, orphans = _find_orphans(incoming_links, note_map, indexes)
    errors.extend(orphan_errors)

    return errors, orphans

def main():
    parser = argparse.ArgumentParser(description="Wiki & Knowledge Linter (Karpathy-style)")
    parser.add_argument("--wiki-dir", type=str, help="Custom path to the Wiki/Knowledge directory to lint")
    parser.add_argument("--skip-yaml-validation", action="store_true", help="Bypass Golden Standard YAML validation")
    args = parser.parse_args()

    global WIKI_DIR, GS_DIR
    if args.wiki_dir:
        WIKI_DIR = Path(args.wiki_dir).resolve()
        GS_DIR = WIKI_DIR.parent

    print("=" * 70)
    print("📖 WIKI & KNOWLEDGE LINTER")
    print(f"Directory: {WIKI_DIR}")
    print("=" * 70)
    
    yaml_errors = []
    if not args.skip_yaml_validation:
        yaml_errors = validate_yaml_integrity()
        
    wiki_errors, orphans = check_wiki_links()
    all_errors = yaml_errors + wiki_errors
    
    if all_errors:
        print(f"\n❌ Linter falló con {len(all_errors)} errores:")
        for err in all_errors:
            print(f"  • {err}")
        return 1
        
    print("\n✅ Linter aprobado. Cero links rotos, cero huérfanos y schemas válidos.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
