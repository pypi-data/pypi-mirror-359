"""This file is used to check the health of the service."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from axmp_ai_agent_studio.scheme.response_model import ResponseModel

log = logging.getLogger("appLogger")

router = APIRouter()


@router.get(
    "/healthz",
    summary="Health Check",
    response_class=JSONResponse,
    response_model=ResponseModel,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def healthz() -> ResponseModel:
    """Check endpoint for the service."""
    return ResponseModel()
