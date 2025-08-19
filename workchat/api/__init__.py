# ABOUTME: API package initialization
# ABOUTME: Centralized FastAPI router exports and configuration

from .channels import router as channels_router

__all__ = ["channels_router"]
