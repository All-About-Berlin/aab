from pathlib import Path
from ursus.config import config
from ursus.linters.markdown import (
    MarkdownInternalLinksLinter as OriginalInternalLinksLinter,
)
import logging
import re


class MarkdownInternalLinksLinter(OriginalInternalLinksLinter):
    ignored_urls = (
        re.compile("^/newsletter$"),
        re.compile("^/donate$"),
        re.compile("^/services$"),
        re.compile("^/google-maps$"),
        re.compile("^/suggest-[a-z]+$"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirects = set()
        with (config.content_path / "redirects/temporary.map").open() as file:
            for line in file:
                if line.strip() and not line.startswith("#"):
                    self.redirects.add(line.strip().split(" ")[0].strip('" '))

    def validate_link_url(self, url: str, is_image: bool, current_file_path: Path):
        if url.startswith("/out"):
            if url not in self.redirects:
                yield "URL redirect not found", logging.ERROR
        else:
            yield from super().validate_link_url(url, is_image, current_file_path)
