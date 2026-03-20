from datetime import date, datetime
from pathlib import Path

from state import STATE_DIR
from utils import parse_duration


class Monitor:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    @property
    def url(self) -> str:
        return self.config["url"]

    @property
    def dir(self) -> Path:
        d = STATE_DIR / "monitors" / self.name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def should_crawl(self) -> bool:
        last_checked = self.get_last_crawl_date()
        if not last_checked:
            return True
        interval = parse_duration(self.config.get("every", "1d"))
        return datetime.now() - last_checked > interval

    def get_last_crawl_date(self) -> datetime | None:
        files = sorted(self.dir.iterdir(), reverse=True)
        return datetime.strptime(files[0].name[:10], "%Y-%m-%d") if files else None

    def mark_as_crawled(self):
        today = date.today().isoformat()
        (self.dir / f"{today}-checked").touch()

    def get_last_crawl_output(self, raw=False) -> str | None:
        inputs = sorted([f for f in self.dir.iterdir() if f.stem.endswith("-in" if raw else "-out")], reverse=True)
        return inputs[0].read_text() if inputs else None

    def save_page_crawl_result(self, raw_input: str, output: str):
        """Write date-stamped input/output files for a page monitor."""
        today = date.today().isoformat()
        (self.dir / f"{today}-in.txt").write_text(raw_input)
        (self.dir / f"{today}-out.txt").write_text(output)

    def save_feed_crawl_result(self, item_id: str, raw_input: str, output: str):
        """Write date-stamped input/output files for a feed item."""
        today = date.today().isoformat()
        (self.dir / f"{today}-{item_id}-in.json").write_text(raw_input)
        (self.dir / f"{today}-{item_id}-out.txt").write_text(output)

    def is_feed_item_processed(self, item_id: str) -> bool:
        return any(f.stem.endswith(f"-{item_id}-in") for f in self.dir.iterdir())
