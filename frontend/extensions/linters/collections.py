from pathlib import Path
from ursus.config import config
from ursus.linters import Linter, LinterResult
import logging
import yaml


class GuideInCollectionsLinter(Linter):
    """
    Ensures that every guide is listed in collections.yaml.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection_uris: set[str] = set()
        with (config.content_path / "collections.yaml").open() as f:
            collections = yaml.safe_load(f)
        self._collect_uris(collections)

    def _collect_uris(self, entries):
        if isinstance(entries, list):
            for entry in entries:
                self._collect_uris(entry)
        elif isinstance(entries, dict):
            if "uri" in entries:
                self.collection_uris.add(entries["uri"])
            if "entries" in entries:
                self._collect_uris(entries["entries"])

    def lint(self, file_path: Path) -> LinterResult:
        if file_path.parts[0] == "guides" and str(file_path) not in self.collection_uris:
            yield None, "Guide is not in collections.yaml", logging.ERROR
