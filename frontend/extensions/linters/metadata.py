from pathlib import Path
from typing import Match
from ursus.config import config
from ursus.linters import Linter, LinterResult, MatchResult, RegexLinter
from ursus.utils import parse_markdown_head_matter
import logging
import re


class DateUpdatedLinter(RegexLinter):
    file_suffixes = (".md",)
    regex = re.compile(r"^date_updated:", flags=re.IGNORECASE)

    def handle_match(self, file_path: Path, match: Match[str]) -> MatchResult:
        yield "Date_updated attribute is deprecated", logging.WARNING


class ShortTitleLinter(RegexLinter):
    file_suffixes = (".md",)
    regex = re.compile(r"^short_title: (.*)", flags=re.IGNORECASE)

    def handle_match(self, file_path: Path, match: Match[str]) -> MatchResult:
        if len(match.group(1)) > 43:
            yield f"Short title is too long: {match.group(1)}", logging.WARNING


class DescriptionLinter(Linter):
    """
    Ensures that entries have a description.
    """

    namespaces = {"docs", "glossary", "guides", "tools", "collections", "newsletter"}

    def lint(self, file_path: Path) -> LinterResult:
        if file_path.parts[0] not in self.namespaces:
            return

        lines = (config.content_path / file_path).read_text().splitlines()
        meta, _ = parse_markdown_head_matter([line + "\n" for line in lines])
        if not meta.get("description"):
            yield (0, 0, 3), "Missing description", logging.ERROR


class LowercaseKeysLinter(Linter):
    """
    Ensures that all frontmatter keys are lowercase.
    """

    key_regex = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")

    def lint(self, file_path: Path) -> LinterResult:
        if file_path.suffix.lower() != ".md":
            return

        lines = (config.content_path / file_path).read_text().splitlines()
        if not lines or lines[0] != "---":
            return

        for line_no, line in enumerate(lines[1:], start=1):
            if line == "---":
                break
            match = self.key_regex.match(line)
            if match and match.group(1) != match.group(1).lower():
                key = match.group(1)
                yield (line_no, 0, len(key)), f"Frontmatter key must be lowercase: {key}", logging.ERROR
