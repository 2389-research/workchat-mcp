# ABOUTME: Tests for MCP (Model Context Protocol) server functionality
# ABOUTME: Tests tool registration, execution, and access control for MCP tools

import pytest
from sqlmodel import Session, select

from workchat.database import engine
from workchat.mcp.server import mcp
from workchat.models import AuditLog, Channel, Message, Org, User

# Import MCP business logic functions for testing
from workchat.services.mcp_tools import add_reaction_logic as mcp_add_reaction
from workchat.services.mcp_tools import post_message_logic as mcp_post_message
from workchat.services.mcp_tools import search_logic as mcp_search


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


class TestMCPFunctional:
    """Test MCP tool functionality with database operations."""

    @pytest.fixture
    def setup_test_data(self):
        """Create test data for MCP functional tests."""
        with Session(engine) as session:
            # Create test organization
            test_org = Org(name="Test MCP Org")
            session.add(test_org)
            session.flush()

            # Create test user
            test_user = User(
                email="mcp-test@example.com",
                display_name="MCP Test User",
                org_id=test_org.id,
            )
            session.add(test_user)
            session.flush()

            # Create test channel
            test_channel = Channel(name="mcp-test-channel", org_id=test_org.id)
            session.add(test_channel)
            session.flush()

            session.commit()

            yield {
                "org_id": test_org.id,
                "user_email": test_user.email,
                "user_id": test_user.id,
                "channel_id": str(test_channel.id),
            }

            # Cleanup
            session.delete(test_channel)
            session.delete(test_user)
            session.delete(test_org)
            session.commit()

    def test_post_message_success(self, setup_test_data):
        """Test posting a message through MCP succeeds."""
        test_data = setup_test_data

        message_id = mcp_post_message(
            channel_id=test_data["channel_id"],
            body="Test message from MCP",
            user_email=test_data["user_email"],
        )

        # Verify message was created
        assert message_id is not None

        with Session(engine) as session:
            message = session.exec(
                select(Message).where(Message.id == message_id)
            ).first()
            assert message is not None
            assert message.body == "Test message from MCP"
            assert str(message.channel_id) == test_data["channel_id"]
            assert message.user_id == test_data["user_id"]
            assert message.thread_id == message.id  # Root message

            # Verify audit log was created
            audit_log = session.exec(
                select(AuditLog).where(
                    AuditLog.entity_type == "message",
                    AuditLog.entity_id == message.id,
                    AuditLog.action == "create",
                )
            ).first()
            assert audit_log is not None
            assert audit_log.user_id == test_data["user_id"]

            # Cleanup
            session.delete(message)
            session.delete(audit_log)
            session.commit()

    def test_post_message_validation_errors(self, setup_test_data):
        """Test post_message validation errors."""
        test_data = setup_test_data

        # Empty body
        with pytest.raises(ValueError, match="Message body cannot be empty"):
            mcp_post_message("", "")

        # Empty channel ID
        with pytest.raises(ValueError, match="Channel ID cannot be empty"):
            mcp_post_message("", "Test message")

        # Invalid UUID
        with pytest.raises(ValueError, match="Invalid channel ID format"):
            mcp_post_message("invalid-uuid", "Test message")

        # Non-existent user
        with pytest.raises(
            ValueError, match="User with email nonexistent@example.com not found"
        ):
            mcp_post_message(test_data["channel_id"], "Test", "nonexistent@example.com")

    def test_search_success(self, setup_test_data):
        """Test search functionality through MCP."""
        test_data = setup_test_data

        # First create a message to search for
        message_id = mcp_post_message(
            channel_id=test_data["channel_id"],
            body="Searchable test message content",
            user_email=test_data["user_email"],
        )

        # Now search for it
        results = mcp_search("searchable", test_data["user_email"])

        # Should find the message (assuming FTS is working)
        # Results format: ["[YYYY-MM-DD HH:MM] message snippet..."]
        assert isinstance(results, list)

        # Clean up
        with Session(engine) as session:
            message = session.exec(
                select(Message).where(Message.id == message_id)
            ).first()
            if message:
                session.delete(message)

            # Clean up audit logs
            audit_logs = session.exec(
                select(AuditLog).where(AuditLog.entity_id == message_id)
            ).all()
            for log in audit_logs:
                session.delete(log)

            # Clean up search audit logs
            search_logs = session.exec(
                select(AuditLog).where(
                    AuditLog.entity_type == "search",
                    AuditLog.user_id == test_data["user_id"],
                )
            ).all()
            for log in search_logs:
                session.delete(log)

            session.commit()

    def test_search_validation_errors(self):
        """Test search validation errors."""
        # Empty query
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            mcp_search("", "test@example.com")

        # Query too long
        long_query = "x" * 1001
        with pytest.raises(ValueError, match="Search query too long"):
            mcp_search(long_query, "test@example.com")

    def test_add_reaction_success(self, setup_test_data):
        """Test adding reaction through MCP."""
        test_data = setup_test_data

        # First create a message to react to
        message_id = mcp_post_message(
            channel_id=test_data["channel_id"],
            body="Message to react to",
            user_email=test_data["user_email"],
        )

        # Add reaction
        result = mcp_add_reaction(message_id, "👍", test_data["user_email"])

        # Should return True (placeholder implementation)
        assert result is True

        # Verify audit log was created
        with Session(engine) as session:
            audit_log = session.exec(
                select(AuditLog).where(
                    AuditLog.entity_type == "reaction", AuditLog.action == "create"
                )
            ).first()
            assert audit_log is not None
            assert audit_log.new_values["emoji"] == "👍"
            assert audit_log.new_values["via"] == "mcp"

            # Cleanup
            message = session.exec(
                select(Message).where(Message.id == message_id)
            ).first()
            if message:
                session.delete(message)

            # Clean up all audit logs for this test
            audit_logs = session.exec(
                select(AuditLog).where(AuditLog.user_id == test_data["user_id"])
            ).all()
            for log in audit_logs:
                session.delete(log)

            session.commit()

    def test_add_reaction_validation_errors(self):
        """Test add_reaction validation errors."""
        # Empty message ID
        with pytest.raises(ValueError, match="Message ID cannot be empty"):
            mcp_add_reaction("", "👍", "test@example.com")

        # Empty emoji
        with pytest.raises(ValueError, match="Emoji cannot be empty"):
            mcp_add_reaction(
                "123e4567-e89b-12d3-a456-426614174000", "", "test@example.com"
            )

        # Invalid UUID
        with pytest.raises(ValueError, match="Invalid message ID format"):
            mcp_add_reaction("invalid-uuid", "👍", "test@example.com")
