#!/usr/bin/env python3
"""
Regularly verifies and updates constants in constants.yaml
"""

from typing import Any
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse
from ursus.config import config
from ursus.linters import Linter, LinterResult
import logging
import re
import requests
import time
import yaml


@dataclass
class MonitorConfig:
    url: str
    crawler: str = "html"
    css_selector: str | None = None
    prompt: str | None = None
    delay: str = "1s"
    every: str = "30d"
    last_verified: date | None = None
    extra_attributes: dict[str, Any] = field(default_factory=dict)


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


def parse_value(value: str, unit: str | None) -> Any:
    try:
        if unit == "euro":
            return Decimal(value).quantize(Decimal("0.01"))
        elif unit == "percent" or unit == "decimal":
            return Decimal(value)
        elif unit == "integer":
            return int(value)
        else:
            return value
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
    return MonitorConfig(**resolved_config)


def query_llm(name: str, system_prompt: str, user_message: str) -> str:
    if not config.openai_api_key:
        raise ValueError("config.openai_api_key is not set")

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
        monitor_config.url,
        headers={"User-Agent": "AllAboutBerlin-Monitor/1.0 (+https://allaboutberlin.com)"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    if monitor_config.css_selector:
        elements = soup.select(monitor_config.css_selector)
        text = "\n".join(el.get_text(strip=True) for el in elements)
        if not text:
            raise ValueError(f"Selector '{monitor_config.css_selector}' matched no text on {monitor_config.url}")
    else:
        body = soup.find("body")
        text = body.get_text(strip=True) if body else soup.get_text(strip=True)

    return text


def crawl_playwright(monitor_config: MonitorConfig) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(monitor_config.url, wait_until="networkidle")

        if monitor_config.css_selector:
            elements = page.query_selector_all(monitor_config.css_selector)
            text = "\n".join(el.inner_text() for el in elements)
            if not text:
                logging.warning(f"Selector '{monitor_config.css_selector}' matched no text on {monitor_config.url}")
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
        if monitor_config.crawler == "html":
            return crawl_html(monitor_config)
        elif monitor_config.crawler == "playwright":
            return crawl_playwright(monitor_config)
        else:
            raise ValueError(f"Unknown crawler: {monitor_config.crawler}")

    def lint(self, file_path: Path) -> LinterResult:
        if file_path.name != "constants.yaml":
            return

        config = yaml.safe_load(file_path.read_text())
        file_modified = False

        for constant_name, constant in config["constants"].items():
            monitor = resolve_monitor_config(config["templates"], constant["monitor"])
            if not monitor:
                yield None, f"[{constant_name}] Constant is not monitored", logging.WARNING
                continue

            if monitor and not constant.get("unit"):
                yield None, f"[{constant_name}] Constant has no unit", logging.ERROR

            if not recrawl_needed(monitor.every, monitor.last_verified):
                yield None, f"[{constant_name}] No recrawl_needed", logging.DEBUG
                continue

            logging.info(f"[{constant_name}] Checking source for updates")

            self.wait_between_requests_to_domain(monitor.url, monitor.delay)

            try:
                content = self.execute_monitor(monitor)
            except Exception as e:
                yield None, f"[{constant_name}] Monitor failed: {e}", logging.ERROR
                continue

            if monitor.prompt:
                try:
                    raw_value = query_llm(constant_name, monitor.prompt, content)
                except Exception as e:
                    yield None, f"[{constant_name}] LLM call failed: {e}", logging.ERROR
                    continue

                if raw_value == "ERROR":
                    yield None, f"[{constant_name}] LLM could not extract value", logging.ERROR
                    continue
            else:
                raw_value = content.strip()

            try:
                new_value = parse_value(raw_value, constant["unit"])
            except ValueError as e:
                yield None, f"[{constant_name}] {e}", logging.ERROR
                continue

            if str(constant["value"]) != str(new_value):
                yield None, f"[{constant_name}] {constant['value']} -> {new_value}", logging.WARNING
                constant["value"] = new_value
            else:
                logging.info(f"[{constant_name}] Value has not changed ({constant['value']})")

            constant["monitor"]["last_verified"] = date.today()
            file_modified = True

        if file_modified:
            file_path.write_text(
                yaml.dump(
                    config,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    width=120,
                )
            )
