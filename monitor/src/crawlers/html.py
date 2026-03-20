"""HTML page crawler using requests + BeautifulSoup."""

import logging

import requests
from bs4 import BeautifulSoup

from crawlers import USER_AGENT, PageResult

log = logging.getLogger(__name__)


class HtmlCrawler:
    is_feed = False

    def fetch(self, url: str, config: dict) -> PageResult:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        selector = config.get("selector")
        if selector:
            elements = soup.select(selector)
            text = "\n".join(el.get_text(strip=True) for el in elements)
            if not text:
                log.warning(f"Selector '{selector}' matched no text on {url}")
        else:
            body = soup.find("body")
            text = body.get_text(strip=True) if body else soup.get_text(strip=True)

        return PageResult(content=text)
