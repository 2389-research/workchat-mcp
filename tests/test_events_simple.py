# ABOUTME: Simple SSE tests to debug issues
# ABOUTME: Step by step testing of SSE functionality

from fastapi.testclient import TestClient

from workchat.events import manager


def test_sse_endpoint_exists(client: TestClient, test_user_headers: dict):
    """Test that SSE endpoint exists and auth works."""
    # With our auth override from fixture, this should work
    response = client.get("/events-simple", headers=test_user_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Check content
    content = response.text
    assert "event: presenceUpdate" in content
    assert '"status": "online"' in content
    assert ": heartbeat" in content


def test_connection_manager():
    """Test connection manager in isolation."""
    import asyncio

    # Test with a fresh manager
    test_manager = manager.__class__()

    async def test_operations():
        user_id = "test-user"
        connection_id = "test-connection"

        # Test connect
        queue = await test_manager.connect(connection_id, user_id)
        assert connection_id in test_manager.connections
        assert user_id in test_manager.user_connections

        # Test sending message to queue
        test_message = "test: data\n\n"
        await queue.put(test_message)
        received = await queue.get()
        assert received == test_message

        # Test disconnect
        test_manager.disconnect(connection_id, user_id)
        assert connection_id not in test_manager.connections

    asyncio.run(test_operations())
