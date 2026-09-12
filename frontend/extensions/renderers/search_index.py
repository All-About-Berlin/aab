import json
import logging
import re
from pathlib import Path

from ursus.config import config
from ursus.context_processors import Context, Entry
from ursus.renderers import Renderer


logger = logging.getLogger(__name__)


EXCLUDED_DIRS = {
    "documents",
    "experts",
    "illustrations",
    "images",
    "places",
    "redirects",
    "reviews",
    "services",
    "tests",
}

TYPE_RANKS = {
    "guides": 100,
    "tools": 80,
    "docs": 80,
    "pages": 80,
    "glossary": 60,
    "newsletter": 50,
}


def is_indexable(entry_uri: str) -> bool:
    path = Path(entry_uri)
    if path.suffix != ".md":
        return False
    if any(part.startswith("_") for part in path.parts):
        return False
    if len(path.parts) > 1 and path.parts[0] in EXCLUDED_DIRS:
        return False
    return True


def classify(entry_uri: str) -> tuple[str, int]:
    path = Path(entry_uri)
    type_name = "pages" if len(path.parts) == 1 else path.parts[0]
    return type_name, TYPE_RANKS.get(type_name, 50)


def get_title(entry: Entry, type_name: str) -> str:
    if type_name == "glossary":
        german = entry.get("german_term")
        english = entry.get("english_term")
        if german and english and german != english:
            return f"{german} ({english})"
        return german or entry["title"]
    return entry["title"]


def make_doc_id(type_name: str, entry_uri: str) -> str:
    parts = list(Path(entry_uri).with_suffix("").parts)
    if type_name != "pages" and len(parts) > 1:
        parts = parts[1:]
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", "_".join(parts))
    return f"{type_name}_{safe}"


def make_relative_url(url: str) -> str:
    if url.startswith(config.site_url):
        return url[len(config.site_url) :]
    return url


class MeilisearchIndexRenderer(Renderer):
    def render(self, context: Context, changed_files: set[Path] | None = None) -> set[Path]:
        output_file = Path("search-index.json")
        documents = []

        entries_to_render = [
            (entry_uri, entry) for entry_uri, entry in context["entries"].items() if is_indexable(entry_uri)
        ]

        for entry_uri, entry in entries_to_render:
            type_name, type_rank = classify(entry_uri)
            date = entry.get("date_updated") or entry["date_created"]
            collections = entry.get("collections") or []
            documents.append(
                {
                    "id": make_doc_id(type_name, entry_uri),
                    "type": type_name,
                    "type_rank": type_rank,
                    "title": get_title(entry, type_name),
                    "description": entry.get("description", ""),
                    "body": entry["plaintext"],
                    "category": collections[0]["id"] if collections else None,
                    "date": int(date.timestamp()),
                    "url": make_relative_url(entry["url"]),
                }
            )

        output_path = config.output_path / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(documents, ensure_ascii=False))
        logger.info(f"Wrote {len(documents)} entries to {output_file}")
        return {output_file}
