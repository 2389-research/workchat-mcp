#!/usr/bin/env python3
"""Manual SSE test to debug streaming issues."""

import time

from fastapi.testclient import TestClient

from workchat.app import app
from workchat.auth import current_active_user
from workchat.models import User, UserRole

# Create a mock user for testing
test_user = User(
    display_name="Test User",
    email="test@example.com",
    role=UserRole.MEMBER,
    hashed_password="fake",
    is_active=True,
    is_verified=True,
)


# Override auth
def mock_auth():
    return test_user


app.dependency_overrides[current_active_user] = mock_auth

client = TestClient(app)


def test_sse_basic():
    """Test basic SSE endpoint."""
    print("Testing SSE endpoint...")

    # Test streaming with timeout
    start_time = time.time()
    with client.stream("GET", "/events", headers={}) as response:
        print(f"Response status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")

        # Read first few lines only
        lines_read = 0
        for line in response.iter_lines():
            print(f"Line {lines_read}: {line}")
            lines_read += 1

            # Read only first few events to avoid hanging
            if lines_read > 10 or time.time() - start_time > 3:
                print("Breaking out of stream...")
                break

    print("Test completed!")


if __name__ == "__main__":
    test_sse_basic()
