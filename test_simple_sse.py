#!/usr/bin/env python3
"""Simple test to check SSE endpoint basic functionality."""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/test-sse")
def test_sse():
    def generate():
        yield "event: test\ndata: hello\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


def test_basic_sse():
    client = TestClient(app)

    # Test the endpoint exists
    response = client.get("/test-sse")
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content: {response.text}")


if __name__ == "__main__":
    test_basic_sse()
