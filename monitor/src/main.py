import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from config import get_monitor_config, load_config
from crawlers import CRAWLERS, crawl_feed, crawl_page
from monitor import Monitor
from state import STATE_DIR
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
        monitor = Monitor(monitor_name, get_monitor_config(config, monitor_name))
        domain = get_domain(monitor.url)

        crawler_type = monitor.config.get("crawler")
        if crawler_type not in CRAWLERS:
            raise ValueError(f"Unknown crawler type '{crawler_type}' for {monitor.name}")

        next_crawl_date = monitor.get_next_crawl_date()
        if datetime.now() < next_crawl_date:
            log.info(f"[{monitor.name}] Skipped (will recrawl on {next_crawl_date.date().isoformat()})")
            skipped += 1
            continue

        log.info(f"[{monitor.name}] Processing single item...")

        debounce_domain(domain, parse_duration(monitor.config.get("delay", "0s")))

        crawler_cls = CRAWLERS[crawler_type]
        crawler = crawler_cls()

        try:
            if crawler_cls.is_feed:
                crawl_feed(monitor, crawler)
            else:
                crawl_page(monitor, crawler)
            succeeded += 1
        except Exception:
            failed += 1
            log.exception(f"[{monitor.name}] Failed to process")

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
