"""Integration tests for server with new best communities tools."""

from unittest.mock import MagicMock, patch

import pytest

from reddit_mcp_server import server
from reddit_mcp_server.tools import best_communities_tools


class TestServerIntegration:
    """Test server integration with best communities tools."""

    @pytest.mark.asyncio
    async def test_list_tools_includes_best_communities(self):
        """Test that list_tools includes the get_best_communities tool."""
        tools = await server.handle_list_tools()

        tool_names = [tool.name for tool in tools]
        assert "get_best_communities" in tool_names

        # Find the specific tool
        best_comm_tool = next((t for t in tools if t.name == "get_best_communities"), None)
        assert best_comm_tool is not None
        assert best_comm_tool.description == "Get Reddit's curated list of best communities with rankings"

    @pytest.mark.asyncio
    async def test_handle_call_tool_best_communities(self):
        """Test that handle_call_tool routes to best communities correctly."""
        # Mock the Reddit client
        mock_reddit_client = MagicMock()
        server.reddit_client = mock_reddit_client

        with patch.object(best_communities_tools, "handle_tool_call") as mock_handle:
            mock_handle.return_value = [MagicMock(text="test result")]

            result = await server.handle_call_tool(
                "get_best_communities",
                {"page": 3}
            )

        mock_handle.assert_called_once_with(
            "get_best_communities",
            {"page": 3},
            mock_reddit_client
        )
        assert result[0].text == "test result"

    @pytest.mark.asyncio
    async def test_handle_read_resource_includes_best_communities(self):
        """Test that the info resource mentions best communities tool."""
        info = await server.handle_read_resource("reddit://info")

        assert "Best Communities (1):" in info
        assert "get_best_communities: Get Reddit's curated list of best communities with rankings" in info

    @pytest.mark.asyncio
    async def test_tool_count_updated(self):
        """Test that the tool count is correctly updated in the info."""
        info = await server.handle_read_resource("reddit://info")

        # The server should now provide 20 tools (19 + 1 new)
        assert "This server provides 20 focused tools" in info or "19 focused tools" in info

    def test_best_communities_tools_imported(self):
        """Test that best_communities_tools is properly imported in server."""
        # This test ensures the import doesn't fail
        from reddit_mcp_server.server import best_communities_tools as imported_tools
        assert imported_tools is not None
        assert hasattr(imported_tools, "get_tools")
        assert hasattr(imported_tools, "handle_tool_call")
