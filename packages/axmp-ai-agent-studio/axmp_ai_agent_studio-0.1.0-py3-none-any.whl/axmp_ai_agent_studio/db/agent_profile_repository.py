"""Agent profile repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult

from axmp_ai_agent_studio.db.base_repository import BaseRepository
from axmp_ai_agent_studio.entity.agent_profile import AgentProfile
from axmp_ai_agent_studio.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
)
from axmp_ai_agent_studio.scheme.agent_profile_query import AgentProfileQueryParameters
from axmp_ai_agent_studio.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_LIMIT,
    SortDirection,
)
from axmp_ai_agent_studio.util.search_utils import get_escaped_regex_pattern
from axmp_ai_agent_studio.util.time_utils import DEFAULT_TIME_ZONE

logger = logging.getLogger("appLogger")


class AgentProfileRepository(BaseRepository[AgentProfile]):
    """Agent profile repository."""

    async def init_index(self) -> None:
        """Create indexes for the collection if needed."""
        indexes = await self._collection.list_indexes().to_list(length=None)

        unique_index_name = "unique_key_name"

        unique_index_exists = False
        for index in indexes:
            if index["name"] == unique_index_name and index.get("unique", True):
                unique_index_exists = True
                break

        if not unique_index_exists:
            self._collection.create_index("name", name=unique_index_name, unique=True)

    async def insert(self, *, item: AgentProfile) -> str:
        """Insert a new agent profile into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        # model_dump will convert datetime to string
        # so we need to set again datetime filed with datetime object
        agent_profile_dict = item.model_dump(by_alias=True, exclude=["id"])
        agent_profile_dict["created_at"] = item.created_at

        result: InsertOneResult = await self._collection.insert_one(agent_profile_dict)

        return str(result.inserted_id)

    async def update(self, *, item: AgentProfile) -> AgentProfile | None:
        """Update an agent profile in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        # model_dump will convert datetime to string
        # so we need to set again datetime filed with datetime object
        agent_profile_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "created_at",
                "created_by",
            ],
        )
        agent_profile_dict["updated_at"] = item.updated_at

        update = [{"$set": agent_profile_dict}]

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
        )

        if document is None:
            raise ObjectNotFoundException(item.id)

        return AgentProfile(**document)

    async def delete(self, *, item_id: str) -> bool:
        """Delete an agent profile from the repository."""
        try:
            query = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one_and_delete(query)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return True

    async def find_by_id(self, *, item_id: str) -> AgentProfile | None:
        """Find an agent profile by ID."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(filter=filter)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return AgentProfile(**document)

    async def find_all(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
        page_number: int = 1,
        page_size: int = 10,
    ) -> List[AgentProfile]:
        """Find all agent profiles in the repository."""
        if page_number < 1:
            page_number = DEFAULT_PAGE_NUMBER
        if page_size < 1:
            page_size = DEFAULT_PAGE_SIZE

        skip, limit = (page_size * (page_number - 1), page_size)

        logger.debug(
            f"page_number={page_number}, page_size={page_size} so skip: {skip}, limit: {limit}"
        )

        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "name"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        cursor = (
            self._collection.find(filter)
            .sort(sort_field, direction)
            .skip(skip)
            .limit(limit)
        )

        # convert cursor to list of agent profiles
        agent_profiles = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    agent_profiles.append(AgentProfile(**document))

        return agent_profiles

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
        max_limit: int = MAX_LIMIT,
    ) -> List[AgentProfile]:
        """Find all agent profiles in the repository without pagination."""
        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "name"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        cursor = (
            self._collection.find(filter).sort(sort_field, direction).limit(max_limit)
        )

        # convert cursor to list of agent profiles
        agent_profiles = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    agent_profiles.append(AgentProfile(**document))

        logger.debug(f"Found {len(agent_profiles)} agent profiles")

        return agent_profiles

    async def count(self, *, query_parameters: AgentProfileQueryParameters) -> int:
        """Count the number of agent profiles in the repository."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter)

    async def find_all_query(
        self, *, query_parameters: AgentProfileQueryParameters
    ) -> Dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: Dict[str, Any] = {}

        if query_parameters.name:
            filter["name"] = {
                "$regex": get_escaped_regex_pattern(query_parameters.name),
                "$options": "i",
            }

        if query_parameters.description:
            filter["description"] = {
                "$regex": get_escaped_regex_pattern(query_parameters.description),
                "$options": "i",
            }

        if query_parameters.created_by:
            filter["created_by"] = query_parameters.created_by

        if query_parameters.updated_by:
            filter["updated_by"] = query_parameters.updated_by

        if query_parameters.status:
            filter["status"] = query_parameters.status

        if query_parameters.labels:
            for label in query_parameters.parsed_labels:
                filter.update({f"labels.{label.key}": label.value})

        return filter
