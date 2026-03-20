from crawlers.types import USER_AGENT, FeedItem, FeedResult
import logging
import feedparser


log = logging.getLogger(__name__)


class RssCrawler:
    is_feed = True

    def fetch(self, url: str, config: dict) -> FeedResult:
        feed = feedparser.parse(url, agent=USER_AGENT)

        items = []
        for entry in feed.entries:
            items.append(
                FeedItem(
                    id=entry.get("id", entry.get("link", "")),
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    content=entry.get("summary", entry.get("description", "")),
                )
            )

        return FeedResult(items=items)
