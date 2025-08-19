# ABOUTME: Channel domain model for organizing conversations
# ABOUTME: Defines channels within organizations with system/user channel types

from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .org import Org


class Channel(BaseModel, table=True):
    """Channel model for organizing conversations within an organization.

    Channels can be regular user-created channels or system channels.
    Channel names must be unique within an organization.
    """

    org_id: UUID = Field(foreign_key="org.id", index=True)
    name: str = Field(max_length=100, index=True)
    description: str = Field(max_length=500, default="")
    is_system: bool = Field(default=False)

    # Relationship to organization
    org: "Org" = Relationship(back_populates="channels")
