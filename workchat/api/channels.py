# ABOUTME: Channel CRUD API endpoints
# ABOUTME: REST endpoints for channel creation, listing, and retrieval

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..auth import UserDB, current_active_user
from ..database import get_session
from ..models import Channel
from ..schemas import ChannelCreate, ChannelRead

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelRead, status_code=201)
def create_channel(
    channel_data: ChannelCreate,
    user: UserDB = Depends(current_active_user),
    session: Session = Depends(get_session),
):
    """Create a new channel in the current user's organization."""
    # Check if channel name already exists in this org
    existing = session.exec(
        select(Channel).where(
            Channel.org_id == user.org_id,
            Channel.name == channel_data.name,
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Channel with name '{channel_data.name}' already exists in this organization",
        )

    # Create new channel
    channel = Channel(
        org_id=user.org_id,
        name=channel_data.name,
        description=channel_data.description,
        is_system=channel_data.is_system,
    )

    session.add(channel)
    session.commit()
    session.refresh(channel)

    return channel


@router.get("/", response_model=List[ChannelRead])
def list_channels(
    user: UserDB = Depends(current_active_user),
    session: Session = Depends(get_session),
):
    """List all channels in the current user's organization."""
    channels = session.exec(
        select(Channel).where(Channel.org_id == user.org_id).order_by(Channel.name)
    ).all()

    return channels


@router.get("/{channel_id}", response_model=ChannelRead)
def get_channel(
    channel_id: UUID,
    user: UserDB = Depends(current_active_user),
    session: Session = Depends(get_session),
):
    """Get a specific channel by ID from the current user's organization."""
    channel = session.exec(
        select(Channel).where(
            Channel.id == channel_id,
            Channel.org_id == user.org_id,
        )
    ).first()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return channel
