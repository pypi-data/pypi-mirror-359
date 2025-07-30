"""This module contains the routers for the agent studio."""

from .agent_profile_router import router as agent_profile_router
from .healthy_router import router as healthy_router

__all__ = ["agent_profile_router", "healthy_router"]
