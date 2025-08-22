# ABOUTME: FastMCP server implementation for WorkChat
# ABOUTME: Exposes chat operations as MCP tools for AI assistant integration

from typing import List

from fastmcp import FastMCP

from ..services.mcp_tools import add_reaction_logic, post_message_logic, search_logic

# Initialize FastMCP server
mcp = FastMCP("WorkChat")


@mcp.tool()
def post_message(
    channel_id: str, body: str, user_email: str = "admin@example.com"
) -> str:
    """Post a message to a channel.

    Args:
        channel_id: The ID of the channel to post to
        body: The message content
        user_email: Email of user posting (defaults to admin)

    Returns:
        The ID of the created message
    """
    return post_message_logic(channel_id, body, user_email)


@mcp.tool()
def search(query: str, user_email: str = "admin@example.com") -> List[str]:
    """Search messages using full-text search.

    Args:
        query: Search query string
        user_email: Email of user searching (for access control)

    Returns:
        List of message snippets matching the search
    """
    return search_logic(query, user_email)


@mcp.tool()
def add_reaction(
    message_id: str, emoji: str, user_email: str = "admin@example.com"
) -> bool:
    """Add a reaction to a message.

    Args:
        message_id: ID of the message to react to
        emoji: Emoji reaction (e.g. "👍", "❤️")
        user_email: Email of user adding reaction

    Returns:
        True if reaction was added successfully
    """
    return add_reaction_logic(message_id, emoji, user_email)


def main():
    """Main entry point for MCP server."""
    # Run FastMCP stdio transport
    mcp.run()


if __name__ == "__main__":
    main()
