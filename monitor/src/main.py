"""Entry point: load sources, check which are due, run pipeline."""

import argparse
import logging
import time
import tomllib
from datetime import datetime, timedelta
from pathlib import Path
from actions.digest import append_to_digest
from actions.pull_request import create_pull_request
from crawlers.html import HtmlCrawler
from crawlers.json import JsonCrawler
from crawlers.playwright import PlaywrightCrawler
from crawlers.reddit import RedditCrawler
from crawlers.rss import RssCrawler
from llm import query_llm
from state import STATE_DIR, load_state, save_state
from utils import get_domain, parse_duration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

CRAWLERS = {
    "html": HtmlCrawler,
    "json": JsonCrawler,
    "playwright": PlaywrightCrawler,
    "reddit": RedditCrawler,
    "rss": RssCrawler,
}
ACTIONS = {
    "digest": append_to_digest,
    "pr": create_pull_request,
}


def get_domain_config(config: dict, domain: str) -> dict:
    """Get merged domain config (default + domain-specific)."""
    domains = config.get("domains", {})
    return {**domains.get("default", {}), **domains.get(domain, {})}


def get_domain_delay(config: dict, domain: str) -> timedelta:
    """Get the crawl delay for a domain from the config."""
    return parse_duration(get_domain_config(config, domain).get("delay", "0s"))


def debounce_domain(state: dict, domain: str, delay: timedelta):
    """Sleep if needed to respect per-domain rate limits."""
    key = f"domain_last_request:{domain}"
    last_request = state.get(key)
    if last_request:
        elapsed = time.time() - last_request
        delay_seconds = delay.total_seconds()
        if elapsed < delay_seconds:
            time.sleep(delay_seconds - elapsed)
    state[key] = time.time()


def should_crawl(monitor_name: str, every: str, state: dict) -> bool:
    last_checked = state.get(f"last_checked:{monitor_name}")
    if not last_checked:
        return True
    interval = parse_duration(every)
    return datetime.now() - datetime.fromisoformat(last_checked) > interval


def crawl_feed(monitor_config: dict, monitor_name: str, crawler, state: dict):
    """Process a feed-type monitor (RSS, Reddit) where items are filtered individually."""
    result = crawler.fetch(monitor_config["url"], monitor_config)
    items = result.get("items", [])
    if not items:
        return

    seen_key = f"seen_ids:{monitor_name}"
    seen_ids = set(state.get(seen_key, []))
    new_items = [item for item in items if item.get("id") not in seen_ids]

    for item in new_items:
        prompt = monitor_config.get("prompt")
        log.info(f'[{monitor_name}] Processing item #{item["id"]}: "{item["title"]}"')
        if prompt:
            llm_response = query_llm(
                monitor_name,
                prompt,
                f"Title: {item['title']}\nPost text: {item['content']}",
            )
            if "NOT_RELEVANT" in llm_response.upper():
                log.info(f"[{monitor_name}] Skipping #{item['id']}: not relevant")
                seen_ids.add(item.get("id"))
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

        seen_ids.add(item.get("id"))

    # Keep only the most recent IDs to prevent unbounded growth
    state[seen_key] = list(seen_ids)[-1000:]


def crawl_page(monitor_config: dict, monitor_name: str, crawler, state: dict):
    """Process a page-type monitor (HTML, JSON) where the full content is diffed."""
    result = crawler.fetch(monitor_config["url"], monitor_config)
    content = result.get("content", "")

    content_key = f"content:{monitor_name}"
    previous_content = state.get(content_key)

    if previous_content == content:
        log.info(f"[{monitor_name}] No changes detected")
        return

    prompt = monitor_config.get("prompt")
    if prompt:
        if previous_content is None:
            user_message = content
        else:
            user_message = f"Previous content:\n{previous_content}\n\nNew content:\n{content}"

        llm_response = query_llm(monitor_name, prompt, user_message)
        if "NOT_RELEVANT" in llm_response.upper():
            state[content_key] = content
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

    state[content_key] = content


def run_pipeline(config: dict):
    state = load_state()

    monitors = config.get("monitors", {})
    if not monitors:
        log.warning("No monitors configured")
        return

    succeeded = 0
    failed = 0
    skipped = 0

    for monitor_name, monitor_config in sorted(monitors.items()):
        # Merge domain defaults into monitor config (monitor-level overrides)
        domain = get_domain(monitor_config["url"])
        domain_config = get_domain_config(config, domain)
        monitor_config = {**domain_config, **monitor_config}

        crawler_type = monitor_config.get("crawler")
        if crawler_type not in CRAWLERS:
            raise ValueError(f"Unknown crawler type '{crawler_type}' for {monitor_name}")

        every = monitor_config.get("every", "1d")
        if not should_crawl(monitor_name, every, state):
            log.info(f"[{monitor_name}] Skipped (not due for a recrawl)")
            skipped += 1
            continue

        log.info(f"[{monitor_name}] Processing single item...")

        debounce_domain(state, domain, get_domain_delay(config, domain))

        crawler_cls = CRAWLERS[crawler_type]
        crawler = crawler_cls()

        try:
            if crawler_cls.is_feed:
                crawl_feed(monitor_config, monitor_name, crawler, state)
            else:
                crawl_page(monitor_config, monitor_name, crawler, state)
            succeeded += 1
            state[f"last_checked:{monitor_name}"] = datetime.now().isoformat()
            save_state(state)
        except Exception:
            failed += 1
            log.exception(f"[{monitor_name}] Failed to process")

    log.log(
        logging.ERROR if failed else logging.INFO,
        f"Run complete: {succeeded} succeeded, {failed} failed, {skipped} skipped",
    )


def load_config(config_path: Path) -> dict:
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor external sources for changes.", epilog="Made with ❤️ in Berlin"
    )
    parser.add_argument("-c", "--config", type=Path, default=Path("monitor.toml"))
    args = parser.parse_args()

    config = load_config(args.config)

    log.info(f"State directory: {STATE_DIR}")
    log.info(f"Config file: {args.config}")

    while True:
        run_pipeline(config)
        time.sleep(60)


if __name__ == "__main__":
    main()
