# ABOUTME: Database configuration and session management
# ABOUTME: Sets up SQLite connection and creates engine for SQLModel

from sqlmodel import Session, SQLModel, create_engine

# SQLite database URL - use in-memory for tests, file for dev
DATABASE_URL = "sqlite:///./workchat.db"

# Create engine with echo for development
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session
