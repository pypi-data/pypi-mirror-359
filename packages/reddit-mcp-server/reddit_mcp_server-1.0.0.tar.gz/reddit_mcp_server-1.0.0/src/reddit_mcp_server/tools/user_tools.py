"""User analysis tools for market research."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.types import TextContent, Tool

if TYPE_CHECKING:
    from ..reddit_client import RedditClient

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of user analysis tools."""
    return [
        Tool(
            name="search_user_content",
            description="Search a specific user's posts and comments",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Reddit username (without u/ prefix)",
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Type of content to search: posts, comments, or both",
                        "enum": ["posts", "comments", "both"],
                        "default": "both",
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order: new, top, hot, controversial",
                        "enum": ["new", "top", "hot", "controversial"],
                        "default": "new",
                    },
                    "time_filter": {
                        "type": "string",
                        "description": "Time filter for top/controversial: hour, day, week, month, year, all",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "default": "all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25, max: 100)",
                        "default": 25,
                    },
                },
                "required": ["username"],
            },
        ),
    ]


async def handle_tool_call(
    name: str, arguments: dict[str, Any], reddit_client: "RedditClient"
) -> list[TextContent]:
    """Handle user tool calls."""

    if name == "search_user_content":
        return await _search_user_content(
            arguments["username"],
            arguments.get("content_type", "both"),
            arguments.get("sort", "new"),
            arguments.get("time_filter", "all"),
            arguments.get("limit", 25),
            reddit_client
        )
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _search_user_content(
    username: str,
    content_type: str,
    sort: str,
    time_filter: str,
    limit: int,
    reddit_client: "RedditClient"
) -> list[TextContent]:
    """Search a user's content."""
    try:
        redditor = await reddit_client.get_redditor(username)
        results = {"posts": [], "comments": []}

        # Get posts if requested
        if content_type in ["posts", "both"]:
            def _get_posts():
                if sort == "new":
                    return list(redditor.submissions.new(limit=min(limit, 100)))
                elif sort == "top":
                    return list(redditor.submissions.top(time_filter=time_filter, limit=min(limit, 100)))
                elif sort == "hot":
                    return list(redditor.submissions.hot(limit=min(limit, 100)))
                elif sort == "controversial":
                    return list(redditor.submissions.controversial(time_filter=time_filter, limit=min(limit, 100)))

            submissions = await reddit_client.safe_execute(_get_posts)

            for submission in submissions:
                results["posts"].append({
                    "id": submission.id,
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "created_utc": submission.created_utc,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "url": submission.url,
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "is_self": submission.is_self,
                    "selftext": submission.selftext[:500] + "..." if len(submission.selftext) > 500 else submission.selftext,
                })

        # Get comments if requested
        if content_type in ["comments", "both"]:
            def _get_comments():
                if sort == "new":
                    return list(redditor.comments.new(limit=min(limit, 100)))
                elif sort == "top":
                    return list(redditor.comments.top(time_filter=time_filter, limit=min(limit, 100)))
                elif sort == "hot":
                    return list(redditor.comments.hot(limit=min(limit, 100)))
                elif sort == "controversial":
                    return list(redditor.comments.controversial(time_filter=time_filter, limit=min(limit, 100)))

            comments = await reddit_client.safe_execute(_get_comments)

            for comment in comments:
                results["comments"].append({
                    "id": comment.id,
                    "body": comment.body[:500] + "..." if len(comment.body) > 500 else comment.body,
                    "subreddit": comment.subreddit.display_name,
                    "created_utc": comment.created_utc,
                    "score": comment.score,
                    "permalink": f"https://reddit.com{comment.permalink}",
                    "submission_id": comment.submission.id,
                    "submission_title": comment.submission.title,
                })

        # Add user info
        user_info = {
            "username": redditor.name,
            "comment_karma": redditor.comment_karma,
            "link_karma": redditor.link_karma,
            "created_utc": redditor.created_utc,
            "is_verified": getattr(redditor, 'verified', False),
            "has_verified_email": getattr(redditor, 'has_verified_email', False),
        }

        final_result = {
            "user": user_info,
            "content": results,
            "summary": {
                "posts_returned": len(results["posts"]),
                "comments_returned": len(results["comments"]),
            }
        }

        return [TextContent(type="text", text=json.dumps(final_result, indent=2))]

    except Exception as e:
        logger.error(f"Error searching user content: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
