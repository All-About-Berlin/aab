"""Playwright crawler for JS-rendered pages."""

import logging

from playwright.sync_api import sync_playwright

log = logging.getLogger(__name__)


class PlaywrightCrawler:
    is_feed = False

    def fetch(self, url: str, config: dict) -> dict:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")

            selector = config.get("selector")
            if selector:
                elements = page.query_selector_all(selector)
                text = "\n".join(el.inner_text() for el in elements)
                if not text:
                    log.warning(f"Selector '{selector}' matched no text on {url}")
            else:
                text = page.inner_text("body")

            browser.close()

        return {"content": text, "items": None}
