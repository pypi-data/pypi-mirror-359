"""This module contains the service for the agent."""

import logging
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from axmp_ai_agent_studio.db.agent_profile_repository import AgentProfileRepository
from axmp_ai_agent_studio.entity.agent_profile import AgentProfile
from axmp_ai_agent_studio.exception.db_exceptions import ObjectNotFoundException
from axmp_ai_agent_studio.exception.servivce_exception import (
    StudioBackendException,
    StudioError,
)
from axmp_ai_agent_studio.scheme.agent_profile_query import AgentProfileQueryParameters
from axmp_ai_agent_studio.setting import mongodb_settings

logger = logging.getLogger("appLogger")


class AgentService:
    """The service for the agent."""

    def __init__(self, database: AsyncIOMotorDatabase):
        """Initialize the agent service."""
        self._database = database
        self._agent_profile_repository: AgentProfileRepository | None = None
        # TODO: add other repository definition here

    @classmethod
    async def initialize(cls, *, database: AsyncIOMotorDatabase) -> "AgentService":
        """Initialize the agent service."""
        instance = cls(database=database)
        instance._agent_profile_repository = await AgentProfileRepository.create(
            collection=database[mongodb_settings.collection_agent_profile]
        )
        # TODO: add other repository create here

        return instance

    async def create_agent_profile(self, *, agent_profile: AgentProfile) -> str:
        """Create a new agent profile."""
        return await self._agent_profile_repository.insert(item=agent_profile)

    async def get_agent_profile_by_id(self, *, id: str) -> AgentProfile:
        """Get an agent profile by ID."""
        try:
            agent_profile = await self._agent_profile_repository.find_by_id(item_id=id)
        except ObjectNotFoundException:
            raise StudioBackendException(
                StudioError.ID_NOT_FOUND,
                document=mongodb_settings.collection_agent_profile,
                object_id=id,
            )

        return agent_profile

    async def modify_agent_profile(
        self, *, agent_profile: AgentProfile
    ) -> AgentProfile:
        """Update an agent profile."""
        return await self._agent_profile_repository.update(item=agent_profile)

    async def remove_agent_profile_by_id(self, *, id: str) -> bool:
        """Delete an agent profile."""
        return await self._agent_profile_repository.delete(item_id=id)

    async def get_agent_profiles(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
        page_number: int = 1,
        page_size: int = 10,
    ) -> List[AgentProfile]:
        """Get agent profiles."""
        return await self._agent_profile_repository.find_all(
            query_parameters=query_parameters,
            page_number=page_number,
            page_size=page_size,
        )

    async def get_agent_profiles_count(
        self, *, query_parameters: AgentProfileQueryParameters
    ) -> int:
        """Get agent profiles count."""
        return await self._agent_profile_repository.count(
            query_parameters=query_parameters
        )
