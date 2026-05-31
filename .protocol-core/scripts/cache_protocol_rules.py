#!/usr/bin/env python3
"""
cache_protocol_rules.py v2.0 — FASE 5: Token-Saving Strategies
Generates .claude/cache/protocol_rules.json for fast mandate loading by agents.
Parses mandates from PROTOCOL_SYSTEM.md and PROTOCOL_BEHAVIOR.md.
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
_logger = logging.getLogger("cache_protocol_rules")

_DEFAULT_CACHE_FILE = Path(".claude/cache/protocol_rules.json")
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MANDATE_RE = re.compile(r"##\s+.*?MANDATO\s+((?:S|B)\d+):\s*([^\n(#]+)", re.IGNORECASE)


def build_cache(rules_dir: Path, cache_file: Path) -> bool:
    """Build mandate cache JSON from PROTOCOL_SYSTEM.md and PROTOCOL_BEHAVIOR.md.

    Args:
        rules_dir: Ignored (legacy REGLAS/ parameter kept for CLI compatibility).
        cache_file: Output path for the JSON cache.

    Returns:
        True on success, False if protocol files not found or no mandates extracted.
    """
    sources = {
        "system": _PROJECT_ROOT / "PROTOCOL_SYSTEM.md",
        "behavior": _PROJECT_ROOT / "PROTOCOL_BEHAVIOR.md",
    }
    missing = [str(p) for p in sources.values() if not p.exists()]
    if missing:
        _logger.error("build_cache: protocol files not found: %s", missing)
        return False

    mandates: list[dict] = []
    seen_codes: set[str] = set()
    for source_name, path in sources.items():
        content = path.read_text(encoding="utf-8", errors="ignore")
        for match in _MANDATE_RE.finditer(content):
            code = match.group(1).upper()
            if code in seen_codes:
                continue
            seen_codes.add(code)
            mandates.append({
                "code": code,
                "title": match.group(2).strip().rstrip(" —"),
                "tier": "SYSTEM" if code.startswith("S") else "BEHAVIOR",
                "source": source_name,
            })

    if not mandates:
        _logger.error("build_cache: no mandates extracted from protocol files")
        return False

    mandates.sort(key=lambda m: (m["tier"], int(re.sub(r"\D", "", m["code"]) or 0)))
    cache: dict = {
        "version": "2.0",
        "total_mandates": len(mandates),
        "mandates": mandates,
        "by_tier": {
            "SYSTEM": [m for m in mandates if m["tier"] == "SYSTEM"],
            "BEHAVIOR": [m for m in mandates if m["tier"] == "BEHAVIOR"],
        },
    }
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache, separators=(",", ":")), encoding="utf-8")
    _logger.info("build_cache: cached %d mandates → %s", len(mandates), cache_file)
    return True


def load_cache(cache_file: Path) -> dict | None:
    """Load cached rules JSON. Returns None if missing or invalid."""
    if not cache_file.exists():
        _logger.warning("load_cache: cache not found at %s", cache_file)
        return None
    try:
        return json.loads(cache_file.read_text(encoding="utf-8"))
    except Exception as e:
        _logger.error("load_cache: failed to load %s: %s", cache_file, e)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Cache protocol rules as minified JSON")
    parser.add_argument("--build", action="store_true", help="Build cache from REGLAS/")
    parser.add_argument("--load", action="store_true", help="Load and verify existing cache")
    parser.add_argument("--rules-dir", type=Path, default=Path("REGLAS"))
    parser.add_argument("--cache-file", type=Path, default=_DEFAULT_CACHE_FILE)
    args = parser.parse_args()

    if args.load:
        cache = load_cache(args.cache_file)
        if cache:
            _logger.info("Cache loaded: %s mandates", cache.get("total_mandates", "?"))
            return 0
        return 1

    ok = build_cache(args.rules_dir, args.cache_file)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
