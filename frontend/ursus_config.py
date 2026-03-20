from datetime import date, datetime
from decimal import Decimal
from extensions.functions import (
    build_wikilinks_url,
    count_weekdays,
    fail_on,
    get_public_holidays,
    glossary_groups,
    or_join,
    patched_slugify,
    random_id,
    to_currency,
    to_percent,
)
from markupsafe import Markup
from pathlib import Path
from ursus.config import config
from zoneinfo import ZoneInfo
import logging
import os
import git
import json


ctx = {}


def _load_constants(path):
    """Load constants from JSON, typecasting values and applying fail_on dates."""
    casters = {"int": int, "Decimal": Decimal}
    result = {}
    for key, entry in json.loads(Path(path).read_text()).items():
        value = casters.get(entry["type"], str)(entry["value"])
        if "fail_on" in entry:
            value = fail_on(entry["fail_on"], value)
        result[key] = value
    return result


ctx.update(_load_constants(Path(__file__).parent / "constants.json"))

# ==============================================================================
# TAXES - Calculated values based on other constants
# ==============================================================================

ctx["BEITRAGSBEMESSUNGSGRENZE"] = ctx["BEITRAGSBEMESSUNGSGRENZE_MONTHLY"] * 12
ctx["ARBEITSLOSENVERSICHERUNG_EMPLOYEE_RATE"] = ctx["ARBEITSLOSENVERSICHERUNG_RATE"] / 2  # § 341 SGB 3, BeiSaV 2019
ctx["GEWERBESTEUER_RATE_BERLIN"] = (ctx["GEWERBESTEUER_RATE"] * ctx["GEWERBESTEUER_HEBESATZ_BERLIN"]).normalize()

# The effective cost of the Gewerbesteuer when accounting for the income tax credit, for Berlin - (%)
ctx["GEWERBESTEUER_EXTRA_COST_BERLIN"] = (
    ctx["GEWERBESTEUER_RATE"] * (ctx["GEWERBESTEUER_HEBESATZ_BERLIN"] - ctx["GEWERBESTEUER_TAX_CREDIT"])
).normalize()


# ==============================================================================
# HEALTH INSURANCE
# ==============================================================================

# Below this income (€/mth), you have a minijob
ctx["MINIJOB_MAX_INCOME"] = round(ctx["MINIMUM_WAGE"] * 130 / 3)  # § 8 SGB IV

# Base contribution (%), including Krankengeld
ctx["GKV_BASE_RATE_STUDENT"] = ctx["GKV_BASE_RATE_EMPLOYEE"] * Decimal("0.7")  # § 245 SGB V

# Mindestbemessungsgrundlage (€/mth) - Below this income, GKV does not get cheaper
ctx["GKV_MIN_INCOME"] = ctx["BEZUGSGROESSE"] / 90 * 30  # § 240 Abs. 4 SGV IV

# Above this income (€/y), you pay the Höchstbeitrag - https://www.bmas.de/DE/Arbeit/Arbeitsrecht/Mindestlohn/mindestlohn.html
ctx["GKV_MAX_INCOME"] = ctx["GKV_MAX_INCOME_MONTHLY"] * 12  # SVBezGrV 2021 [BBGKVPV]

# Above this income, it's no longer a Nebenjob
ctx["GKV_NEBENJOB_MAX_INCOME"] = ctx["BEZUGSGROESSE"] * Decimal("0.75")

# Jahresarbeitsentgeltgrenze or Versicherungspflichtgrenze - Above this income (€/y), you are freiwillig versichert
ctx["GKV_FREIWILLIG_VERSICHERT_MIN_INCOME"] = ctx["GKV_FREIWILLIG_VERSICHERT_MIN_INCOME_MONTHLY"] * 12

# Above this income (€/m), you can't have Familienversicherung
ctx["GKV_FAMILIENVERSICHERUNG_MAX_INCOME"] = (Decimal(1 / 7) * ctx["BEZUGSGROESSE"]).normalize()  # § 10 SGB V

ctx["GKV_ZUSATZBEITRAG_AVERAGE"] = ctx["GKV_AVG_ZUSATZBEITRAG"]

ctx["EXPAT_INSURANCE_COST"] = {
    "feather-basic": ctx["EXPAT_INSURANCE_COST_FEATHER_BASIC"],
    "feather-premium": ctx["EXPAT_INSURANCE_COST_FEATHER_PREMIUM"],
    "ottonova-expat": ctx["EXPAT_INSURANCE_COST_OTTONOVA_EXPAT"],
    "hansemerkur-basic": ctx["EXPAT_INSURANCE_COST_HANSEMERKUR_BASIC"],
    "hansemerkur-profi": ctx["EXPAT_INSURANCE_COST_HANSEMERKUR_PROFI"],
}

# Maximum daily Krankengeld
ctx["GKV_KRANKENGELD_DAILY_LIMIT"] = (ctx["GKV_MAX_INCOME"] * Decimal("0.7") / 360).normalize()  # § 47 SGB V

# BAFöG Bedarfssatz (€/y)
ctx["SPERRKONTO_AMOUNT"] = (
    ctx["BAFOG_BEDARFSSATZ"] + ctx["SPERRKONTO_SURCHARGE_INSURANCE"] + ctx["SPERRKONTO_SURCHARGE_OTHER"]
) * 12  # § 13 BAföG Abs 1.2 + 2.2 + § 13a BAföG Abs 1

# Pflegeversicherung (%) - § 55 Abs. 1 SGB XI, can be changed in external regulation (like PBAV 2026)
ctx["PFLEGEVERSICHERUNG_EMPLOYER_RATE"] = ctx["PFLEGEVERSICHERUNG_BASE_RATE"] / 2

ctx["PFLEGEVERSICHERUNG_MIN_RATE"] = (
    ctx["PFLEGEVERSICHERUNG_BASE_RATE"]
    - ctx["PFLEGEVERSICHERUNG_DISCOUNT_PER_CHILD"] * (ctx["PFLEGEVERSICHERUNG_DISCOUNT_MAX_CHILDREN"] - 1)
).normalize()
ctx["PFLEGEVERSICHERUNG_MAX_RATE"] = (
    ctx["PFLEGEVERSICHERUNG_BASE_RATE"] + ctx["PFLEGEVERSICHERUNGS_SURCHARGE"]
).normalize()

# ==============================================================================
# PENSIONS
# ==============================================================================

# Public pension contribution (%) - RVBeitrSBek 202X
ctx["RV_MIN_CONTRIBUTION"] = (ctx["RV_BASE_RATE"] * ctx["MINIJOB_MAX_INCOME"] / 100).normalize()


gkv_min_rate_employee = (  # Total rate for employees
    ctx["GKV_BASE_RATE_EMPLOYEE"] + ctx["PFLEGEVERSICHERUNG_MIN_RATE"] + ctx["GKV_AVG_ZUSATZBEITRAG"]
)

gkv_max_rate_employee = (  # Total rate for employees
    ctx["GKV_BASE_RATE_EMPLOYEE"] + ctx["PFLEGEVERSICHERUNG_MAX_RATE"] + ctx["GKV_AVG_ZUSATZBEITRAG"]
)

# Min/max health insurance rate for employees (%), with avg. Zusatzbeitrag
ctx["GKV_MIN_RATE_EMPLOYEE"] = (
    gkv_min_rate_employee
    - (  # Employer's contribution
        ctx["GKV_BASE_RATE_EMPLOYEE"] + ctx["PFLEGEVERSICHERUNG_BASE_RATE"] + ctx["GKV_AVG_ZUSATZBEITRAG"]
    )
    / 2
).normalize()
ctx["GKV_MAX_RATE_EMPLOYEE"] = (
    (  # Total cost
        ctx["GKV_BASE_RATE_EMPLOYEE"] + ctx["PFLEGEVERSICHERUNG_MAX_RATE"] + ctx["GKV_AVG_ZUSATZBEITRAG"]
    )
    - (  # Employer's contribution
        ctx["GKV_BASE_RATE_EMPLOYEE"] + ctx["PFLEGEVERSICHERUNG_BASE_RATE"] + ctx["GKV_AVG_ZUSATZBEITRAG"]
    )
    / 2
).normalize()

ctx["GKV_MIN_RATE_SELF_PAY"] = (
    ctx["GKV_BASE_RATE_SELF_PAY"] + ctx["PFLEGEVERSICHERUNG_MIN_RATE"] + ctx["GKV_MIN_ZUSATZBEITRAG"]
).normalize()
ctx["GKV_MAX_RATE_SELF_PAY"] = (
    ctx["GKV_BASE_RATE_SELF_PAY"] + ctx["PFLEGEVERSICHERUNG_MAX_RATE"] + ctx["GKV_MAX_ZUSATZBEITRAG"]
).normalize()

# Min/max health insurance cost for employees (€/mth), with avg. Zusatzbeitrag
ctx["GKV_MIN_COST_EMPLOYEE"] = round(ctx["GKV_MIN_INCOME"] * ctx["GKV_MIN_RATE_EMPLOYEE"] / 100, -1)
ctx["GKV_MAX_COST_EMPLOYEE"] = round(ctx["GKV_MAX_INCOME"] / 12 * ctx["GKV_MAX_RATE_EMPLOYEE"] / 100, -1)


# Contribution (€/mth) for self-pay tariff without right to Krankengeld
ctx["GKV_MIN_COST_SELF_PAY"] = round(ctx["GKV_MIN_INCOME"] * ctx["GKV_MIN_RATE_SELF_PAY"] / 100, -1)

# Maximum health insurance cost for freelancers (€/mth), with max Zusatzbeitrag
ctx["GKV_MAX_COST_SELF_PAY"] = round(ctx["GKV_MAX_INCOME"] / 12 * ctx["GKV_MAX_RATE_SELF_PAY"] / 100, -1)

# Contribution for students (€/mth), with avg. Zusatzbeitrag
ctx["GKV_COST_STUDENT"] = round(
    ctx["BAFOG_BEDARFSSATZ"]
    * (ctx["GKV_BASE_RATE_STUDENT"] + ctx["PFLEGEVERSICHERUNG_MAX_RATE"] + ctx["GKV_AVG_ZUSATZBEITRAG"])
    / 100,
    -1,
)


# ==============================================================================
# IMMIGRATION
# ==============================================================================

# Minimum income (€/y) to get a Blue Card - § 18g AufenthG
ctx["BLUE_CARD_MIN_INCOME"] = round(Decimal("0.5") * ctx["BEITRAGSBEMESSUNGSGRENZE"])

# Minimum income (€/y) to get a Blue Card in shortage fields - § 18g AufenthG
ctx["BLUE_CARD_SHORTAGE_MIN_INCOME"] = round(Decimal("0.453") * ctx["BEITRAGSBEMESSUNGSGRENZE"])

# Minimum guaranteed pension payment (€/m) to get a freelance visa above age 45
# VAB, https://www.bmas.de/DE/Soziales/Rente-und-Altersvorsorge/rentenversicherungsbericht-art.html
ctx["FREELANCE_VISA_MIN_PENSION"] = round(ctx["FREELANCE_VISA_MIN_MONTHLY_PENSION"] * 144)

# Minimum gross income (€/y) to get a work visa above age 45 - service.berlin.de/dienstleistung/305304
ctx["WORK_VISA_MIN_INCOME"] = ctx["BEITRAGSBEMESSUNGSGRENZE"] * Decimal("0.55")

# Nationalities that can apply for a residence permit directly in Germany - § 41 AufenthV
beschv_26_1_countries = [
    "Australia",
    "Canada",
    "Israel",
    "Japan",
    "Monaco",
    "New Zealand",
    "San Marino",
    "South Korea",
    "the United Kingdom",
    "the United States",
]
beschv_26_2_countries = [
    "Albania",
    "Bosnia-Herzegovina",
    "Kosovo",
    "North Macedonia",
    "Montenegro",
    "Serbia",
]
ctx["BESCHV_26_COUNTRIES"] = or_join(sorted(beschv_26_1_countries + beschv_26_2_countries))
ctx["BESCHV_26_1_COUNTRIES"] = or_join(beschv_26_1_countries)
ctx["BESCHV_26_2_COUNTRIES"] = or_join(beschv_26_2_countries)

# Exempt from freelance visa pension requirement
ctx["AUFENTHG_21_2_COUNTRIES"] = or_join(
    [
        "the Dominican Republic",
        "Indonesia",
        # "Iran",  # Missing from VAB since at least 2018
        "Japan",
        "Philippines",
        "Sri Lanka",
        "Turkey",
        "the United States",
    ]
)

# Visa-free entry to apply for a residence permit
ctx["AUFENTHV_41_COUNTRIES"] = or_join(
    [
        "Australia",
        "Canada",
        "Israel",
        "Japan",
        "New Zealand",
        "South Korea",
        "the United Kingdom",
        "the United States",
    ]
)

# ==============================================================================
# ADMINISTRATION
# ==============================================================================

# Maximum income from employment to stay a member of the KSK (€/y)
ctx["KSK_MAX_EMPLOYMENT_INCOME"] = ctx["BEITRAGSBEMESSUNGSGRENZE"] / 2  # § 4 KSVG

# ==============================================================================
# DATES
# ==============================================================================

ctx["now"] = datetime.now(ZoneInfo("Europe/Berlin"))
ctx["count_weekdays"] = count_weekdays
ctx["get_public_holidays"] = get_public_holidays
ctx["PUBLIC_HOLIDAYS_BY_DATE_JSON"] = json.dumps(
    list(d.isoformat() for d in get_public_holidays(range(date.today().year, date.today().year + 3)).keys())
)

# ==============================================================================
# TECHNICAL
# ==============================================================================

ctx["SITE_URL"] = os.environ.get("URSUS_SITE_URL", "")  # No trailing slash!
ctx["random_id"] = random_id
ctx["fail_on"] = fail_on
ctx["GOOGLE_MAPS_JAVASCRIPT_API_KEY"] = os.environ.get("GOOGLE_MAPS_JAVASCRIPT_API_KEY")  # Frontend use, to show a map
ctx["glossary_groups"] = glossary_groups

ctx["RECOMMENDED"] = Markup(
    '&nbsp; <a target="_blank" class="recommended" aria-label="Recommended option" href="/glossary/Recommended"></a>'
)

content_path = Path(__file__).parent / "content"
templates_path = Path(__file__).parent / "templates"

ctx["commit_id"] = git.Repo(content_path, search_parent_directories=True).head.commit.hexsha


# ==============================================================================
# URSUS
# ==============================================================================

config.site_url = ctx["SITE_URL"]
config.content_path = content_path
config.templates_path = templates_path

config.output_path = (
    Path(env_output_dir) if (env_output_dir := os.environ.get("URSUS_OUTPUT_DIR")) else Path(__file__).parent / "output"
)

config.google_maps_places_api_key = os.environ.get("GOOGLE_MAPS_PLACES_API_KEY", "")  # Backend use, to lint places
config.google_tts_api_key = os.environ.get("GOOGLE_TTS_API_KEY", "")  # Backend use, to generate pronunciation files

config.html_url_extension = ""

# JS is minified in production and for running tests, but served as-is by default
# When minify_js is True, changing .mjs files do not re-render the pages
config.minify_js = bool(int(os.environ.get("BUNDLE_JS", 0)))
config.minify_css = True

config.context_globals = ctx
config.jinja_filters = {
    "cur": to_currency,
    "percent": to_percent,
}

config.jinja_extensions.remove("ursus.renderers.jinja.JsLoaderExtension")
config.jinja_extensions.extend(
    [
        "extensions.renderers.jinja.ToolExtension",
        "extensions.renderers.jinja.EsbuildJsLoaderExtension",
        "extensions.renderers.jinja.TableOfContentsExtension",
    ]
)

config.context_processors.extend(
    [
        "extensions.renderers.entry_images.EntryImageUrlProcessor",
        "ursus.context_processors.git_date.GitDateProcessor",
        "extensions.context_processors.hyphenated_titles.HyphenatedTitleProcessor",
        "extensions.context_processors.tool_tests.ToolTestEntriesProcessor",
        "extensions.context_processors.collections.CollectionsProcessor",
    ]
)

config.markdown_extensions["toc"]["slugify"] = patched_slugify
config.markdown_extensions["wikilinks"]["base_url"] = f"{config.site_url}/glossary/"
config.markdown_extensions["wikilinks"]["build_url"] = build_wikilinks_url
config.markdown_extensions["tasklist"]["list_item_class"] = "checkbox"
config.add_markdown_extension("extensions.markdown:WrappedTableExtension", {"wrapper_class": "table-wrapper"})
config.add_markdown_extension("extensions.markdown:ArrowLinkIconExtension")
config.add_markdown_extension("extensions.markdown:CurrencyExtension")
config.add_markdown_extension("extensions.markdown:HyphenatedTitleExtension")
config.add_markdown_extension("extensions.markdown:TypographyExtension")

config.renderers.extend(
    [
        "extensions.renderers.entry_images.EntryImageRenderer",
        "extensions.renderers.nginx_map.NginxMapRenderer",
        "extensions.renderers.glossary_audio.GlossaryAudioRenderer",
    ]
)

config.linters = [
    # 'extensions.linters.places.PlacesLinter',
    # 'ursus.linters.markdown.MarkdownExternalLinksLinter',
    # 'extensions.linters.redirects.RedirectsLinter',
    "extensions.linters.currency.CurrencyLinter",
    "extensions.linters.currency.JinjaCurrencyLinter",
    "extensions.linters.footnotes.CitationNeededLinter",
    "extensions.linters.footnotes.FootnoteLocationLinter",
    "extensions.linters.footnotes.QuestionMarkLinter",
    "extensions.linters.internal_links.MarkdownInternalLinksLinter",
    "extensions.linters.lists.MultilineListsLinter",
    "extensions.linters.metadata.DateUpdatedLinter",
    "extensions.linters.metadata.ShortTitleLinter",
    "extensions.linters.places.UnusedPlacesLinter",
    "extensions.linters.section.SectionSignLinter",
    "extensions.linters.table_of_contents.TableOfContentsLinter",
    "extensions.linters.wikilinks.WikilinksLinter",
    # 'extensions.linters.titles.DuplicateTitlesLinter',
    "extensions.linters.titles.SequentialTitlesLinter",
    "extensions.linters.titles.TitleCountLinter",
    "ursus.linters.footnotes.OrphanFootnotesLinter",
    "ursus.linters.images.UnusedImagesLinter",
    "ursus.linters.markdown.MarkdownLinkTextsLinter",
    "ursus.linters.markdown.MarkdownLinkTitlesLinter",
    "ursus.linters.markdown.RelatedEntriesLinter",
]

config.image_default_sizes = "(min-width: 800px) 800px, 100vw"
config.image_transforms = {
    "": {
        "exclude": ("experts/photos/*",),
        "max_size": (int(800 * 2), int(800 * 2 * 1.5)),
        "output_types": ("webp", "original"),
    },
    "content1.5x": {
        "include": ("images/*", "illustrations/*"),
        "exclude": ("*.pdf", "*.svg"),
        "max_size": (int(800 * 1.5), int(800 * 1.5 * 1.5)),
        "output_types": ("webp", "original"),
    },
    "content1x": {
        "include": ("images/*", "illustrations/*"),
        "exclude": ("*.pdf", "*.svg"),
        "max_size": (800, int(800 * 1.5)),
        "output_types": ("webp", "original"),
    },
    "content0.75x": {
        "include": ("images/*", "illustrations/*"),
        "exclude": ("*.pdf", "*.svg"),
        "max_size": (int(800 * 0.75), int(800 * 0.75 * 1.5)),
        "output_types": ("webp", "original"),
    },
    "content0.5x": {
        "include": ("images/*", "illustrations/*"),
        "exclude": ("*.pdf", "*.svg"),
        "max_size": (int(800 * 0.5), int(800 * 0.5 * 1.5)),
        "output_types": ("webp", "original"),
    },
    "bioLarge2x": {
        "include": "experts/photos/*",
        "max_size": (250, 250),
    },
    "bioLarge1x": {
        "include": "experts/photos/*",
        "max_size": (125, 125),
    },
    "bio2x": {
        "include": "experts/photos/*",
        "max_size": (150, 150),
    },
    "bio1x": {
        "include": "experts/photos/*",
        "max_size": (75, 75),
    },
    "previews": {
        "include": "documents/*",
        "max_size": (300, 600),
        "output_types": ("webp", "png"),
    },
    "previews2x": {
        "include": "documents/*",
        "max_size": (600, 1200),
        "output_types": ("webp", "png"),
    },
}

config.lunr_indexes = {
    "indexed_fields": (
        "title",
        "short_title",
        "description",
        "german_term",
        "english_term",
    ),
    "indexes": [
        {
            "uri_pattern": "guides/*.md",
            "returned_fields": (
                "title",
                "short_title",
                "url",
            ),
            "boost": 2,
        },
        {
            "uri_pattern": "guides/*/*.md",
            "returned_fields": (
                "title",
                "short_title",
                "url",
            ),
            "boost": 2,
        },
        {
            "uri_pattern": "glossary/*.md",
            "returned_fields": (
                "title",
                "english_term",
                "german_term",
                "url",
            ),
            "boost": 1,
        },
        {
            "uri_pattern": "docs/*.md",
            "returned_fields": (
                "title",
                "english_term",
                "german_term",
                "url",
            ),
            "boost": 1,
        },
        {
            "uri_pattern": "tools/*.md",
            "returned_fields": (
                "title",
                "url",
            ),
            "boost": 1,
        },
        {
            "uri_pattern": "contact.md",
            "returned_fields": (
                "title",
                "url",
            ),
            "boost": 2,
        },
        {
            "uri_pattern": "terms.md",
            "returned_fields": (
                "title",
                "url",
            ),
            "boost": 0.5,
        },
    ],
}

config.logging = {
    "level": logging.INFO,
    "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s",
    "handlers": [
        logging.StreamHandler(),
    ],
}
