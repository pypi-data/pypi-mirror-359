"""Tests for Reddit client functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest

from reddit_mcp_server.reddit_client import RedditClient


class TestRedditClient:
    """Test cases for Reddit client."""

    @pytest.fixture
    def mock_env(self):
        """Mock environment variables."""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_client_id",
            "REDDIT_CLIENT_SECRET": "test_client_secret",
            "REDDIT_USER_AGENT": "test_user_agent"
        }):
            yield

    @pytest.fixture
    def mock_env_with_auth(self):
        """Mock environment variables with authentication."""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_client_id",
            "REDDIT_CLIENT_SECRET": "test_client_secret",
            "REDDIT_USER_AGENT": "test_user_agent",
            "REDDIT_USERNAME": "test_user",
            "REDDIT_PASSWORD": "test_pass"
        }):
            yield

    @pytest.mark.asyncio
    async def test_initialize_read_only(self, mock_env):
        """Test initialization in read-only mode."""
        with patch("reddit_mcp_server.reddit_client.load_dotenv"):  # Don't load real .env
            with patch("reddit_mcp_server.reddit_client.praw.Reddit") as mock_reddit:
                mock_instance = MagicMock()
                mock_reddit.return_value = mock_instance

                client = RedditClient()
                await client.initialize()

                mock_reddit.assert_called_once_with(
                    client_id="test_client_id",
                    client_secret="test_client_secret",
                    user_agent="test_user_agent"
                )
                assert client.reddit == mock_instance

    @pytest.mark.asyncio
    async def test_initialize_authenticated(self, mock_env_with_auth):
        """Test initialization with authentication."""
        with patch("reddit_mcp_server.reddit_client.praw.Reddit") as mock_reddit:
            mock_instance = MagicMock()
            mock_instance.user.me.return_value = MagicMock(name="test_user")
            mock_reddit.return_value = mock_instance

            client = RedditClient()
            await client.initialize()

            mock_reddit.assert_called_once_with(
                client_id="test_client_id",
                client_secret="test_client_secret",
                user_agent="test_user_agent",
                username="test_user",
                password="test_pass"
            )

    @pytest.mark.asyncio
    async def test_get_subreddit(self, mock_env):
        """Test getting a subreddit."""
        with patch("reddit_mcp_server.reddit_client.praw.Reddit") as mock_reddit:
            mock_subreddit = MagicMock()
            mock_instance = MagicMock()
            mock_instance.subreddit.return_value = mock_subreddit
            mock_reddit.return_value = mock_instance

            client = RedditClient()
            await client.initialize()

            result = await client.get_subreddit("test_subreddit")

            mock_instance.subreddit.assert_called_once_with("test_subreddit")
            assert result == mock_subreddit

    @pytest.mark.asyncio
    async def test_search_subreddits(self, mock_env):
        """Test searching subreddits."""
        with patch("reddit_mcp_server.reddit_client.praw.Reddit") as mock_reddit:
            mock_subreddit1 = MagicMock()
            mock_subreddit2 = MagicMock()
            mock_search = MagicMock()
            mock_search.return_value = [mock_subreddit1, mock_subreddit2]

            mock_instance = MagicMock()
            mock_instance.subreddits.search = mock_search
            mock_reddit.return_value = mock_instance

            client = RedditClient()
            await client.initialize()

            result = await client.search_subreddits("test query", limit=10)

            mock_search.assert_called_once_with("test query", limit=10)
            assert result == [mock_subreddit1, mock_subreddit2]

    def test_reddit_client_creation(self):
        """Test that RedditClient can be created."""
        client1 = RedditClient()
        client2 = RedditClient()
        # Each instance is separate since no singleton pattern is used
        assert client1 is not client2
        assert isinstance(client1, RedditClient)
        assert isinstance(client2, RedditClient)

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_env):
        """Test error handling in Reddit client methods."""
        with patch("reddit_mcp_server.reddit_client.praw.Reddit") as mock_reddit:
            mock_instance = MagicMock()
            mock_instance.subreddit.side_effect = Exception("API Error")
            mock_reddit.return_value = mock_instance

            client = RedditClient()
            await client.initialize()

            with pytest.raises(Exception) as exc_info:
                await client.get_subreddit("test")

            assert "API Error" in str(exc_info.value)
