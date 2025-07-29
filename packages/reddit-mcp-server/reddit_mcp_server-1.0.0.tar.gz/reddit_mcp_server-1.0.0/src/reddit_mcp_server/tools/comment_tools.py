"""Comment analysis tools - placeholder."""

from typing import TYPE_CHECKING, Any

from mcp.types import TextContent, Tool

if TYPE_CHECKING:
    from ..reddit_client import RedditClient

def get_tools() -> list[Tool]:
    return []

async def handle_tool_call(name: str, arguments: dict[str, Any], reddit_client: "RedditClient") -> list[TextContent]:
    raise ValueError(f"Unknown tool: {name}")
