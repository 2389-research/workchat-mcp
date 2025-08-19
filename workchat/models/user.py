# ABOUTME: User domain model with role-based access
# ABOUTME: Links users to organizations with admin/member permissions

from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .org import Org


class UserRole(str, Enum):
    """User roles within an organization."""

    ADMIN = "admin"
    MEMBER = "member"


class User(BaseModel, table=True):
    """User model with organization membership and role."""

    org_id: UUID = Field(foreign_key="org.id", index=True)
    display_name: str = Field(max_length=100)
    email: str = Field(max_length=255, unique=True, index=True)
    role: UserRole = Field(default=UserRole.MEMBER)

    # Relationship to organization
    org: "Org" = Relationship(back_populates="users")
