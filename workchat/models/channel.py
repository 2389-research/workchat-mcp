# ABOUTME: Channel domain model for organizing conversations
# ABOUTME: Defines channels within organizations with system/user channel types

from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .message import Message
    from .org import Org


class Channel(BaseModel, table=True):
    """Channel model for organizing conversations within an organization.

    Channels can be regular user-created channels or system channels.
    Channel names must be unique within an organization.
    """

    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_channel_name_per_org"),
    )

    org_id: UUID = Field(foreign_key="org.id", index=True)
    name: str = Field(max_length=100, index=True)
    description: str = Field(max_length=500, default="")
    is_system: bool = Field(default=False)

    # Relationships
    org: "Org" = Relationship(back_populates="channels")
    messages: List["Message"] = Relationship(back_populates="channel")
