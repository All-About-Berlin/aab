"""Reddit crawler using the JSON API."""

import logging

import requests

from crawlers.types import USER_AGENT, FeedItem, FeedResult

log = logging.getLogger(__name__)


class RedditCrawler:
    is_feed = True

    def fetch(self, url: str, config: dict) -> FeedResult:
        if not url.endswith(".json"):
            url = url.rstrip("/") + ".json"

        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()

        data = response.json()
        posts = data.get("data", {}).get("children", [])

        items = []
        for post in posts:
            post_data = post.get("data", {})
            items.append(
                FeedItem(
                    id=post_data.get("id"),
                    title=post_data.get("title", ""),
                    url=f"https://old.reddit.com{post_data.get('permalink', '')}",
                    content=post_data.get("selftext", ""),
                )
            )

        return FeedResult(items=items)
