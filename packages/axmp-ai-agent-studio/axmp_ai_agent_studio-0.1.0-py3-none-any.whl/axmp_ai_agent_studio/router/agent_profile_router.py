"""This module contains the routes for the agent profiles."""

import logging
from typing import List

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import JSONResponse
from zmp_authentication_provider.auth.oauth2_keycloak import get_current_user
from zmp_authentication_provider.scheme.auth_model import TokenData

from axmp_ai_agent_studio.entity.agent_profile import AgentProfile, AgentProfileStatus
from axmp_ai_agent_studio.scheme.agent_profile_dto import (
    AgentProfileCreateRequest,
    AgentProfileUpdateRequest,
)
from axmp_ai_agent_studio.scheme.agent_profile_query import (
    AgentProfileQueryParameters,
    AgentProfileSortField,
)
from axmp_ai_agent_studio.scheme.list_model import AgentProfileList
from axmp_ai_agent_studio.scheme.response_model import ResponseModel
from axmp_ai_agent_studio.service.agent_service import AgentService
from axmp_ai_agent_studio.util.depends_utils import get_agent_service
from axmp_ai_agent_studio.util.list_utils import SortDirection

logger = logging.getLogger("appLogger")

router = APIRouter()


@router.get(
    "/agent/profiles",
    summary="Get agent profiles",
    response_class=JSONResponse,
    response_model=AgentProfileList,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_agent_profiles(
    name: str = Query(None, description="The name of the agent profile."),
    description: str = Query(None, description="The description of the agent profile."),
    labels: List[str] = Query(
        None, description="The labels of the agent profile. e.g.) 'type:agent'"
    ),
    status: AgentProfileStatus = Query(
        None, description="The status of the agent profile."
    ),
    created_by: str = Query(None, description="The created by of the agent profile."),
    updated_by: str = Query(None, description="The updated by of the agent profile."),
    page_number: int = Query(1, description="The page number."),
    page_size: int = Query(10, description="The page size."),
    sort_field: AgentProfileSortField = Query(
        AgentProfileSortField.UPDATED_AT,
        description="The field to sort by. default: updated_at",
    ),
    sort_direction: SortDirection = Query(
        SortDirection.DESC,
        description="The direction to sort by. default: desc",
    ),
    oauth_user: TokenData = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentProfileList:
    """Get agent profiles."""
    query_parameters = AgentProfileQueryParameters(
        name=name,
        description=description,
        labels=labels,
        status=status,
        created_by=created_by,
        updated_by=updated_by,
        sort_field=sort_field.value,
        sort_direction=sort_direction,
    )

    data = await agent_service.get_agent_profiles(
        query_parameters=query_parameters,
        page_number=page_number,
        page_size=page_size,
    )
    total = await agent_service.get_agent_profiles_count(
        query_parameters=query_parameters
    )

    return AgentProfileList(
        data=data,
        total=total,
        current_page=page_number,
        page_size=page_size,
    )


@router.get(
    "/agent/profiles/{id}",
    summary="Get agent profile by ID",
    response_class=JSONResponse,
    response_model=AgentProfile,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_agent_profile_by_id(
    request: Request,
    id: str = Path(..., description="The ID of the agent profile."),
    oauth_user: TokenData = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentProfile:
    """Get agent profile by ID."""
    return await agent_service.get_agent_profile_by_id(id=id)


@router.post(
    "/agent/profiles",
    summary="Create agent profile",
    response_class=JSONResponse,
    response_model=AgentProfile,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def create_agent_profile(
    agent_profile_create_request: AgentProfileCreateRequest,
    oauth_user: TokenData = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentProfile:
    """Create agent profile."""
    agent_profile = AgentProfile(**agent_profile_create_request.model_dump())
    agent_profile.created_by = oauth_user.username

    inserted_id = await agent_service.create_agent_profile(agent_profile=agent_profile)
    return await agent_service.get_agent_profile_by_id(id=inserted_id)


@router.put(
    "/agent/profiles/{id}",
    summary="Update agent profile",
    response_class=JSONResponse,
    response_model=AgentProfile,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def update_agent_profile(
    agent_profile_update_request: AgentProfileUpdateRequest,
    id: str = Path(..., description="The ID of the agent profile."),
    oauth_user: TokenData = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentProfile:
    """Update agent profile."""
    agent_profile = AgentProfile(**agent_profile_update_request.model_dump())
    agent_profile.id = id
    agent_profile.updated_by = oauth_user.username

    return await agent_service.modify_agent_profile(agent_profile=agent_profile)


@router.delete(
    "/agent/profiles/{id}",
    summary="Delete agent profile",
    response_class=JSONResponse,
    response_model=ResponseModel,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def delete_agent_profile(
    id: str = Path(..., description="The ID of the agent profile."),
    oauth_user: TokenData = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> ResponseModel:
    """Delete agent profile."""
    result = await agent_service.remove_agent_profile_by_id(id=id)
    return ResponseModel(
        message="Agent profile deleted successfully"
        if result
        else "Agent profile deletion failed"
    )
