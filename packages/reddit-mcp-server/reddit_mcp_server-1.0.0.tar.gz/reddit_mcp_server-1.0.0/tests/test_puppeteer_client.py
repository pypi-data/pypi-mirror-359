"""Tests for the Puppeteer client module."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from reddit_mcp_server.puppeteer_client import PuppeteerClient


class TestPuppeteerClient:
    """Test cases for PuppeteerClient class."""

    @pytest.fixture
    def client(self):
        """Create a PuppeteerClient instance."""
        return PuppeteerClient()

    @pytest.mark.asyncio
    async def test_scrape_best_communities_success(self, client):
        """Test successful scraping of best communities."""
        mock_stdout = json.dumps({
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
                    "members": "56M members"
                }
            ],
            "pagination": {
                "currentPage": 1,
                "totalPages": 10,
                "hasNext": True,
                "hasPrev": False
            }
        }).encode()

        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (mock_stdout, b"")

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await client.scrape_best_communities(page=1)

        assert len(result["communities"]) == 2
        assert result["communities"][0]["name"] == "funny"
        assert result["pagination"]["currentPage"] == 1
        assert result["pagination"]["hasNext"] is True

    @pytest.mark.asyncio
    async def test_scrape_best_communities_page_number(self, client):
        """Test that page number is correctly passed to the script."""
        mock_stdout = json.dumps({
            "communities": [],
            "pagination": {"currentPage": 5, "totalPages": 10, "hasNext": True, "hasPrev": True}
        }).encode()

        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (mock_stdout, b"")

        with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
            await client.scrape_best_communities(page=5)

        # Check that the URL in the script contains page 5
        call_args = mock_exec.call_args[0]
        script = call_args[2]  # The script is the third argument
        assert "https://www.reddit.com/best/communities/5/" in script

    @pytest.mark.asyncio
    async def test_scrape_best_communities_script_error(self, client):
        """Test handling of script execution errors."""
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"Error: Puppeteer not found")

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            with pytest.raises(Exception) as exc_info:
                await client.scrape_best_communities(page=1)

        assert "Puppeteer script failed" in str(exc_info.value)
        assert "Puppeteer not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_scrape_best_communities_json_parse_error(self, client):
        """Test handling of invalid JSON output."""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"Invalid JSON", b"")

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            with pytest.raises(json.JSONDecodeError):
                await client.scrape_best_communities(page=1)

    @pytest.mark.asyncio
    async def test_scrape_best_communities_subprocess_error(self, client):
        """Test handling of subprocess creation errors."""
        with patch("asyncio.create_subprocess_exec", side_effect=OSError("Command not found")):
            with pytest.raises(OSError) as exc_info:
                await client.scrape_best_communities(page=1)

        assert "Command not found" in str(exc_info.value)


