import json
from pathlib import Path
from ursus.config import config
from ursus.context_processors import Context, ContextProcessor, Entry, EntryURI
from ursus.utils import get_files_in_path


class JsonContextProcessor(ContextProcessor):
    def process(self, context: Context, changed_files: set[Path] | None = None) -> Context:
        for file_path in get_files_in_path(config.content_path, changed_files, ".json"):
            entry_uri = EntryURI(str(file_path))
            data = json.loads((config.content_path / file_path).read_text())
            context["entries"][entry_uri] = Entry(data)
        return context
