# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

reddit-mcp is a Market Research Platform for Reddit implemented as an MCP (Model Context Protocol) server. It provides 19 specialized tools for gathering Reddit data using PRAW (Python Reddit API Wrapper), designed for AI-powered market research and analysis.

## Development Commands

### Setup and Installation
```bash
# Install in editable mode
pip install -e .

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Reddit API credentials:
# - REDDIT_CLIENT_ID
# - REDDIT_CLIENT_SECRET
# - REDDIT_USER_AGENT
```

### Running the Server
```bash
# Run the MCP server
python -m reddit_mcp_server.server
# or
reddit-mcp-server
```

### Code Quality and Testing
```bash
# Run tests
pytest tests/

# Run a specific test
pytest tests/test_specific.py::test_function_name

# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
ruff src/ tests/
```

## Architecture Overview

### Core Components

1. **server.py**: Main MCP server implementation
   - Handles stdio transport for MCP protocol
   - Manages tool listing and execution
   - Entry point for the application

2. **reddit_client.py**: PRAW wrapper with async support
   - Manages Reddit API authentication
   - Provides singleton Reddit instance
   - Handles both authenticated and read-only access

3. **tools/**: Tool implementations organized by category
   - `reddit_instance_tools.py`: Random subreddit, username checks
   - `subreddit_tools.py`: Subreddit discovery and analysis (8 tools)
   - `content_tools.py`: Post and content retrieval (6 tools)
   - `user_tools.py`: User post/comment analysis
   - `comment_tools.py`: Comment-specific operations
   - `advanced_tools.py`: Data export functionality

4. **utils/export.py**: Data export utilities
   - JSON and CSV export capabilities
   - Handles complex Reddit data structures

### Tool Categories and Usage

The server provides 19 tools for Reddit data collection:
- Reddit Instance Tools (3): Basic Reddit operations
- Subreddit Discovery (8): Find and analyze subreddits
- Content Retrieval (6): Get posts and comments
- User Analysis (1): Analyze user activity
- Data Export (1): Export collected data

### Key Design Patterns

1. **Async/Await**: All tools use async patterns for non-blocking operations
2. **Error Handling**: Comprehensive try-catch blocks with meaningful error messages
3. **Data Transformation**: Tools return structured data optimized for AI analysis
4. **Modular Structure**: Clear separation between server, client, and tool implementations

## Important Notes

- The project uses PRAW (Python Reddit API Wrapper) which has rate limiting built-in
- Authentication is optional but provides higher rate limits and access to more features
- All tools return data in formats optimized for market research analysis
- The server uses MCP v1.0.0+ protocol for communication with AI models