from dataclasses import dataclass

USER_AGENT = "AllAboutBerlin-Monitor/1.0 (+https://allaboutberlin.com)"


@dataclass
class FeedItem:
    id: str
    title: str
    url: str
    content: str


@dataclass
class PageResult:
    content: str


@dataclass
class FeedResult:
    items: list[FeedItem]
