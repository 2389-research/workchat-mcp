# ABOUTME: Tests for MCP (Model Context Protocol) server functionality
# ABOUTME: Tests tool registration, execution, and access control for MCP tools

import pytest

from workchat.mcp.server import mcp


class TestMCPServer:
    """Test MCP server functionality."""

    @pytest.mark.asyncio
    async def test_mcp_tools_registered(self):
        """Test that all required MCP tools are registered."""
        # Get list of registered tools
        tools = await mcp._list_tools()
        tool_names = [tool.name for tool in tools]

        # Verify all required tools are present
        assert "post_message" in tool_names
        assert "search" in tool_names
        assert "add_reaction" in tool_names

        # Verify tool count matches expectation
        assert len(tools) == 3

    @pytest.mark.asyncio
    async def test_tool_descriptions(self):
        """Test tool descriptions are correct."""
        tools = await mcp._list_tools()

        post_message_tool = next(tool for tool in tools if tool.name == "post_message")
        search_tool = next(tool for tool in tools if tool.name == "search")
        reaction_tool = next(tool for tool in tools if tool.name == "add_reaction")

        # Check tool descriptions
        assert "Post a message to a channel" in post_message_tool.description
        assert "Search messages using full-text search" in search_tool.description
        assert "Add a reaction to a message" in reaction_tool.description

    @pytest.mark.asyncio
    async def test_list_tools_output(self):
        """Test list_tools() output format for doctest."""
        tools = await mcp._list_tools()

        # Verify it's a list of tool objects
        assert isinstance(tools, list)
        assert len(tools) > 0

        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")

        # Print tools for manual verification (doctest equivalent)
        print("\\n=== MCP Tools Available ===")
        for tool in tools:
            print(f"- {tool.name}: {tool.description[:50]}...")
        print(f"\\nTotal tools: {len(tools)}")
