"""Base repository for MongoDB operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection

from axmp_ai_agent_studio.scheme.base_search_query import BaseQueryParameters
from axmp_ai_agent_studio.util.list_utils import MAX_LIMIT

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """BaseRepository class to handle MongoDB operation."""

    def __init__(self, *, collection: AsyncIOMotorCollection):
        """Initialize the repository with MongoDB database."""
        self._collection = collection

    @classmethod
    async def create(cls, *, collection: AsyncIOMotorCollection) -> BaseRepository[T]:
        """Create a new instance of the repository."""
        instance = cls(collection=collection)
        await instance.init_index()
        return instance

    @abstractmethod
    async def init_index(self) -> None:
        """Initialize the index."""
        pass

    @abstractmethod
    async def insert(self, *, item: T) -> str:
        """Insert a new item into the repository."""
        pass

    @abstractmethod
    async def update(self, *, item: T) -> T | None:
        """Update an item in the repository."""
        pass

    @abstractmethod
    async def delete(self, *, item_id: str) -> bool:
        """Delete an item from the repository."""
        pass

    @abstractmethod
    async def find_by_id(self, *, item_id: str) -> T | None:
        """Find one item in the repository."""
        pass

    @abstractmethod
    async def find_all(
        self,
        *,
        query_parameters: BaseQueryParameters,
        page_number: int = 1,
        page_size: int = 10,
    ) -> List[T]:
        """Find all items in the repository."""
        pass

    @abstractmethod
    async def find_all_without_pagination(
        self,
        *,
        query_parameters: BaseQueryParameters,
        max_limit: int = MAX_LIMIT,
    ) -> List[T]:
        """Find all items in the repository without pagination."""
        pass

    @abstractmethod
    async def count(self, *, query_parameters: BaseQueryParameters) -> int:
        """Count the number of items in the repository."""
        pass

    @abstractmethod
    async def find_all_query(
        self,
        *,
        query_parameters: BaseQueryParameters,
    ) -> Dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        pass
