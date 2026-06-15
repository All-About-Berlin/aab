from datetime import date
from decimal import Decimal
from markdown.extensions.toc import slugify
from pathlib import Path
from typing import Iterable, Match
from ursus.context_processors import Entry
import holidays
from ordered_set import OrderedSet
import pycountry
import pyphen
import re
import secrets
import string
import urllib
import yaml


def to_currency(value: Decimal) -> str:
    try:
        return "{:0,.2f}".format(value).replace(".00", "") if value is not None else ""
    except:
        raise ValueError(f"{value} can't be formatted as currency")


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


_COUNTRY_OVERRIDES = {
    "CD": "Democratic Republic of the Congo",
    "KR": "South Korea",
    "TW": "Taiwan",
    "XK": "Kosovo",
}

_COUNTRIES_WITH_THE_PREFIX = {
    "AE",  # United Arab Emirates
    "BS",  # Bahamas
    "CF",  # Central African Republic
    "CG",  # Congo
    "CK",  # Cook Islands
    "DO",  # Dominican Republic
    "FK",  # Falkland Islands (Malvinas)
    "FO",  # Faroe Islands
    "GB",  # United Kingdom
    "GM",  # Gambia
    "MH",  # Marshall Islands
    "NE",  # Niger
    "NL",  # Netherlands
    "PH",  # Philippines
    "RU",  # Russian Federation
    "SD",  # Sudan
    "US",  # United States
    "VA",  # Holy See
}


def country_list(countries: list[str]) -> list[str]:
    names = []
    for code in countries:
        if code in _COUNTRY_OVERRIDES:
            names.append(_COUNTRY_OVERRIDES[code])
        else:
            country = pycountry.countries.get(alpha_2=code)
            if not country:
                raise ValueError(f"Unknown country code: {code}")
            name = getattr(country, "common_name", None) or country.name
            if code in _COUNTRIES_WITH_THE_PREFIX:
                name = f"the {name}"
            names.append(name)
    names.sort(key=lambda n: n.removeprefix("the "))
    return names


def or_list(items: list[str]) -> str:
    unique = list(OrderedSet(items))
    if len(unique) == 1:
        return unique[0]
    return ", ".join(unique[:-1]) + " or " + unique[-1]


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


def load_constants_from_file(path: Path) -> dict:
    constants_config = yaml.safe_load(path.read_text())
    constants = {}
    for constant_name, constant in constants_config["constants"].items():
        unit = constant.get("unit")
        if unit == "euros":
            value = Decimal(str(constant["value"])).quantize(Decimal("0.01"))
        elif unit == "percent" or unit == "decimal":
            value = Decimal(str(constant["value"]))
        elif unit == "integer":
            value = int(constant["value"])
        elif unit == "countries":
            codes = str(constant["value"]).split(",")
            constants[f"{constant_name}_CODES"] = codes
            countries = country_list(codes)
            constants[f"{constant_name}_LIST"] = (
                "<ul>" + "".join([f"<li>{country}</li>" for country in countries]) + "</ul>"
            )
            value = countries
        else:
            value = constant["value"]
        constants[constant_name] = value
    return constants
