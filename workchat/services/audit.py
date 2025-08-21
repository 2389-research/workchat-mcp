# ABOUTME: Audit service for tracking entity changes
# ABOUTME: Handles JSON diff generation and audit log creation

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import Request
from sqlmodel import Session

from ..models import AuditLog, BaseModel


class AuditService:
    """Service for creating audit log entries."""

    def __init__(self, session: Session):
        self.session = session

    def create_audit_log(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: UUID,
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Create an audit log entry for an entity change.

        Args:
            entity_type: Type of entity (e.g., "message", "channel")
            entity_id: ID of the entity that was changed
            user_id: ID of the user who made the change
            action: Type of action ("create", "update", "delete")
            old_values: Previous values (for updates/deletes)
            new_values: New values (for creates/updates)
            request: Optional FastAPI request for metadata

        Returns:
            Created AuditLog instance
        """
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
        )

        # Add request metadata if available
        if request:
            audit_log.endpoint = f"{request.method} {request.url.path}"
            audit_log.user_agent = request.headers.get("user-agent")
            audit_log.ip_address = self._get_client_ip(request)

        self.session.add(audit_log)
        return audit_log

    def track_update(
        self,
        entity: BaseModel,
        old_data: Dict[str, Any],
        user_id: UUID,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Track an update to an entity by comparing old and new values.

        Args:
            entity: The updated entity instance
            old_data: Dictionary of old field values
            user_id: ID of the user who made the change
            request: Optional FastAPI request for metadata

        Returns:
            Created AuditLog instance
        """
        # Convert entity to dict for comparison
        new_data = self._entity_to_dict(entity)

        # Calculate diff - only include changed fields
        old_values = {}
        new_values = {}

        for field, new_value in new_data.items():
            old_value = old_data.get(field)
            if old_value != new_value:
                old_values[field] = old_value
                new_values[field] = new_value

        return self.create_audit_log(
            entity_type=entity.__class__.__name__.lower(),
            entity_id=entity.id,
            user_id=user_id,
            action="update",
            old_values=old_values if old_values else None,
            new_values=new_values if new_values else None,
            request=request,
        )

    def _entity_to_dict(self, entity: BaseModel) -> Dict[str, Any]:
        """Convert entity to dictionary with JSON-serializable values."""
        data = {}
        for field_name in entity.__class__.model_fields:
            value = getattr(entity, field_name)
            # Convert UUIDs to strings for JSON serialization
            if isinstance(value, UUID):
                value = str(value)
            # Convert datetime to ISO string
            elif hasattr(value, "isoformat"):
                value = value.isoformat()
            data[field_name] = value
        return data

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP from request, handling proxies."""
        # Check for forwarded headers first (common in production)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return None
