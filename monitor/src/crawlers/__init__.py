import json
import logging
from monitor.src.actions import ACTIONS
from monitor.src.llm import query_llm
from monitor.src.state import (
    STATE_DIR,
    is_feed_item_processed,
    read_page_content,
    save_feed_crawl_result,
    save_page_crawl_result,
    touch_monitor,
)
from crawlers.html import HtmlCrawler
from crawlers.json import JsonCrawler
from crawlers.playwright import PlaywrightCrawler
from crawlers.reddit import RedditCrawler
from crawlers.rss import RssCrawler


log = logging.getLogger(__name__)


USER_AGENT = "AllAboutBerlin-Monitor/1.0 (+https://allaboutberlin.com)"

CRAWLERS = {
    "html": HtmlCrawler,
    "json": JsonCrawler,
    "playwright": PlaywrightCrawler,
    "reddit": RedditCrawler,
    "rss": RssCrawler,
}


def crawl_feed(monitor_config: dict, monitor_name: str, crawler):
    """Process a feed-type monitor (RSS, Reddit) where items are filtered individually."""
    result = crawler.fetch(monitor_config["url"], monitor_config)
    items = result.get("items", [])
    if not items:
        return

    new_items = [item for item in items if not is_feed_item_processed(monitor_name, item.get("id"))]

    if not new_items:
        touch_monitor(monitor_name)
        return

    for item in new_items:
        prompt = monitor_config.get("prompt", "").format_map(monitor_config) or None
        log.info(f'[{monitor_name}] Processing item #{item["id"]}: "{item["title"]}"')
        raw_input = json.dumps(item, indent=2, ensure_ascii=False)

        if prompt:
            llm_response = query_llm(
                monitor_name,
                prompt,
                f"Title: {item['title']}\nPost text: {item['content']}",
            )
            if "NOT_RELEVANT" in llm_response.upper():
                log.info(f"[{monitor_name}] Skipping #{item['id']}: not relevant")
                save_feed_crawl_result(monitor_name, item["id"], raw_input, "NOT_RELEVANT")
                continue
            summary = llm_response
        else:
            summary = item.get("content", "")

        ACTIONS[monitor_config["action"]](
            state_dir=STATE_DIR,
            title=item.get("title", "Untitled"),
            url=item.get("url", monitor_config["url"]),
            summary=summary,
            source_name=monitor_name,
            monitor_config=monitor_config,
        )

        save_feed_crawl_result(monitor_name, item["id"], raw_input, summary)


def crawl_page(monitor_config: dict, monitor_name: str, crawler):
    """Process a page-type monitor (HTML, JSON) where the full content is diffed."""
    result = crawler.fetch(monitor_config["url"], monitor_config)
    content = result.get("content", "")

    previous_content = read_page_content(monitor_name)

    if previous_content == content:
        log.info(f"[{monitor_name}] No changes detected")
        save_page_crawl_result(monitor_name, content, "NO_CHANGE")
        return

    prompt = monitor_config.get("prompt", "").format_map(monitor_config) or None
    if prompt:
        if previous_content is None:
            user_message = content
        else:
            user_message = f"Previous content:\n{previous_content}\n\nNew content:\n{content}"

        llm_response = query_llm(monitor_name, prompt, user_message)
        if "NOT_RELEVANT" in llm_response.upper():
            save_page_crawl_result(monitor_name, content, "NOT_RELEVANT")
            return
        summary = llm_response
    else:
        summary = content

    ACTIONS[monitor_config["action"]](
        state_dir=STATE_DIR,
        title="Changes detected",
        url=monitor_config["url"],
        summary=summary,
        source_name=monitor_name,
        monitor_config=monitor_config,
    )

    save_page_crawl_result(monitor_name, content, summary)
