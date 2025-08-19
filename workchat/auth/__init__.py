# ABOUTME: Authentication package exports
# ABOUTME: Provides JWT-based authentication with fastapi-users

from .config import auth_backend, current_active_user, fastapi_users, get_user_manager
from .models import UserDB
from .schemas import UserCreate, UserRead, UserUpdate

__all__ = [
    "UserDB",
    "get_user_manager",
    "auth_backend",
    "fastapi_users",
    "current_active_user",
    "UserRead",
    "UserCreate",
    "UserUpdate",
]
