from pathlib import Path
import tomllib


def load_config(config_path: Path) -> dict:
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def get_domain_config(config: dict, domain: str) -> dict:
    """Get merged domain config (default + domain-specific)."""
    domains = config.get("domains", {})
    return {**domains.get("default", {}), **domains.get(domain, {})}


def get_monitor_config(config: dict, monitor_name: str) -> dict:
    """Get the fully merged config for a monitor (domain defaults + monitor overrides)."""
    from utils import get_domain

    monitor_config = config["monitors"][monitor_name]
    domain = get_domain(monitor_config["url"])
    domain_config = get_domain_config(config, domain)
    return {**domain_config, **monitor_config}
