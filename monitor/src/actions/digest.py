"""Queue items for the daily digest and send digest emails."""

import json
import logging
import os
from datetime import date
from html import escape
from pathlib import Path

import requests

from state import STATE_DIR

log = logging.getLogger(__name__)


def append_to_digest(state_dir: Path, title: str, url: str, summary: str, source_name: str, **kwargs):
    """Append an item to today's digest file."""
    digest_file = state_dir / "digest" / f"{date.today().isoformat()}.json"
    digest_file.parent.mkdir(parents=True, exist_ok=True)

    items = []
    if digest_file.exists():
        items = json.loads(digest_file.read_text())

    items.append(
        {
            "title": title,
            "url": url,
            "summary": summary,
            "source_name": source_name,
        }
    )

    digest_file.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    log.info(f"[{source_name}] Added to digest: {title}")


def send_digest():
    """Send the daily digest email via Mailgun, then clear the digest file."""

    digest_dir = STATE_DIR / "digest"
    digest_file = digest_dir / f"{date.today().isoformat()}.json"

    if not digest_file.exists():
        log.info("No digest file for today, nothing to send")
        return

    items = json.loads(digest_file.read_text())
    if not items:
        log.info("Digest is empty, nothing to send")
        return

    mailgun_api_key = os.environ.get("MAILGUN_API_KEY")
    if not mailgun_api_key:
        log.error("MAILGUN_API_KEY not set")
        return

    html = render_digest_html(items)

    response = requests.post(
        "https://api.eu.mailgun.net/v3/allaboutberlin.com/messages",
        auth=("api", mailgun_api_key),
        data={
            "from": "All About Berlin <contact@allaboutberlin.com>",
            "to": ["contact@allaboutberlin.com"],  # TODO: Make this configurable
            "subject": f"Monitor digest for {date.today().isoformat()}",
            "html": html,
        },
    )

    if response.ok:
        log.info("Digest sent.")
        digest_file.unlink()
    else:
        log.error(f"Failed to send digest: {response.status_code} {response.text}")


def render_digest_html(items: list[dict]) -> str:
    entries = ""
    for item in items:
        entries += (
            f"<li>"
            f"<h3><a href='{escape(item['url'])}'>{escape(item['title'])}</a></h3>"
            f"<p>{escape(item['summary'])}</p>"
            f"<p><small>Source: {escape(item['source_name'])}</small></p>"
            f"</li>"
        )

    return f"<html><body><h2>Monitor Digest</h2><ul>{entries}</ul></body></html>"
