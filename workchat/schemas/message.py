# ABOUTME: Message request/response schemas
# ABOUTME: Pydantic models for message posting and thread retrieval

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema with common fields."""

    body: str = Field(
        ..., min_length=1, max_length=10000, description="Message content"
    )


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    thread_id: Optional[UUID] = Field(
        default=None, description="Thread ID for replies, null for root messages"
    )


class MessageUpdate(BaseModel):
    """Schema for updating/editing an existing message."""

    body: str = Field(
        ..., min_length=1, max_length=10000, description="Updated message content"
    )
    version: int = Field(..., description="Current version for optimistic locking")


class MessageRead(MessageBase):
    """Schema for message API responses."""

    id: UUID
    channel_id: UUID
    user_id: UUID
    thread_id: Optional[UUID]
    created_at: datetime
    edited_at: Optional[datetime]
    version: int

    class Config:
        from_attributes = True
