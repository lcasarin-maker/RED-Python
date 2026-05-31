"""protocol_engine package initialization.

Provides access to the consolidated Golden Standard knowledge base.
"""

from .knowledge_loader import (
    get_golden_standard,
    get_golden_summary,
    get_project_insight,
    get_project_insight_recommendations,
    get_project_insights,
)

__all__ = [
    "get_golden_standard",
    "get_golden_summary",
    "get_project_insight",
    "get_project_insight_recommendations",
    "get_project_insights",
]
