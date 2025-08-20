# ABOUTME: API package initialization
# ABOUTME: Centralized FastAPI router exports and configuration

from .channels import router as channels_router
from .messages import router as messages_router

__all__ = ["channels_router", "messages_router"]
