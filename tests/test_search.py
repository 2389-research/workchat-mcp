# ABOUTME: Search API and FTS5 functionality tests
# ABOUTME: Test full-text search with SQLite FTS5 and channel scoping

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from workchat.models import Channel, Message, Org, User
from workchat.repositories.search import SearchRepository


class TestSearchRepository:
    """Test the search repository layer."""

    def test_search_messages_basic(
        self, session: Session, test_user: User, test_org: Org
    ):
        """Test basic message search functionality."""
        # Create a channel and messages
        channel = Channel(
            org_id=test_org.id,
            name="general",
            description="General channel",
        )
        session.add(channel)
        session.commit()

        # Create test messages
        messages = [
            Message(
                channel_id=channel.id,
                user_id=test_user.id,
                body="Hello world this is a test message",
            ),
            Message(
                channel_id=channel.id,
                user_id=test_user.id,
                body="Another message about programming",
            ),
            Message(
                channel_id=channel.id,
                user_id=test_user.id,
                body="Final message with different content",
            ),
        ]

        for message in messages:
            session.add(message)
        session.commit()

        # Search for messages
        search_repo = SearchRepository(session)

        # Search for "test" should return first message
        results = search_repo.search_messages("test")
        assert len(results) == 1
        assert results[0].body == "Hello world this is a test message"

        # Search for "message" should return all three
        results = search_repo.search_messages("message")
        assert len(results) == 3

        # Search for "programming" should return second message
        results = search_repo.search_messages("programming")
        assert len(results) == 1
        assert results[0].body == "Another message about programming"

    def test_search_with_channel_scope(
        self, session: Session, test_user: User, test_org: Org
    ):
        """Test search scoped to specific channel."""
        # Create two channels
        channel1 = Channel(org_id=test_org.id, name="general")
        channel2 = Channel(org_id=test_org.id, name="random")
        session.add(channel1)
        session.add(channel2)
        session.commit()

        # Add messages to both channels
        msg1 = Message(
            channel_id=channel1.id,
            user_id=test_user.id,
            body="Python programming is fun",
        )
        msg2 = Message(
            channel_id=channel2.id,
            user_id=test_user.id,
            body="Python development rocks",
        )
        session.add(msg1)
        session.add(msg2)
        session.commit()

        search_repo = SearchRepository(session)

        # Search all channels for "Python"
        results = search_repo.search_messages("Python")
        assert len(results) == 2

        # Search only channel1 for "Python"
        results = search_repo.search_messages("Python", channel_id=channel1.id)
        assert len(results) == 1
        assert results[0].body == "Python programming is fun"

        # Search only channel2 for "Python"
        results = search_repo.search_messages("Python", channel_id=channel2.id)
        assert len(results) == 1
        assert results[0].body == "Python development rocks"

    def test_search_message_ids(self, session: Session, test_user: User, test_org: Org):
        """Test searching for message IDs only."""
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        message = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            body="Unique search term xyzabc123",
        )
        session.add(message)
        session.commit()

        search_repo = SearchRepository(session)

        # Search for IDs
        ids = search_repo.search_message_ids("xyzabc123")
        assert len(ids) == 1
        assert ids[0] == message.id

    def test_search_snippet(self, session: Session, test_user: User, test_org: Org):
        """Test search snippet generation."""
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        message = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            body="This is a long message with many words to test snippet generation functionality",
        )
        session.add(message)
        session.commit()

        search_repo = SearchRepository(session)

        # Get snippet for search term
        snippet = search_repo.get_search_snippet("snippet", message.id)
        assert snippet is not None
        assert "snippet" in snippet.lower()


class TestSearchAPI:
    """Test the search API endpoints."""

    def test_search_endpoint_basic(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test basic search endpoint functionality."""
        # Create channel and messages
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        messages = [
            Message(
                channel_id=channel.id,
                user_id=test_user.id,
                body="Python is awesome for development",
            ),
            Message(
                channel_id=channel.id,
                user_id=test_user.id,
                body="JavaScript is also great",
            ),
            Message(
                channel_id=channel.id,
                user_id=test_user.id,
                body="Both Python and JavaScript are popular",
            ),
        ]

        for msg in messages:
            session.add(msg)
        session.commit()

        # Test search
        response = client.get(
            "/api/search/",
            params={"q": "Python"},
            headers=test_user_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "Python"
        assert len(data["results"]) == 2  # Two messages contain "Python"
        assert data["total_count"] == 2
        assert data["limit"] == 50
        assert data["offset"] == 0

        # Verify result structure
        result = data["results"][0]
        assert "message" in result
        assert "snippet" in result
        assert result["message"]["body"] in [
            "Python is awesome for development",
            "Both Python and JavaScript are popular",
        ]

    def test_search_with_channel_scope(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test search with channel scope parameter."""
        # Create two channels with messages
        channel1 = Channel(org_id=test_org.id, name="general")
        channel2 = Channel(org_id=test_org.id, name="tech")
        session.add(channel1)
        session.add(channel2)
        session.commit()

        msg1 = Message(
            channel_id=channel1.id,
            user_id=test_user.id,
            body="Docker containers are useful",
        )
        msg2 = Message(
            channel_id=channel2.id,
            user_id=test_user.id,
            body="Docker deployment strategies",
        )
        session.add(msg1)
        session.add(msg2)
        session.commit()

        # Search all channels
        response = client.get(
            "/api/search/",
            params={"q": "Docker"},
            headers=test_user_headers,
        )
        assert response.status_code == 200
        assert len(response.json()["results"]) == 2

        # Search specific channel
        response = client.get(
            "/api/search/",
            params={"q": "Docker", "scope": f"channel:{channel1.id}"},
            headers=test_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["message"]["body"] == "Docker containers are useful"
        assert data["search_scope"] == f"channel:{channel1.id}"

    def test_search_pagination(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test search pagination parameters."""
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        # Create many messages
        for i in range(10):
            message = Message(
                channel_id=channel.id,
                user_id=test_user.id,
                body=f"Test message number {i} with search term",
            )
            session.add(message)
        session.commit()

        # Test pagination
        response = client.get(
            "/api/search/",
            params={"q": "search", "limit": 5, "offset": 0},
            headers=test_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 5
        assert data["limit"] == 5
        assert data["offset"] == 0

        # Second page
        response = client.get(
            "/api/search/",
            params={"q": "search", "limit": 5, "offset": 5},
            headers=test_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 5
        assert data["offset"] == 5

    def test_search_validation(self, client: TestClient, test_user_headers: dict):
        """Test search parameter validation."""
        # Empty query
        response = client.get(
            "/api/search/",
            params={"q": ""},
            headers=test_user_headers,
        )
        assert response.status_code == 422  # Validation error

        # Invalid scope format
        response = client.get(
            "/api/search/",
            params={"q": "test", "scope": "invalid:format"},
            headers=test_user_headers,
        )
        assert response.status_code == 400

        # Invalid channel UUID
        response = client.get(
            "/api/search/",
            params={"q": "test", "scope": "channel:not-a-uuid"},
            headers=test_user_headers,
        )
        assert response.status_code == 400

    def test_search_requires_auth(self, client: TestClient):
        """Test that search requires authentication."""
        response = client.get("/api/search/", params={"q": "test"})
        assert response.status_code == 401

    def test_search_org_isolation(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        session: Session,
    ):
        """Test that search results are isolated by organization."""
        # Create another org with user and channel
        other_org = Org(name="Other Organization")
        session.add(other_org)
        session.commit()

        other_channel = Channel(org_id=other_org.id, name="secret")
        session.add(other_channel)
        session.commit()

        # Create message in other org
        other_message = Message(
            channel_id=other_channel.id,
            user_id=test_user.id,  # Same user but different org channel
            body="Secret message in other org",
        )
        session.add(other_message)
        session.commit()

        # Search should not find the message from other org
        response = client.get(
            "/api/search/",
            params={"q": "Secret"},
            headers=test_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0  # Should not see other org's messages
