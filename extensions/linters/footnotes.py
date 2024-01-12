from pathlib import Path
from ursus.linters import RegexLinter
import logging
import re


class FootnoteLocationLinter(RegexLinter):
    """
    Verifies that footnotes appear after punctuation, not before.
    """
    file_suffixes = '.md'
    regex = re.compile(r'(?<!^)\[\^\d+\][\.,;:].{0,15}')

    def handle_match(self, file_path: Path, match: re.Match):
        yield f"Footnote before punctuation: {match.group(0)}", logging.ERROR


class CitationNeededLinter(RegexLinter):
    """
    Raises error on "Citation needed"
    """
    file_suffixes = '.md'
    regex = re.compile(r'.{0,5}[Cc]itation needed.{0,5}')

    def handle_match(self, file_path: Path, match: re.Match):
        yield f"Missing source: {match.group(0)}", logging.ERROR


class QuestionMarkLinter(RegexLinter):
    """
    Raises error on "???"
    """
    file_suffixes = '.md'
    regex = re.compile(r'.{0,5}\?{3}.{0,5}')

    def handle_match(self, file_path: Path, match: re.Match):
        yield f"Question marks: {match.group(0)}", logging.ERROR