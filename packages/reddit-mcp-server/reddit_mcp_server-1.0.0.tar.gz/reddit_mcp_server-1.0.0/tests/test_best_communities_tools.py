"""Tests for the best communities tools module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.types import TextContent, Tool

from reddit_mcp_server.tools import best_communities_tools


class TestBestCommunitiesTools:
    """Test cases for best communities tools."""

    def test_get_tools(self):
        """Test that get_tools returns the correct tool definition."""
        tools = best_communities_tools.get_tools()

        assert len(tools) == 1
        assert isinstance(tools[0], Tool)
        assert tools[0].name == "get_best_communities"
        assert tools[0].description == "Get Reddit's curated list of best communities with rankings"

        # Check input schema
        schema = tools[0].inputSchema
        assert schema["type"] == "object"
        assert "page" in schema["properties"]
        assert schema["properties"]["page"]["type"] == "integer"
        assert schema["properties"]["page"]["default"] == 1
        assert schema["properties"]["page"]["minimum"] == 1
        assert schema["properties"]["page"]["maximum"] == 10

    @pytest.mark.asyncio
    async def test_handle_tool_call_success(self):
        """Test successful tool call handling."""
        mock_reddit_client = MagicMock()

        with patch("reddit_mcp_server.tools.best_communities_tools._get_best_communities") as mock_get:
            mock_get.return_value = [TextContent(type="text", text="test result")]

            result = await best_communities_tools.handle_tool_call(
                "get_best_communities",
                {"page": 2},
                mock_reddit_client
            )

        mock_get.assert_called_once_with(2)
        assert len(result) == 1
        assert result[0].text == "test result"

    @pytest.mark.asyncio
    async def test_handle_tool_call_invalid_tool(self):
        """Test handling of invalid tool name."""
        mock_reddit_client = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            await best_communities_tools.handle_tool_call(
                "invalid_tool",
                {},
                mock_reddit_client
            )

        assert "Unknown tool: invalid_tool" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_tool_call_default_page(self):
        """Test that default page 1 is used when not specified."""
        mock_reddit_client = MagicMock()

        with patch("reddit_mcp_server.tools.best_communities_tools._get_best_communities") as mock_get:
            mock_get.return_value = [TextContent(type="text", text="test result")]

            await best_communities_tools.handle_tool_call(
                "get_best_communities",
                {},  # No page specified
                mock_reddit_client
            )

        mock_get.assert_called_once_with(1)


class TestGetBestCommunities:
    """Test cases for _get_best_communities function."""

    @pytest.mark.asyncio
    async def test_get_best_communities_with_puppeteer(self):
        """Test successful scraping using Puppeteer client."""
        mock_data = {
            "communities": [
                {
                    "rank": 1,
                    "name": "funny",
                    "url": "https://reddit.com/r/funny",
                    "members": "67M members"
                },
                {
                    "rank": 2,
                    "name": "AskReddit",
                    "url": "https://reddit.com/r/AskReddit",
                    "members": "3.4M members"
                }
            ],
            "pagination": {
                "currentPage": 1,
                "totalPages": 10,
                "hasNext": True,
                "hasPrev": False
            }
        }

        with patch("reddit_mcp_server.puppeteer_client.PuppeteerClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.scrape_best_communities.return_value = mock_data
            mock_client_class.return_value = mock_client

            result = await best_communities_tools._get_best_communities(1)

        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        data = json.loads(result[0].text)
        assert data["page"] == 1
        assert data["total_pages"] == 10
        assert data["has_next"] is True
        assert data["has_previous"] is False
        assert len(data["communities"]) == 2
        assert data["communities"][0]["name"] == "funny"
        assert data["communities"][0]["members_count"] == 67000000
        assert data["communities"][1]["members_count"] == 3400000

    @pytest.mark.asyncio
    async def test_get_best_communities_import_error(self):
        """Test error handling when Puppeteer import fails."""
        # Create a mock module that raises ImportError when accessed
        import sys
        original_module = sys.modules.get('reddit_mcp_server.puppeteer_client')
        
        # Temporarily remove the module from sys.modules
        if 'reddit_mcp_server.puppeteer_client' in sys.modules:
            del sys.modules['reddit_mcp_server.puppeteer_client']
        
        # Create a module that raises ImportError when imported
        class FailingModule:
            def __getattr__(self, name):
                raise ImportError("No module named 'pyppeteer'")
        
        sys.modules['reddit_mcp_server.puppeteer_client'] = FailingModule()
        
        try:
            result = await best_communities_tools._get_best_communities(1)
        finally:
            # Restore the original module
            if original_module is not None:
                sys.modules['reddit_mcp_server.puppeteer_client'] = original_module
            else:
                sys.modules.pop('reddit_mcp_server.puppeteer_client', None)

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_get_best_communities_puppeteer_runtime_error(self):
        """Test error handling when Puppeteer execution fails."""
        with patch("reddit_mcp_server.puppeteer_client.PuppeteerClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.scrape_best_communities.side_effect = Exception("Puppeteer failed")
            mock_client_class.return_value = mock_client

            result = await best_communities_tools._get_best_communities(1)

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error:" in result[0].text
        assert "Puppeteer failed" in result[0].text

    @pytest.mark.asyncio
    async def test_get_best_communities_error_handling(self):
        """Test general error handling in _get_best_communities."""
        with patch("reddit_mcp_server.puppeteer_client.PuppeteerClient", side_effect=Exception("Test error")):
            result = await best_communities_tools._get_best_communities(1)

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error:" in result[0].text
        assert "Test error" in result[0].text


class TestParseMemberCount:
    """Test cases for _parse_member_count function."""

    def test_parse_member_count_millions_whole(self):
        """Test parsing whole millions."""
        assert best_communities_tools._parse_member_count("67M members") == 67000000

    def test_parse_member_count_millions_decimal(self):
        """Test parsing decimal millions."""
        assert best_communities_tools._parse_member_count("3.4M members") == 3400000

    def test_parse_member_count_thousands_whole(self):
        """Test parsing whole thousands."""
        assert best_communities_tools._parse_member_count("47K members") == 47000

    def test_parse_member_count_thousands_decimal(self):
        """Test parsing decimal thousands."""
        assert best_communities_tools._parse_member_count("2.5K members") == 2500

    def test_parse_member_count_plain_number(self):
        """Test parsing plain number."""
        assert best_communities_tools._parse_member_count("123 members") == 123

    def test_parse_member_count_no_suffix(self):
        """Test parsing number without 'members' suffix."""
        assert best_communities_tools._parse_member_count("5000") == 5000

    def test_parse_member_count_invalid_format(self):
        """Test handling of invalid format."""
        assert best_communities_tools._parse_member_count("invalid") == 0
        assert best_communities_tools._parse_member_count("") == 0
        assert best_communities_tools._parse_member_count("abc members") == 0

    def test_parse_member_count_edge_cases(self):
        """Test edge cases."""
        assert best_communities_tools._parse_member_count("0 members") == 0
        assert best_communities_tools._parse_member_count("0.5M members") == 500000
        assert best_communities_tools._parse_member_count("999K members") == 999000
