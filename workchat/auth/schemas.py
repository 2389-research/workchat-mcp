# ABOUTME: Pydantic schemas for authentication
# ABOUTME: Request/response models for user registration and auth

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_users import schemas

from ..models.user import UserRole


class UserRead(schemas.BaseUser[UUID]):
    """User read schema for API responses."""

    org_id: UUID
    display_name: str
    role: UserRole
    created_at: datetime
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(schemas.BaseUserCreate):
    """User creation schema for registration."""

    org_id: UUID
    display_name: str
    role: UserRole = UserRole.MEMBER


class UserUpdate(schemas.BaseUserUpdate):
    """User update schema."""

    display_name: Optional[str] = None
    role: Optional[UserRole] = None
