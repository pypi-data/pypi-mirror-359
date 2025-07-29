"""Reddit instance tools - basic Reddit API functionality."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.types import TextContent, Tool

if TYPE_CHECKING:
    from ..reddit_client import RedditClient

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of Reddit instance tools."""
    return [
        Tool(
            name="get_random_subreddit",
            description="Get a random subreddit from Reddit",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="check_username_available",
            description="Check if a Reddit username is available",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username to check availability for",
                    }
                },
                "required": ["username"],
            },
        ),
        Tool(
            name="get_reddit_info",
            description="Get information about the Reddit instance and authentication status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


async def handle_tool_call(
    name: str, arguments: dict[str, Any], reddit_client: "RedditClient"
) -> list[TextContent]:
    """Handle Reddit instance tool calls."""

    if name == "get_random_subreddit":
        return await _get_random_subreddit(reddit_client)
    elif name == "check_username_available":
        return await _check_username_available(arguments["username"], reddit_client)
    elif name == "get_reddit_info":
        return await _get_reddit_info(reddit_client)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _get_random_subreddit(reddit_client: "RedditClient") -> list[TextContent]:
    """Get a random subreddit."""
    try:
        subreddit = await reddit_client.get_random_subreddit()

        result = {
            "name": subreddit.display_name,
            "title": subreddit.title,
            "description": subreddit.public_description or subreddit.description,
            "subscribers": subreddit.subscribers,
            "created_utc": subreddit.created_utc,
            "over18": subreddit.over18,
            "url": f"https://reddit.com/r/{subreddit.display_name}",
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error getting random subreddit: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _check_username_available(
    username: str, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Check if a username is available."""
    try:
        is_available = await reddit_client.check_username_available(username)

        result = {
            "username": username,
            "available": is_available,
            "message": f"Username '{username}' is {'available' if is_available else 'not available'}",
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error checking username availability: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_reddit_info(reddit_client: "RedditClient") -> list[TextContent]:
    """Get Reddit instance information."""
    try:
        reddit = reddit_client.get_reddit()

        result = {
            "client_id": reddit.config.client_id[:8] + "..." if reddit.config.client_id else None,
            "user_agent": reddit.config.user_agent,
            "authenticated": reddit_client.is_authenticated(),
            "read_only": reddit.read_only,
            "username": None,
        }

        # Try to get current user if authenticated
        if reddit_client.is_authenticated():
            try:
                user = await reddit_client.safe_execute(lambda: reddit.user.me())
                if user:
                    result["username"] = user.name
            except Exception:
                pass  # User might not be authenticated despite credentials

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error getting Reddit info: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
