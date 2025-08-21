# ABOUTME: Audit service for tracking entity changes
# ABOUTME: Handles JSON diff generation and audit log creation

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException, Request
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
        org_id: UUID,
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
            org_id: ID of the organization (for isolation)
            action: Type of action ("create", "update", "delete")
            old_values: Previous values (for updates/deletes)
            new_values: New values (for creates/updates)
            request: Optional FastAPI request for metadata

        Returns:
            Created AuditLog instance
        """
        # Validate input parameters
        self._validate_audit_params(entity_type, action)
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            org_id=org_id,
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
        # Note: Caller is responsible for committing the transaction
        return audit_log

    def track_update(
        self,
        entity: BaseModel,
        old_data: Dict[str, Any],
        user_id: UUID,
        org_id: UUID,
        request: Optional[Request] = None,
    ) -> Optional[AuditLog]:
        """Track an update to an entity by comparing old and new values.

        Args:
            entity: The updated entity instance
            old_data: Dictionary of old field values
            user_id: ID of the user who made the change
            org_id: ID of the organization (for isolation)
            request: Optional FastAPI request for metadata

        Returns:
            Created AuditLog instance
        """
        # Convert entity to dict for comparison
        new_data = self.entity_to_dict(entity)

        # Calculate diff - only include changed fields
        old_values = {}
        new_values = {}

        for field, new_value in new_data.items():
            old_value = old_data.get(field)
            if old_value != new_value:
                old_values[field] = old_value
                new_values[field] = new_value

        # Don't create audit log if nothing actually changed
        if not old_values and not new_values:
            return None

        return self.create_audit_log(
            entity_type=entity.__class__.__name__.lower(),
            entity_id=entity.id,
            user_id=user_id,
            org_id=org_id,
            action="update",
            old_values=old_values if old_values else None,
            new_values=new_values if new_values else None,
            request=request,
        )

    def entity_to_dict(self, entity: BaseModel) -> Dict[str, Any]:
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

    def _validate_audit_params(self, entity_type: str, action: str) -> None:
        """Validate audit log parameters."""
        valid_actions = {"create", "update", "delete"}
        if action not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action '{action}'. Must be one of: {valid_actions}",
            )

        if not entity_type or len(entity_type.strip()) == 0:
            raise HTTPException(status_code=400, detail="Entity type cannot be empty")

        if len(entity_type) > 50:
            raise HTTPException(
                status_code=400, detail="Entity type cannot exceed 50 characters"
            )
