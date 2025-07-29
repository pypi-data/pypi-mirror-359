"""Content retrieval tools for market research."""

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.types import TextContent, Tool

if TYPE_CHECKING:
    from ..reddit_client import RedditClient

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of content retrieval tools."""
    return [
        Tool(
            name="search_subreddit_content",
            description="Search for posts within a specific subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords, brand names, etc.)",
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order: relevance, hot, top, new, comments",
                        "enum": ["relevance", "hot", "top", "new", "comments"],
                        "default": "relevance",
                    },
                    "time_filter": {
                        "type": "string",
                        "description": "Time filter: all, day, week, month, year",
                        "enum": ["all", "day", "week", "month", "year"],
                        "default": "all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25, max: 100)",
                        "default": 25,
                    },
                },
                "required": ["subreddit_name", "query"],
            },
        ),
        Tool(
            name="get_hot_posts",
            description="Get trending/hot posts from a subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25, max: 100)",
                        "default": 25,
                    },
                },
                "required": ["subreddit_name"],
            },
        ),
        Tool(
            name="get_top_posts",
            description="Get top posts from a subreddit with time filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit_name": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/ prefix)",
                    },
                    "time_filter": {
                        "type": "string",
                        "description": "Time filter: hour, day, week, month, year, all",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "default": "day",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25, max: 100)",
                        "default": 25,
                    },
                },
                "required": ["subreddit_name"],
            },
        ),
        Tool(
            name="get_post_details",
            description="Get detailed information about a specific post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID (the alphanumeric ID from the URL)",
                    },
                },
                "required": ["post_id"],
            },
        ),
        Tool(
            name="get_post_comments",
            description="Get all comments from a specific post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID (the alphanumeric ID from the URL)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of top-level comments to retrieve (default: 100)",
                        "default": 100,
                    },
                    "sort": {
                        "type": "string",
                        "description": "Comment sort order: best, top, new, controversial, old, qa",
                        "enum": ["best", "top", "new", "controversial", "old", "qa"],
                        "default": "best",
                    },
                },
                "required": ["post_id"],
            },
        ),
        Tool(
            name="search_all_reddit",
            description="Search across all of Reddit for keywords/brands",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords, brand names, etc.)",
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order: relevance, hot, top, new, comments",
                        "enum": ["relevance", "hot", "top", "new", "comments"],
                        "default": "relevance",
                    },
                    "time_filter": {
                        "type": "string",
                        "description": "Time filter: all, day, week, month, year",
                        "enum": ["all", "day", "week", "month", "year"],
                        "default": "all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 25, max: 100)",
                        "default": 25,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


async def handle_tool_call(
    name: str, arguments: dict[str, Any], reddit_client: "RedditClient"
) -> list[TextContent]:
    """Handle content tool calls."""

    if name == "search_subreddit_content":
        return await _search_subreddit_content(
            arguments["subreddit_name"],
            arguments["query"],
            arguments.get("sort", "relevance"),
            arguments.get("time_filter", "all"),
            arguments.get("limit", 25),
            reddit_client
        )
    elif name == "get_hot_posts":
        return await _get_hot_posts(
            arguments["subreddit_name"],
            arguments.get("limit", 25),
            reddit_client
        )
    elif name == "get_top_posts":
        return await _get_top_posts(
            arguments["subreddit_name"],
            arguments.get("time_filter", "day"),
            arguments.get("limit", 25),
            reddit_client
        )
    elif name == "get_post_details":
        return await _get_post_details(
            arguments["post_id"],
            reddit_client
        )
    elif name == "get_post_comments":
        return await _get_post_comments(
            arguments["post_id"],
            arguments.get("limit", 100),
            arguments.get("sort", "best"),
            reddit_client
        )
    elif name == "search_all_reddit":
        return await _search_all_reddit(
            arguments["query"],
            arguments.get("sort", "relevance"),
            arguments.get("time_filter", "all"),
            arguments.get("limit", 25),
            reddit_client
        )
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _search_subreddit_content(
    subreddit_name: str,
    query: str,
    sort: str,
    time_filter: str,
    limit: int,
    reddit_client: "RedditClient"
) -> list[TextContent]:
    """Search for posts within a specific subreddit."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        def _search():
            return list(subreddit.search(
                query,
                sort=sort,
                time_filter=time_filter,
                limit=min(limit, 100)
            ))

        submissions = await reddit_client.safe_execute(_search)

        results = []
        for submission in submissions:
            results.append(_format_submission(submission))

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error searching subreddit content: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_hot_posts(
    subreddit_name: str,
    limit: int,
    reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get hot posts from a subreddit."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        def _get_hot():
            return list(subreddit.hot(limit=min(limit, 100)))

        submissions = await reddit_client.safe_execute(_get_hot)

        results = []
        for submission in submissions:
            results.append(_format_submission(submission))

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error getting hot posts: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_top_posts(
    subreddit_name: str,
    time_filter: str,
    limit: int,
    reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get top posts from a subreddit."""
    try:
        subreddit = await reddit_client.get_subreddit(subreddit_name)

        def _get_top():
            return list(subreddit.top(time_filter=time_filter, limit=min(limit, 100)))

        submissions = await reddit_client.safe_execute(_get_top)

        results = []
        for submission in submissions:
            results.append(_format_submission(submission))

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error getting top posts: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_post_details(
    post_id: str,
    reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get detailed information about a post."""
    try:
        submission = await reddit_client.get_submission(post_id)

        result = {
            "id": submission.id,
            "title": submission.title,
            "author": submission.author.name if submission.author else "[deleted]",
            "subreddit": submission.subreddit.display_name,
            "created_utc": submission.created_utc,
            "url": submission.url,
            "selftext": submission.selftext,
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "is_video": submission.is_video,
            "over_18": submission.over_18,
            "spoiler": submission.spoiler,
            "stickied": submission.stickied,
            "locked": submission.locked,
            "awards": len(submission.all_awardings) if hasattr(submission, 'all_awardings') else 0,
            "permalink": f"https://reddit.com{submission.permalink}",
            "link_flair_text": submission.link_flair_text,
            "domain": submission.domain,
            "is_self": submission.is_self,
            "thumbnail": submission.thumbnail,
            "edited": submission.edited,
            "num_crossposts": submission.num_crossposts,
            "view_count": submission.view_count,
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error getting post details: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _get_post_comments(
    post_id: str,
    limit: int,
    sort: str,
    reddit_client: "RedditClient"
) -> list[TextContent]:
    """Get comments from a post."""
    try:
        submission = await reddit_client.get_submission(post_id)

        def _get_comments():
            submission.comment_sort = sort
            submission.comments.replace_more(limit=0)  # Remove "load more comments"
            return submission.comments.list()[:limit]

        comments = await reddit_client.safe_execute(_get_comments)

        results = []
        for comment in comments:
            if hasattr(comment, 'body'):
                results.append({
                    "id": comment.id,
                    "author": comment.author.name if comment.author else "[deleted]",
                    "body": comment.body,
                    "score": comment.score,
                    "created_utc": comment.created_utc,
                    "edited": comment.edited,
                    "is_submitter": comment.is_submitter,
                    "stickied": comment.stickied,
                    "depth": comment.depth,
                    "permalink": f"https://reddit.com{comment.permalink}",
                    "parent_id": comment.parent_id,
                    "num_replies": len(comment.replies) if hasattr(comment, 'replies') else 0,
                })

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error getting post comments: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _search_all_reddit(
    query: str,
    sort: str,
    time_filter: str,
    limit: int,
    reddit_client: "RedditClient"
) -> list[TextContent]:
    """Search across all of Reddit."""
    try:
        reddit = reddit_client.get_reddit()

        def _search():
            return list(reddit.subreddit("all").search(
                query,
                sort=sort,
                time_filter=time_filter,
                limit=min(limit, 100)
            ))

        submissions = await reddit_client.safe_execute(_search)

        results = []
        for submission in submissions:
            results.append(_format_submission(submission))

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    except Exception as e:
        logger.error(f"Error searching all of Reddit: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def _format_submission(submission) -> dict:
    """Format submission data for output."""
    return {
        "id": submission.id,
        "title": submission.title,
        "author": submission.author.name if submission.author else "[deleted]",
        "subreddit": submission.subreddit.display_name,
        "created_utc": submission.created_utc,
        "score": submission.score,
        "upvote_ratio": submission.upvote_ratio,
        "num_comments": submission.num_comments,
        "url": submission.url,
        "permalink": f"https://reddit.com{submission.permalink}",
        "is_self": submission.is_self,
        "selftext": submission.selftext[:500] + "..." if len(submission.selftext) > 500 else submission.selftext,
        "link_flair_text": submission.link_flair_text,
        "over_18": submission.over_18,
    }
