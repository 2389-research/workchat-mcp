# ABOUTME: Server-sent events for real-time messaging
# ABOUTME: Handles presence updates, message broadcasts, and heartbeat management

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from .auth import UserDB, current_active_user
from .database import get_session
from .schemas import MessageRead

logger = logging.getLogger(__name__)


# Global connection manager
class ConnectionManager:
    """Manages SSE connections and broadcasts events to connected clients."""

    def __init__(self):
        self.connections: Dict[str, asyncio.Queue] = {}
        self.user_connections: Dict[str, List[str]] = {}  # user_id -> connection_ids

    async def connect(self, connection_id: str, user_id: str) -> asyncio.Queue:
        """Add a new SSE connection."""
        queue = asyncio.Queue()
        self.connections[connection_id] = queue

        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)

        logger.info(f"New SSE connection: {connection_id} for user {user_id}")
        return queue

    def disconnect(self, connection_id: str, user_id: str):
        """Remove an SSE connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

        if user_id in self.user_connections:
            self.user_connections[user_id] = [
                cid for cid in self.user_connections[user_id] if cid != connection_id
            ]
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"SSE connection closed: {connection_id} for user {user_id}")

    async def broadcast_to_all(self, event_type: str, data: dict):
        """Send an event to all connected clients."""
        if not self.connections:
            return

        message = self._format_sse_message(event_type, data)

        # Send to all connections
        for connection_id, queue in self.connections.items():
            try:
                await queue.put(message)
            except Exception as e:
                logger.error(f"Failed to send to connection {connection_id}: {e}")

    async def broadcast_to_user(self, user_id: str, event_type: str, data: dict):
        """Send an event to all connections for a specific user."""
        if user_id not in self.user_connections:
            return

        message = self._format_sse_message(event_type, data)

        for connection_id in self.user_connections[user_id]:
            if connection_id in self.connections:
                try:
                    await self.connections[connection_id].put(message)
                except Exception as e:
                    logger.error(
                        f"Failed to send to user {user_id} connection {connection_id}: {e}"
                    )

    def _format_sse_message(self, event_type: str, data: dict) -> str:
        """Format data as SSE message."""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    async def send_heartbeat(self):
        """Send heartbeat to all connections."""
        if not self.connections:
            return

        heartbeat = f": heartbeat {datetime.now(timezone.utc).isoformat()}\n\n"

        for connection_id, queue in self.connections.items():
            try:
                await queue.put(heartbeat)
            except Exception as e:
                logger.error(f"Failed to send heartbeat to {connection_id}: {e}")


# Global connection manager instance
manager = ConnectionManager()


async def event_stream_generator(user: UserDB, session: Session, connection_id: str):
    """Generate SSE events for a connected user."""
    queue = await manager.connect(connection_id, str(user.id))

    try:
        # Send initial presence update
        presence_data = {
            "user_id": str(user.id),
            "display_name": user.display_name,
            "status": "online",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # Yield directly instead of using queue for initial message
        yield manager._format_sse_message("presenceUpdate", presence_data)

        # Main event loop
        while True:
            try:
                # Wait for events with timeout for heartbeat
                message = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield message
            except asyncio.TimeoutError:
                # Send heartbeat
                heartbeat = f": heartbeat {datetime.now(timezone.utc).isoformat()}\n\n"
                yield heartbeat

    except asyncio.CancelledError:
        logger.info(f"SSE stream cancelled for user {user.id}")
    except Exception as e:
        logger.error(f"Error in SSE stream for user {user.id}: {e}")
    finally:
        manager.disconnect(connection_id, str(user.id))


def get_event_stream(
    user: UserDB = Depends(current_active_user), session: Session = Depends(get_session)
):
    """SSE endpoint for real-time events."""
    connection_id = str(uuid.uuid4())

    return StreamingResponse(
        event_stream_generator(user, session, connection_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


async def broadcast_new_message(message: MessageRead):
    """Broadcast a new message to all connected clients."""
    data = {
        "id": str(message.id),
        "channel_id": str(message.channel_id),
        "user_id": str(message.user_id),
        "thread_id": str(message.thread_id) if message.thread_id else None,
        "body": message.body,
        "created_at": message.created_at.isoformat(),
        "edited_at": message.edited_at.isoformat() if message.edited_at else None,
        "version": message.version,
    }

    await manager.broadcast_to_all("newMessage", data)


async def broadcast_message_updated(message: MessageRead):
    """Broadcast a message update to all connected clients."""
    data = {
        "id": str(message.id),
        "channel_id": str(message.channel_id),
        "user_id": str(message.user_id),
        "thread_id": str(message.thread_id) if message.thread_id else None,
        "body": message.body,
        "created_at": message.created_at.isoformat(),
        "edited_at": message.edited_at.isoformat() if message.edited_at else None,
        "version": message.version,
    }

    await manager.broadcast_to_all("messageUpdated", data)
