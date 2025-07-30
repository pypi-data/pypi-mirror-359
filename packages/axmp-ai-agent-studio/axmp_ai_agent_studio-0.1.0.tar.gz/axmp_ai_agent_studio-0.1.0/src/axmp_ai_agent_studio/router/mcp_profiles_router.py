"""Backend service router."""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse
from zmp_authentication_provider.auth.oauth2_keycloak import get_current_user
from zmp_authentication_provider.scheme.auth_model import TokenData

from axmp_ai_agent_studio.scheme.backend_service_dto import (
    ApiSuccessResponseDto,
    BackendServiceAuthUpdateRequestDto,
    BackendServiceCreateRequestDto,
    BackendServiceResponseDto,
    BackendServiceStatusUpdateRequestDto,
    BackendServiceUpdateRequestDto,
    FilterOptionsResponseDto,
    PagedResponseDto,
    PaginationDto,
    SwaggerParseRequestDto,
    SwaggerParseResponseDto,
)
from axmp_ai_agent_studio.scheme.backend_service_query import BackendServiceQueryParameters
from axmp_ai_agent_studio.service.backend_service_service import BackendServiceService
from axmp_ai_agent_studio.util.list_utils import SortDirection

logger = logging.getLogger("appLogger")

router = APIRouter()


async def get_backend_service_service(request: Request) -> BackendServiceService:
    """Get the backend service service."""
    return request.app.state.backend_service_service


def create_paged_response(
    data: List[BackendServiceResponseDto], 
    page: int, 
    limit: int, 
    total: int
) -> PagedResponseDto:
    """Create a paged response."""
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    pagination = PaginationDto(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )
    
    return PagedResponseDto(
        data=data,
        pagination=pagination,
        success=True,
        message="조회 성공",
        timestamp=datetime.now().isoformat()
    )


@router.get(
    "/backend-services",
    summary="Get backend services list",
    response_class=JSONResponse,
    response_model=PagedResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_backend_services(
    status: Optional[str] = Query(None, description="Status: active|inactive"),
    search: Optional[str] = Query(None, description="Search keyword"),
    page: int = Query(1, description="Page number", ge=1),
    limit: int = Query(12, description="Items per page", ge=1, le=100),
    sort: str = Query("created", description="Sort field: name|created|updated"),
    order: str = Query("desc", description="Sort order: asc|desc"),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> PagedResponseDto:
    """Get backend services list."""
    logger.debug(f"Get backend services router: {status}, {search}, {page}, {limit}, {sort}, {order}")
    sort_direction = SortDirection.ASC if order == "asc" else SortDirection.DESC
    
    # Sort field mapping
    sort_field_map = {
        "name": "name",
        "created": "created_at", 
        "updated": "updated_at"
    }
    sort_field = sort_field_map.get(sort, "created_at")
    
    query_parameters = BackendServiceQueryParameters(
        status=status,
        search=search,
        sort_field=sort_field,
        sort_direction=sort_direction,
    )

    services = await service.get_backend_services(
        query_parameters=query_parameters,
        page_number=page,
        page_size=limit,
    )
    total = await service.get_backend_services_count(query_parameters=query_parameters)

    return create_paged_response(services, page, limit, total)


@router.get(
    "/backend-services/search",
    summary="Search backend services",
    response_class=JSONResponse,
    response_model=PagedResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def search_backend_services(
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Status filter"),
    labels: Optional[str] = Query(None, description="Labels filter (comma separated)"),
    page: int = Query(1, description="Page number", ge=1),
    limit: int = Query(12, description="Items per page", ge=1, le=100),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> PagedResponseDto:
    """Search backend services."""
    logger.debug(f"Search backend services router: {q}, {status}, {labels}, {page}, {limit}")
    try:
        # 모든 검색 파라미터가 없거나 비어있으면 전체 목록 반환
        has_query = q and q.strip() != ""
        has_labels = labels and labels.strip() != ""
        has_status = status and status.strip() != ""
        
        if not has_query and not has_labels and not has_status:
            logger.debug("No search parameters provided, returning all services")
            
            # 전체 목록 조회를 위한 쿼리 파라미터 설정
            query_parameters = BackendServiceQueryParameters(
                status=status,
                search=None,  # 검색어 없음
                sort_field="created_at",
                sort_direction=SortDirection.DESC,
            )
            
            # 전체 서비스 조회
            services = await service.get_backend_services(
                query_parameters=query_parameters,
                page_number=page,
                page_size=limit,
            )
            total = await service.get_backend_services_count(query_parameters=query_parameters)
            
            return create_paged_response(services, page, limit, total)
        
        # 검색어가 있는 경우 기존 검색 로직 수행
        labels_list = labels.split(',') if labels else None
        
        services = await service.search_backend_services(
            query=q,
            labels=labels_list,
            status=status
        )
        
        # Manual pagination for search results
        start = (page - 1) * limit
        end = start + limit
        paginated_services = services[start:end]
        total = len(services)
        
        return create_paged_response(paginated_services, page, limit, total)
    except Exception as e:
        logger.error(f"Error searching backend services: {e}")
        raise HTTPException(status_code=400, detail="Search failed")


@router.get(
    "/backend-services/filter-options",
    summary="Get filter options",
    response_class=JSONResponse,
    response_model=FilterOptionsResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_filter_options(
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> FilterOptionsResponseDto:
    """Get filter options for backend services."""
    try:
        return await service.get_filter_options()
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        raise HTTPException(status_code=500, detail="Failed to get filter options")


@router.get(
    "/backend-services/by-labels",
    summary="Get backend services by labels",
    response_class=JSONResponse,
    response_model=PagedResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_backend_services_by_labels(
    labels: str = Query(..., description="Labels (comma separated)"),
    match_all: bool = Query(False, description="Match all labels"),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> PagedResponseDto:
    """Get backend services by labels."""
    try:
        labels_list = [label.strip() for label in labels.split(',')]
        
        services = await service.get_backend_services_by_labels(
            labels=labels_list,
            match_all=match_all
        )
        
        # For simplicity, return all results without pagination
        return create_paged_response(services, 1, len(services), len(services))
    except Exception as e:
        logger.error(f"Error getting backend services by labels: {e}")
        raise HTTPException(status_code=400, detail="Failed to get services by labels")


@router.post(
    "/backend-services/parse-swagger",
    summary="Parse and validate Swagger JSON",
    response_class=JSONResponse,
    response_model=SwaggerParseResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def parse_swagger(
    request_dto: SwaggerParseRequestDto,
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> SwaggerParseResponseDto:
    """Parse and validate Swagger JSON."""
    return await service.parse_swagger_json(swagger_json=request_dto.swagger_json)


@router.post(
    "/backend-services",
    summary="Create backend service",
    response_class=JSONResponse,
    response_model=ApiSuccessResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def create_backend_service(
    request_dto: BackendServiceCreateRequestDto,
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> ApiSuccessResponseDto:
    """Create backend service."""
    try:
        service_id = await service.create_backend_service(
            request_dto=request_dto,
            created_by=oauth_user.username
        )
        
        return ApiSuccessResponseDto(
            success=True,
            message="Backend service created successfully",
            data={"id": service_id},
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error creating backend service: {e}")
        raise HTTPException(status_code=400, detail="Failed to create backend service")


@router.get(
    "/backend-services/{service_id}",
    summary="Get backend service by ID",
    response_class=JSONResponse,
    response_model=BackendServiceResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_backend_service_by_id(
    service_id: str = Path(..., description="Backend service ID"),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> BackendServiceResponseDto:
    """Get backend service by ID."""
    logger.debug(f"Get backend service by ID router: {service_id}")
    try:
        return await service.get_backend_service_by_id(service_id=service_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Backend service not found")


@router.put(
    "/backend-services/{service_id}",
    summary="Update backend service",
    response_class=JSONResponse,
    response_model=ApiSuccessResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def update_backend_service(
    request_dto: BackendServiceUpdateRequestDto,
    service_id: str = Path(..., description="Backend service ID"),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> ApiSuccessResponseDto:
    """Update backend service."""
    try:
        await service.update_backend_service(
            service_id=service_id,
            request_dto=request_dto,
            updated_by=oauth_user.username
        )
        
        return ApiSuccessResponseDto(
            success=True,
            message="Backend service updated successfully",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error updating backend service: {e}")
        raise HTTPException(status_code=404, detail="Backend service not found")


@router.patch(
    "/backend-services/{service_id}/status",
    summary="Update backend service status",
    response_class=JSONResponse,
    response_model=ApiSuccessResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def update_backend_service_status(
    request_dto: BackendServiceStatusUpdateRequestDto,
    service_id: str = Path(..., description="Backend service ID"),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> ApiSuccessResponseDto:
    """Update backend service status."""
    try:
        await service.update_backend_service_status(
            service_id=service_id,
            request_dto=request_dto,
            updated_by=oauth_user.username
        )
        
        return ApiSuccessResponseDto(
            success=True,
            message=f"Backend service status updated to {request_dto.status}",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error updating backend service status: {e}")
        raise HTTPException(status_code=404, detail="Backend service not found")


@router.patch(
    "/backend-services/{service_id}/auth",
    summary="Update backend service auth",
    response_class=JSONResponse,
    response_model=ApiSuccessResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def update_backend_service_auth(
    request_dto: BackendServiceAuthUpdateRequestDto,
    service_id: str = Path(..., description="Backend service ID"),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> ApiSuccessResponseDto:
    """Update backend service auth information."""
    try:
        await service.update_backend_service_auth(
            service_id=service_id,
            request_dto=request_dto,
            updated_by=oauth_user.username
        )
        
        return ApiSuccessResponseDto(
            success=True,
            message="Backend service auth updated successfully",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error updating backend service auth: {e}")
        raise HTTPException(status_code=404, detail="Backend service not found")


@router.delete(
    "/backend-services/{service_id}",
    summary="Delete backend service",
    response_class=JSONResponse,
    response_model=ApiSuccessResponseDto,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def delete_backend_service(
    service_id: str = Path(..., description="Backend service ID"),
    oauth_user: TokenData = Depends(get_current_user),
    service: BackendServiceService = Depends(get_backend_service_service),
) -> ApiSuccessResponseDto:
    """Delete backend service."""
    try:
        await service.delete_backend_service(service_id=service_id)
        
        return ApiSuccessResponseDto(
            success=True,
            message="Backend service deleted successfully",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error deleting backend service: {e}")
        raise HTTPException(status_code=404, detail="Backend service not found") 