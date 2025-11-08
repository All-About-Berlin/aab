from slugify import slugify
from datetime import datetime, timedelta
import logging
import yaml
import difflib
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from platformdirs import user_cache_dir
from typing import Any, Iterable, NewType


date_format = "%Y-%m-%d_%H-%M-%S"


Target = NewType("Target", dict[str, Any])
Result = NewType("Result", dict[str, Any])


class Status:
    NEW = "NEW"
    SKIPPED = "SKIPPED"
    SAME = "SAME"
    CHANGED = "CHANGED"
    ERROR = "ERROR"


def parse_timedelta(s: str) -> timedelta:
    """
    Converts "7d3h2m" to a timedelta object
    """
    units = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}
    kwargs = {}
    for value, unit in re.findall(r"(\d+)([dhms])", s):
        kwargs[units[unit]] = kwargs.get(units[unit], 0) + int(value)
    return timedelta(**kwargs)


def parse_config(config_path: Path) -> list[Target]:
    targets = yaml.safe_load(config_path.read_text())["targets"]
    for target in targets:
        target["frequency"] = parse_timedelta(target["every"])
    return targets


def monitor_target(browser, target: Target, cache_path: Path) -> Result:
    page = browser.new_page()
    page.set_default_timeout(2000)

    name = target["name"]
    status = None

    results_dir = cache_path / slugify(name)
    results_dir.mkdir(exist_ok=True, parents=True)

    try:
        previous_results_path = max(results_dir.glob("*.json"), key=lambda f: f.stem)
        previous_results_date = datetime.strptime(previous_results_path.stem, date_format)
    except ValueError:
        logging.error(f"{name} was never parsed.")
        previous_results_path = None
        status = Status.NEW
    else:
        if (datetime.now() - previous_results_date) >= target["frequency"]:
            logging.info(f"{name} was parsed recently. Skipping.")
            return Result(
                {
                    **target,
                    "previous": None,
                    "current": None,
                    "diff": None,
                    "status": Status.SKIPPED,
                }
            )

    try:
        logging.info(f"Fetching {name} ({target['url']})")
        page.goto(target["url"])

        logging.info(f"Parsing {name} ({target['selector']})")
        result = page.locator(target["selector"]).inner_text()
    except:
        logging.exception(f"Error while parsing {name} ({target['selector']})")
        status = Status.ERROR
        result = None

    previous_result = None
    diff = None
    if result:
        current_results_path = results_dir / f"{datetime.now().strftime(date_format)}.json"
        current_results_path.write_text(result)

        if previous_results_path:
            previous_result = previous_results_path.read_text()
            if result == previous_result:
                logging.info(f"'{name}' has not changed.")
                status = Status.SAME
            else:
                diff = "\n".join(
                    difflib.unified_diff(
                        previous_result.splitlines(), result.splitlines(), fromfile="old", tofile="new", lineterm=""
                    )
                )
                logging.error(f"'{name}' has changed:\n{diff}")
                status = Status.CHANGED

        status = Status.NEW

    return Result(
        {
            **target,
            "previous": previous_result,
            "current": result,
            "diff": diff,
            "status": status,
        }
    )


def monitor_targets(targets: Iterable[Target], cache_path: Path) -> Iterable[Result]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for target in targets:
            yield monitor_target(browser, target, cache_path)
        browser.close()


if __name__ == "__main__":
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s",
        level=logging.INFO,
    )

    import argparse

    parser = argparse.ArgumentParser(description="Monitor URLs for changes")
    parser.add_argument(
        "--cache-path",
        dest="cache_path",
        nargs="?",
        type=Path,
        help="Where to store the downloaded pages.",
        default=Path(user_cache_dir("urlmonitor", "nicolasb")),
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        nargs="?",
        type=Path,
        help="Path to a YAML config file.",
    )
    args = parser.parse_args()

    for result in monitor_targets(parse_config(args.config_path), args.cache_path):
        pass
