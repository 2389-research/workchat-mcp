# ABOUTME: Search repository for full-text search operations
# ABOUTME: Handles SQLite FTS5 queries and result processing

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, text

from ..models import Message


class SearchRepository:
    """Repository for full-text search operations."""

    def __init__(self, session: Session):
        self.session = session

    def search_messages(
        self,
        query: str,
        channel_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Message]:
        """
        Search messages using SQLite FTS5.

        Args:
            query: Search query string
            channel_id: Optional channel to limit search scope
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of matching messages ordered by relevance
        """
        # Build the SQL query
        base_query = """
            SELECT m.* FROM message m
            INNER JOIN message_fts fts ON m.id = fts.message_id
            WHERE message_fts MATCH :query
        """

        params = {"query": query, "limit": limit, "offset": offset}

        # Add channel filter if specified
        if channel_id:
            base_query += " AND m.channel_id = :channel_id"
            params["channel_id"] = str(channel_id)

        # Add ordering and pagination
        base_query += """
            ORDER BY fts.rank
            LIMIT :limit OFFSET :offset
        """

        # Execute the query and get message IDs first using FTS5
        fts_query = """
            SELECT message_id FROM message_fts
            WHERE message_fts MATCH :query
        """

        if channel_id:
            fts_query += " AND channel_id = :channel_id"

        fts_query += """
            ORDER BY rank
            LIMIT :limit OFFSET :offset
        """

        result = self.session.execute(text(fts_query), params)

        message_ids = [row[0] for row in result]

        # Now get the full Message objects using SQLModel
        if not message_ids:
            return []

        messages = self.session.exec(
            select(Message).where(Message.id.in_(message_ids))
        ).all()

        # Preserve FTS ranking order
        id_to_message = {msg.id: msg for msg in messages}
        return [
            id_to_message[msg_id] for msg_id in message_ids if msg_id in id_to_message
        ]

    def search_message_ids(
        self,
        query: str,
        channel_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[UUID]:
        """
        Search messages and return only IDs for lightweight operations.

        Args:
            query: Search query string
            channel_id: Optional channel to limit search scope
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of matching message IDs ordered by relevance
        """
        # Build the SQL query for IDs only using FTS5 directly
        fts_query = """
            SELECT message_id FROM message_fts
            WHERE message_fts MATCH :query
        """

        params = {"query": query, "limit": limit, "offset": offset}

        # Add channel filter if specified
        if channel_id:
            fts_query += " AND channel_id = :channel_id"
            params["channel_id"] = str(channel_id)

        # Add ordering and pagination
        fts_query += """
            ORDER BY rank
            LIMIT :limit OFFSET :offset
        """

        # Execute the query
        result = self.session.execute(text(fts_query), params)
        return [UUID(str(row[0])) for row in result]

    def get_search_snippet(self, query: str, message_id: UUID) -> Optional[str]:
        """
        Get a search result snippet with highlighted matches.

        Args:
            query: The search query used
            message_id: ID of the message to get snippet for

        Returns:
            Snippet with highlighted matches or None if not found
        """
        snippet_query = """
            SELECT snippet(message_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
            FROM message_fts
            WHERE message_fts MATCH :query AND message_id = :message_id
        """

        result = self.session.execute(
            text(snippet_query), {"query": query, "message_id": str(message_id)}
        )

        row = result.first()
        return row[0] if row else None
