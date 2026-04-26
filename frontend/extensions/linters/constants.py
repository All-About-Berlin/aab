#!/usr/bin/env python3
"""
Linter that monitors external websites for changes to constants.
Crawls URLs, extracts values via LLM, and updates constants.yaml directly.
"""

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse
from ursus.linters import Linter, LinterResult
import logging
import os
import re
import requests
import time
import yaml

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

USER_AGENT = "AllAboutBerlin-Monitor/1.0 (+https://allaboutberlin.com)"
OPENAI_MODEL = "gpt-4.1-mini"

_DURATION_RE = re.compile(r"(\d+)\s*([smhdw])")


def parse_duration(duration_str: str) -> timedelta:
    matches = _DURATION_RE.findall(duration_str.strip().lower())
    if not matches:
        raise ValueError(f"Invalid duration: {duration_str}")
    units = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    return timedelta(**{units[u]: int(v) for v, u in matches})


def resolve_template(templates: dict, template_name: str, _seen: set | None = None) -> dict:
    if _seen is None:
        _seen = set()
    if template_name in _seen:
        raise ValueError(f"Circular template inheritance: {template_name}")
    _seen.add(template_name)

    if template_name not in templates:
        raise ValueError(f"Template '{template_name}' not found")
    template = templates[template_name]
    parent_name = template.get("extends")
    if parent_name:
        parent = resolve_template(templates, parent_name, _seen)
        return {**parent, **{k: v for k, v in template.items() if k != "extends"}}
    return {k: v for k, v in template.items() if k != "extends"}


def resolve_placeholders(merged: dict) -> dict:
    resolved = {}
    for key, value in merged.items():
        if isinstance(value, str):
            resolved[key] = value.format_map(merged)
        else:
            resolved[key] = value
    return resolved


def resolve_config(templates: dict, monitor: dict) -> dict:
    template_name = monitor.get("template")
    if template_name:
        template = resolve_template(templates, template_name)
        merged = {**template, **{k: v for k, v in monitor.items() if k != "template"}}
    else:
        merged = dict(monitor)
    return resolve_placeholders(merged)


def query_llm(name: str, system_prompt: str, user_message: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
        timeout=120,
    )
    response.raise_for_status()
    result = response.json()["choices"][0]["message"]["content"].strip()
    log.debug(f"[{name}] LLM response: {result}")
    return result


def crawl_html(url: str, config: dict) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    selector = config.get("css_selector")
    if selector:
        elements = soup.select(selector)
        text = "\n".join(el.get_text(strip=True) for el in elements)
        if not text:
            log.warning(f"Selector '{selector}' matched no text on {url}")
    else:
        body = soup.find("body")
        text = body.get_text(strip=True) if body else soup.get_text(strip=True)

    return text


def crawl_playwright(url: str, config: dict) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")

        selector = config.get("css_selector")
        if selector:
            elements = page.query_selector_all(selector)
            text = "\n".join(el.inner_text() for el in elements)
            if not text:
                log.warning(f"Selector '{selector}' matched no text on {url}")
        else:
            text = page.inner_text("body")

        browser.close()

    return text


class ConstantsLinter(Linter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._has_run = False
        self._domain_timestamps: dict[str, float] = {}

    def _debounce_domain(self, url: str, delay_str: str):
        domain = urlparse(url).netloc.removeprefix("www.")
        delay = parse_duration(delay_str).total_seconds()
        last = self._domain_timestamps.get(domain, 0)
        elapsed = time.time() - last
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._domain_timestamps[domain] = time.time()

    def _crawl(self, url: str, config: dict) -> str:
        crawler_type = config.get("crawler", "html")
        if crawler_type == "html":
            return crawl_html(url, config)
        elif crawler_type == "playwright":
            return crawl_playwright(url, config)
        else:
            raise ValueError(f"Unknown crawler: {crawler_type}")

    def lint(self, file_path: Path) -> LinterResult:  # noqa: ARG002
        if self._has_run:
            return
        self._has_run = True

        constants_path = Path(__file__).parents[2] / "constants.yaml"
        data = yaml.safe_load(constants_path.read_text())
        templates = data.get("templates", {})
        constants = {k: v for k, v in data.items() if k != "templates"}
        modified = False

        for const_name in sorted(constants):
            entry = constants[const_name]
            monitor = entry.get("monitor")
            if not monitor:
                continue

            config = resolve_config(templates, monitor)

            last_verified = monitor.get("lastVerified")
            interval_days = parse_duration(config.get("every", "30d")).days
            if last_verified:
                if (date.today() - date.fromisoformat(last_verified)).days < interval_days:
                    continue

            url = config.get("url")
            if not url:
                yield None, f"{const_name}: No URL configured", logging.ERROR
                continue

            log.info(f"[{const_name}] Checking {url}")

            self._debounce_domain(url, config.get("delay", "1s"))

            try:
                content = self._crawl(url, config)
            except Exception as e:
                yield None, f"{const_name}: Crawl failed: {e}", logging.ERROR
                continue

            prompt = config.get("prompt")
            if prompt:
                try:
                    new_value = query_llm(const_name, prompt, content).strip()
                except Exception as e:
                    yield None, f"{const_name}: LLM failed: {e}", logging.ERROR
                    continue

                if new_value == "ERROR":
                    yield None, f"{const_name}: LLM could not extract value", logging.ERROR
                    continue
            else:
                new_value = content.strip()

            old_value = entry["value"]
            if str(old_value) != str(new_value):
                yield None, f"{const_name}: {old_value} -> {new_value}", logging.WARNING
                entry["value"] = new_value

            monitor["lastVerified"] = date.today().isoformat()
            modified = True

        if modified:
            output = {"templates": templates, **constants}
            constants_path.write_text(
                yaml.dump(output, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
            )
