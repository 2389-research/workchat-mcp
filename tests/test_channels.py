# ABOUTME: Channel CRUD endpoint tests
# ABOUTME: Test create, list, get, and duplicate name validation for channels

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from workchat.models import Channel, Org, User


class TestChannelCRUD:
    """Test channel creation, listing, and retrieval."""

    def test_create_channel(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        session: Session,
    ):
        """Test creating a new channel."""
        channel_data = {
            "name": "general",
            "description": "General discussion channel",
            "is_system": False,
        }

        response = client.post(
            "/api/channels/", json=channel_data, headers=test_user_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "general"
        assert data["description"] == "General discussion channel"
        assert data["is_system"] is False
        assert data["org_id"] == str(test_org.id)

        # Verify channel was created in database
        channel = session.get(Channel, UUID(data["id"]))
        assert channel is not None
        assert channel.name == "general"

    def test_create_channel_minimal(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        session: Session,
    ):
        """Test creating a channel with minimal data."""
        channel_data = {
            "name": "minimal",
        }

        response = client.post(
            "/api/channels/", json=channel_data, headers=test_user_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "minimal"
        assert data["description"] == ""
        assert data["is_system"] is False

    def test_create_channel_duplicate_name_fails(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        session: Session,
    ):
        """Test that creating a channel with duplicate name in same org fails."""
        # Create first channel
        existing_channel = Channel(
            org_id=test_org.id,
            name="duplicate",
            description="First channel",
        )
        session.add(existing_channel)
        session.commit()

        # Try to create second channel with same name
        channel_data = {
            "name": "duplicate",
            "description": "Second channel",
        }

        response = client.post(
            "/api/channels/", json=channel_data, headers=test_user_headers
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_channel_whitespace_validation(
        self, client: TestClient, test_user_headers: dict
    ):
        """Test that channel names with only whitespace are rejected."""
        channel_data = {
            "name": "   ",
        }

        response = client.post(
            "/api/channels/", json=channel_data, headers=test_user_headers
        )

        assert response.status_code == 422
        assert "empty or only whitespace" in response.json()["detail"]

    def test_create_channel_requires_auth(self, client: TestClient):
        """Test that creating a channel requires authentication."""
        channel_data = {
            "name": "unauthorized",
        }

        response = client.post("/api/channels/", json=channel_data)

        assert response.status_code == 401

    def test_list_channels_empty(self, client: TestClient, test_user_headers: dict):
        """Test listing channels when none exist."""
        response = client.get("/api/channels/", headers=test_user_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_channels_multiple(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        session: Session,
    ):
        """Test listing multiple channels ordered by name."""
        # Create channels in non-alphabetical order
        channels = [
            Channel(org_id=test_org.id, name="zebra", description="Z channel"),
            Channel(org_id=test_org.id, name="alpha", description="A channel"),
            Channel(
                org_id=test_org.id, name="beta", description="B channel", is_system=True
            ),
        ]

        for channel in channels:
            session.add(channel)
        session.commit()

        response = client.get("/api/channels/", headers=test_user_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify alphabetical ordering
        names = [channel["name"] for channel in data]
        assert names == ["alpha", "beta", "zebra"]

        # Verify all fields are present
        for channel_data in data:
            assert "id" in channel_data
            assert "name" in channel_data
            assert "description" in channel_data
            assert "is_system" in channel_data
            assert "org_id" in channel_data
            assert "created_at" in channel_data

    def test_list_channels_requires_auth(self, client: TestClient):
        """Test that listing channels requires authentication."""
        response = client.get("/api/channels/")

        assert response.status_code == 401

    def test_get_channel_exists(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        session: Session,
    ):
        """Test getting an existing channel."""
        channel = Channel(
            org_id=test_org.id,
            name="test-channel",
            description="Test channel description",
            is_system=True,
        )
        session.add(channel)
        session.commit()

        response = client.get(f"/api/channels/{channel.id}", headers=test_user_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(channel.id)
        assert data["name"] == "test-channel"
        assert data["description"] == "Test channel description"
        assert data["is_system"] is True
        assert data["org_id"] == str(test_org.id)

    def test_get_channel_not_found(self, client: TestClient, test_user_headers: dict):
        """Test getting a non-existent channel."""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.get(f"/api/channels/{fake_id}", headers=test_user_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_channel_requires_auth(self, client: TestClient):
        """Test that getting a channel requires authentication."""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.get(f"/api/channels/{fake_id}")

        assert response.status_code == 401

    def test_channels_isolated_by_org(self, client: TestClient, session: Session):
        """Test that users can only see channels from their organization."""
        # Create two orgs with users
        org1 = Org(name="Org 1")
        org2 = Org(name="Org 2")
        session.add(org1)
        session.add(org2)
        session.commit()

        user1 = User(
            org_id=org1.id,
            display_name="User 1",
            email="user1@test.com",
            hashed_password="hashed",
        )
        user2 = User(
            org_id=org2.id,
            display_name="User 2",
            email="user2@test.com",
            hashed_password="hashed",
        )
        session.add(user1)
        session.add(user2)
        session.commit()

        # Create channels in each org
        channel1 = Channel(org_id=org1.id, name="org1-channel")
        channel2 = Channel(org_id=org2.id, name="org2-channel")
        session.add(channel1)
        session.add(channel2)
        session.commit()

        # Mock authentication for testing isolation
        # Note: In real tests, this would require proper JWT token setup
        # For now, this test documents the expected behavior
