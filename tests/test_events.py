# ABOUTME: SSE event stream endpoint tests
# ABOUTME: Test real-time message broadcasting and presence updates

import asyncio
import uuid

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from workchat.events import manager
from workchat.models import Channel, Message, Org, User


class TestSSEEvents:
    """Test server-sent events for real-time messaging."""

    @pytest.mark.asyncio
    async def test_sse_connect_and_presence(
        self,
        async_client: httpx.AsyncClient,
        test_user_headers: dict,
        test_user: User,
    ):
        """Test SSE connection and initial presence update."""
        async with async_client.stream(
            "GET", "/events", headers=test_user_headers
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"

            # Read the first event (presence update)
            event_data = ""
            async for line in response.aiter_lines():
                event_data += line + "\n"
                if line == "":  # End of event
                    break

            assert "event: presenceUpdate" in event_data
            assert f'"user_id": "{test_user.id}"' in event_data
            assert '"status": "online"' in event_data
            assert f'"display_name": "{test_user.display_name}"' in event_data

    @pytest.mark.asyncio
    async def test_new_message_broadcast(
        self,
        async_client: httpx.AsyncClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test that posting a message broadcasts to SSE connections."""
        # Create a channel
        channel = Channel(
            org_id=test_org.id,
            name="general",
            description="General channel",
        )
        session.add(channel)
        session.commit()

        # Start SSE connection
        async with async_client.stream(
            "GET", "/events", headers=test_user_headers
        ) as sse_response:
            # Skip the initial presence event
            event_data = ""
            async for line in sse_response.aiter_lines():
                event_data += line + "\n"
                if line == "":  # End of first event
                    break

            # Post a message in another task
            async def post_message():
                await asyncio.sleep(0.1)  # Small delay to ensure SSE is ready
                message_data = {
                    "body": "Hello from SSE test!",
                    "thread_id": None,
                }

                response = await async_client.post(
                    f"/api/messages/?channel_id={channel.id}",
                    json=message_data,
                    headers=test_user_headers,
                )
                assert response.status_code == 201
                return response.json()

            # Start the message posting task
            post_task = asyncio.create_task(post_message())

            # Read the newMessage event
            event_data = ""
            async for line in sse_response.aiter_lines():
                event_data += line + "\n"
                if line == "":  # End of event
                    break

            # Wait for the message to be posted
            await post_task

            # Verify the SSE event
            assert "event: newMessage" in event_data
            assert '"body": "Hello from SSE test!"' in event_data
            assert f'"channel_id": "{channel.id}"' in event_data
            assert f'"user_id": "{test_user.id}"' in event_data

    @pytest.mark.asyncio
    async def test_message_update_broadcast(
        self,
        async_client: httpx.AsyncClient,
        test_user_headers: dict,
        test_user: User,
        test_org: Org,
        session: Session,
    ):
        """Test that editing a message broadcasts to SSE connections."""
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

        # Start SSE connection
        async with async_client.stream(
            "GET", "/events", headers=test_user_headers
        ) as sse_response:
            # Skip the initial presence event
            event_data = ""
            async for line in sse_response.aiter_lines():
                event_data += line + "\n"
                if line == "":
                    break

            # Edit the message in another task
            async def edit_message():
                await asyncio.sleep(0.1)
                edit_data = {
                    "body": "Edited message",
                    "version": 1,
                }

                response = await async_client.patch(
                    f"/api/messages/{message.id}",
                    json=edit_data,
                    headers=test_user_headers,
                )
                assert response.status_code == 200
                return response.json()

            # Start the message editing task
            edit_task = asyncio.create_task(edit_message())

            # Read the messageUpdated event
            event_data = ""
            async for line in sse_response.aiter_lines():
                event_data += line + "\n"
                if line == "":
                    break

            # Wait for the edit to complete
            await edit_task

            # Verify the SSE event
            assert "event: messageUpdated" in event_data
            assert '"body": "Edited message"' in event_data
            assert f'"id": "{message.id}"' in event_data
            assert '"version": 2' in event_data

    @pytest.mark.asyncio
    async def test_heartbeat(
        self,
        async_client: httpx.AsyncClient,
        test_user_headers: dict,
    ):
        """Test that heartbeat comments are sent."""
        async with async_client.stream(
            "GET", "/events", headers=test_user_headers, timeout=20.0
        ) as response:
            # Skip the initial presence event
            event_data = ""
            async for line in response.aiter_lines():
                event_data += line + "\n"
                if line == "":
                    break

            # Wait for heartbeat (should come within 15 seconds + buffer)
            heartbeat_received = False
            async for line in response.aiter_lines():
                if line.startswith(": heartbeat"):
                    heartbeat_received = True
                    break

            assert heartbeat_received

    def test_sse_requires_auth(self, client: TestClient):
        """Test that SSE endpoint requires authentication."""
        with client.stream("GET", "/events") as response:
            assert response.status_code == 401

    def test_connection_manager_basic_ops(self):
        """Test the connection manager basic operations."""
        # Create a new manager for isolated testing
        test_manager = manager.__class__()

        # Test connect
        user_id = str(uuid.uuid4())
        connection_id = str(uuid.uuid4())

        # Connect should create the connection
        asyncio.run(test_manager.connect(connection_id, user_id))
        assert connection_id in test_manager.connections
        assert user_id in test_manager.user_connections
        assert connection_id in test_manager.user_connections[user_id]

        # Test disconnect
        test_manager.disconnect(connection_id, user_id)
        assert connection_id not in test_manager.connections
        assert user_id not in test_manager.user_connections
