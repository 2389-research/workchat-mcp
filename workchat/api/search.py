# ABOUTME: Search API endpoints for full-text search
# ABOUTME: Handles message search with FTS5 and channel scoping

import re
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..auth import UserDB, current_active_user
from ..database import get_session
from ..models import Channel
from ..repositories.search import SearchRepository
from ..schemas.search import SearchResponse, SearchResult

router = APIRouter(prefix="/search", tags=["search"])


def parse_search_scope(scope: Optional[str]) -> tuple[Optional[str], Optional[UUID]]:
    """
    Parse search scope parameter.

    Args:
        scope: Scope string like "channel:uuid" or None

    Returns:
        Tuple of (scope_type, scope_value)
    """
    if not scope:
        return None, None

    if scope.startswith("channel:"):
        channel_id_str = scope[8:]  # Remove "channel:" prefix
        try:
            channel_id = UUID(channel_id_str)
            return "channel", channel_id
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid channel ID in scope: {channel_id_str}"
            )

    raise HTTPException(
        status_code=400, detail=f"Invalid scope format: {scope}. Use 'channel:uuid'"
    )


@router.get("/", response_model=SearchResponse)
def search_messages(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    scope: Optional[str] = Query(
        default=None, description="Search scope (e.g., channel:uuid)"
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Results to skip"),
    user: UserDB = Depends(current_active_user),
    session: Session = Depends(get_session),
):
    """
    Search messages using full-text search.

    Supports scoping by channel. Results are filtered by user's organization access.
    """
    # Parse search scope
    scope_type, scope_value = parse_search_scope(scope)

    # If searching within a specific channel, verify user has access
    channel_id = None
    if scope_type == "channel":
        channel_id = scope_value

        # Verify channel exists and user has access to it
        channel = session.exec(
            select(Channel).where(
                Channel.id == channel_id,
                Channel.org_id == user.org_id,  # Ensure user's org
            )
        ).first()

        if not channel:
            raise HTTPException(
                status_code=404, detail="Channel not found or access denied"
            )

    # Sanitize search query to prevent FTS injection
    # Remove special FTS characters that could cause issues
    sanitized_query = re.sub(r"[^\w\s\-\+\*]", " ", q).strip()
    if not sanitized_query:
        raise HTTPException(
            status_code=400, detail="Search query contains no valid terms"
        )

    # Perform the search
    search_repo = SearchRepository(session)

    try:
        messages = search_repo.search_messages(
            query=sanitized_query,
            channel_id=channel_id,
            limit=limit,
            offset=offset,
        )
    except Exception:
        # Log the error and return user-friendly message
        raise HTTPException(status_code=400, detail="Invalid search query format")

    # Filter results by user's organization access
    # (Additional security layer beyond channel filtering)
    filtered_messages = []
    for message in messages:
        # Get the message's channel to verify org access
        msg_channel = session.exec(
            select(Channel).where(
                Channel.id == message.channel_id,
                Channel.org_id == user.org_id,  # Ensure same org
            )
        ).first()

        if msg_channel:
            filtered_messages.append(message)

    # Build search results with snippets
    results = []
    for message in filtered_messages:
        # Get search snippet
        snippet = search_repo.get_search_snippet(sanitized_query, message.id)

        result = SearchResult(
            message=message,
            snippet=snippet,
        )
        results.append(result)

    return SearchResponse(
        query=q,
        results=results,
        total_count=len(results),  # Simple count, could be optimized
        limit=limit,
        offset=offset,
        search_scope=scope,
    )
