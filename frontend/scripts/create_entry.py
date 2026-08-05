#!/usr/bin/env python3
"""
Create a new content entry from a template.
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

from dateutil.relativedelta import relativedelta

FRONTEND_DIR = Path(__file__).parent.parent
CONTENT_DIR = FRONTEND_DIR / "content"
SUBLIME_PROJECT = FRONTEND_DIR.parent.parent / "aab.sublime-project"

SECTIONS = {
    "guide": "guides",
    "guides": "guides",
    "tool": "tools",
    "tools": "tools",
    "doc": "docs",
    "docs": "docs",
    "document": "docs",
    "glossary": "glossary",
    "term": "glossary",
    "newsletter": "newsletter",
}


def create(section: str, title: str | None) -> Path:
    if section not in SECTIONS:
        sys.exit(f"Unknown section: '{section}'. Use: {', '.join(SECTIONS)}")
    section = SECTIONS[section]

    template = CONTENT_DIR / "_templates" / f"{section}.md"
    if not template.exists():
        sys.exit(f"Template not found: {template}")

    today = date.today()  # noqa: DTZ011
    substitutions = {"{{date}}": today.isoformat(), "{{month}}": "", "{{year}}": ""}

    if section == "newsletter":
        slug = title or (today + relativedelta(months=1, day=1)).strftime("%B-%Y").lower()
        month, year = slug.rsplit("-", 1)
        substitutions["{{month}}"] = month.capitalize()
        substitutions["{{year}}"] = year
        output = CONTENT_DIR / section / f"_{slug}.md"
    else:
        output = CONTENT_DIR / section / f"{title or today.isoformat()}.md"

    if output.exists():
        sys.exit(f"File already exists: {output}")

    text = template.read_text()
    for placeholder, value in substitutions.items():
        text = text.replace(placeholder, value)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("section", help="guide|tool|doc|document|glossary|term|newsletter")
    parser.add_argument("title", nargs="?", help="Optional title/slug")
    args = parser.parse_args()

    output = create(args.section, args.title or None)
    print(f"Created: {output.relative_to(FRONTEND_DIR.parent)}")

    if SUBLIME_PROJECT.exists():
        subprocess.run(
            ["subl", "--project", str(SUBLIME_PROJECT), "--add", str(output)],
            check=False,
        )
