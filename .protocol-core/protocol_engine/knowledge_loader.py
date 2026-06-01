"""Load and normalize Golden Standard knowledge for Cerberus."""

import json
import pathlib
from typing import Iterable

import yaml

_GOLDEN_MANIFEST_PATH = pathlib.Path(__file__).parent.parent / "Golden_Standard" / "golden_standard.yaml"
_SATELLITE_LEARNINGS_PATH = pathlib.Path(__file__).parent.parent / ".protocol" / "metadata" / "satellite_learnings.json"


def _load_yaml_mapping(path: pathlib.Path) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"Golden Standard file not found at {path}")
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"Golden Standard file at {path} must contain a mapping")
    return data


def load_golden_standard_manifest() -> dict[str, object]:
    """Load the Golden Standard manifest.

    The manifest may be either the legacy unified mapping or the split index that
    enumerates catalog fragments.
    """
    return _load_yaml_mapping(_GOLDEN_MANIFEST_PATH)


def get_golden_catalog_paths() -> dict[str, pathlib.Path]:
    """Return the resolved catalog file paths keyed by logical catalog name."""
    manifest = load_golden_standard_manifest()
    catalogs = manifest.get("catalogs")
    if not isinstance(catalogs, dict) or not catalogs:
        return {"legacy": _GOLDEN_MANIFEST_PATH}
    resolved: dict[str, pathlib.Path] = {}
    for catalog_name, relative_path in catalogs.items():
        resolved[str(catalog_name)] = (_GOLDEN_MANIFEST_PATH.parent / str(relative_path)).resolve()
    return resolved


def load_golden_standard_catalogs() -> dict[str, dict[str, object]]:
    """Load every catalog referenced by the Golden Standard manifest."""
    manifest = load_golden_standard_manifest()
    catalogs = manifest.get("catalogs")
    if not isinstance(catalogs, dict) or not catalogs:
        return {"legacy": manifest}

    loaded: dict[str, dict[str, object]] = {}
    for catalog_name, path in get_golden_catalog_paths().items():
        loaded[catalog_name] = _load_yaml_mapping(path)
    return loaded


def load_golden_standard() -> dict[str, object]:
    """Load the full Golden Standard view by merging all split catalogs."""
    catalogs = load_golden_standard_catalogs()
    if len(catalogs) == 1 and "legacy" in catalogs:
        return catalogs["legacy"]

    merged: dict[str, object] = {}
    for catalog_name, catalog in catalogs.items():
        for key, value in catalog.items():
            if key in merged and merged[key] != value:
                raise ValueError(
                    f"Golden Standard collision for key {key!r} while merging catalog {catalog_name!r}"
                )
            merged[key] = value
    return merged


def load_satellite_learnings() -> list[dict[str, object]]:
    """Load optional satellite learning payloads from the canonical metadata inbox."""
    if not _SATELLITE_LEARNINGS_PATH.is_file():
        return []
    try:
        with open(_SATELLITE_LEARNINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


# Expose a singleton for fast access
_GOLDEN_CACHE: dict[str, object] | None = None


def normalize_knowledge_text(value: object) -> str:
    """Normalize knowledge text so ingest can deduplicate semantically identical entries."""
    return " ".join(str(value).strip().split())


def get_golden_standard() -> dict[str, object]:
    """Return the Golden Standard data, caching the merged load for subsequent calls."""
    global _GOLDEN_CACHE
    if _GOLDEN_CACHE is None:
        _GOLDEN_CACHE = load_golden_standard()
    return _GOLDEN_CACHE


def get_project_insights() -> dict[str, str]:
    """Return the project-insight layer as a normalized mapping."""
    data = get_golden_standard()
    raw = data.get("project_insights", {})
    if not isinstance(raw, dict):
        return {}
    base = {
        str(key): normalize_knowledge_text(value)
        for key, value in raw.items()
        if str(key).startswith("PI-")
    }
    return ingest_satellite_learnings(load_satellite_learnings(), base_insights=base)


def ingest_satellite_learnings(
    sources: Iterable[dict[str, object]],
    *,
    base_insights: dict[str, str] | None = None,
) -> dict[str, str]:
    """Merge satellite learning payloads into the canonical insight map with deduplication."""
    merged = dict(base_insights or get_project_insights())
    seen_texts = {normalize_knowledge_text(text) for text in merged.values()}

    for source in sources:
        if not isinstance(source, dict):
            continue
        payload = source.get("project_insights")
        if not isinstance(payload, dict):
            payload = source.get("insights")
        if not isinstance(payload, dict):
            continue
        for raw_id, raw_text in payload.items():
            insight_id = str(raw_id).strip()
            if not insight_id.startswith("PI-"):
                continue
            insight_text = normalize_knowledge_text(raw_text)
            if not insight_text or insight_text in seen_texts:
                continue
            if insight_id in merged:
                continue
            merged[insight_id] = insight_text
            seen_texts.add(insight_text)
    return merged


def get_project_insight(insight_id: str) -> str:
    """Return a single project insight by ID, or an empty string if absent."""
    return get_project_insights().get(insight_id, "")


def get_golden_summary() -> dict[str, int]:
    """Return compact counts for the main Golden Standard sections."""
    data = get_golden_standard()
    get_project_insight("PI-001")
    return {
        "tokenomics": len(data.get("tokenomics", [])),
        "testing_vices": len(data.get("testing_vices", [])),
        "coding_vices": len(data.get("coding_vices", [])),
        "project_insights": len(get_project_insights()),
    }


def get_project_insight_recommendations() -> dict[str, list[dict[str, str]]]:
    """Return domain-oriented recommendations derived from the project insights."""
    return {
        "D1": [
            {
                "insight_id": "PI-001",
                "project": "deptry",
                "action": "Compare imports against declared dependencies and fail on missing, unused, transitive or misplaced packages.",
            },
            {
                "insight_id": "PI-004",
                "project": "trivy",
                "action": "Scan repos, images and filesystems for secrets, CVEs, misconfigurations and SBOM gaps before release.",
            },
            {
                "insight_id": "PI-010",
                "project": "cerberus",
                "action": "Keep the working tree clean after audits; treat historical artifacts as reference material, not active output.",
            },
        ],
        "D2": [
            {
                "insight_id": "PI-001",
                "project": "deptry",
                "action": "Treat missing or stale dependency declarations as completeness debt and block delivery until reconciled.",
            },
            {
                "insight_id": "PI-006",
                "project": "cerberus",
                "action": "Keep the operational contract complete by storing state, evidence and checkpoints outside the chat.",
            },
            {
                "insight_id": "PI-008",
                "project": "cerberus",
                "action": "Batch predictable authorizations and questions before long runs so the control plane can execute without interruptions.",
            },
            {
                "insight_id": "PI-014",
                "project": "cerberus",
                "action": "Keep the knowledge base alive by continuously absorbing lessons from the core project and its satellites.",
            },
        ],
        "D3": [
            {
                "insight_id": "PI-002",
                "project": "pytest-good-assertions",
                "action": "Require failure messages that explain the mismatch clearly enough to debug without guesswork.",
            },
            {
                "insight_id": "PI-006",
                "project": "cerberus",
                "action": "Use explicit state and evidence fields so the system tells a clear causal story instead of relying on memory.",
            },
            {
                "insight_id": "PI-011",
                "project": "cerberus",
                "action": "Prefer descriptive names and reduce structural noise so purpose is visible at first glance.",
            },
        ],
        "D4": [
            {
                "insight_id": "PI-005",
                "project": "litellm",
                "action": "Centralize provider routing and fallbacks so the code does not grow provider-specific branching spaghetti.",
            },
            {
                "insight_id": "PI-011",
                "project": "cerberus",
                "action": "Flatten nested structure when it simplifies maintenance and removes needless indirection.",
            }
        ],
        "D5": [
            {
                "insight_id": "PI-006",
                "project": "cerberus",
                "action": "Turn failure handling into a structured protocol with next steps, evidence and a visible recovery path.",
            },
            {
                "insight_id": "PI-002",
                "project": "pytest-good-assertions",
                "action": "Make failing assertions explain what to do next so the angry path is actionable, not noisy.",
            },
            {
                "insight_id": "PI-009",
                "project": "cerberus",
                "action": "Treat warnings and known non-blocking findings as operational errors until they are fixed or explicitly blocked.",
            },
        ],
        "D6": [
            {
                "insight_id": "PI-006",
                "project": "cerberus",
                "action": "Enforce clean boundaries, compact state and explicit handoffs to avoid slop and context drift.",
            },
            {
                "insight_id": "PI-012",
                "project": "cerberus",
                "action": "Allow exclusions only when they are minimal, justified and real; do not use theater constructs to simulate progress.",
            }
        ],
        "D7": [
            {
                "insight_id": "PI-004",
                "project": "trivy",
                "action": "Use security scanning as a mandatory gate for secrets, vulnerabilities and IaC misconfigurations.",
            },
            {
                "insight_id": "PI-013",
                "project": "cerberus",
                "action": "Observe risky signals during execution, not after the fact, so live monitoring can interrupt damage early.",
            }
        ],
        "D8": [
            {
                "insight_id": "PI-002",
                "project": "pytest-good-assertions",
                "action": "Keep tests high-signal: assertions should discriminate behavior, not merely confirm presence.",
            },
            {
                "insight_id": "PI-001",
                "project": "deptry",
                "action": "Prevent dependency drift from destabilizing the test suite by validating imports before running coverage gates.",
            },
            {
                "insight_id": "PI-012",
                "project": "cerberus",
                "action": "Reject fake coverage patterns such as xfail-as-expected, placeholder tests, mocks without intent or broad skips without evidence.",
            },
            {
                "insight_id": "PI-015",
                "project": "cerberus",
                "action": "Require each new guard to break a real circularity and reduce the baseline instead of merely naming the problem.",
            },
            {
                "insight_id": "PI-017",
                "project": "cerberus",
                "action": "Split broad coverage theater into discriminative checks so one test never pretends to cover many unrelated vices.",
            },
        ],
        "D9": [
            {
                "insight_id": "PI-002",
                "project": "pytest-good-assertions",
                "action": "Preserve assertion quality so tests fail with precise, inspectable output instead of theater.",
            },
            {
                "insight_id": "PI-012",
                "project": "cerberus",
                "action": "Prefer discriminative tests over symbolic coverage; if a test cannot fail for the right reason, it is not protecting the system.",
            },
            {
                "insight_id": "PI-016",
                "project": "cerberus",
                "action": "Mark non-falsifiable lessons as DOC_ONLY instead of pretending they can be proved automatically.",
            },
        ],
        "D10": [
            {
                "insight_id": "PI-003",
                "project": "tokencost",
                "action": "Meter tokens before and during LLM calls so cost is visible before usage grows.",
            },
            {
                "insight_id": "PI-005",
                "project": "litellm",
                "action": "Unify provider routing, fallbacks and telemetry so cost and resilience are handled once.",
            },
            {
                "insight_id": "PI-007",
                "project": "cerberus",
                "action": "Treat output trimming, context hygiene and history externalization as a first-class control, not an afterthought.",
            },
            {
                "insight_id": "PI-009",
                "project": "cerberus",
                "action": "Convert every warning and findable issue into a tracked operational error until the backlog is clean.",
            },
            {
                "insight_id": "PI-010",
                "project": "cerberus",
                "action": "Keep the root workspace clean so historical data lives in archives instead of polluting active context.",
            },
            {
                "insight_id": "PI-013",
                "project": "cerberus",
                "action": "Watch token and quality signals live during the run, not only in a post-mortem report.",
            },
        ],
        "D11": [
            {
                "insight_id": "PI-004",
                "project": "trivy",
                "action": "Use security scanning as a pre-merge and pre-release gate for filesystems, images and IaC.",
            },
            {
                "insight_id": "PI-012",
                "project": "cerberus",
                "action": "Keep exclusions minimal and auditable so the security posture stays real instead of ceremonial.",
            },
        ],
        "D12": [
            {
                "insight_id": "PI-014",
                "project": "cerberus",
                "action": "Fuse satellite learnings into the canonical knowledge base only after normalization and deduplication.",
            },
            {
                "insight_id": "PI-018",
                "project": "cerberus",
                "action": "Normalize, deduplicate and record new learnings before folding them into the central knowledge base.",
            },
        ],
    }
