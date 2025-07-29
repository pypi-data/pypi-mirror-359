"""Puppeteer client for web scraping Reddit pages not available via API."""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PuppeteerClient:
    """Client for interacting with Puppeteer to scrape Reddit web pages."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None

    async def scrape_best_communities(self, page: int = 1) -> Dict[str, Any]:
        """Scrape Reddit's best communities page.

        Args:
            page: Page number to scrape (1-10)

        Returns:
            Dictionary containing communities data and pagination info
        """
        url = f"https://www.reddit.com/best/communities/{page}/"
        logger.info(f"Scraping best communities page {page}")

        try:
            # Use subprocess to run a Node.js script that uses Puppeteer
            script = f"""
const puppeteer = require('puppeteer');

(async () => {{
    const browser = await puppeteer.launch({{
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }});

    try {{
        const page = await browser.newPage();
        await page.goto('{url}', {{ waitUntil: 'networkidle2' }});

        // Extract community data
        const data = await page.evaluate(() => {{
            const communities = [];
            const links = document.querySelectorAll('a[href^="/r/"]');
            const subredditMap = new Map();

            links.forEach(link => {{
                const match = link.href.match(/\\/r\\/([^\\/]+)/);
                if (match && !subredditMap.has(match[1])) {{
                    let parent = link.parentElement;
                    let memberCount = '';

                    // Search for member count
                    for (let i = 0; i < 5 && parent; i++) {{
                        const text = parent.textContent || '';
                        const memberMatch = text.match(
                            /(\\d+(?:\\.\\d+)?[KM]?)\\s*members/i
                        );
                        if (memberMatch) {{
                            memberCount = memberMatch[0];
                            break;
                        }}
                        parent = parent.parentElement;
                    }}

                    subredditMap.set(match[1], {{
                        name: match[1],
                        url: link.href,
                        members: memberCount
                    }});
                }}
            }});

            // Convert to array with ranking
            const communitiesArray = Array.from(subredditMap.values());
            communitiesArray.forEach((comm, index) => {{
                comm.rank = index + 1 + ({page - 1} * 30);
            }});

            // Get pagination info
            const pageNumber = window.location.pathname.match(
                /\\/(\\d+)\\/?$/
            )?.[1] || '1';
            const pageLinks = Array.from(
                document.querySelectorAll('a[href*="/communities/"]')
            )
                .filter(a => /\\/communities\\/\\d+/.test(a.href))
                .map(a => a.href.match(/\\/communities\\/(\\d+)/)?.[1])
                .filter(Boolean)
                .map(Number);

            return {{
                communities: communitiesArray.slice(0, 30),
                pagination: {{
                    currentPage: parseInt(pageNumber),
                    totalPages: Math.max(...pageLinks, parseInt(pageNumber)),
                    hasNext: pageLinks.some(p => p > parseInt(pageNumber)),
                    hasPrev: parseInt(pageNumber) > 1
                }}
            }};
        }});

        console.log(JSON.stringify(data));
    }} finally {{
        await browser.close();
    }}
}})();
"""

            # Run the script
            result = await asyncio.create_subprocess_exec(
                'node', '-e', script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Puppeteer script failed: {error_msg}")

            # Parse the JSON output
            data = json.loads(stdout.decode())
            return data

        except Exception as e:
            logger.error(f"Error scraping best communities: {e}")
            raise



