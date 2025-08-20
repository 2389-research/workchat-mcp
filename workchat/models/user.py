# ABOUTME: User domain model with role-based access
# ABOUTME: Links users to organizations with admin/member permissions

from enum import Enum
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .message import Message
    from .org import Org


class UserRole(str, Enum):
    """User roles within an organization."""

    ADMIN = "admin"
    MEMBER = "member"


class User(BaseModel, table=True):
    """User model with organization membership and role.

    Extended with authentication fields for fastapi-users integration.
    Note: SQLModel with table=True doesn't support Pydantic validators.
    Input validation should be handled at the API layer.
    """

    org_id: UUID = Field(foreign_key="org.id", index=True)
    display_name: str = Field(max_length=100)
    email: str = Field(max_length=255, unique=True, index=True)
    role: UserRole = Field(default=UserRole.MEMBER)

    # Authentication fields (added via migration)
    hashed_password: str = Field(default="")
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False)

    # Relationships
    org: "Org" = Relationship(back_populates="users")
    messages: List["Message"] = Relationship(back_populates="user")

    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role."""
        return self.role == role or self.is_superuser

    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.has_role(UserRole.ADMIN)
