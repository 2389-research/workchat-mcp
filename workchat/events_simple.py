# ABOUTME: Simplified SSE implementation for testing
# ABOUTME: Test version without infinite loops

import json
from datetime import datetime, timezone

from fastapi import Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from .auth import UserDB, current_active_user
from .database import get_session


def simple_event_stream(
    user: UserDB = Depends(current_active_user), session: Session = Depends(get_session)
):
    """Simple SSE endpoint that sends one event and closes."""

    def generate():
        # Send initial presence update
        presence_data = {
            "user_id": str(user.id),
            "display_name": user.display_name,
            "status": "online",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        event = f"event: presenceUpdate\ndata: {json.dumps(presence_data)}\n\n"
        yield event

        # Send one heartbeat and close
        heartbeat = f": heartbeat {datetime.now(timezone.utc).isoformat()}\n\n"
        yield heartbeat

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
