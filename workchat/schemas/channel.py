# ABOUTME: Channel request/response schemas
# ABOUTME: Pydantic models for channel API endpoints

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChannelBase(BaseModel):
    """Base channel schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Channel name")
    description: str = Field(
        default="", max_length=500, description="Channel description"
    )
    is_system: bool = Field(
        default=False, description="Whether this is a system channel"
    )


class ChannelCreate(ChannelBase):
    """Schema for creating a new channel."""

    pass


class ChannelUpdate(BaseModel):
    """Schema for updating an existing channel."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_system: Optional[bool] = None


class ChannelRead(ChannelBase):
    """Schema for channel API responses."""

    id: UUID
    org_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
