"""protocol_engine package initialization.

Provides access to the consolidated Golden Standard knowledge base.
"""

from .knowledge_loader import (
    get_golden_standard,
    get_golden_standard_root,
    get_golden_summary,
    get_golden_catalog_paths,
    get_project_insight,
    get_project_insight_recommendations,
    get_project_insights,
    load_golden_standard_audit,
    load_golden_standard_catalogs,
    load_golden_standard_manifest,
    load_satellite_learnings,
    ingest_satellite_learnings,
    normalize_knowledge_text,
)

__all__ = [
    "get_golden_standard",
    "get_golden_standard_root",
    "get_golden_summary",
    "get_golden_catalog_paths",
    "get_project_insight",
    "get_project_insight_recommendations",
    "get_project_insights",
    "load_golden_standard_audit",
    "load_golden_standard_catalogs",
    "load_golden_standard_manifest",
    "load_satellite_learnings",
    "ingest_satellite_learnings",
    "normalize_knowledge_text",
]
