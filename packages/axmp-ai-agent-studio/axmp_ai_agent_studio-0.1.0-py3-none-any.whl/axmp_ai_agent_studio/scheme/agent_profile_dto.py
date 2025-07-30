"""Agent profile DTO."""

from typing import Dict

from pydantic import BaseModel, Field

from axmp_ai_agent_studio.entity.agent_profile import AgentProfileStatus


class AgentProfileCreateRequest(BaseModel):
    """Agent profile create request."""

    name: str = Field(
        ..., description="The name of the agent profile.", min_length=1, max_length=255
    )
    description: str | None = Field(
        None,
        description="The description of the agent profile.",
        min_length=1,
        max_length=2000,
    )
    status: AgentProfileStatus = Field(
        AgentProfileStatus.ACTIVE, description="The status of the agent profile."
    )
    labels: Dict[str, str] = Field(
        {}, description="The labels of the agent profile. e.g.) {'type': 'agent'}"
    )


class AgentProfileUpdateRequest(AgentProfileCreateRequest):
    """Agent profile update request."""
