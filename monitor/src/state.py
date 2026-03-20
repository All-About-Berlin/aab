import time
from datetime import date, datetime
from pathlib import Path

from platformdirs import user_state_dir

from monitor.src.utils import parse_duration

STATE_DIR = Path(user_state_dir("aab-monitor"))


def get_monitor_dir(monitor_name: str) -> Path:
    """Return and create the per-monitor state directory."""
    d = STATE_DIR / "monitors" / monitor_name
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_last_crawl_date(monitor_name: str) -> datetime | None:
    files = sorted(get_monitor_dir(monitor_name).iterdir(), reverse=True)
    if not files:
        return None
    # Parse date from filename: "2026-01-23-in.txt" or "2026-01-23-abc-in.json"
    return datetime.strptime(files[0].name[:10], "%Y-%m-%d")


def should_crawl(monitor_name: str, monitor_config: dict) -> bool:
    last_checked = get_last_crawl_date(monitor_name)
    if not last_checked:
        return True
    interval = parse_duration(monitor_config.get("every", "1d"))
    return datetime.now() - last_checked > interval


def read_page_content(monitor_name: str) -> str | None:
    """Read the most recent raw input file for a page monitor."""
    inputs = sorted([f for f in get_monitor_dir(monitor_name).iterdir() if f.name.endswith("-in.txt")], reverse=True)
    return inputs[0].read_text() if inputs else None


def save_page_crawl_result(monitor_name: str, raw_input: str, output: str):
    """Write date-stamped input/output files for a page monitor."""
    d = get_monitor_dir(monitor_name)
    today = date.today().isoformat()
    (d / f"{today}-in.txt").write_text(raw_input)
    (d / f"{today}-out.txt").write_text(output)


def save_feed_crawl_result(monitor_name: str, item_id: str, raw_input: str, output: str):
    """Write date-stamped input/output files for a feed item."""
    d = get_monitor_dir(monitor_name)
    today = date.today().isoformat()
    (d / f"{today}-{item_id}-in.json").write_text(raw_input)
    (d / f"{today}-{item_id}-out.txt").write_text(output)


def is_feed_item_processed(monitor_name: str, item_id: str) -> bool:
    return any(f.stem.endswith(f"-{item_id}-in") for f in get_monitor_dir(monitor_name).iterdir())


def touch_monitor(monitor_name: str):
    """Create a marker file to record that a monitor was checked today."""
    d = get_monitor_dir(monitor_name)
    today = date.today().isoformat()
    marker = d / f"{today}-checked"
    marker.touch()


def read_domain_timestamp(domain: str) -> float | None:
    """Read the last request timestamp for a domain."""
    f = STATE_DIR / "domains" / domain
    try:
        return float(f.read_text())
    except (FileNotFoundError, ValueError):
        return None


def write_domain_timestamp(domain: str):
    """Write the current timestamp for a domain."""
    d = STATE_DIR / "domains"
    d.mkdir(parents=True, exist_ok=True)
    (d / domain).write_text(str(time.time()))
