# ABOUTME: Organization domain model
# ABOUTME: Defines the top-level tenant structure for multi-org chat system

from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class Org(BaseModel, table=True):
    """Organization model representing a tenant in the multi-org system.

    Note: SQLModel with table=True doesn't support Pydantic validators.
    Input validation should be handled at the API layer.
    """

    name: str = Field(max_length=100, unique=True, index=True)

    # Relationship to users
    users: List["User"] = Relationship(back_populates="org")
