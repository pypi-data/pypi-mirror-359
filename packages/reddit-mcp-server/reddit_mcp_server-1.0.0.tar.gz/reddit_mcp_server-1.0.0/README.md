# Reddit MCP Server

A focused market research platform for Reddit using PRAW (Python Reddit API Wrapper) built as an MCP (Model Context Protocol) server. This server provides 20 specialized tools for gathering Reddit data, optimized for AI-powered market research and analysis.

**Note**: This server focuses on data collection while the AI model using this MCP performs the actual analysis. All tools return structured JSON data optimized for AI processing.

## Features

This MCP server is optimized for market research, providing 20 focused tools for gathering Reddit data. The AI model using this server will perform the actual analysis.

### 🔧 **Reddit Instance Tools (3)**
- `get_random_subreddit` - Get a random subreddit
- `check_username_available` - Check if a username is available  
- `get_reddit_info` - Get Reddit instance information

### 🏘️ **Subreddit Discovery & Analysis (8)**
- `search_subreddits` - Search for subreddits by name or topic
- `get_popular_subreddits` - Get popular subreddits
- `get_new_subreddits` - Get newly created subreddits
- `get_subreddit_info` - Get detailed subreddit information
- `get_subreddit_rules` - Get subreddit rules
- `get_subreddit_moderators` - Get subreddit moderators
- `get_subreddit_traffic` - Get subreddit traffic stats (requires mod access)
- `get_subreddit_wiki` - Get subreddit wiki pages

### 📄 **Content Retrieval (6)**
- `search_subreddit_content` - Search for posts within a specific subreddit (keywords, brands)
- `get_hot_posts` - Get trending posts from a subreddit
- `get_top_posts` - Get top posts with time filters (day/week/month/year/all)
- `get_post_details` - Get detailed post information including engagement metrics
- `get_post_comments` - Get all comments from a post for sentiment analysis
- `search_all_reddit` - Search across all of Reddit for keywords/brands

### 👤 **User Analysis (1)**
- `search_user_content` - Search a specific user's posts and comments

### 🏆 **Best Communities (1)**
- `get_best_communities` - Get Reddit's curated list of best communities with rankings

### 📊 **Data Export (1)**
- `export_data` - Export collected data as JSON or CSV for external analysis

## ✅ Completed Implementation (20 Tools)

All 20 tools have been fully implemented and are ready for use:

- **Reddit Instance Tools**: 3/3 ✅
- **Subreddit Discovery & Analysis**: 8/8 ✅
- **Content Retrieval**: 6/6 ✅
- **User Analysis**: 1/1 ✅
- **Best Communities**: 1/1 ✅
- **Data Export**: 1/1 ✅

## 🎯 Key Features for Market Research

### 1. **Brand Monitoring**
- Search for brand mentions across Reddit or within specific communities
- Track competitor discussions and comparisons
- Monitor product launches and announcements

### 2. **Engagement Metrics**
- Get upvote ratios, comment counts, and award data
- Track post performance over time
- Identify viral content and trending discussions

### 3. **Time-based Analysis**
- Filter content by time periods: hour, day, week, month, year
- Track seasonal trends and patterns
- Monitor real-time discussions with "new" and "hot" sorting

### 4. **Export Capabilities**
- Export data as JSON for programmatic analysis
- Export as CSV for Excel, Google Sheets, or BI tools
- Flatten nested data structures automatically

### 5. **Influencer Tracking**
- Monitor specific user activity and engagement
- Track user karma and posting patterns
- Analyze influencer impact on discussions

## Installation

### 1. Install the package

```bash
# Clone the repository
git clone https://github.com/your-org/reddit-mcp-server
cd reddit-mcp-server

# Install dependencies
pip install -e .
```

### 2. Additional Requirements

This server uses Puppeteer for web scraping certain Reddit pages that aren't available through the API (such as the best communities rankings). You'll need:

- Node.js (v14 or higher)
- Puppeteer (installed via npm)

The Puppeteer dependency will need to be installed separately:

```bash
# Install Node.js if you don't have it
# On Ubuntu/Debian:
sudo apt-get install nodejs npm

# On macOS with Homebrew:
brew install node

# Install Puppeteer globally
npm install -g puppeteer
```

Note: The server will attempt to use Puppeteer for the `get_best_communities` tool. Make sure Puppeteer is properly installed for this feature to work.

### 3. Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps/
2. Click \"Create App\" or \"Create Another App\"
3. Choose \"script\" as the app type
4. Note down your `client_id` and `client_secret`

### 4. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Reddit API credentials:

```env
# Required credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=reddit-mcp-server:v1.0.0 (by /u/yourusername)

# Optional - for authenticated access
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### 5. Configure MCP Client

Add the server to your MCP client configuration (e.g., Claude Desktop):

```json
{
  \"mcpServers\": {
    \"reddit-research\": {
      \"command\": \"python\",
      \"args\": [\"-m\", \"reddit_mcp_server.server\"],
      \"cwd\": \"/path/to/your/reddit-mcp-server\",
      \"env\": {
        \"REDDIT_CLIENT_ID\": \"your_client_id_here\",
        \"REDDIT_CLIENT_SECRET\": \"your_client_secret_here\", 
        \"REDDIT_USER_AGENT\": \"reddit-mcp-server:v1.0.0 (by /u/yourusername)\",
        \"REDDIT_USERNAME\": \"your_reddit_username\",
        \"REDDIT_PASSWORD\": \"your_reddit_password\"
      }
    }
  }
}
```

## Usage

### Quick Start Examples

```python
# 1. Brand Monitoring - Track iPhone 15 discussions
iphone_mentions = search_subreddit_content(
    subreddit_name=\"apple\", 
    query=\"iPhone 15 Pro\", 
    time_filter=\"week\",
    sort=\"top\"
)

# 2. Competitor Analysis - Compare brands
competitor_data = search_all_reddit(
    query=\"Samsung Galaxy S24 vs iPhone 15\",
    time_filter=\"month\",
    limit=100
)

# 3. Market Trends - Find trending topics
trending = get_hot_posts(subreddit_name=\"technology\", limit=50)
top_weekly = get_top_posts(subreddit_name=\"gadgets\", time_filter=\"week\")

# 4. Product Launch Reception - Analyze a specific announcement
post_data = get_post_details(post_id=\"1ac3def\")
user_feedback = get_post_comments(post_id=\"1ac3def\", limit=500, sort=\"best\")

# 5. Influencer Tracking - Monitor key voices
tech_influencer = search_user_content(
    username=\"mkbhd\",
    content_type=\"posts\",
    sort=\"top\",
    time_filter=\"month\"
)

# 6. Subreddit Discovery - Find your audience
crypto_communities = search_subreddits(query=\"cryptocurrency\", limit=20)
finance_subs = get_popular_subreddits(limit=50)

# 7. Best Communities - Discover top-ranked communities
best_communities = get_best_communities(page=1)
# Returns ranked communities with member counts and pagination info
# Navigate through pages to explore more communities
page_2_communities = get_best_communities(page=2)

# 8. Export for Analysis
export_data(data={
    \"brand_mentions\": iphone_mentions,
    \"competitor_analysis\": competitor_data,
    \"user_feedback\": user_feedback
}, format=\"csv\")
```

### Complete Market Research Workflow Example

```python
# Step 1: Find relevant subreddits for your market
subreddits = search_subreddits(query=\"electric vehicles\", limit=10)

# Step 2: Explore top-ranked communities in your market
best_communities = get_best_communities(page=1)
# Find highly engaged communities related to your market
for community in best_communities[\"communities\"]:
    if \"tech\" in community[\"name\"].lower() or \"electric\" in community[\"name\"].lower():
        print(f\"Found relevant community: {community['name']} with {community['members_count']} members\")

# Step 3: Analyze trending discussions in the main subreddit
hot_posts = get_hot_posts(subreddit_name=\"electricvehicles\", limit=50)

# Step 4: Search for specific brand mentions
brand_mentions = search_subreddit_content(
    subreddit_name=\"electricvehicles\", 
    query=\"Tesla Model 3 vs Polestar 2\",
    time_filter=\"month\",
    sort=\"relevance\"
)

# Step 5: Deep dive into high-engagement posts
for post in brand_mentions[:5]:  # Top 5 posts
    # Get detailed metrics
    post_details = get_post_details(post_id=post[\"id\"])
    
    # Get all comments for sentiment analysis
    comments = get_post_comments(post_id=post[\"id\"], limit=200, sort=\"best\")
    
    # Export individual post analysis
    export_data(
        data={
            \"post\": post_details,
            \"comments\": comments,
            \"metadata\": {
                \"subreddit\": \"electricvehicles\",
                \"search_query\": \"Tesla Model 3 vs Polestar 2\",
                \"collected_date\": \"2025-01-24\"
            }
        },
        format=\"json\"
    )

# Step 6: Track influencer opinions
influencers = [\"teslaexpert123\", \"evanalyst\", \"electriccarsguy\"]
influencer_data = []

for username in influencers:
    user_content = search_user_content(
        username=username,
        content_type=\"both\",
        sort=\"top\",
        time_filter=\"month\"
    )
    influencer_data.append(user_content)

# Step 7: Export complete dataset for analysis
export_data(
    data={
        \"market_subreddits\": subreddits,
        \"trending_posts\": hot_posts,
        \"brand_comparisons\": brand_mentions,
        \"influencer_opinions\": influencer_data
    },
    format=\"csv\"
)
```

### Authentication Modes

#### Read-Only Mode
- Only requires `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `REDDIT_USER_AGENT`
- Can access public content, popular subreddits, search functionality
- Cannot access user-specific data or private subreddits

#### Authenticated Mode  
- Requires all credentials including `REDDIT_USERNAME` and `REDDIT_PASSWORD`
- Full access to Reddit API including private subreddits and user data
- Rate limits apply (60 requests per minute)

## Development

### Project Structure

```
src/reddit_mcp_server/
├── __init__.py              # Package initialization
├── server.py                # Main MCP server
├── reddit_client.py         # PRAW wrapper with async support
├── puppeteer_client.py      # Puppeteer integration for web scraping
├── tools/                   # Tool implementations
│   ├── __init__.py
│   ├── reddit_instance_tools.py
│   ├── subreddit_tools.py
│   ├── content_tools.py
│   ├── user_tools.py
│   ├── comment_tools.py
│   ├── advanced_tools.py
│   └── best_communities_tools.py
└── utils/                   # Utility functions
    ├── __init__.py
    └── export.py
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports  
isort src/ tests/

# Type checking
mypy src/

# Linting
ruff src/ tests/
```

## Rate Limits & Best Practices

- Reddit API has a rate limit of 60 requests per minute per OAuth client ID
- The server implements error handling and logging for failed requests
- Use appropriate limits when fetching large datasets
- Consider implementing caching for frequently accessed data

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Use Cases for Market Research

### Brand Monitoring
- Track brand mentions and sentiment across Reddit
- Monitor competitor discussions
- Identify emerging trends in your market

### Audience Research  
- Discover where your target audience congregates
- Analyze discussion patterns and interests
- Track influencer activity and impact

### Product Feedback
- Find unfiltered user opinions about products
- Identify common complaints or feature requests
- Track product launch reception

### Trend Analysis
- Monitor emerging topics in specific industries
- Track viral content patterns
- Identify seasonal trends and patterns

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-org/reddit-mcp-server/issues) page
2. Review the Reddit API documentation: https://praw.readthedocs.io/
3. Create a new issue with detailed information about your problem