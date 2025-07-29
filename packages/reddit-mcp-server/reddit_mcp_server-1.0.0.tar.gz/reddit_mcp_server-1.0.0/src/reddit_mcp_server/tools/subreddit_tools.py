"""Subreddit discovery and analysis tools."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.types import TextContent, Tool

if TYPE_CHECKING:
    from ..reddit_client import RedditClient

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of subreddit tools."""
    return [
        Tool(
            name="search_subreddits",
            description="Search for subreddits by name or topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for subreddits",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25)",
                        "default": 25,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_popular_subreddits",
            description="Get list of popular subreddits",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25)",
                        "default": 25,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_new_subreddits",
            description="Get list of newly created subreddits",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25)",
                        "default": 25,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_subreddit_info",
            description="Get detailed information about a specific subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                },
                "required": ["subreddit_name"],
            },
        ),
        Tool(
            name="get_subreddit_rules",
            description="Get the rules of a specific subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                },
                "required": ["subreddit_name"],
            },
        ),
        Tool(
            name="get_subreddit_moderators",
            description="Get list of moderators for a specific subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                },
                "required": ["subreddit_name"],
            },
        ),
        Tool(
            name="get_subreddit_traffic",
            description="Get traffic statistics for a specific subreddit (requires mod access)",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                },
                "required": ["subreddit_name"],
            },
        ),
        Tool(
            name="get_subreddit_wiki",
            description="Get wiki pages from a specific subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                    "page_name": {
                        "type": "string",
                        "description": "Name of the wiki page (optional, defaults to index)",
                        "default": "index",
                    },
                },
                "required": ["subreddit_name"],
            },
        ),
    ]


async def handle_tool_call(
    name: str, arguments: dict[str, Any], reddit_client: "RedditClient"
) -> list[TextContent]:
    """Handle subreddit tool calls."""

    if name == "search_subreddits":
        return await _search_subreddits(
            arguments["query"], arguments.get("limit", 25), reddit_client
        )
    elif name == "get_popular_subreddits":
        return await _get_popular_subreddits(arguments.get("limit", 25), reddit_client)
    elif name == "get_new_subreddits":
        return await _get_new_subreddits(arguments.get("limit", 25), reddit_client)
    elif name == "get_subreddit_info":
        return await _get_subreddit_info(arguments["subreddit_name"], reddit_client)
    elif name == "get_subreddit_rules":
        return await _get_subreddit_rules(arguments["subreddit_name"], reddit_client)
    elif name == "get_subreddit_moderators":
        return await _get_subreddit_moderators(arguments["subreddit_name"], reddit_client)
    elif name == "get_subreddit_traffic":
        return await _get_subreddit_traffic(arguments["subreddit_name"], reddit_client)
    elif name == "get_subreddit_wiki":
        return await _get_subreddit_wiki(
            arguments["subreddit_name"],
            arguments.get("page_name", "index"),
            reddit_client
        )
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _search_subreddits(
    query: str, limit: int, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Search for subreddits."""
    try:
        subreddits = await reddit_client.search_subreddits(query, limit)

        results = []
        for subreddit in subreddits:
            results.append({
                "name": subreddit.display_name,
                "title": subreddit.title,
                "description": subreddit.public_description or subreddit.description,
                "subscribers": subreddit.subscribers,
                "created_utc": subreddit.created_utc,
                "over18": subreddit.over18,
                "url": f"https://reddit.com/r/{subreddit.display_name}",
            })

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error searching subreddits: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_popular_subreddits(
    limit: int, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get popular subreddits."""
    try:
        subreddits = await reddit_client.get_popular_subreddits(limit)

        results = []
        for subreddit in subreddits:
            results.append({
                "name": subreddit.display_name,
                "title": subreddit.title,
                "description": subreddit.public_description or subreddit.description,
                "subscribers": subreddit.subscribers,
                "created_utc": subreddit.created_utc,
                "over18": subreddit.over18,
                "url": f"https://reddit.com/r/{subreddit.display_name}",
            })

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error getting popular subreddits: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_new_subreddits(
    limit: int, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get new subreddits."""
    try:
        subreddits = await reddit_client.get_new_subreddits(limit)

        results = []
        for subreddit in subreddits:
            results.append({
                "name": subreddit.display_name,
                "title": subreddit.title,
                "description": subreddit.public_description or subreddit.description,
                "subscribers": subreddit.subscribers,
                "created_utc": subreddit.created_utc,
                "over18": subreddit.over18,
                "url": f"https://reddit.com/r/{subreddit.display_name}",
            })

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error getting new subreddits: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_subreddit_info(
    subreddit_name: str, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get detailed subreddit information."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        result = {
            "name": subreddit.display_name,
            "title": subreddit.title,
            "description": subreddit.description,
            "public_description": subreddit.public_description,
            "subscribers": subreddit.subscribers,
            "active_user_count": subreddit.active_user_count,
            "created_utc": subreddit.created_utc,
            "over18": subreddit.over18,
            "quarantine": subreddit.quarantine,
            "lang": subreddit.lang,
            "url": f"https://reddit.com/r/{subreddit.display_name}",
            "subreddit_type": subreddit.subreddit_type,
            "submission_type": subreddit.submission_type,
            "can_assign_link_flair": subreddit.can_assign_link_flair,
            "can_assign_user_flair": subreddit.can_assign_user_flair,
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error getting subreddit info: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_subreddit_rules(
    subreddit_name: str, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get subreddit rules."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        def _get_rules():
            return list(subreddit.rules)

        rules = await reddit_client.safe_execute(_get_rules)

        results = []
        for rule in rules:
            results.append({
                "short_name": rule.short_name,
                "description": rule.description,
                "kind": rule.kind,
                "violation_reason": rule.violation_reason,
                "created_utc": rule.created_utc,
                "priority": rule.priority,
            })

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error getting subreddit rules: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_subreddit_moderators(
    subreddit_name: str, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get subreddit moderators."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        def _get_moderators():
            return list(subreddit.moderator())

        moderators = await reddit_client.safe_execute(_get_moderators)

        results = []
        for mod in moderators:
            results.append({
                "name": mod.name,
                "date": mod.date if hasattr(mod, 'date') else None,
                "mod_permissions": list(mod.mod_permissions) if hasattr(mod, 'mod_permissions') else None,
            })

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error getting subreddit moderators: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_subreddit_traffic(
    subreddit_name: str, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get subreddit traffic statistics."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        def _get_traffic():
            return subreddit.traffic()

        traffic = await reddit_client.safe_execute(_get_traffic)

        result = {
            "day": traffic.get("day", []),
            "hour": traffic.get("hour", []),
            "month": traffic.get("month", []),
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error getting subreddit traffic: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)} (requires moderator access)")]


async def _get_subreddit_wiki(
    subreddit_name: str, page_name: str, reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get subreddit wiki page."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        def _get_wiki():
            wiki_page = subreddit.wiki[page_name]
            return {
                "content_md": wiki_page.content_md,
                "content_html": wiki_page.content_html,
                "revision_date": wiki_page.revision_date,
                "revision_by": wiki_page.revision_by.name if wiki_page.revision_by else None,
            }

        wiki_data = await reddit_client.safe_execute(_get_wiki)

        return [TextContent(type="text", text=json.dumps(wiki_data, indent=2))]

    except Exception as e:
        logger.error(f"Error getting subreddit wiki: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
