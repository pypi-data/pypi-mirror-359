"""Reddit client wrapper using PRAW with environment variable configuration."""

import asyncio
import logging
import os
from typing import Optional

import praw
from dotenv import load_dotenv
from praw.exceptions import PRAWException

logger = logging.getLogger(__name__)


class RedditClient:
    """Wrapper around PRAW Reddit client with environment-based configuration."""

    def __init__(self):
        """Initialize the Reddit client."""
        load_dotenv()  # Load .env file if present
        self.reddit: Optional[praw.Reddit] = None
        self._authenticated = False

    async def initialize(self) -> None:
        """Initialize the PRAW Reddit instance with environment variables."""
        try:
            # Required credentials
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            user_agent = os.getenv("REDDIT_USER_AGENT")

            if not all([client_id, client_secret, user_agent]):
                raise ValueError(
                    "Missing required Reddit credentials. Set REDDIT_CLIENT_ID, "
                    "REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT environment variables."
                )

            # Optional credentials for authenticated access
            username = os.getenv("REDDIT_USERNAME")
            password = os.getenv("REDDIT_PASSWORD")

            # Initialize PRAW instance
            if username and password:
                logger.info("Initializing Reddit client with authenticated access")
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                    username=username,
                    password=password,
                )
                self._authenticated = True
            else:
                logger.info("Initializing Reddit client with read-only access")
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                )
                self._authenticated = False

            # Test the connection
            await self._test_connection()
            logger.info("Reddit client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            raise

    async def _test_connection(self) -> None:
        """Test the Reddit connection."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            user = await loop.run_in_executor(None, lambda: self.reddit.user.me())
            if user:
                logger.info(f"Authenticated as user: {user.name}")
            else:
                logger.info("Connected with read-only access")
        except Exception as e:
            logger.warning(f"Connection test failed (this is normal for read-only): {e}")

    def get_reddit(self) -> praw.Reddit:
        """Get the PRAW Reddit instance."""
        if self.reddit is None:
            raise RuntimeError("Reddit client not initialized. Call initialize() first.")
        return self.reddit

    def is_authenticated(self) -> bool:
        """Check if client has authenticated access."""
        return self._authenticated

    async def safe_execute(self, func, *args, **kwargs):
        """Execute a PRAW function safely with error handling."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, func, *args, **kwargs)
            return result
        except PRAWException as e:
            logger.error(f"PRAW error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    async def get_subreddit(self, name: str):
        """Get a subreddit safely."""
        return await self.safe_execute(self.reddit.subreddit, name)

    async def get_submission(self, submission_id: str):
        """Get a submission safely."""
        return await self.safe_execute(self.reddit.submission, submission_id)

    async def get_comment(self, comment_id: str):
        """Get a comment safely."""
        return await self.safe_execute(self.reddit.comment, comment_id)

    async def get_redditor(self, username: str):
        """Get a redditor safely."""
        return await self.safe_execute(self.reddit.redditor, username)

    async def search_subreddits(self, query: str, limit: int = 25):
        """Search for subreddits."""
        def _search():
            return list(self.reddit.subreddits.search(query, limit=limit))

        return await self.safe_execute(_search)

    async def get_popular_subreddits(self, limit: int = 25):
        """Get popular subreddits."""
        def _get_popular():
            return list(self.reddit.subreddits.popular(limit=limit))

        return await self.safe_execute(_get_popular)

    async def get_new_subreddits(self, limit: int = 25):
        """Get new subreddits."""
        def _get_new():
            return list(self.reddit.subreddits.new(limit=limit))

        return await self.safe_execute(_get_new)

    async def get_random_subreddit(self):
        """Get a random subreddit."""
        return await self.safe_execute(self.reddit.random_subreddit)

    async def check_username_available(self, username: str) -> bool:
        """Check if a username is available."""
        return await self.safe_execute(self.reddit.username_available, username)
