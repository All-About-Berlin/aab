"""JSON endpoint crawler."""

import json as json_lib
import logging

import requests

from crawlers import USER_AGENT

log = logging.getLogger(__name__)


class JsonCrawler:
    is_feed = False

    def fetch(self, url: str, config: dict) -> dict:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()

        data = response.json()
        content = json_lib.dumps(data, indent=2, ensure_ascii=False)

        return {"content": content, "items": None}
