from crawlers.html import HtmlCrawler
from crawlers.json import JsonCrawler
from crawlers.playwright import PlaywrightCrawler
from crawlers.reddit import RedditCrawler
from crawlers.rss import RssCrawler
from actions import ACTIONS
from llm import query_llm
from state import STATE_DIR
import dataclasses
import json
import logging

log = logging.getLogger(__name__)

CRAWLERS = {
    "html": HtmlCrawler,
    "json": JsonCrawler,
    "playwright": PlaywrightCrawler,
    "reddit": RedditCrawler,
    "rss": RssCrawler,
}


def crawl_feed(monitor, crawler, debug=False):
    """Process a feed-type monitor (RSS, Reddit) where items are filtered individually."""
    result = crawler.fetch(monitor.url, monitor.config)
    if not result.items:
        log.info(f"[{monitor.name}] Feed is empty")
        return

    new_items = [item for item in result.items if not monitor.is_feed_item_processed(item.id)]

    if not new_items:
        log.info(f"[{monitor.name}] No new items")
        monitor.mark_as_crawled()
        return

    for item in new_items:
        prompt = monitor.config.get("prompt", "").format_map(monitor.config) or None
        log.info(f'[{monitor.name}] Processing item #{item.id}: "{item.title}"')
        raw_input = json.dumps(dataclasses.asdict(item), indent=2, ensure_ascii=False)

        if prompt:
            llm_response = query_llm(
                monitor.name,
                prompt,
                f"Title: {item.title}\nPost text: {item.content}",
            )
            if llm_response.strip() == "ERROR":
                raise ValueError(f"[{monitor.name}] LLM could not extract value for #{item.id}")
            if "NOT_RELEVANT" in llm_response.upper():
                log.info(f"[{monitor.name}] Skipping #{item.id}: not relevant")
                monitor.save_feed_crawl_result(item.id, raw_input, "NOT_RELEVANT")
                continue
            summary = llm_response
        else:
            summary = item.content

        ACTIONS[monitor.config["action"]](
            state_dir=STATE_DIR,
            title=item.title or "Untitled",
            url=item.url or monitor.url,
            summary=summary,
            source_name=monitor.name,
            monitor_config=monitor.config,
            debug=debug,
        )

        monitor.save_feed_crawl_result(item.id, raw_input, summary)


def crawl_page(monitor, crawler, debug=False):
    """Process a page-type monitor (HTML, JSON) where the full content is diffed."""
    result = crawler.fetch(monitor.url, monitor.config)
    content = result.content

    previous_content = monitor.get_last_crawl_output(raw=True)

    if previous_content == content:
        log.info(f"[{monitor.name}] No changes detected")
        monitor.mark_as_crawled()
        return

    previous_summary = monitor.get_last_crawl_output(raw=False)

    prompt = monitor.config.get("prompt", "").format_map(monitor.config) or None
    if prompt:
        if previous_content is None:
            user_message = content
        else:
            user_message = f"Previous content:\n{previous_content}\n\nNew content:\n{content}"

        llm_response = query_llm(monitor.name, prompt, user_message)
        if llm_response.strip() == "ERROR":
            raise ValueError(f"[{monitor.name}] LLM could not extract value from page")
        if "NOT_RELEVANT" in llm_response.upper():
            log.info(f"[{monitor.name}] Changes not relevant")
            monitor.save_page_crawl_result(content, "NOT_RELEVANT")
            return
        summary = llm_response
    else:
        summary = content

    if previous_summary and previous_summary == summary:
        log.info(f"[{monitor.name}] Value unchanged: {summary}")
        monitor.save_page_crawl_result(content, summary)
        return

    ACTIONS[monitor.config["action"]](
        state_dir=STATE_DIR,
        title="Changes detected",
        url=monitor.url,
        summary=summary,
        raw_content=content,
        source_name=monitor.name,
        monitor_config=monitor.config,
        debug=debug,
    )

    monitor.save_page_crawl_result(content, summary)
