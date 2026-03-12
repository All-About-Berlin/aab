from datetime import date, datetime
from decimal import Decimal
from markdown.extensions.toc import slugify
from typing import Iterable, Match, Any
from ursus.context_processors import Entry
import holidays
import pyphen
import re
import secrets
import string
import urllib


def to_currency(value: Decimal) -> str:
    return "{:0,.2f}".format(value).replace(".00", "") if value is not None else ""


def to_percent(value: Decimal, max_decimals: int = 2) -> str:
    return f"{float(value):.{max_decimals}f}".rstrip("0").rstrip(".")


def random_id() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(5))


def build_wikilinks_url(label: str, base: str, end: str) -> str:
    return "{}{}{}".format(base, urllib.parse.quote(label), end)


def patched_slugify(value: str, separator: str, keep_unicode: bool = False) -> str:
    """
    Removes leading numbers from slugs
    """
    return slugify(value.lstrip(" 0123456789"), separator, keep_unicode)


def fail_on(expiration_date: str, value: Any | None = None) -> Any:
    # Fails when the expiration date is reached. Used to set content date limits.
    assert datetime.strptime(expiration_date, "%Y-%m-%d") >= datetime.now(), f"Content expired on {expiration_date}"
    return "" if value is None else value


def or_join(items: list[str]) -> str:
    return ", ".join(items[:-1]) + " or " + items[-1]


def remove_accents(string: str) -> str:
    substitutions = (
        (r"[àáâãäå]", "a"),
        (r"[èéêë]", "e"),
        (r"[ìíîï]", "i"),
        (r"[òóôõö]", "o"),
        (r"[ùúûü]", "u"),
    )
    for substitution in substitutions:
        string = re.sub(*substitution, string, flags=re.IGNORECASE)
    return string.upper()


def glossary_sorter(entry: Entry) -> str:
    return remove_accents(entry["german_term"])


def glossary_groups(entries: list[Entry]) -> dict[str, list[Entry]]:
    entry_groups: dict[str, list[Entry]] = {}
    for entry in entries:
        group_name = re.sub(r"[^a-z]", "#", remove_accents(entry["german_term"]), flags=re.IGNORECASE)[0]
        entry_groups.setdefault(group_name, [])
        entry_groups[group_name].append(entry)

    for group_name in entry_groups:
        entry_groups[group_name].sort(key=glossary_sorter)

    return entry_groups


hyphenation_dict = pyphen.Pyphen(lang="de_DE")
long_word_pattern = re.compile(r"\b([^\W\d]{15,})\b", re.MULTILINE | re.UNICODE)
soft_hyphen = "­"


def hyphenate(text: str, lang: str = "en_US", hyphen: str = soft_hyphen) -> str:
    def hyphenate_word(match: Match[str]) -> str:
        return str(hyphenation_dict.inserted(match.group(), hyphen))

    return re.sub(long_word_pattern, hyphenate_word, text)


def get_public_holidays(years: Iterable[int]):
    in_german = holidays.country_holidays("DE", subdiv="BE", language="de", years=years)
    in_english = holidays.country_holidays("DE", subdiv="BE", language="en_US", years=years)
    return {
        date: {
            "en": in_english[date],
            "de": in_german[date],
        }
        for date in sorted(in_english.keys())
    }


def count_weekdays(dates: Iterable[date]) -> int:
    return len([d for d in dates if d.weekday() < 5])
