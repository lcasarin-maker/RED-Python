import pathlib
import yaml
from typing import Dict, Any

_GOLDEN_PATH = pathlib.Path(__file__).parent.parent / "Golden_Standard" / "golden_standard.yaml"

def load_golden_standard() -> Dict[str, Any]:
    """Load the consolidated Golden Standard YAML file.
    Returns a dictionary with top-level keys such as `tokenomics`, `testing_vices`,
    `coding_vices`, and `project_insights`.
    """
    if not _GOLDEN_PATH.is_file():
        raise FileNotFoundError(f"Golden Standard file not found at {_GOLDEN_PATH}")
    with open(_GOLDEN_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

# Expose a singleton for fast access
_GOLDEN_CACHE: Dict[str, Any] | None = None

def get_golden_standard() -> Dict[str, Any]:
    """Return the Golden Standard data, caching the load for subsequent calls."""
    global _GOLDEN_CACHE
    if _GOLDEN_CACHE is None:
        _GOLDEN_CACHE = load_golden_standard()
    return _GOLDEN_CACHE


def get_project_insights() -> Dict[str, str]:
    """Return the project-insight layer as a normalized mapping."""
    data = get_golden_standard()
    raw = data.get("project_insights", {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(key): str(value).strip()
        for key, value in raw.items()
        if str(key).startswith("PI-")
    }


def get_project_insight(insight_id: str) -> str:
    """Return a single project insight by ID, or an empty string if absent."""
    return get_project_insights().get(insight_id, "")


def get_golden_summary() -> Dict[str, int]:
    """Return compact counts for the main Golden Standard sections."""
    data = get_golden_standard()
    return {
        "tokenomics": len(data.get("tokenomics", [])),
        "testing_vices": len(data.get("testing_vices", [])),
        "coding_vices": len(data.get("coding_vices", [])),
        "project_insights": len(get_project_insights()),
    }


def get_project_insight_recommendations() -> Dict[str, list[dict[str, str]]]:
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
        ],
        "D4": [
            {
                "insight_id": "PI-005",
                "project": "litellm",
                "action": "Centralize provider routing and fallbacks so the code does not grow provider-specific branching spaghetti.",
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
        ],
        "D6": [
            {
                "insight_id": "PI-006",
                "project": "cerberus",
                "action": "Enforce clean boundaries, compact state and explicit handoffs to avoid slop and context drift.",
            }
        ],
        "D7": [
            {
                "insight_id": "PI-004",
                "project": "trivy",
                "action": "Use security scanning as a mandatory gate for secrets, vulnerabilities and IaC misconfigurations.",
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
        ],
        "D9": [
            {
                "insight_id": "PI-002",
                "project": "pytest-good-assertions",
                "action": "Preserve assertion quality so tests fail with precise, inspectable output instead of theater.",
            }
        ],
        "D10": [
            {
                "insight_id": "PI-003",
                "project": "tokencost",
                "action": "Measure prompt and completion cost before calling LLMs so token usage is visible and budgetable.",
            },
            {
                "insight_id": "PI-005",
                "project": "litellm",
                "action": "Use provider routing and cost tracking together to pick the cheapest viable model path.",
            },
            {
                "insight_id": "PI-006",
                "project": "cerberus",
                "action": "Preserve compact state, checkpoints and summaries to keep context budgets under control.",
            },
        ],
    }
