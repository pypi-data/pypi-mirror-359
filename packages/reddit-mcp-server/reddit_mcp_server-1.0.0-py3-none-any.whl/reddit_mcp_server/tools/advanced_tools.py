"""Advanced research tools for data export and analysis."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.types import TextContent, Tool

from ..utils import export_data as export_util

if TYPE_CHECKING:
    from ..reddit_client import RedditClient

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of advanced research tools."""
    return [
        Tool(
            name="export_data",
            description="Export collected data in JSON or CSV format",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": ["array", "object"],
                        "description": "Data to export (array of objects or single object)",
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format: json or csv",
                        "enum": ["json", "csv"],
                        "default": "json",
                    },
                },
                "required": ["data"],
            },
        ),
    ]


async def handle_tool_call(
    name: str, arguments: dict[str, Any], reddit_client: "RedditClient"
) -> list[TextContent]:
    """Handle advanced tool calls."""

    if name == "export_data":
        return await _export_data(
            arguments["data"],
            arguments.get("format", "json")
        )
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _export_data(
    data: Any,
    format: str
) -> list[TextContent]:
    """Export data in the specified format."""
    try:
        exported_data = export_util(data, format)

        result = {
            "status": "success",
            "format": format,
            "data": exported_data,
            "message": f"Data exported successfully as {format.upper()}"
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
