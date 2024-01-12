from pathlib import Path
from ursus.linters import LineLinter
import logging
import re


class MultilineListsLinter(LineLinter):
    """
    Lints missing double space at the end of a multiline list item.
    """
    file_suffixes = ('.md', )

    previous_file_path = None
    item_indent = None
    item_has_double_space = None
    list_regex = re.compile(r'^(?P<indent> *)(?P<bullet>[-*+]|\d+\.) (?P<content>.*)')

    def lint_line(self, file_path: Path, line: str):
        match = self.list_regex.match(line)

        if self.previous_file_path != file_path:
            self.item_indent = None
            self.previous_file_path = file_path

        # List item first line
        if match:
            self.item_indent = len(match['indent'])//4
            assert len(match['indent']) % 4 == 0

            self.item_has_double_space = match['content'].endswith('  ')
        # Empty line
        elif line.strip() == '':
            self.item_indent = None
            self.item_has_double_space = None
        # List item continuation
        elif self.item_indent is not None:
            required_indent = ' ' * (self.item_indent + 1) * 4
            if not line.startswith(required_indent):
                yield "Incorrect line indent", logging.ERROR
            elif not self.item_has_double_space:
                yield "Missing double space before line break in list", logging.ERROR
            self.item_indent = None
        # Normal line
        else:
            self.item_indent = None
