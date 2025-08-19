# ABOUTME: Authentication tests
# ABOUTME: Tests JWT auth routes, user registration, and protected endpoints

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine

from workchat.app import app
from workchat.auth.models import UserDB
from workchat.database import get_session
from workchat.models import Org, UserRole


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="override_get_session")
def override_get_session_fixture(session: Session):
    """Override database session for testing."""

    def _get_session():
        yield session

    app.dependency_overrides[get_session] = _get_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(name="org")
def org_fixture(session: Session, override_get_session):
    """Create test organization."""
    org = Org(name="Test Organization")
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session, org: Org, override_get_session):
    """Create test user."""
    user = UserDB(
        org_id=org.id,
        display_name="Test User",
        email="test@example.com",
        role=UserRole.ADMIN,
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest_asyncio.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient, test_user: UserDB):
    """Create authenticated async test client."""
    # Login to get JWT token
    response = await async_client.post(
        "/auth/jwt/login", data={"username": test_user.email, "password": "secret"}
    )

    assert response.status_code == 200
    token_data = response.json()
    access_token = token_data["access_token"]

    # Set authorization header for subsequent requests
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


def test_unauthenticated_orgs_me(override_get_session):
    """Test that /orgs/me returns 401 without authentication."""
    with TestClient(app) as client:
        response = client.get("/orgs/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_orgs_me(
    authenticated_client: AsyncClient, test_user: UserDB
):
    """Test that /orgs/me returns 200 with authentication."""
    response = await authenticated_client.get("/orgs/me")
    assert response.status_code == 200

    data = response.json()
    assert data["org_id"] == str(test_user.org_id)
    assert data["user_id"] == str(test_user.id)
    assert data["display_name"] == test_user.display_name
    assert data["role"] == test_user.role.value


@pytest.mark.asyncio
async def test_jwt_login_success(async_client: AsyncClient, test_user: UserDB):
    """Test successful JWT login."""
    response = await async_client.post(
        "/auth/jwt/login", data={"username": test_user.email, "password": "secret"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_jwt_login_invalid_credentials(
    async_client: AsyncClient, test_user: UserDB
):
    """Test JWT login with invalid credentials."""
    response = await async_client.post(
        "/auth/jwt/login",
        data={"username": test_user.email, "password": "wrong-password"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_user_registration(async_client: AsyncClient, org: Org):
    """Test user registration."""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "org_id": str(org.id),
        "display_name": "New User",
        "role": "member",
    }

    response = await async_client.post("/auth/register", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["display_name"] == user_data["display_name"]
    assert data["role"] == user_data["role"]
    assert "id" in data


def test_app_endpoints_exist():
    """Test that basic app endpoints exist."""
    with TestClient(app) as client:
        # Root endpoint
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello from WorkChat!"}

        # Health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
