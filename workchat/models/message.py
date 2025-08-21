# ABOUTME: Message domain model for storing chat messages and threads
# ABOUTME: Handles both root messages (which create threads) and replies within threads

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .channel import Channel
    from .user import User


class Message(BaseModel, table=True):
    """Message model for chat messages within channels.

    Messages can be either:
    - Root messages: thread_id equals the message id (self-referencing)
    - Reply messages: thread_id points to the root message's id

    Version column supports optimistic locking for edits.
    """

    channel_id: UUID = Field(foreign_key="channel.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    thread_id: Optional[UUID] = Field(
        default=None,
        foreign_key="message.id",  # Self-reference for thread integrity
        index=True,
    )
    body: str = Field(max_length=10000)
    edited_at: Optional[datetime] = Field(default=None)
    version: int = Field(default=1)

    # Relationships
    channel: "Channel" = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")
