import argparse
import logging
import time
from pathlib import Path
from config import get_monitor_config, load_config
from monitor.src.crawlers import CRAWLERS, crawl_feed, crawl_page
from state import (
    STATE_DIR,
    should_crawl,
)
from utils import debounce_domain, get_domain, parse_duration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def run(config: dict):
    monitors = config.get("monitors", {})
    if not monitors:
        log.warning("No monitors configured")
        return

    succeeded = 0
    failed = 0
    skipped = 0

    for monitor_name in sorted(monitors):
        monitor_config = get_monitor_config(config, monitor_name)
        domain = get_domain(monitor_config["url"])

        crawler_type = monitor_config.get("crawler")
        if crawler_type not in CRAWLERS:
            raise ValueError(f"Unknown crawler type '{crawler_type}' for {monitor_name}")

        if not should_crawl(monitor_name, monitor_config):
            log.info(f"[{monitor_name}] Skipped (not due for a recrawl)")
            skipped += 1
            continue

        log.info(f"[{monitor_name}] Processing single item...")

        debounce_domain(domain, parse_duration(monitor_config.get("delay", "0s")))

        crawler_cls = CRAWLERS[crawler_type]
        crawler = crawler_cls()

        try:
            if crawler_cls.is_feed:
                crawl_feed(monitor_config, monitor_name, crawler)
            else:
                crawl_page(monitor_config, monitor_name, crawler)
            succeeded += 1
        except Exception:
            failed += 1
            log.exception(f"[{monitor_name}] Failed to process")

    log.log(
        logging.ERROR if failed else logging.INFO,
        f"Run complete: {succeeded} succeeded, {failed} failed, {skipped} skipped",
    )


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
        run(config)
        time.sleep(60)


if __name__ == "__main__":
    main()
