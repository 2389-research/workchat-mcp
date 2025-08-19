# ABOUTME: FastAPI application entry point
# ABOUTME: Configures routes, middleware, and application lifecycle

from fastapi import FastAPI

app = FastAPI(
    title="WorkChat",
    description="A real-time team chat application",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Hello from WorkChat!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
