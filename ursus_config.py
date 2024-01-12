from datetime import datetime
from ursus.config import config
from extensions.functions import glossary_groups
from pathlib import Path
import logging
import os
import secrets
import string
import urllib


logging.addLevelName(logging.DEBUG, ' D ')
logging.addLevelName(logging.INFO, '\033[37m\033[0;100m I \033[0m')
logging.addLevelName(logging.WARNING, '\033[37m\033[43m W \033[0m')
logging.addLevelName(logging.ERROR, '\033[37m\033[41m E \033[0m')
logging.addLevelName(logging.CRITICAL, '\033[37m\033[41m C \033[0m')


def to_number(value):
    return "{:,}".format(value) if value else ''


def to_currency(value):
    return "{:0,.2f}".format(value).replace('.00', '') if value else ''


def random_id():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(5))


def build_wikilinks_url(label, base, end):
    return '{}{}{}'.format(base, urllib.parse.quote(label), end)


def fail_on(expiration_date: str) -> str:
    # Fails when the expiration date is reached. Used to set content date limits.
    assert datetime.strptime(expiration_date, "%Y-%m-%d") >= datetime.now(), f"Content expired on {expiration_date}"
    return ''


def or_join(items):
    return ', '.join(items[:-1]) + ' or ' + items[-1]


config.content_path = Path(__file__).parent / 'content'
config.templates_path = Path(__file__).parent / 'templates'
config.output_path = Path(__file__).parent.parent / 'output'

config.site_url = os.environ.get('SITE_URL', '')
config.html_url_extension = ''

config.checkbox_list_item_class = 'checkbox'
config.table_wrapper_class = 'table-wrapper'

config.lunr_indexes = {
    'indexed_fields': ('title', 'short_title', 'description', 'german_term', 'english_term',),
    'indexes': [
        {
            'uri_pattern': 'guides/*.md',
            'returned_fields': ('title', 'short_title', 'url', ),
            'boost': 2,
        },
        {
            'uri_pattern': 'glossary/*.md',
            'returned_fields': ('title', 'english_term', 'german_term', 'url', ),
            'boost': 1,
        },
        {
            'uri_pattern': 'docs/*.md',
            'returned_fields': ('title', 'english_term', 'german_term', 'url', ),
            'boost': 1,
        },
        {
            'uri_pattern': 'tools/*.md',
            'returned_fields': ('title', 'url', ),
            'boost': 1,
        },
        {
            'uri_pattern': 'contact.md',
            'returned_fields': ('title', 'url',),
            'boost': 2,
        },
        {
            'uri_pattern': 'terms.md',
            'returned_fields': ('title', 'url',),
            'boost': 0.5,
        },
    ]
}

config.image_default_sizes = '(min-width: 800px) 800px, 100vw'
config.image_transforms = {
    '': {
        'exclude': ('experts/photos/*', ),
        'max_size': (int(800 * 2), int(800 * 2 * 1.5)),
        'output_types': ('webp', 'original'),
    },
    'content1.5x': {
        'include': ('images/*', 'illustrations/*'),
        'exclude': ('*.pdf', '*.svg'),
        'max_size': (int(800 * 1.5), int(800 * 1.5 * 1.5)),
        'output_types': ('webp', 'original'),
    },
    'content1x': {
        'include': ('images/*', 'illustrations/*'),
        'exclude': ('*.pdf', '*.svg'),
        'max_size': (800, int(800 * 1.5)),
        'output_types': ('webp', 'original'),
    },
    'content0.75x': {
        'include': ('images/*', 'illustrations/*'),
        'exclude': ('*.pdf', '*.svg'),
        'max_size': (int(800 * 0.75), int(800 * 0.75 * 1.5)),
        'output_types': ('webp', 'original'),
    },
    'content0.5x': {
        'include': ('images/*', 'illustrations/*'),
        'exclude': ('*.pdf', '*.svg'),
        'max_size': (int(800 * 0.5), int(800 * 0.5 * 1.5)),
        'output_types': ('webp', 'original'),
    },
    'bioLarge2x': {
        'include': 'experts/photos/*',
        'max_size': (250, 250),
    },
    'bioLarge1x': {
        'include': 'experts/photos/*',
        'max_size': (125, 125),
    },
    'bio2x': {
        'include': 'experts/photos/*',
        'max_size': (150, 150),
    },
    'bio1x': {
        'include': 'experts/photos/*',
        'max_size': (75, 75),
    },
    'previews': {
        'include': 'documents/*',
        'max_size': (300, 600),
        'output_types': ('webp', 'png'),
    },
    'previews2x': {
        'include': 'documents/*',
        'max_size': (600, 1200),
        'output_types': ('webp', 'png'),
    },
}

config.context_processors += (
    'extensions.renderers.entry_images.EntryImageUrlProcessor',
    'ursus.context_processors.git_date.GitDateProcessor',
)

config.renderers += (
    'extensions.renderers.entry_images.EntryImageRenderer',
)

config.linters = (
    # 'extensions.linters.places.PlacesLinter',
    # 'ursus.linters.markdown.MarkdownExternalLinksLinter',
    'extensions.linters.footnotes.CitationNeededLinter',
    'extensions.linters.footnotes.FootnoteLocationLinter',
    'extensions.linters.footnotes.QuestionMarkLinter',
    'extensions.linters.internal_links.MarkdownInternalLinksLinter',
    'extensions.linters.lists.MultilineListsLinter',
    'extensions.linters.metadata.DateUpdatedLinter',
    'extensions.linters.metadata.ShortTitleLinter',
    'extensions.linters.places.UnusedPlacesLinter',
    'extensions.linters.table_of_contents.TableOfContentsLinter',
    'extensions.linters.wikilinks.WikilinksLinter',
    'ursus.linters.footnotes.OrphanFootnotesLinter',
    'ursus.linters.images.UnusedImagesLinter',
    'ursus.linters.markdown.MarkdownLinkTextsLinter',
    'ursus.linters.markdown.MarkdownLinkTitlesLinter',
)

config.minify_js = True
config.minify_css = True

config.wikilinks_base_url = f'{config.site_url}/glossary'
config.wikilinks_url_builder = build_wikilinks_url
config.jinja_filters = {
    'number': to_number,
    'num': to_number,
    'currency': to_currency,
    'cur': to_currency,
}

config.google_maps_api_key = 'AIzaSyAke3v8wHo91JZBiU8B6q6zMtOPn9i_xeM'  # Backend use only


minimum_wage = 12.41
beitragsbemessungsgrenze_west = 90600
gkv_hoechstbeitrag_min_income = 62100
bezugsgroesse_west = 3535
health_insurance_base_contrib = 14.6
health_insurance_min_pflegeversicherung = 2.4
health_insurance_max_pflegeversicherung = 4
health_insurance_min_zusatzbeitrag = 1
health_insurance_max_zusatzbeitrag = 1.9

aufenthv_41_countries = [
    "Australia",
    "Canada",
    "Israel",
    "Japan",
    "New Zealand",
    "South Korea",
    "the United Kingdom",
    "the United States",
]

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

aufenthg_21_2_countries = [  # Exempt from freelance visa pension requirement
    "Dominican Republic",
    "Indonesia",
    "Iran",
    "Japan",
    "Philippines",
    "Sri Lanka",
    "Turkey",
    "the United States",
]

config.context_globals = {
    'now': datetime.now(),
    'site_url': config.site_url,
    'random_id': random_id,
    'fail_on': fail_on,
    'google_maps_api_key': 'AIzaSyBtGlbcvFspb9habWlXiFcptF8wdFjCb-E',  # Frontend use
    'glossary_groups': glossary_groups,

    # ==============================================================================
    # HEALTH INSURANCE
    # ==============================================================================

    # Mindestbemessungsgrundlage (€/mth) - §240 Abs. 4 SGV IV
    "GKV_MIN_INCOME": bezugsgroesse_west / 90 * 30,

    # Jahresarbeitsentgeltgrenze or Versicherungspflichtgrenze - Above this income (€/y), you are freiwillig versichert
    "GKV_FREIWILLIG_VERSICHERT_MIN_INCOME": 69300,

    # Above this income (€/mth), your employer pays for health insurance - §20 SGB IV
    "GKV_AZUBI_FREIBETRAG": 325,

    # Above this income, it's no longer a Nebenjob
    "GKV_NEBENJOB_MAX_INCOME": bezugsgroesse_west * 0.75,

    # Besondere Versicherungspflichtgrenze - Above this income (€/y), you pay the Höchstbeitrag - SVBezGrV 2021 [BBGKVPV]
    "GKV_HÖCHSTBEITRAG_MIN_INCOME": gkv_hoechstbeitrag_min_income,

    # Maximum daily Krankengeld - § 47 SGB V
    "GKV_KRANKENGELD_DAILY_LIMIT": gkv_hoechstbeitrag_min_income * 0.7 / 360,

    # Above this income (€/m), you can't have Familienversicherung - §10 SGB V
    "GKV_FAMILIENVERSICHERUNG_MAX_INCOME": 1 / 7 * bezugsgroesse_west,

    # Base contribution (%), including Krankengeld - § 241 SGB V
    "GKV_BASE_CONTRIBUTION": health_insurance_base_contrib,

    # Base contribution (%) for students - § 245 SGB V
    "GKV_STUDENT_BASE_CONTRIBUTION": health_insurance_base_contrib * 0.7,

    # Base contribution (%), excluding Krankengeld - § 243 SGB V
    "GKV_SELF_EMPLOYED_BASE_CONTRIBUTION": 14,

    # Estimated minimum contribution (€/mth) without employer contribution
    # TODO (2024-01-01)
    "GKV_ESTIMATED_MIN_CONTRIBUTION": 210,

    # Estimated maximum contribution for employees (€/mth)
    # TODO (2024-01-01)
    "GKV_ESTIMATED_EMPLOYEE_MAX_CONTRIBUTION": 470,

    # Estimated maximum contribution for freelancers (€/mth)
    # TODO (2024-01-01)
    "GKV_ESTIMATED_SELF_EMPLOYED_MAX_CONTRIBUTION": 925,

    # Estimated contribution for students (€/mth)
    # TODO (2024-01-01)
    "GKV_ESTIMATED_STUDENT_CONTRIBUTION": 120,

    # Used to calculate health insurance for a midijob - § 20 SGB IV - monitored
    "GKV_FACTOR_F": 0.6846,

    # Not quite accurate, but good enough
    "GKV_MIN_EMPLOYEE_RATE": round(
        (health_insurance_base_contrib + health_insurance_min_pflegeversicherung + health_insurance_min_zusatzbeitrag)
        / 2,
        1
    ),
    "GKV_MAX_EMPLOYEE_RATE": round(
        (health_insurance_base_contrib + health_insurance_max_pflegeversicherung + health_insurance_max_zusatzbeitrag)
        / 2,
        1
    ),
    "GKV_MIN_FREELANCER_RATE": round(
        health_insurance_base_contrib + health_insurance_min_pflegeversicherung + health_insurance_min_zusatzbeitrag,
        1
    ),
    "GKV_MAX_FREELANCER_RATE": round(
        health_insurance_base_contrib + health_insurance_max_pflegeversicherung + health_insurance_max_zusatzbeitrag,
        1
    ),

    # Pflegeversicherung (%)
    "PFLEGEVERSICHERUNG_WITH_SURCHARGE": health_insurance_max_pflegeversicherung,
    "PFLEGEVERSICHERUNG_NO_SURCHARGE": 3.4,
    "PFLEGEVERSICHERUNG_DISCOUNT_PER_CHILD": 0.25,
    "PFLEGEVERSICHERUNG_NO_SURCHARGE_MAX_AGE": 22,

    # BAFöG Bedarfssatz (€/y) - sum of §13 BAföG Abs 1.2 + 2.2
    "GKV_BAFOG_BEDARFSSATZ": 812,

    # Minimum income (€/y) to join the Künstlersozialkasse - § 3 Abs. 1 KSVG
    "KSK_MIN_INCOME": 3900,

    # Zusatzbeiträge
    "GKV_ZUSATZBEITRAG_AVERAGE": 1.7,
    "GKV_ZUSATZBEITRAG_AOK": 2.7,
    "GKV_ZUSATZBEITRAG_BARMER": 2.19,
    "GKV_ZUSATZBEITRAG_DAK": 1.7,
    "GKV_ZUSATZBEITRAG_HKK": 0.98,
    "GKV_ZUSATZBEITRAG_TK": 1.2,

    # ==============================================================================
    # IMMIGRATION
    # ==============================================================================

    "RESIDENCE_PERMIT_WAIT_TIME": "6 to 10 weeks",

    # Minimum income (€/y) to get a Blue Card - §18b AufenthG
    "BLUE_CARD_MIN_INCOME": 2 / 3 * beitragsbemessungsgrenze_west,

    # Minimum income (€/y) to get a Blue Card in shortage fields - §18b AufenthG
    "BLUE_CARD_SHORTAGE_MIN_INCOME": 0.52 * beitragsbemessungsgrenze_west,

    # Visa fees (€) - §44 AufenthV
    "SCHENGEN_VISA_FEE": 75,
    "NATIONAL_VISA_FEE": 100,
    "NATIONAL_VISA_RENEWAL_FEE": 96,

    # Minimum pension value (€) to get a freelance visa above age 45 - A21.3 VAB
    # 144 times FREELANCE_VISA_MIN_MONTHLY_PENSION, it seems
    # TODO (2024-01-01)
    "FREELANCE_VISA_MIN_PENSION": 206293,

    # Minimum guaranteed pension payment (€/m) to get a freelance visa above age 45
    # TODO (2024-01-01)
    "FREELANCE_VISA_MIN_MONTHLY_PENSION": 1432.59,

    # Minimum income (€/mth) before health insurance and rent to get a freelance visa - Anlage SGB 12
    "FREELANCE_VISA_MIN_INCOME": 563,

    # Minimum gross income (€/y) to get a work visa above age 45 - service.berlin.de/dienstleistung/305304
    "WORK_VISA_MIN_INCOME": beitragsbemessungsgrenze_west * 0.55,

    # Nationalities that can apply for a residence permit directly in Germany - §41 AufenthV

    "AUFENTHG_21_2_COUNTRIES": or_join(aufenthg_21_2_countries),
    "AUFENTHV_41_COUNTRIES": or_join(aufenthv_41_countries),
    "BESCHV_26_COUNTRIES": or_join(sorted(beschv_26_1_countries + beschv_26_2_countries)),
    "BESCHV_26_1_COUNTRIES": or_join(beschv_26_1_countries),
    "BESCHV_26_2_COUNTRIES": or_join(beschv_26_2_countries),

    # ==============================================================================
    # TAXES
    # ==============================================================================

    # German minimum wage (€/h)
    "MINIMUM_WAGE": minimum_wage,

    # Minimum allowance for au pairs (€/mth)
    "AU_PAIR_MIN_ALLOWANCE": 280,

    # Below this income (€/mth), you have a minijob - § 8 SGB IV
    "MINIJOB_MAX_INCOME": round(minimum_wage * 130 / 3),

    # Below this income (€/mth), you have a midijob - §20 SGB IV
    "MIDIJOB_MAX_INCOME": 2000,

    # Median income (€/m) of all people who pay social contribs - SGB VI Anlage 1
    "BEZUGSGRÖSSE_WEST": bezugsgroesse_west,

    # Median income (€/y) - rounded
    # TODO (2024-01-01)
    "MEDIAN_INCOME_BERLIN": 43572,  # 2021
    "MEDIAN_INCOME_GERMANY": 42192,  # 2021

    # Public pension contribution (%) - RVBeitrSBek 202X
    "RENTENVERSICHERUNG_EMPLOYEE_CONTRIBUTION": 9.3,
    "RENTENVERSICHERUNG_TOTAL_CONTRIBUTION": 18.6,

    # Minimum Vorsorgepauschale - §39b Abs. 2.3 EStG
    "VORSORGEPAUSCHAL_MIN": 1900,
    "VORSORGEPAUSCHAL_MIN_TAX_CLASS_3": 3000,

    # Grundfreibetrag (€/y) - § 32a EstG [GFB]
    "GRUNDFREIBETRAG": 11604,

    # Upper bound (€/y) of income tax tarif zones 2, 3 and 4 - § 32a EstG
    "INCOME_TAX_TARIF_2_MAX_INCOME": 17005,
    "INCOME_TAX_TARIF_3_MAX_INCOME": 66760,
    "INCOME_TAX_TARIF_4_MAX_INCOME": 277825,

    # Upper bound (€/y) of income tax tarif zones for tax classes 5 and 6 - § 39b Abs. 2 Satz 7 EstG [W1STKL5][W2STKL5][W3STKL5]
    "INCOME_TAX_CLASS_56_LIMIT_1": 13279,
    "INCOME_TAX_CLASS_56_LIMIT_2": 33380,
    "INCOME_TAX_CLASS_56_LIMIT_3": 222260,

    # Maximum income tax rate - § 32b EstG
    "INCOME_TAX_MAX_RATE": 45,

    # Church tax rate as percentage of income tax
    "CHURCH_TAX_RATE": 9,
    "CHURCH_TAX_RATE_BW_BY": 8,

    # Above that income tax amount, you pay a 11.9% solidarity tax (€/y) - §3 SolzG 4a [SOLZFREI]
    "SOLIDARITY_TAX_MILDERUNGSZONE_MIN_INCOME_TAX": 18130,
    "SOLIDARITY_TAX_MILDERUNGSZONE_RATE": 0.119,
    "SOLIDARITY_TAX_MAX_RATE": 0.055,

    # (€/y) - §9a EStG
    "ARBEITNEHMERPAUSCHALE": 1230,

    # The employee's contribution (%) for Arbeitslosenversicherung - § 341 SGB 3, BeiSaV 2019
    "ARBEITSLOSENVERSICHERUNG_EMPLOYEE_RATE": 1.3,

    # Maximum income used to calculate pension contributions (€/y) [BBGRV] - § SGB 6, Anlage 2
    "BEITRAGSBEMESSUNGSGRENZE_EAST": 89400,
    "BEITRAGSBEMESSUNGSGRENZE_WEST": beitragsbemessungsgrenze_west,

    # Maximum income from employment to stay a member of the KSK (€/y) - § 4 KSVG
    "KSK_MAX_EMPLOYMENT_INCOME": beitragsbemessungsgrenze_west / 2,

    # (€/y) §10c EStG [SAP]
    "SONDERAUSGABEN_PAUSCHBETRAG": 36,

    # Kindergeld amount per child (€/m) - §6 BKGG
    "KINDERGELD": 250,

    # Tax break for parents (€/y) - § 32 EStG [KFB] - monitored
    "KINDERFREIBETRAG": 9312,

    # Tax break for single parents (€/y) - § 24b EStG [EFA]
    "ENTLASTUNGSBETRAG_ALLEINERZIEHENDE": 4260,
    "ENTLASTUNGSBETRAG_ALLEINERZIEHENDE_EXTRA_CHILD": 240,

    # Below that amount (€/y), you don't pay Gewerbesteuer - § 11 GewStG
    # WARNING: If you change this, some example calculations in the content will be incorrect
    "GEWERBESTEUER_FREIBETRAG": 24500,

    # Above that amount (€/y), you are no longer a Kleinunternehmer - § 19 UStG
    "KLEINUNTERNEHMER_MAX_INCOME_FIRST_YEAR": 22000,
    "KLEINUNTERNEHMER_MAX_INCOME": 50000,

    # Above that amount (€/y), you must use double entry bookkeeping - § 241a HGB
    "DOUBLE_ENTRY_MIN_REVENUE": 600000,
    "DOUBLE_ENTRY_MIN_INCOME": 60000,

    # (€/m) - monitored
    "RUNDFUNKBEITRAG_FEE": 18.36,

    # Fee to change the address on your vehicle papers - service.berlin.de/dienstleistung/120658
    "VEHICLE_UMMELDUNG_FEE": 10.80,

    # VAT (%) - § 12 UStG (Abs 1 and 2)
    "VAT_RATE": 19,
    "VAT_RATE_REDUCED": 7,

    # Below 10,000€/y in VAT, simplified rules for intra-EU VAT
    "EU_VAT_SCHWELLENWERT": 10000,

    # Umsatzsteuer-Voranmeldung minimum amounts, based on VAT paid last year (€/year) - § 18 UStG
    "VAT_MIN_QUARTERLY_AMOUNT": 1000,
    "VAT_MIN_MONTHLY_AMOUNT": 7500,

    # Capital gains tax - § 32d EStG
    "CAPITAL_GAINS_TAX_RATE": 25,
    # Sparer-Pauschbetrag, § 20 Abs. 9 EStG
    "CAPITAL_GAINS_FREIBETRAG": 1000,

    # ==============================================================================
    # PUBLIC TRANSIT
    # ==============================================================================

    # € - monitored
    "BVG_AB_TICKET": 3.50,
    "BVG_ABC_TICKET": 4.40,
    "BVG_FINE": 60,
    "BVG_REDUCED_FINE": 7,
    "DEUTSCHLAND_TICKET_PRICE": 49,

    # ==============================================================================
    # ADMINISTRATION
    # ==============================================================================

    "DIGITAL_ABMELDUNG_FEE": 15,

    # € - service.berlin.de/dienstleistung/121921
    "GEWERBEANMELDUNG_FEE": 15,

    # € - hunderegister.berlin.de
    "HUNDEREGISTER_FEE": 17.50,

    # Dog tax (€/y) - §4 HuStG BE
    "HUNDESTEUER_FIRST_DOG": 120,
    "HUNDESTEUER_MORE_DOGS": 180,

    # Fee for registering dangerous breeds - service.berlin.de/dienstleistung/326263
    "ORDNUNGSAMT_DANGEROUS_DOG_FEE": 30,

    # (€) - service.berlin.de/dienstleistung/121822
    "HUNDEFUHRERSCHEIN_FEE": 94,

    # (€) - service.berlin.de/dienstleistung/121627
    "DRIVING_LICENCE_FEE": 49.80,

    # (€) - https://service.berlin.de/dienstleistung/327537/
    "DRIVING_LICENCE_CONVERSION_FEE": 36.30,

    # (€) - https://www.meineschufa.de/de/datenkopie, https://bonitaetscheck.immobilienscout24.de/
    "SCHUFA_REPORT_FEE": 29.95,
}

config.logging = {
    'datefmt': '%H:%M:%S',
    'fmt': '%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s',
    'level': logging.INFO,
}
