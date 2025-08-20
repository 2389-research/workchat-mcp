# ABOUTME: Message and threading endpoint tests
# ABOUTME: Test message posting, replies, edits, thread logic, and optimistic locking

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from workchat.models import Channel, Message, Org, User


class TestMessageCRUD:
    """Test message creation, thread handling, and editing."""

    def test_post_root_message(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        session: Session,
    ):
        """Test posting a root message that creates a new thread."""
        # Create a channel
        channel = Channel(
            org_id=test_org.id,
            name="general",
            description="General channel",
        )
        session.add(channel)
        session.commit()

        message_data = {
            "body": "This is a root message",
            "thread_id": None,
        }

        response = client.post(
            f"/api/messages/?channel_id={channel.id}",
            json=message_data,
            headers=test_user_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["body"] == "This is a root message"
        assert data["channel_id"] == str(channel.id)
        assert (
            data["thread_id"] == data["id"]
        )  # Root message: thread_id equals message id
        assert data["version"] == 1
        assert data["edited_at"] is None

        # Verify in database
        message = session.get(Message, UUID(data["id"]))
        assert message is not None
        assert message.thread_id == message.id

    def test_post_reply_message(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test posting a reply to an existing thread."""
        # Create channel and root message
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        root_message = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            body="Root message",
        )
        session.add(root_message)
        session.commit()

        # Set thread_id to self for root message
        root_message.thread_id = root_message.id
        session.commit()

        # Post a reply
        reply_data = {
            "body": "This is a reply",
            "thread_id": str(root_message.id),
        }

        response = client.post(
            f"/api/messages/?channel_id={channel.id}",
            json=reply_data,
            headers=test_user_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["body"] == "This is a reply"
        assert data["thread_id"] == str(root_message.id)
        assert data["version"] == 1

    def test_post_reply_to_nonexistent_thread(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        session: Session,
    ):
        """Test that replying to a non-existent thread fails."""
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        fake_thread_id = "12345678-1234-1234-1234-123456789012"
        reply_data = {
            "body": "This should fail",
            "thread_id": fake_thread_id,
        }

        response = client.post(
            f"/api/messages/?channel_id={channel.id}",
            json=reply_data,
            headers=test_user_headers,
        )

        assert response.status_code == 404
        assert "Thread not found" in response.json()["detail"]

    def test_post_message_to_nonexistent_channel(
        self, client: TestClient, test_user_headers: dict
    ):
        """Test posting to a non-existent channel fails."""
        fake_channel_id = "12345678-1234-1234-1234-123456789012"
        message_data = {
            "body": "This should fail",
        }

        response = client.post(
            f"/api/messages/?channel_id={fake_channel_id}",
            json=message_data,
            headers=test_user_headers,
        )

        assert response.status_code == 404
        assert "Channel not found" in response.json()["detail"]

    def test_get_thread_messages(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test retrieving all messages in a thread."""
        # Create channel
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        # Create root message
        root_message = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            body="Root message",
        )
        session.add(root_message)
        session.commit()
        root_message.thread_id = root_message.id
        session.commit()

        # Create reply messages
        reply1 = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            thread_id=root_message.id,
            body="Reply 1",
        )
        reply2 = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            thread_id=root_message.id,
            body="Reply 2",
        )
        session.add(reply1)
        session.add(reply2)
        session.commit()

        # Get thread messages
        response = client.get(
            f"/api/messages/threads/{root_message.id}?channel_id={channel.id}",
            headers=test_user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # Root + 2 replies

        # Verify chronological order
        bodies = [msg["body"] for msg in data]
        assert bodies == ["Root message", "Reply 1", "Reply 2"]

    def test_edit_message_success(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test editing a message with correct version."""
        # Create channel and message
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        message = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            body="Original message",
            version=1,
        )
        session.add(message)
        session.commit()

        # Edit the message
        edit_data = {
            "body": "Edited message",
            "version": 1,
        }

        response = client.patch(
            f"/api/messages/{message.id}",
            json=edit_data,
            headers=test_user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["body"] == "Edited message"
        assert data["version"] == 2
        assert data["edited_at"] is not None

    def test_edit_message_version_conflict(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test that editing with wrong version fails (optimistic locking)."""
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        message = Message(
            channel_id=channel.id,
            user_id=test_user.id,
            body="Original message",
            version=2,  # Current version is 2
        )
        session.add(message)
        session.commit()

        # Try to edit with wrong version
        edit_data = {
            "body": "Edited message",
            "version": 1,  # Wrong version
        }

        response = client.patch(
            f"/api/messages/{message.id}",
            json=edit_data,
            headers=test_user_headers,
        )

        assert response.status_code == 409
        assert "modified by another user" in response.json()["detail"]

    def test_message_requires_auth(
        self, client: TestClient, test_org: Org, session: Session
    ):
        """Test that message operations require authentication."""
        channel = Channel(org_id=test_org.id, name="general")
        session.add(channel)
        session.commit()

        message_data = {
            "body": "Unauthorized message",
        }

        response = client.post(
            f"/api/messages/?channel_id={channel.id}",
            json=message_data,
        )

        assert response.status_code == 401
