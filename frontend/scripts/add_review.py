#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
from ursus.config import config
from ursus.utils import import_module_or_path
import re
import readline
import yaml


if "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


class IndentedListDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        # Enforce indented lists as used in the rest of the content
        return super().increase_indent(flow, False)


def get_user_input(title: str, autocompleter=None):
    print(f"\033[1m{title}:\033[0m")
    readline.set_completer_delims("")
    readline.set_completer(autocompleter)
    return input("> \033[0m")


def autocomplete_entries(query, state):
    options = [str(p.relative_to(config.content_path)) for p in (config.content_path).rglob(f"{query}*.md")]
    return options[state] if state < len(options) else None


def autocomplete_experts(query, state):
    options = [p.stem for p in (config.content_path / "experts").rglob(f"{query}*.md")]
    return options[state] if state < len(options) else None


def write_markdown(path: Path, metadata: dict, body: str = ""):
    frontmatter = yaml.dump(metadata, Dumper=IndentedListDumper, allow_unicode=True, sort_keys=False, indent=4)
    content = f"---\n{frontmatter}---\n"
    if body:
        content += f"\n{body}\n"
    path.write_text(content)


def add_expert(expert_slug: str):
    metadata = {
        "name": get_user_input("Expert name"),
        "job_title": get_user_input("Job title"),
        "email": get_user_input("Email"),
        "website": get_user_input("Website"),
        "picture": f"experts/photos/{expert_slug}.jpg",
    }
    body = get_user_input("Description")

    file_path = config.content_path / f"experts/{expert_slug}.md"
    print(f"Saving to {str(file_path)}")
    write_markdown(file_path, metadata, body)
    print("\n---\n")


def add_review():
    entry_uri = get_user_input("Entry URI", autocomplete_entries)
    entry_slug = Path(entry_uri).stem
    expert_slug = get_user_input("Expert slug", autocomplete_experts)

    if not (config.content_path / f"experts/{expert_slug}.md").exists():
        add_expert(expert_slug)

    review_metadata = {
        "related_expert": f"experts/{expert_slug}.md",
        "date_reviewed": datetime.now().date(),
    }

    review_path = config.content_path / f"reviews/{entry_slug}/{expert_slug}.md"
    print(f"Saving review to {str(review_path.relative_to(config.content_path))}")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(review_path, review_metadata)
    print("\n---\n")

    print(f"Adding review to {entry_uri}")
    guide_path = config.content_path / entry_uri

    markdown_content = guide_path.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", markdown_content, re.DOTALL)
    if match:
        metadata = yaml.safe_load(match.group(1)) or {}
        body = markdown_content[match.end() :]
    else:
        metadata = {}
        body = markdown_content

    reviews = metadata.setdefault("related_reviews", [])
    reviews.append(str(review_path.relative_to(config.content_path)))
    write_markdown(guide_path, metadata, body)


if __name__ == "__main__":
    import_module_or_path(Path(__file__).parent.parent / "ursus_config.py")
    add_review()
