"""Agent profile query."""

from enum import Enum
from typing import List

from axmp_ai_agent_studio.entity.agent_profile import AgentProfileStatus
from axmp_ai_agent_studio.scheme.base_search_query import BaseQueryParameters


class AgentProfileSortField(str, Enum):
    """Agent profile sort field."""

    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class AgentProfileQueryParameters(BaseQueryParameters):
    """Agent profile query."""

    name: str | None = None
    description: str | None = None
    status: AgentProfileStatus | None = None
    created_by: str | None = None
    updated_by: str | None = None
    labels: List[str] | None = None
