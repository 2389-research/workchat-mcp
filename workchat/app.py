# ABOUTME: FastAPI application entry point
# ABOUTME: Configures routes, middleware, and application lifecycle

from fastapi import Depends, FastAPI

from .api import channels_router, messages_router
from .auth import (
    UserCreate,
    UserDB,
    UserRead,
    auth_backend,
    current_active_user,
    fastapi_users,
)
from .events import get_event_stream
from .events_simple import simple_event_stream

app = FastAPI(
    title="WorkChat",
    description="A real-time team chat application",
    version="0.1.0",
)

# Include auth routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Include API routes
app.include_router(channels_router, prefix="/api")
app.include_router(messages_router, prefix="/api")

# SSE endpoint
app.get("/events", response_class=None)(get_event_stream)
app.get("/events-simple", response_class=None)(simple_event_stream)


@app.get("/")
async def root():
    return {"message": "Hello from WorkChat!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/orgs/me")
async def get_my_org(user: UserDB = Depends(current_active_user)):
    """Get current user's organization info."""
    return {
        "org_id": user.org_id,
        "user_id": user.id,
        "display_name": user.display_name,
        "role": user.role,
    }
