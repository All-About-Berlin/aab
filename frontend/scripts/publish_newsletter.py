#!/usr/bin/env python3
"""
Prepare a newsletter markdown file and upload it to Buttondown as a draft.
"""

import argparse
import os
import re
import sys
import urllib.parse
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import yaml


SITE_URL = "https://allaboutberlin.com"
IMAGE_SIZE = "content1x"
NEWSLETTER_DIR = Path(__file__).parent.parent / "content" / "newsletter"
BUTTONDOWN_EMAILS_URL = "https://api.buttondown.com/v1/emails"
BUTTONDOWN_ADMIN_URL = "https://buttondown.com/emails"
PUBLISH_TIME = time(8, 45, tzinfo=ZoneInfo("Europe/Berlin"))


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text
    return yaml.safe_load(match.group(1)) or {}, text[match.end() :]


def rewrite_images(text: str) -> str:
    """
    Use absolute, size-appropriate image paths
    """
    pattern = re.compile(
        r"(!\[[^\]]*\]\()"
        r"/(images|illustrations)/([^\s)]+)"
        r"(\s+\"[^\"]*\")?"
        r"(\))"
    )

    def replace(match: re.Match) -> str:
        prefix, folder, path, title, suffix = match.groups()
        return f"{prefix}{SITE_URL}/{folder}/{IMAGE_SIZE}/{path}{title or ''}{suffix}"

    return pattern.sub(replace, text)


def rewrite_wikilinks(text: str) -> str:
    """
    Replace short-form glossary links with the real thing
    """

    def replace(match: re.Match) -> str:
        label = match.group(1)
        return f"[{label}]({SITE_URL}/glossary/{urllib.parse.quote(label)})"

    return re.sub(r"\[\[([^\]]+)\]\]", replace, text)


def rewrite_relative_links(text: str) -> str:
    """
    Replace relative URLs with absolute URLs
    """
    return re.sub(
        r"(?<!!)(\[[^\]]+\]\()/([^)]+)\)",
        rf"\1{SITE_URL}/\2)",
        text,
    )


def remove_footnotes(text: str) -> str:
    text = re.sub(r"^\[\^[^\]]+\]:.*(?:\n[ \t]+.*)*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def prepare_newsletter(slug: str) -> tuple[dict, str]:
    source = NEWSLETTER_DIR / f"{slug}.md"
    if not source.exists():
        sys.exit(f"Newsletter not found: {source}")

    metadata, body = split_frontmatter(source.read_text())
    body = rewrite_images(body)
    body = rewrite_wikilinks(body)
    body = rewrite_relative_links(body)
    body = remove_footnotes(body)
    return metadata, body.lstrip("\n")


def publish_to_buttondown(
    slug: str, subject: str, description: str, body: str, publish_date: datetime, canonical_url: str
) -> dict:
    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key:
        sys.exit("BUTTONDOWN_API_KEY is not set")

    headers = {"Authorization": f"Token {api_key}"}
    payload = {
        "slug": slug,
        "subject": subject,
        "description": description,
        "body": body,
        "status": "scheduled",
        "publish_date": publish_date.isoformat(),
        "canonical_url": canonical_url,
    }

    lookup = requests.get(BUTTONDOWN_EMAILS_URL, headers=headers, params={"slug": slug})
    if not lookup.ok:
        sys.exit(f"Buttondown API error {lookup.status_code}: {lookup.text}")
    existing = next((e for e in lookup.json().get("results", []) if e.get("slug") == slug), None)

    if existing:
        response = requests.patch(f"{BUTTONDOWN_EMAILS_URL}/{existing['id']}", headers=headers, json=payload)
    else:
        response = requests.post(BUTTONDOWN_EMAILS_URL, headers=headers, json=payload)

    if not response.ok:
        sys.exit(f"Buttondown API error {response.status_code}: {response.text}")
    return response.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Newsletter slug, e.g. august-2026")
    args = parser.parse_args()

    metadata, body = prepare_newsletter(args.slug)
    date_created = metadata.get("date_created")
    if not date_created:
        sys.exit("Newsletter is missing date_created in its frontmatter")

    publish_date = datetime.combine(date_created, PUBLISH_TIME)
    email = publish_to_buttondown(
        slug=args.slug,
        subject=metadata.get("title", args.slug),
        description=metadata.get("description", ""),
        body=body,
        publish_date=publish_date,
        canonical_url=f"{SITE_URL}/newsletter/{args.slug}",
    )
    print(f"Scheduled for {publish_date.isoformat()}: {BUTTONDOWN_ADMIN_URL}/{email['id']}")
