"""Depends utils."""

from fastapi import HTTPException, Request

from axmp_ai_agent_studio.service.agent_service import AgentService


async def get_agent_service(request: Request) -> AgentService:
    """Get the agent service."""
    service = getattr(request.app.state, "agent_service", None)
    if not service:
        raise HTTPException(
            status_code=500,
            detail="Service(agent_service) is not available in the request state. "
            "You should set the service in the request state.",
        )
    return service
