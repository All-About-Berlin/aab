from pathlib import Path
from ursus.linters import LineLinter, LineLinterResult
import logging
import re


class MultilineListsLinter(LineLinter):
    """
    Lints missing double space at the end of a multiline list item.
    """

    file_suffixes = (".md",)

    previous_file_path = None
    item_indent = None
    item_has_double_space = None
    _line_count = 0
    _in_frontmatter = False
    list_regex = re.compile(r"^(?P<indent> *)(?P<bullet>[-*+]|\d+\.) (?P<content>.*)")

    def lint_line(self, file_path: Path, line: str) -> LineLinterResult:
        if self.previous_file_path != file_path:
            self.item_indent = None
            self.previous_file_path = file_path
            self._line_count = 0
            self._in_frontmatter = False

        self._line_count += 1
        stripped = line.rstrip("\n")

        # Skip front matter
        if self._line_count == 1 and stripped == "---":
            self._in_frontmatter = True
            return
        if self._in_frontmatter:
            if stripped == "---":
                self._in_frontmatter = False
            return

        match = self.list_regex.match(line)

        # List item first line
        if match:
            self.item_indent = len(match["indent"]) // 4
            assert len(match["indent"]) % 4 == 0

            self.item_has_double_space = match["content"].endswith("  ")
        # Empty line
        elif line.strip() == "":
            self.item_indent = None
            self.item_has_double_space = None
        # List item continuation
        elif self.item_indent is not None:
            required_indent = " " * (self.item_indent + 1) * 4
            if self.item_has_double_space and line.startswith("> "):
                # Nested blockquote
                pass
            elif not line.startswith(required_indent):
                yield (0, self.item_indent * 4), "Incorrect line indent", logging.ERROR
            elif not self.item_has_double_space:
                yield (
                    (len(line) - 3, len(line) - 1),
                    "Missing double space before line break in list",
                    logging.ERROR,
                )
            self.item_indent = None
        # Normal line
        else:
            self.item_indent = None
