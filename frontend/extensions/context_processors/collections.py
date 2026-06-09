from datetime import datetime
from pathlib import Path
from typing import Any, List
from ursus.config import config
from ursus.context_processors import Context, Entry, EntryContextProcessor, EntryURI
from ursus.context_processors.get_entries import get_entries
import yaml


def parse_collections(entry_uri: str) -> dict[str, Any]:
    raw_collections = yaml.safe_load((config.content_path / entry_uri).read_text())

    collections = {}
    for collection in raw_collections:
        uri = EntryURI(str(Path(entry_uri).parent / "collections" / collection["id"]))
        collection["url"] = f"{config.site_url}/{uri}"
        collection["date_updated"] = datetime.now().astimezone()
        collections[uri] = collection

    return collections


def entries_in_collection(collection: Entry) -> set[EntryURI]:
    entry_uris = set()

    def traverse(items: List[dict[str, Any]]):
        for item in items:
            if "uri" in item:
                entry_uris.add(EntryURI(item["uri"]))
            if "entries" in item:
                traverse(item["entries"])

    traverse(collection.get("entries", []))
    return entry_uris


class CollectionsProcessor(EntryContextProcessor):
    def process(self, context: Context, changed_files: set[Path] | None = None) -> None:
        super().process(context, changed_files)

        for entry_uri, entry in context["entries"].items():
            entry.pop("collections", "")

        for collection in get_entries(context["entries"], "collections"):
            for entry_uri in entries_in_collection(collection):
                context["entries"][entry_uri].setdefault("collections", [])
                context["entries"][entry_uri]["collections"].append(collection)

    def process_entry(
        self,
        context: Context,
        entry_uri: EntryURI,
        changed_files: set[Path] | None = None,
    ) -> None:
        if Path(entry_uri).name == "collections.yaml" and (
            changed_files is None or (config.content_path / entry_uri) in changed_files
        ):
            context["entries"].update(parse_collections(entry_uri))
