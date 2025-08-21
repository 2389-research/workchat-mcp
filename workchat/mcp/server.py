# ABOUTME: FastMCP server implementation for WorkChat
# ABOUTME: Exposes chat operations as MCP tools for AI assistant integration

from typing import List
from uuid import UUID

from fastmcp import FastMCP
from sqlmodel import Session, select

from ..database import engine
from ..models import Channel, Message, User
from ..repositories.search import SearchRepository

# Initialize FastMCP server
mcp = FastMCP("WorkChat")


@mcp.tool()
def post_message(
    channel_id: str, body: str, user_email: str = "admin@example.com"
) -> str:
    """Post a message to a channel.

    Args:
        channel_id: The ID of the channel to post to
        body: The message content
        user_email: Email of user posting (defaults to admin)

    Returns:
        The ID of the created message
    """
    with Session(engine) as session:
        # Find user by email
        user = session.exec(select(User).where(User.email == user_email)).first()
        if not user:
            raise ValueError(f"User with email {user_email} not found")

        # Verify channel exists and user has access
        channel = session.exec(
            select(Channel).where(
                Channel.id == UUID(channel_id), Channel.org_id == user.org_id
            )
        ).first()
        if not channel:
            raise ValueError(f"Channel {channel_id} not found or access denied")

        # Create root message (thread_id will be set to message id)
        message = Message(
            channel_id=UUID(channel_id),
            user_id=user.id,
            thread_id=None,  # Will be set to message.id after creation
            body=body.strip(),
        )

        session.add(message)
        session.flush()  # Get the ID

        # Set thread_id to message id for root messages
        message.thread_id = message.id

        session.commit()
        session.refresh(message)

        return str(message.id)


@mcp.tool()
def search(query: str, user_email: str = "admin@example.com") -> List[str]:
    """Search messages using full-text search.

    Args:
        query: Search query string
        user_email: Email of user searching (for access control)

    Returns:
        List of message snippets matching the search
    """
    with Session(engine) as session:
        # Find user by email
        user = session.exec(select(User).where(User.email == user_email)).first()
        if not user:
            raise ValueError(f"User with email {user_email} not found")

        # Use search repository to find messages
        search_repo = SearchRepository(session)
        results = search_repo.search_messages(query, limit=10)

        # Filter results by organization (messages from channels user has access to)
        filtered_results = []
        for message in results:
            # Check if message's channel belongs to user's organization
            channel = session.exec(
                select(Channel).where(
                    Channel.id == message.channel_id, Channel.org_id == user.org_id
                )
            ).first()
            if channel:
                filtered_results.append(message)

        # Return message snippets
        snippets = []
        for result in filtered_results:
            # Truncate long messages for snippet
            snippet = result.body[:100]
            if len(result.body) > 100:
                snippet += "..."
            snippets.append(
                f"[{result.created_at.strftime('%Y-%m-%d %H:%M')}] {snippet}"
            )

        return snippets


@mcp.tool()
def add_reaction(
    message_id: str, emoji: str, user_email: str = "admin@example.com"
) -> bool:
    """Add a reaction to a message.

    Args:
        message_id: ID of the message to react to
        emoji: Emoji reaction (e.g. "👍", "❤️")
        user_email: Email of user adding reaction

    Returns:
        True if reaction was added successfully
    """
    with Session(engine) as session:
        # Find user by email
        user = session.exec(select(User).where(User.email == user_email)).first()
        if not user:
            raise ValueError(f"User with email {user_email} not found")

        # Find message and verify access
        message = session.exec(
            select(Message).where(Message.id == UUID(message_id))
        ).first()
        if not message:
            raise ValueError(f"Message {message_id} not found")

        # Verify user has access to message's channel
        channel = session.exec(
            select(Channel).where(
                Channel.id == message.channel_id, Channel.org_id == user.org_id
            )
        ).first()
        if not channel:
            raise ValueError("Access denied to message's channel")

        # For now, just return True - reactions would need their own table
        # This is a placeholder implementation for the MCP demo
        return True


def main():
    """Main entry point for MCP server."""
    # Run FastMCP stdio transport
    mcp.run()


if __name__ == "__main__":
    main()
