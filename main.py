#!/usr/bin/env python3
# ABOUTME: Development server entry point
# ABOUTME: Runs the FastAPI application with uvicorn

import uvicorn

from workchat.app import app


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
