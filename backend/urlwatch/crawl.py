from slugify import slugify
from datetime import datetime, timedelta
import logging
import yaml
import difflib
import re
from pathlib import Path
from playwright.sync_api import sync_playwright


date_format = "%Y-%m-%d_%H-%M-%S"


def parse_timedelta(s: str) -> timedelta:
    units = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}
    kwargs = {}
    for value, unit in re.findall(r"(\d+)([dhms])", s):
        kwargs[units[unit]] = kwargs.get(units[unit], 0) + int(value)
    return timedelta(**kwargs)


config = yaml.safe_load(Path("config.yaml").read_text())
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_default_timeout(2000)

    for target in config["targets"]:
        url = target["url"]
        name = target["name"]
        selector = target["selector"]
        frequency = parse_timedelta(target["every"])

        results_dir = Path(".") / slugify(name)
        results_dir.mkdir(exist_ok=True, parents=True)

        try:
            previous_results_path = max(results_dir.glob("*.json"), key=lambda f: f.stem)
            previous_results_date = datetime.strptime(previous_results_path.stem, date_format)
        except ValueError:
            logging.error(f"{name} was never parsed.")
            previous_results_path = None
        else:
            if (datetime.now() - previous_results_date) >= frequency:
                logging.info(f"{name} was parsed recently. Skipping.")
                continue

        logging.info(f"Fetching {name} ({url})")
        page.goto(url)

        logging.info(f"Parsing {name} ({selector})")
        result = page.locator(selector).inner_text()

        if previous_results_path:
            previous_result = previous_results_path.read_text()
            if result == previous_result:
                logging.info(f"'{name}' has not changed.")
            else:
                diff = "\n".join(
                    difflib.unified_diff(
                        previous_result.splitlines(), result.splitlines(), fromfile="old", tofile="new", lineterm=""
                    )
                )
                logging.error(f"'{name}' has changed:\n{diff}")

        current_results_path = results_dir / f"{datetime.now().strftime(date_format)}.json"
        current_results_path.write_text(result)

    browser.close()
