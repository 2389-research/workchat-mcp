# ABOUTME: Pytest configuration and shared fixtures
# ABOUTME: Database setup, test client, and auth fixtures for testing

import httpx
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session
from sqlmodel import create_engine as sqlmodel_create_engine

from workchat.app import app
from workchat.auth import current_active_user
from workchat.database import get_session
from workchat.models import BaseModel, Org, User, UserRole

# Create in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = sqlmodel_create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Global test session for sharing between fixtures and API calls
_test_session = None


def override_get_session():
    """Override database session for testing."""
    global _test_session
    if _test_session is None:
        _test_session = Session(engine)
    try:
        yield _test_session
    except Exception:
        _test_session.rollback()
        raise


# Override the database dependency
app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="function")
def session():
    """Create a fresh database session for each test."""
    global _test_session

    # Create tables with all constraints (including unique constraint from model definition)
    BaseModel.metadata.create_all(bind=engine)

    # Reset the global session for this test
    if _test_session:
        _test_session.close()
    _test_session = Session(engine)

    yield _test_session

    # Clean up
    _test_session.close()
    _test_session = None
    BaseModel.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client for SSE testing."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture
def test_org(session: Session):
    """Create a test organization."""
    org = Org(name="Test Organization")
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


@pytest.fixture
def test_user(session: Session, test_org: Org):
    """Create a test user in the test organization."""
    user = User(
        org_id=test_org.id,
        display_name="Test User",
        email="test@example.com",
        role=UserRole.MEMBER,
        hashed_password="$2b$12$test_hashed_password",
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_user_headers(test_user: User):
    """Create authorization headers for test user and override auth dependency."""

    # Override the current_active_user dependency to return our test user
    def override_current_active_user():
        return test_user

    app.dependency_overrides[current_active_user] = override_current_active_user

    # Return empty headers since auth is mocked via dependency override
    yield {}

    # Clean up the override after the test
    if current_active_user in app.dependency_overrides:
        del app.dependency_overrides[current_active_user]
