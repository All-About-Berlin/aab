from datetime import datetime
from pathlib import Path
from typing import Any, Match
from ursus.linters import MatchResult, RegexLinter
import logging
import re


def fail_on(expiration_date: str, value: Any | None = None) -> Any:
    if datetime.strptime(expiration_date, "%Y-%m-%d") < datetime.now():
        raise AssertionError(f"Content expired on {expiration_date}")
    return "" if value is None else value


class FailOnLinter(RegexLinter):
    """
    Raises an error when a fail_on() call in a template has an expired date.
    """

    file_suffixes = (".md",)
    regex = re.compile(r"""\{\{\s*fail_on\(\s*['"](\d{4}-\d{2}-\d{2})['"]\s*\)\s*\}\}""")

    def handle_match(self, file_path: Path, match: Match[str]) -> MatchResult:
        expiration_date = match.group(1)
        if datetime.strptime(expiration_date, "%Y-%m-%d") < datetime.now():
            yield f"Content expired on {expiration_date}", logging.ERROR
