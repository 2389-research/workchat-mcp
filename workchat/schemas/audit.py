# ABOUTME: Audit log response schemas
# ABOUTME: Pydantic models for audit API responses

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogRead(BaseModel):
    """Audit log response schema."""

    id: UUID
    created_at: datetime
    entity_type: str
    entity_id: UUID
    user_id: UUID
    action: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    endpoint: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class AuditLogListResponse(BaseModel):
    """Response for audit log listing endpoint."""

    audit_logs: List[AuditLogRead] = Field(
        default=[], description="List of audit log entries"
    )
    total_count: int = Field(
        default=0, description="Total number of audit logs (for pagination)"
    )
    limit: int = Field(description="Maximum results returned")
    offset: int = Field(description="Number of results skipped")
