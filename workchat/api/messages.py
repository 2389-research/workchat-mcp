# ABOUTME: Message and threading API endpoints
# ABOUTME: Handles message posting, replies, edits, and thread retrieval

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..auth import UserDB, current_active_user
from ..database import get_session
from ..models import Channel, Message
from ..schemas import MessageCreate, MessageRead, MessageUpdate

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageRead, status_code=201)
def create_message(
    channel_id: UUID,
    message_data: MessageCreate,
    user: UserDB = Depends(current_active_user),
    session: Session = Depends(get_session),
):
    """Post a new message or reply to an existing thread.

    If thread_id is None, creates a new thread (root message).
    If thread_id is provided, creates a reply in that thread.
    """
    # Verify channel exists and user has access to it
    channel = session.exec(
        select(Channel).where(
            Channel.id == channel_id,
            Channel.org_id == user.org_id,
        )
    ).first()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # If replying to a thread, verify the thread exists in this channel
    if message_data.thread_id:
        thread_root = session.exec(
            select(Message).where(
                Message.id == message_data.thread_id,
                Message.channel_id == channel_id,
            )
        ).first()

        if not thread_root:
            raise HTTPException(
                status_code=404, detail="Thread not found in this channel"
            )

    # Create the message
    message = Message(
        channel_id=channel_id,
        user_id=user.id,
        thread_id=message_data.thread_id,
        body=message_data.body.strip(),
    )

    try:
        session.add(message)
        session.commit()

        # For root messages, set thread_id to the message's own id
        if message_data.thread_id is None:
            message.thread_id = message.id
            session.commit()

        session.refresh(message)
        return message

    except IntegrityError as e:
        session.rollback()
        if "FOREIGN KEY constraint failed" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Invalid channel or user ID",
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while creating message",
            )


@router.get("/threads/{thread_id}", response_model=List[MessageRead])
def get_thread_messages(
    thread_id: UUID,
    channel_id: UUID,
    user: UserDB = Depends(current_active_user),
    session: Session = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
):
    """Get all messages in a thread, paginated and ordered chronologically."""
    # Verify channel exists and user has access to it
    channel = session.exec(
        select(Channel).where(
            Channel.id == channel_id,
            Channel.org_id == user.org_id,
        )
    ).first()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Verify thread exists in this channel
    thread_root = session.exec(
        select(Message).where(
            Message.id == thread_id,
            Message.channel_id == channel_id,
        )
    ).first()

    if not thread_root:
        raise HTTPException(status_code=404, detail="Thread not found in this channel")

    # Get all messages in the thread
    messages = session.exec(
        select(Message)
        .where(
            Message.thread_id == thread_id,
            Message.channel_id == channel_id,
        )
        .order_by(Message.created_at)
        .offset(offset)
        .limit(limit)
    ).all()

    return messages


@router.patch("/{message_id}", response_model=MessageRead)
def update_message(
    message_id: UUID,
    message_data: MessageUpdate,
    user: UserDB = Depends(current_active_user),
    session: Session = Depends(get_session),
):
    """Edit an existing message with optimistic locking."""
    # Get the message
    message = session.exec(select(Message).where(Message.id == message_id)).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify user has access to the message's channel
    channel = session.exec(
        select(Channel).where(
            Channel.id == message.channel_id,
            Channel.org_id == user.org_id,
        )
    ).first()

    if not channel:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only allow users to edit their own messages
    if message.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="You can only edit your own messages"
        )

    # Optimistic locking check
    if message.version != message_data.version:
        raise HTTPException(
            status_code=409,
            detail=f"Message was modified by another user. Current version is {message.version}",
        )

    # Update the message
    message.body = message_data.body.strip()
    message.edited_at = datetime.now(timezone.utc)
    message.version += 1

    try:
        session.commit()
        session.refresh(message)
        return message

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while updating message",
        )
