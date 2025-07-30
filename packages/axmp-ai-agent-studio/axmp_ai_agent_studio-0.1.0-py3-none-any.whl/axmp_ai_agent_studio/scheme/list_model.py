"""This module contains the list model for the alert."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from axmp_ai_agent_studio.entity.agent_profile import AgentProfile
from axmp_ai_agent_studio.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)


class BaseListModel(BaseModel):
    """Base list model for alert."""

    current_page: int = Field(DEFAULT_PAGE_NUMBER, ge=DEFAULT_PAGE_NUMBER)
    page_size: int = Field(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE)
    total: int = Field(0, ge=0)

    model_config = ConfigDict(exclude_none=True)


class AgentProfileList(BaseListModel):
    """Agent profile list model."""

    data: List[AgentProfile]
