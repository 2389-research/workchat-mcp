# ABOUTME: Audit log model for tracking changes to entities
# ABOUTME: Stores JSON diffs of modifications with metadata for compliance and debugging

from typing import Any, Dict, Optional
from uuid import UUID

from sqlmodel import JSON, Column, Field

from .base import BaseModel


class AuditLog(BaseModel, table=True):
    """Audit log for tracking changes to entities.

    Records changes made to any entity in the system with:
    - What was changed (entity_type, entity_id)
    - Who made the change (user_id)
    - When it was changed (created_at)
    - What changed (old_values, new_values as JSON diffs)
    - How it was changed (action: create, update, delete)
    """

    # What was changed
    entity_type: str = Field(
        max_length=50, index=True
    )  # e.g., "message", "channel", "user"
    entity_id: UUID = Field(index=True)

    # Who made the change and which organization
    user_id: UUID = Field(foreign_key="user.id", index=True)
    org_id: UUID = Field(foreign_key="org.id", index=True)

    # What kind of change
    action: str = Field(max_length=20, index=True)  # "create", "update", "delete"

    # Change details as JSON
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Additional context
    endpoint: Optional[str] = Field(default=None, max_length=200)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 max length
