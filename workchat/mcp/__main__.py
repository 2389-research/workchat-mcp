# ABOUTME: Entry point for running WorkChat as MCP server
# ABOUTME: Enables "python -m workchat.mcp" to start the MCP server

from .server import main

if __name__ == "__main__":
    main()
