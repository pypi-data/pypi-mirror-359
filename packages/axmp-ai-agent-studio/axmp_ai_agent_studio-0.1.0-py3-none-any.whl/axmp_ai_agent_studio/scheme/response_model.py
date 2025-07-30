"""Response model for AIOps Pilot."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class Result(str, Enum):
    """Result model for AIOps Pilot."""

    SUCCESS = "success"
    FAILED = "failed"


class ResponseModel(BaseModel):
    """Result model for alert request."""

    result: Result = Result.SUCCESS
    message: Optional[str] = None
    code: Optional[str] = None
    data: Optional[Any] = None

    model_config = ConfigDict(exclude_none=True)
