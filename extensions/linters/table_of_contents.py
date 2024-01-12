from pathlib import Path
from ursus.config import config
from ursus.linters import Linter
import logging


class TableOfContentsLinter(Linter):
    file_suffixes = ('.md', )

    def lint(self, file_path: Path):
        """
        Raises a warning when a guide has no table of contents
        """
        if not (file_path.suffix.lower() == '.md' and file_path.is_relative_to('guides')):
            return

        with (config.content_path / file_path).open() as file:
            for line in file.readlines():
                if '_blocks/tableOfContents.html' in line:
                    return

        yield 1, "No table of contents", logging.WARNING
