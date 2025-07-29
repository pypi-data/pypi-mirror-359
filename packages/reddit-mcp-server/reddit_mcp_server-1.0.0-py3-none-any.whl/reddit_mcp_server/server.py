"""Main MCP server implementation for Reddit research using PRAW."""

import asyncio
import logging
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)

from .reddit_client import RedditClient
from .tools import (
    advanced_tools,
    best_communities_tools,
    comment_tools,
    content_tools,
    reddit_instance_tools,
    subreddit_tools,
    user_tools,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("reddit-mcp-server")

# Global Reddit client instance
reddit_client: RedditClient | None = None


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="reddit://info",
            name="Reddit Server Info",
            description="Information about the Reddit MCP server capabilities",
            mimeType="text/plain",
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    if uri == "reddit://info":
        return """Reddit MCP Server - Market Research Platform for Reddit

This server provides 19 focused tools for Reddit market research using PRAW:

Reddit Instance Tools (3):
- get_random_subreddit: Get a random subreddit
- check_username_available: Check if a username is available
- get_reddit_info: Get Reddit instance information

Subreddit Discovery & Analysis (8):
- search_subreddits: Search for subreddits by name or topic
- get_popular_subreddits: Get popular subreddits
- get_new_subreddits: Get newly created subreddits
- get_subreddit_info: Get detailed subreddit information
- get_subreddit_rules: Get subreddit rules
- get_subreddit_moderators: Get subreddit moderators
- get_subreddit_traffic: Get subreddit traffic stats (requires mod access)
- get_subreddit_wiki: Get subreddit wiki pages

Content Retrieval (6):
- search_subreddit_content: Search for posts within a specific subreddit
- get_hot_posts: Get trending posts from a subreddit
- get_top_posts: Get top posts with time filters
- get_post_details: Get detailed post information including metrics
- get_post_comments: Get all comments from a post
- search_all_reddit: Search across all of Reddit for keywords/brands

User Analysis (1):
- search_user_content: Search a specific user's posts and comments

Data Export (1):
- export_data: Export collected data as JSON or CSV

Best Communities (1):
- get_best_communities: Get Reddit's curated list of best communities with rankings

Authentication: Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT in environment
Optional: REDDIT_USERNAME, REDDIT_PASSWORD for authenticated access

Note: This server is optimized for market research data collection. The AI model using this MCP will perform the analysis.
"""
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools."""
    tools = []

    # Add tools from each module
    tools.extend(reddit_instance_tools.get_tools())
    tools.extend(subreddit_tools.get_tools())
    tools.extend(content_tools.get_tools())
    tools.extend(user_tools.get_tools())
    tools.extend(comment_tools.get_tools())
    tools.extend(advanced_tools.get_tools())
    tools.extend(best_communities_tools.get_tools())

    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    global reddit_client

    # Initialize Reddit client if not already done
    if reddit_client is None:
        reddit_client = RedditClient()
        await reddit_client.initialize()

    # Route to appropriate tool handler
    if name in [tool.name for tool in reddit_instance_tools.get_tools()]:
        return await reddit_instance_tools.handle_tool_call(name, arguments, reddit_client)
    elif name in [tool.name for tool in subreddit_tools.get_tools()]:
        return await subreddit_tools.handle_tool_call(name, arguments, reddit_client)
    elif name in [tool.name for tool in content_tools.get_tools()]:
        return await content_tools.handle_tool_call(name, arguments, reddit_client)
    elif name in [tool.name for tool in user_tools.get_tools()]:
        return await user_tools.handle_tool_call(name, arguments, reddit_client)
    elif name in [tool.name for tool in comment_tools.get_tools()]:
        return await comment_tools.handle_tool_call(name, arguments, reddit_client)
    elif name in [tool.name for tool in advanced_tools.get_tools()]:
        return await advanced_tools.handle_tool_call(name, arguments, reddit_client)
    elif name in [tool.name for tool in best_communities_tools.get_tools()]:
        return await best_communities_tools.handle_tool_call(name, arguments, reddit_client)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the server."""
    logger.info("Starting Reddit MCP Server...")

    # Check required environment variables
    required_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these environment variables in your MCP config.json")
        sys.exit(1)

    logger.info("Environment variables configured")

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
