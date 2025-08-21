# ABOUTME: Audit log API endpoints
# ABOUTME: Admin-only endpoints for viewing audit logs and change history

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select

from ..auth import UserDB, current_active_user
from ..database import get_session
from ..models import AuditLog, UserRole
from ..schemas import AuditLogListResponse, AuditLogRead

router = APIRouter(prefix="/audit", tags=["audit"])


def require_admin_user(user: UserDB = Depends(current_active_user)) -> UserDB:
    """Dependency to ensure only admin users can access audit endpoints."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Admin access required to view audit logs"
        )
    return user


@router.get("/", response_model=AuditLogListResponse)
def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=200, description="Max results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    entity_type: Optional[str] = Query(
        default=None, description="Filter by entity type"
    ),
    entity_id: Optional[UUID] = Query(default=None, description="Filter by entity ID"),
    action: Optional[str] = Query(default=None, description="Filter by action type"),
    user_id: Optional[UUID] = Query(default=None, description="Filter by user ID"),
    admin_user: UserDB = Depends(require_admin_user),
    session: Session = Depends(get_session),
) -> AuditLogListResponse:
    """
    List audit logs with optional filtering.

    Admin-only endpoint that returns audit log entries with pagination and filtering.
    Results are ordered by creation date (newest first).
    """
    # Build base query with direct organization isolation
    query = select(AuditLog).where(AuditLog.org_id == admin_user.org_id)
    count_query = select(func.count(AuditLog.id)).where(
        AuditLog.org_id == admin_user.org_id
    )

    # Apply filters
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
        count_query = count_query.where(AuditLog.entity_type == entity_type)

    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
        count_query = count_query.where(AuditLog.entity_id == entity_id)

    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)
        count_query = count_query.where(AuditLog.user_id == user_id)

    # Order by newest first and apply pagination
    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)

    # Execute queries
    audit_logs = session.exec(query).all()
    total_count = session.exec(count_query).first() or 0

    return AuditLogListResponse(
        audit_logs=[
            AuditLogRead.model_validate(log.model_dump()) for log in audit_logs
        ],
        total_count=total_count,
        limit=limit,
        offset=offset,
    )


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogRead])
def get_entity_audit_history(
    entity_type: str,
    entity_id: UUID,
    limit: int = Query(default=100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    admin_user: UserDB = Depends(require_admin_user),
    session: Session = Depends(get_session),
) -> List[AuditLogRead]:
    """
    Get complete audit history for a specific entity.

    Returns audit log entries for the specified entity with pagination,
    ordered chronologically (oldest first) to show the evolution of changes.
    Only returns audit logs from the admin user's organization.
    """
    # Direct organization isolation using org_id
    audit_logs = session.exec(
        select(AuditLog)
        .where(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
            AuditLog.org_id == admin_user.org_id,
        )
        .order_by(AuditLog.created_at.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    return [AuditLogRead.model_validate(log.model_dump()) for log in audit_logs]
