import re
from datetime import timedelta
import time
from urllib.parse import urlparse

from monitor.src.state import read_domain_timestamp, write_domain_timestamp

_DURATION_RE = re.compile(r"(\d+)\s*([smhdw])")


def parse_duration(duration_str: str) -> timedelta:
    """Parse a duration string like '30d', '6h', '1s', '1d12h', '2h30m'."""
    matches = _DURATION_RE.findall(duration_str.strip().lower())
    if not matches:
        raise ValueError(f"Invalid duration: {duration_str}")
    units = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    return timedelta(**{units[u]: int(v) for v, u in matches})


def get_domain(url: str) -> str:
    domain = urlparse(url).netloc
    return domain.removeprefix("www.")


def debounce_domain(domain: str, delay: timedelta):
    """Sleep if needed to respect per-domain rate limits."""
    last_request = read_domain_timestamp(domain)
    if last_request:
        elapsed = time.time() - last_request
        delay_seconds = delay.total_seconds()
        if elapsed < delay_seconds:
            time.sleep(delay_seconds - elapsed)
    write_domain_timestamp(domain)
