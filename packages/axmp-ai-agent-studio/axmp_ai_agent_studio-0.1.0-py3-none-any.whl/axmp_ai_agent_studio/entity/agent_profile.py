"""Agent profile entity."""

from enum import Enum
from typing import Dict

from axmp_ai_agent_studio.entity.base_model import StudioBaseModel


class AgentProfileStatus(str, Enum):
    """Agent profile status."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class AgentProfile(StudioBaseModel):
    """Agent profile entity."""

    name: str
    description: str | None = None
    status: AgentProfileStatus = AgentProfileStatus.ACTIVE
    labels: Dict[str, str] | None = None
