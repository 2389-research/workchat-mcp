# ABOUTME: Search request and response schemas
# ABOUTME: Pydantic models for search API parameters and results

from typing import List, Optional

from pydantic import BaseModel, Field

from .message import MessageRead


class SearchParams(BaseModel):
    """Search query parameters."""

    q: str = Field(..., min_length=1, max_length=200, description="Search query")
    scope: Optional[str] = Field(
        default=None,
        description="Search scope, e.g., 'channel:uuid' to limit to specific channel",
    )
    limit: int = Field(
        default=50, ge=1, le=100, description="Maximum results to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class SearchResult(BaseModel):
    """Individual search result."""

    message: MessageRead
    snippet: Optional[str] = Field(
        default=None, description="Highlighted search snippet"
    )
    relevance_score: Optional[float] = Field(
        default=None, description="Relevance score"
    )


class SearchResponse(BaseModel):
    """Search API response."""

    query: str = Field(..., description="The search query that was executed")
    results: List[SearchResult] = Field(
        default=[], description="List of matching messages"
    )
    total_count: int = Field(default=0, description="Total number of matching results")
    limit: int = Field(..., description="Limit used in the query")
    offset: int = Field(..., description="Offset used in the query")
    search_scope: Optional[str] = Field(
        default=None, description="Search scope that was applied"
    )
