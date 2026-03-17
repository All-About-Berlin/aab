"""RSS/Atom feed crawler using feedparser."""

import logging

import feedparser

from crawlers import USER_AGENT

log = logging.getLogger(__name__)


class RssCrawler:
    is_feed = True

    def fetch(self, url: str, config: dict) -> dict:
        feed = feedparser.parse(url, agent=USER_AGENT)

        items = []
        for entry in feed.entries:
            items.append(
                {
                    "id": entry.get("id", entry.get("link", "")),
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "content": entry.get("summary", entry.get("description", "")),
                }
            )

        return {"content": None, "items": items}
