# ABOUTME: Business logic for MCP tools - separated for easier testing
# ABOUTME: Contains the core functionality without FastMCP decorators

from typing import List
from uuid import UUID

from sqlmodel import Session, select

from ..database import engine
from ..models import Channel, Message, User
from ..repositories.search import SearchRepository
from ..services.audit import AuditService


def post_message_logic(
    channel_id: str, body: str, user_email: str = "admin@example.com"
) -> str:
    """Post a message to a channel - core business logic."""
    # Validate inputs
    if not body or not body.strip():
        raise ValueError("Message body cannot be empty")
    if len(body.strip()) > 10000:  # Reasonable message length limit
        raise ValueError("Message body too long (max 10,000 characters)")
    if not channel_id or not channel_id.strip():
        raise ValueError("Channel ID cannot be empty")
    if not user_email or not user_email.strip():
        raise ValueError("User email cannot be empty")

    with Session(engine) as session:
        try:
            # Find user by email
            user = session.exec(select(User).where(User.email == user_email)).first()
            if not user:
                raise ValueError(f"User with email {user_email} not found")

            # Parse and validate channel_id UUID
            try:
                channel_uuid = UUID(channel_id)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid channel ID format: {channel_id}")

            # Verify channel exists and user has access
            channel = session.exec(
                select(Channel).where(
                    Channel.id == channel_uuid, Channel.org_id == user.org_id
                )
            ).first()
            if not channel:
                raise ValueError(f"Channel {channel_id} not found or access denied")

            # Create root message (thread_id will be set to message id)
            message = Message(
                channel_id=channel_uuid,
                user_id=user.id,
                thread_id=None,  # Will be set to message.id after creation
                body=body.strip(),
            )

            session.add(message)
            session.flush()  # Get the ID

            # Set thread_id to message id for root messages
            message.thread_id = message.id

            # Create audit log for message creation
            audit_service = AuditService(session)
            audit_service.create_audit_log(
                entity_type="message",
                entity_id=message.id,
                user_id=user.id,
                org_id=user.org_id,
                action="create",
                new_values=audit_service.entity_to_dict(message),
            )

            session.commit()
            session.refresh(message)

            return str(message.id)
        except Exception:
            session.rollback()
            raise


def search_logic(query: str, user_email: str = "admin@example.com") -> List[str]:
    """Search messages using full-text search - core business logic."""
    # Validate inputs
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    if len(query.strip()) > 1000:  # Reasonable query length limit
        raise ValueError("Search query too long (max 1,000 characters)")
    if not user_email or not user_email.strip():
        raise ValueError("User email cannot be empty")

    with Session(engine) as session:
        try:
            # Find user by email
            user = session.exec(select(User).where(User.email == user_email)).first()
            if not user:
                raise ValueError(f"User with email {user_email} not found")

            # Use search repository to find messages
            search_repo = SearchRepository(session)
            results = search_repo.search_messages(query, limit=10)

            # Filter results by organization using a single JOIN query
            if not results:
                filtered_results = []
            else:
                message_ids = [message.id for message in results]
                # Single query to get messages that belong to user's organization
                filtered_results = session.exec(
                    select(Message)
                    .join(Channel, Message.channel_id == Channel.id)
                    .where(Message.id.in_(message_ids), Channel.org_id == user.org_id)
                ).all()

                # Preserve FTS ranking order
                id_to_message = {msg.id: msg for msg in filtered_results}
                filtered_results = [
                    id_to_message[msg.id] for msg in results if msg.id in id_to_message
                ]

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

            # Audit the search operation
            audit_service = AuditService(session)
            audit_service.create_audit_log(
                entity_type="search",
                entity_id=user.id,  # Using user ID as entity ID for search operations
                user_id=user.id,
                org_id=user.org_id,
                action="search",
                new_values={
                    "query": query,
                    "results_count": len(filtered_results),
                    "via": "mcp",
                },
            )
            session.commit()

            return snippets
        except Exception:
            session.rollback()
            raise


def add_reaction_logic(
    message_id: str, emoji: str, user_email: str = "admin@example.com"
) -> bool:
    """Add a reaction to a message - core business logic."""
    # Validate inputs
    if not message_id or not message_id.strip():
        raise ValueError("Message ID cannot be empty")
    if not emoji or not emoji.strip():
        raise ValueError("Emoji cannot be empty")
    if len(emoji.strip()) > 10:  # Reasonable emoji length limit
        raise ValueError("Emoji too long (max 10 characters)")
    if not user_email or not user_email.strip():
        raise ValueError("User email cannot be empty")

    with Session(engine) as session:
        try:
            # Find user by email
            user = session.exec(select(User).where(User.email == user_email)).first()
            if not user:
                raise ValueError(f"User with email {user_email} not found")

            # Parse and validate message_id UUID
            try:
                message_uuid = UUID(message_id)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid message ID format: {message_id}")

            # Find message and verify access
            message = session.exec(
                select(Message).where(Message.id == message_uuid)
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

            # Audit the reaction operation
            audit_service = AuditService(session)
            audit_service.create_audit_log(
                entity_type="reaction",
                entity_id=message.id,
                user_id=user.id,
                org_id=user.org_id,
                action="create",
                new_values={
                    "message_id": str(message.id),
                    "emoji": emoji,
                    "via": "mcp",
                },
            )
            session.commit()

            # For now, just return True - reactions would need their own table
            # This is a placeholder implementation for the MCP demo
            return True
        except Exception:
            session.rollback()
            raise
