#!/usr/bin/env python3
"""
Regularly verifies and updates constants in constants.yaml
"""

from typing import Any, NotRequired, TypedDict
from bs4 import BeautifulSoup
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from extensions.functions import fail_on
from pathlib import Path
from urllib.parse import urlparse
from ursus.config import config
from ursus.linters import Linter, LinterResult
import logging
import re
import requests
import time
import yaml


def yaml_multiline_str_representer(dumper: yaml.Dumper, data: str):
    """
    Preserve the style of multiline strings in the yaml config, so that prompts
    remain readable.
    """
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def yaml_decimal_representer(dumper: yaml.Dumper, data: Decimal):
    """Dump Decimal values as plain unquoted numbers, preserving formatting (e.g. 13.90)."""
    return dumper.represent_scalar("tag:yaml.org,2002:float", str(data))


yaml.add_representer(str, yaml_multiline_str_representer)
yaml.add_representer(Decimal, yaml_decimal_representer)


class MonitorConfig(TypedDict):
    url: str
    crawler: str
    css_selector: NotRequired[str]
    prompt: str
    delay: str
    every: str
    last_verified: NotRequired[date]


def parse_duration(duration_str: str) -> timedelta:
    """
    Time delta from a duration like "4w5d15m30s"
    """
    duration_matches = re.compile(r"(\d+)\s*([smhdw])").findall(duration_str.strip().lower())
    if not duration_matches:
        raise ValueError(f"Invalid duration: {duration_str}")
    units = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    return timedelta(**{units[u]: int(v) for v, u in duration_matches})


def recrawl_needed(every: str, last_verified: date | None) -> bool:
    """
    Accepts named intervals (every "quarter", "month", "day" or "week") or
    durations (every "30d" or "4w5d15m30s")
    """
    if not last_verified:
        return True

    today = date.today()
    if every == "day":
        return last_verified < today
    if every == "week":
        return last_verified.strftime("%G-W%V") < today.strftime("%G-W%V")
    if every == "month":
        return last_verified.strftime("%Y-%m") < today.strftime("%Y-%m")
    if every == "quarter":
        last_verified_quarter = f"{last_verified.year}-Q{(last_verified.month - 1) // 3 + 1}"  # "2026-Q2"
        current_quarter = f"{today.year}-Q{(today.month - 1) // 3 + 1}"
        return last_verified_quarter < current_quarter
    if every == "year":
        return last_verified.year < today.year
    return today - last_verified >= parse_duration(every)


def format_yaml_value(value: str, unit: str | None) -> Any:
    normalized_number = re.sub(r"[^\d.,]", "", value)
    try:
        if unit == "euros":
            # Only show cents if it's not a round amount
            euro_amount = Decimal(normalized_number).quantize(Decimal("0.01"))
            if str(euro_amount).rstrip("0").endswith("."):
                return int(euro_amount)
            else:
                return Decimal(euro_amount)
        elif unit == "percent" or unit == "decimal":
            return Decimal(normalized_number.rstrip("0").rstrip(".")).normalize()
        elif unit == "integer":
            return int(normalized_number)
        else:
            return str(value)
    except (ValueError, InvalidOperation):
        raise ValueError(f"Cannot parse {unit} value: {value!r}")


def resolve_template(templates: dict, template_name: str) -> dict:
    """
    MonitorConfigs can inherit values from a template. Templates can also have parent templates.
    """
    try:
        resolved_template = {**templates[template_name]}
    except KeyError as e:
        raise ValueError(f"Template does not exist: {template_name}") from e

    if parent_template_name := resolved_template.get("template"):
        parent_template = resolve_template(templates, parent_template_name)
        resolved_template = {**parent_template, **resolved_template}
    return resolved_template


def resolve_placeholders(monitor_config: dict) -> dict:
    """
    String values in monitor configs can contain placeholders which are other monitor config values:

    For example:
        prompt: "hello {name}",
        name: "John"
    """
    resolved = {}
    for key, value in monitor_config.items():
        if isinstance(value, str):
            resolved[key] = value.format_map(monitor_config)
        else:
            resolved[key] = value
    return resolved


def resolve_monitor_config(templates: dict, monitor_config: dict | None) -> MonitorConfig | None:
    if not monitor_config:
        return None

    template_name = monitor_config.get("template")
    config_from_template = resolve_template(templates, template_name) if template_name else {}
    resolved_config = {**config_from_template, **monitor_config}
    resolved_config = resolve_placeholders(resolved_config)
    resolved_config.pop("template")
    return MonitorConfig(**resolved_config)


def query_llm(name: str, system_prompt: str, user_message: str) -> str:
    if not config.openai_api_key:
        raise ValueError("config.openai_api_key is not set")

    logging.debug(f"[{name}] System prompt:\n\t{system_prompt}")
    logging.debug(f"[{name}] User message:\n\t{user_message}")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
        timeout=120,
    )
    response.raise_for_status()
    result = response.json()["choices"][0]["message"]["content"].strip()
    logging.debug(f"[{name}] LLM response: {result}")
    return result.strip()


def crawl_html(monitor_config: MonitorConfig) -> str:
    response = requests.get(
        monitor_config["url"],
        headers={"User-Agent": "AllAboutBerlin-Monitor/1.0 (+https://allaboutberlin.com)"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    if selector := monitor_config.get("css_selector"):
        elements = soup.select(selector)
        text = "\n".join(el.get_text(strip=True) for el in elements)
        if not text:
            raise ValueError(f"Selector '{selector}' matched no text on {monitor_config['url']}")
    else:
        body = soup.find("body")
        text = body.get_text(strip=True) if body else soup.get_text(strip=True)

    return text


def crawl_playwright(monitor_config: MonitorConfig) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(monitor_config["url"], wait_until="networkidle")

        if selector := monitor_config.get("css_selector"):
            elements = page.query_selector_all(selector)
            text = "\n".join(el.inner_text() for el in elements)
            if not text:
                logging.warning(f"Selector '{selector}' matched no text on {monitor_config['url']}")
        else:
            text = page.inner_text("body")

        browser.close()

    return text


class ConstantsLinter(Linter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._domain_timestamps: dict[str, float] = {}

    def wait_between_requests_to_domain(self, url: str, delay_str: str):
        domain = urlparse(url).netloc.removeprefix("www.")
        delay = parse_duration(delay_str).total_seconds()
        last = self._domain_timestamps.get(domain, 0)
        elapsed = time.time() - last
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._domain_timestamps[domain] = time.time()

    def execute_monitor(self, monitor_config: MonitorConfig) -> str:
        if monitor_config["crawler"] == "html":
            return crawl_html(monitor_config)
        elif monitor_config["crawler"] == "playwright":
            return crawl_playwright(monitor_config)
        else:
            raise ValueError(f"Unknown crawler: {monitor_config['crawler']}")

    def lint(self, file_path: Path) -> LinterResult:
        abs_file_path = config.content_path / file_path
        if abs_file_path.name != "constants.yaml":
            return

        constants_config = yaml.safe_load(abs_file_path.read_text())
        file_modified = False

        for constant_name, constant in constants_config["constants"].items():
            monitor = resolve_monitor_config(constants_config["templates"], constant.get("monitor"))

            if constant.get("fail_on"):
                fail_on(str(constant["fail_on"]))

            if not monitor:
                yield None, f"[{constant_name}] Constant is not monitored", logging.WARNING
                continue

            if monitor and not constant.get("unit"):
                yield None, f"[{constant_name}] Constant has no unit", logging.ERROR
                continue

            if not recrawl_needed(monitor["every"], monitor.get("last_verified")):
                logging.debug(f"[{constant_name}] No recrawl_needed")
                continue

            logging.info(f"[{constant_name}] Checking if value has changed")

            self.wait_between_requests_to_domain(monitor["url"], monitor["delay"])

            try:
                content = self.execute_monitor(monitor)
            except Exception as e:
                yield None, f"[{constant_name}] Monitor failed: {e}", logging.ERROR
                continue

            if monitor["prompt"]:
                raw_value = query_llm(
                    constant_name, f"{monitor['prompt']}\n{monitor.get('formatting_instructions', '')}", content
                )

                if raw_value == "ERROR":
                    yield None, f"[{constant_name}] LLM could not extract value", logging.ERROR
                    continue
            else:
                raw_value = content.strip()

            try:
                new_value = format_yaml_value(raw_value, constant["unit"])
            except ValueError as e:
                yield None, f"[{constant_name}] {e}", logging.ERROR
                continue

            if str(constant["value"]) != str(new_value):
                message = f"[{constant_name}] Value has changed: {constant['value']} -> {new_value}"
                logging.info(message)
                yield None, message, logging.ERROR
                constants_config["constants"][constant_name]["value"] = new_value
            else:
                logging.info(f"[{constant_name}] Value has not changed: {constant['value']}")

            constants_config["constants"][constant_name]["monitor"]["last_verified"] = date.today()
            file_modified = True

        if file_modified:
            abs_file_path.write_text(
                yaml.dump(
                    constants_config,
                    allow_unicode=True,
                    sort_keys=False,
                    width=120,
                )
            )
