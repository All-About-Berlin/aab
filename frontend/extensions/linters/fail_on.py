from datetime import datetime
from pathlib import Path
from typing import Any, Match
from ursus.linters import MatchResult, RegexLinter
import logging
import re


def _parse_expiration_date(expiration_date: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(expiration_date, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid fail_on date: {expiration_date!r}")


def fail_on(expiration_date: str, value: Any | None = None) -> Any:
    if _parse_expiration_date(expiration_date) < datetime.now():
        raise AssertionError(f"Content expired on {expiration_date}")
    return "" if value is None else value


class FailOnLinter(RegexLinter):
    """
    Raises an error when a fail_on() call in a template has an expired date.
    """

    file_suffixes = (".md",)
    regex = re.compile(r"""\{\{\s*fail_on\(\s*['"](\d{4}(?:-\d{2}(?:-\d{2})?)?)['"]\s*\)\s*\}\}""")

    def handle_match(self, file_path: Path, match: Match[str]) -> MatchResult:
        expiration_date = match.group(1)
        if _parse_expiration_date(expiration_date) < datetime.now():
            yield f"Content expired on {expiration_date}", logging.ERROR
