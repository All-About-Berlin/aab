import re
from datetime import timedelta
from urllib.parse import urlparse

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
