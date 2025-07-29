"""Tools for scraping Reddit's best communities rankings."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.types import TextContent, Tool

if TYPE_CHECKING:
    from ..reddit_client import RedditClient

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of best communities tools."""
    return [
        Tool(
            name="get_best_communities",
            description="Get Reddit's curated list of best communities with rankings",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number to retrieve (1-10, default: 1)",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": [],
            },
        ),
    ]


async def handle_tool_call(
    name: str, arguments: dict[str, Any], reddit_client: "RedditClient"
) -> list[TextContent]:
    """Handle tool calls for best communities tools."""
    if name == "get_best_communities":
        return await _get_best_communities(arguments.get("page", 1))
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _get_best_communities(page: int) -> list[TextContent]:
    """Get Reddit's best communities from the web interface.

    This scrapes the /best/communities/ page which shows Reddit's
    curated ranking of top communities.
    """
    try:
        from ..puppeteer_client import PuppeteerClient

        # Use Puppeteer scraper
        client = PuppeteerClient()
        data = await client.scrape_best_communities(page)

        # Format the response
        result = {
            "page": data["pagination"]["currentPage"],
            "total_pages": data["pagination"]["totalPages"],
            "has_next": data["pagination"]["hasNext"],
            "has_previous": data["pagination"]["hasPrev"],
            "communities": []
        }

        for community in data["communities"]:
            result["communities"].append({
                "rank": community["rank"],
                "name": community["name"],
                "url": community["url"],
                "members": community["members"],
                "members_count": _parse_member_count(community["members"])
            })

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error getting best communities: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def _parse_member_count(members_str: str) -> int:
    """Parse member count string to integer.

    Examples:
        "67M members" -> 67000000
        "3.4M members" -> 3400000
        "47K members" -> 47000
        "123 members" -> 123
    """
    try:
        # Remove " members" suffix
        count_str = members_str.replace(" members", "").strip()

        # Handle M (millions)
        if "M" in count_str:
            number = float(count_str.replace("M", ""))
            return int(number * 1_000_000)

        # Handle K (thousands)
        elif "K" in count_str:
            number = float(count_str.replace("K", ""))
            return int(number * 1_000)

        # Plain number
        else:
            return int(count_str)

    except Exception:
        return 0

