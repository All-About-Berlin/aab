import time
from pathlib import Path

from platformdirs import user_state_dir

STATE_DIR = Path(user_state_dir("aab-monitor"))


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
