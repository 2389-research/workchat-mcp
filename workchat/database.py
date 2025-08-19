# ABOUTME: Database configuration and session management
# ABOUTME: Sets up SQLite connection and creates engine for SQLModel

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Session, SQLModel, create_engine

# SQLite database URLs
DATABASE_URL = "sqlite:///./workchat.db"
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./workchat.db"

# Create engines - sync for general use, async for fastapi-users
engine = create_engine(DATABASE_URL, echo=True)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get sync database session."""
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


async def get_async_session():
    """Dependency to get async database session for fastapi-users."""
    async with AsyncSession(async_engine) as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
