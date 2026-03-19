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
_v = json.loads((Path(__file__).parent / "constants.json").read_text())

# ==============================================================================
# TAXES
# ==============================================================================

# German minimum wage (€/h) - https://www.bmas.de/DE/Arbeit/Arbeitsrecht/Mindestlohn/mindestlohn.html - https://www.destatis.de/DE/Themen/Arbeit/Verdienste/Mindestloehne/_inhalt.html
ctx["MINIMUM_WAGE"] = fail_on("2026-06-01", Decimal(_v["MINIMUM_WAGE"]))

ctx["MEDIAN_INCOME_BERLIN"] = fail_on(
    "2026-06-01", _v["MEDIAN_INCOME_BERLIN"]
)  # 2025 - sparkasse.de/aktuelles/einkommen-wohlhabend-im-vergleich.html
ctx["MEDIAN_INCOME_GERMANY"] = fail_on("2026-06-01", _v["MEDIAN_INCOME_GERMANY"])  # Early 2025

# Minimum allowance for au pairs (€/mth)
ctx["AU_PAIR_MIN_ALLOWANCE"] = fail_on("2026-06-01", _v["AU_PAIR_MIN_ALLOWANCE"])

# Maximum income used to calculate pension contributions (€/y)
ctx["BEITRAGSBEMESSUNGSGRENZE"] = fail_on(
    "2026-12-31", _v["BEITRAGSBEMESSUNGSGRENZE_MONTHLY"] * 12
)  # § SGB 6 Anlage 2 [BBGRV]

# Income tax calculation - https://www.lohn-info.de/lohnsteuerzahlen.html
ctx["GRUNDFREIBETRAG"] = fail_on("2026-12-31", _v["GRUNDFREIBETRAG"])  # § 32a EstG [GFB]
ctx["INCOME_TAX_BRACKET_2_MAX_INCOME"] = fail_on(
    "2026-03-20", _v["INCOME_TAX_BRACKET_2_MAX_INCOME"]
)  # § 32a EstG [UPTAB26 - 1]
ctx["INCOME_TAX_BRACKET_3_MAX_INCOME"] = fail_on(
    "2026-03-20", _v["INCOME_TAX_BRACKET_3_MAX_INCOME"]
)  # § 32a EstG [UPTAB26 - 1]
ctx["INCOME_TAX_BRACKET_4_MAX_INCOME"] = fail_on(
    "2026-03-20", _v["INCOME_TAX_BRACKET_4_MAX_INCOME"]
)  # § 32a EstG [UPTAB26 - 1]

# Upper bound (€/y) of income tax tariff zones for tax classes 5 and 6
ctx["INCOME_TAX_CLASS_56_LIMIT_1"] = fail_on(
    "2026-03-20", _v["INCOME_TAX_CLASS_56_LIMIT_1"]
)  # § 39b Abs. 2 Satz 7 EstG [W1STKL5]
ctx["INCOME_TAX_CLASS_56_LIMIT_2"] = fail_on(
    "2026-03-20", _v["INCOME_TAX_CLASS_56_LIMIT_2"]
)  # § 39b Abs. 2 Satz 7 EstG [W2STKL5]
ctx["INCOME_TAX_CLASS_56_LIMIT_3"] = fail_on(
    "2026-03-20", _v["INCOME_TAX_CLASS_56_LIMIT_3"]
)  # § 39b Abs. 2 Satz 7 EstG [W3STKL5]

ctx["INCOME_TAX_MAX_RATE"] = _v["INCOME_TAX_MAX_RATE"]  # (%) - § 32b EstG

ctx["CHURCH_TAX_RATE"] = Decimal(_v["CHURCH_TAX_RATE"])  # (%)
ctx["CHURCH_TAX_RATE_BW_BY"] = Decimal(_v["CHURCH_TAX_RATE_BW_BY"])  # (%)

ctx["SOLIDARITY_TAX_MILDERUNGSZONE_MIN_INCOME_TAX"] = fail_on(
    "2026-12-31", _v["SOLIDARITY_TAX_MILDERUNGSZONE_MIN_INCOME_TAX"]
)  # § 3 SolzG [SOLZFREI]
ctx["SOLIDARITY_TAX_MILDERUNGSZONE_RATE"] = fail_on(
    "2026-12-31", Decimal(_v["SOLIDARITY_TAX_MILDERUNGSZONE_RATE"])
)  # § 4 SolzG
ctx["SOLIDARITY_TAX_MAX_RATE"] = fail_on("2026-12-31", Decimal(_v["SOLIDARITY_TAX_MAX_RATE"]))  # § 4 SolzG

ctx["VORSORGEPAUSCHAL_MIN"] = fail_on("2026-12-31", _v["VORSORGEPAUSCHAL_MIN"])  # § 39b Abs. 2.3.e EStG
ctx["VORSORGEPAUSCHAL_MIN_TAX_CLASS_3"] = _v["VORSORGEPAUSCHAL_MIN_TAX_CLASS_3"]  # ??
ctx["ARBEITNEHMERPAUSCHALE"] = fail_on("2026-12-31", _v["ARBEITNEHMERPAUSCHALE"])  # (€/y) - § 9a EStG
ctx["SONDERAUSGABEN_PAUSCHBETRAG"] = fail_on("2026-03-20", _v["SONDERAUSGABEN_PAUSCHBETRAG"])  # (€/y) § 10c EStG [SAP]

ctx["ARBEITSLOSENVERSICHERUNG_EMPLOYEE_RATE"] = (
    Decimal(_v["ARBEITSLOSENVERSICHERUNG_RATE"]) / 2
)  # § 341 SGB 3, BeiSaV 2019

# Kindergeld amount per child (€/m) - § 6 Abs. 1 BKGG, § 66 EStG
ctx["KINDERGELD"] = fail_on("2026-12-31", _v["KINDERGELD"])

# Tax break for parents (€/y) - § 32 Abs. 6 EStG [KFB] - monitored
ctx["KINDERFREIBETRAG"] = fail_on("2026-03-20", _v["KINDERFREIBETRAG"])

# Tax break for single parents (€/y) - § 24b EStG [EFA]
ctx["ENTLASTUNGSBETRAG_ALLEINERZIEHENDE"] = fail_on("2026-03-20", _v["ENTLASTUNGSBETRAG_ALLEINERZIEHENDE"])
ctx["ENTLASTUNGSBETRAG_ALLEINERZIEHENDE_EXTRA_CHILD"] = fail_on(
    "2026-03-20", _v["ENTLASTUNGSBETRAG_ALLEINERZIEHENDE_EXTRA_CHILD"]
)

ctx["CAPITAL_GAINS_TAX_RATE"] = Decimal(_v["CAPITAL_GAINS_TAX_RATE"])  # (%) - § 32d EStG
ctx["CAPITAL_GAINS_FREIBETRAG"] = _v["CAPITAL_GAINS_FREIBETRAG"]  # Sparer-Pauschbetrag, § 20 Abs. 9 EStG

# Below that amount (€/y), you don't pay Gewerbesteuer - § 11 GewStG
ctx["GEWERBESTEUER_FREIBETRAG"] = _v["GEWERBESTEUER_FREIBETRAG"]

# Used as the basis, multiplied by the Hebesatz - (%) - § 11 GewStG
ctx["GEWERBESTEUER_RATE"] = Decimal(_v["GEWERBESTEUER_RATE"])

# The part of the Gewerbesteuer that is credited from your income tax (%)
ctx["GEWERBESTEUER_TAX_CREDIT"] = fail_on(
    "2026-12-31", Decimal(_v["GEWERBESTEUER_TAX_CREDIT"])
)  # (%) - TODO: Not watched, no source

ctx["GEWERBESTEUER_HEBESATZ_BERLIN"] = fail_on(
    "2026-12-31", Decimal(_v["GEWERBESTEUER_HEBESATZ_BERLIN"])
)  # (%) - TODO: Not watched
ctx["GEWERBESTEUER_RATE_BERLIN"] = (ctx["GEWERBESTEUER_RATE"] * ctx["GEWERBESTEUER_HEBESATZ_BERLIN"]).normalize()  # (%)

# The effective cost of the Gewerbesteuer when accounting for the income tax credit, for Berlin - (%)
ctx["GEWERBESTEUER_EXTRA_COST_BERLIN"] = (
    ctx["GEWERBESTEUER_RATE"] * (ctx["GEWERBESTEUER_HEBESATZ_BERLIN"] - ctx["GEWERBESTEUER_TAX_CREDIT"])
).normalize()

ctx["KLEINUNTERNEHMER_MAX_INCOME_FIRST_YEAR"] = _v["KLEINUNTERNEHMER_MAX_INCOME_FIRST_YEAR"]  # § 19 Abs. 1 UStG
ctx["KLEINUNTERNEHMER_MAX_INCOME"] = _v["KLEINUNTERNEHMER_MAX_INCOME"]  # § 19 Abs. 1 UStG

# Above that amount (€/y), you must use double entry bookkeeping - § 241a HGB
ctx["DOUBLE_ENTRY_MIN_REVENUE"] = _v["DOUBLE_ENTRY_MIN_REVENUE"]
ctx["DOUBLE_ENTRY_MIN_INCOME"] = _v["DOUBLE_ENTRY_MIN_INCOME"]

# VAT (%) - § 12 UStG (Abs 1 and 2)
ctx["VAT_RATE"] = Decimal(_v["VAT_RATE"])
ctx["VAT_RATE_REDUCED"] = Decimal(_v["VAT_RATE_REDUCED"])

# Below 10,000€/y in VAT, simplified rules for intra-EU VAT
ctx["EU_VAT_SCHWELLENWERT"] = _v["EU_VAT_SCHWELLENWERT"]

# Umsatzsteuer-Voranmeldung minimum amounts, based on VAT paid last year (€/year) - § 18 UStG
ctx["VAT_MIN_QUARTERLY_AMOUNT"] = _v["VAT_MIN_QUARTERLY_AMOUNT"]
ctx["VAT_MIN_MONTHLY_AMOUNT"] = _v["VAT_MIN_MONTHLY_AMOUNT"]


# ==============================================================================
# HEALTH INSURANCE
# ==============================================================================

# Below this income (€/mth), you have a minijob
ctx["MINIJOB_MAX_INCOME"] = round(ctx["MINIMUM_WAGE"] * 130 / 3)  # § 8 SGB IV

# Below this income (€/mth), you have a midijob - § 20 SGB IV
ctx["MIDIJOB_MAX_INCOME"] = fail_on("2026-03-20", _v["MIDIJOB_MAX_INCOME"])

# Used to calculate health insurance for a midijob
ctx["GKV_FACTOR_F"] = fail_on(
    "2026-12-31", Decimal(_v["GKV_FACTOR_F"])
)  # § 20 SGB IV - TODO: Can be calculated from other vals

# Median income (€/m) of all people who pay social contribs
ctx["BEZUGSGROESSE"] = fail_on("2026-12-31", Decimal(_v["BEZUGSGROESSE"]))  # SGB VI Anlage 1

# Base contribution (%), including Krankengeld
ctx["GKV_BASE_RATE_EMPLOYEE"] = Decimal(_v["GKV_BASE_RATE_EMPLOYEE"])  # § 241 SGB V
ctx["GKV_BASE_RATE_STUDENT"] = ctx["GKV_BASE_RATE_EMPLOYEE"] * Decimal("0.7")  # § 245 SGB V

# Base contribution (%), excluding Krankengeld (freelanccers, unemployed, students over 30)
ctx["GKV_BASE_RATE_SELF_PAY"] = Decimal(_v["GKV_BASE_RATE_SELF_PAY"])  # § 243 SGB V

# Mindestbemessungsgrundlage (€/mth) - Below this income, GKV does not get cheaper
ctx["GKV_MIN_INCOME"] = ctx["BEZUGSGROESSE"] / 90 * 30  # § 240 Abs. 4 SGV IV

# Above this income (€/y), you pay the Höchstbeitrag - https://www.bmas.de/DE/Arbeit/Arbeitsrecht/Mindestlohn/mindestlohn.html
ctx["GKV_MAX_INCOME"] = fail_on("2026-12-31", Decimal(_v["GKV_MAX_INCOME_MONTHLY"]) * 12)  # SVBezGrV 2021 [BBGKVPV]

# Above this income (€/mth), your employer pays for health insurance
ctx["GKV_AZUBI_FREIBETRAG"] = fail_on("2026-12-31", _v["GKV_AZUBI_FREIBETRAG"])  # § 20 Abs. 3 SGB IV

# Above this income, it's no longer a Nebenjob
ctx["GKV_NEBENJOB_MAX_INCOME"] = ctx["BEZUGSGROESSE"] * Decimal("0.75")

# Jahresarbeitsentgeltgrenze or Versicherungspflichtgrenze - Above this income (€/y), you are freiwillig versichert
ctx["GKV_FREIWILLIG_VERSICHERT_MIN_INCOME"] = fail_on(
    "2026-12-31", _v["GKV_FREIWILLIG_VERSICHERT_MIN_INCOME_MONTHLY"] * 12
)

# If you earn less than that (€/y), private health insurers usually reject you
ctx["PKV_MIN_INCOME"] = fail_on("2026-12-31", _v["PKV_MIN_INCOME"])

# Above this income (€/m), you can't have Familienversicherung
ctx["GKV_FAMILIENVERSICHERUNG_MAX_INCOME"] = (Decimal(1 / 7) * ctx["BEZUGSGROESSE"]).normalize()  # § 10 SGB V

# Zusatzbeiträge - https://www.check24.de/gesetzliche-krankenversicherung/erhoehung-zusatzbeitraege/
ctx["GKV_MIN_ZUSATZBEITRAG"] = fail_on("2026-12-31", Decimal(_v["GKV_MIN_ZUSATZBEITRAG"]))  # HKK
ctx["GKV_MAX_ZUSATZBEITRAG"] = fail_on("2026-12-31", Decimal(_v["GKV_MAX_ZUSATZBEITRAG"]))  # AOK Nordost
ctx["GKV_AVG_ZUSATZBEITRAG"] = fail_on("2026-12-31", Decimal(_v["GKV_AVG_ZUSATZBEITRAG"]))

# https://www.check24.de/gesetzliche-krankenversicherung/erhoehung-zusatzbeitraege/
ctx["GKV_ZUSATZBEITRAG_AVERAGE"] = ctx["GKV_AVG_ZUSATZBEITRAG"]
ctx["GKV_ZUSATZBEITRAG_AOK"] = fail_on("2026-12-31", Decimal(_v["GKV_ZUSATZBEITRAG_AOK"]))
ctx["GKV_ZUSATZBEITRAG_BARMER"] = fail_on("2026-12-31", Decimal(_v["GKV_ZUSATZBEITRAG_BARMER"]))
ctx["GKV_ZUSATZBEITRAG_DAK"] = fail_on("2026-12-31", Decimal(_v["GKV_ZUSATZBEITRAG_DAK"]))
ctx["GKV_ZUSATZBEITRAG_HKK"] = fail_on("2026-12-31", Decimal(_v["GKV_ZUSATZBEITRAG_HKK"]))
ctx["GKV_ZUSATZBEITRAG_TK"] = fail_on("2026-12-31", Decimal(_v["GKV_ZUSATZBEITRAG_TK"]))

ctx["TRAVEL_INSURANCE_COST"] = fail_on("2026-12-31", _v["TRAVEL_INSURANCE_COST"])  # Guesstimated
ctx["EXPAT_INSURANCE_COST"] = fail_on("2026-03-20", _v["EXPAT_INSURANCE_COST"])

ctx["EXPAT_STUDENT_COST"] = fail_on("2026-03-20", _v["EXPAT_STUDENT_COST"])  # /out/feather-expats

# Maximum daily Krankengeld
ctx["GKV_KRANKENGELD_DAILY_LIMIT"] = (ctx["GKV_MAX_INCOME"] * Decimal("0.7") / 360).normalize()  # § 47 SGB V

# BAFöG Bedarfssatz (€/y)
ctx["BAFOG_BEDARFSSATZ"] = fail_on("2026-06-01", _v["BAFOG_BEDARFSSATZ"])  # § 13 BAföG Abs 1.2 + 2.2
ctx["SPERRKONTO_AMOUNT"] = fail_on(
    "2026-06-01",
    (ctx["BAFOG_BEDARFSSATZ"] + _v["SPERRKONTO_SURCHARGE_INSURANCE"] + _v["SPERRKONTO_SURCHARGE_OTHER"]) * 12,
)  # § 13 BAföG Abs 1.2 + 2.2 + § 13a BAföG Abs 1

# Pflegeversicherung (%) - § 55 Abs. 1 SGB XI, can be changed in external regulation (like PBAV 2026)
ctx["PFLEGEVERSICHERUNG_BASE_RATE"] = fail_on("2026-12-31", Decimal(_v["PFLEGEVERSICHERUNG_BASE_RATE"]))
ctx["PFLEGEVERSICHERUNG_BASE_RATE_MAX_AGE"] = _v["PFLEGEVERSICHERUNG_BASE_RATE_MAX_AGE"]  # § 55 Abs. 1 SGB XI
ctx["PFLEGEVERSICHERUNG_EMPLOYER_RATE"] = ctx["PFLEGEVERSICHERUNG_BASE_RATE"] / 2

# Surcharge for people over 23 with no kids
ctx["PFLEGEVERSICHERUNGS_SURCHARGE"] = Decimal(_v["PFLEGEVERSICHERUNGS_SURCHARGE"])  # § 55 Abs. 3 SGB XI
ctx["PFLEGEVERSICHERUNG_DISCOUNT_PER_CHILD"] = Decimal(
    _v["PFLEGEVERSICHERUNG_DISCOUNT_PER_CHILD"]
)  # § 55 Abs. 3 SGB XI
ctx["PFLEGEVERSICHERUNG_DISCOUNT_MIN_CHILDREN"] = _v["PFLEGEVERSICHERUNG_DISCOUNT_MIN_CHILDREN"]
ctx["PFLEGEVERSICHERUNG_DISCOUNT_MAX_CHILDREN"] = _v["PFLEGEVERSICHERUNG_DISCOUNT_MAX_CHILDREN"]

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
ctx["RV_BASE_RATE"] = fail_on("2026-12-31", Decimal(_v["RV_BASE_RATE"]))  # RVBeitrSBek 202X
ctx["RV_EMPLOYEE_CONTRIBUTION"] = fail_on("2026-12-31", Decimal(_v["RV_EMPLOYEE_CONTRIBUTION"]))
ctx["RV_MIN_CONTRIBUTION"] = (ctx["RV_BASE_RATE"] * ctx["MINIJOB_MAX_INCOME"] / 100).normalize()

ctx["FUNDSBACK_FEE"] = Decimal(_v["FUNDSBACK_FEE"])  # %
ctx["FUNDSBACK_MIN_FEE"] = Decimal(_v["FUNDSBACK_MIN_FEE"])  # €
ctx["FUNDSBACK_MAX_FEE"] = Decimal(_v["FUNDSBACK_MAX_FEE"])  # €
ctx["GERMANYPENSIONREFUND_FEE"] = Decimal(_v["GERMANYPENSIONREFUND_FEE"])  # %
ctx["PENSIONREFUNDGERMANY_FEE"] = Decimal(_v["PENSIONREFUNDGERMANY_FEE"])  # %
ctx["PENSIONREFUNDGERMANY_MAX_FEE"] = _v["PENSIONREFUNDGERMANY_MAX_FEE"]  # €
ctx["GERMANYPENSIONREFUND_MAX_FEE"] = _v["GERMANYPENSIONREFUND_MAX_FEE"]  # €


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
# PUBLIC TRANSIT
# ==============================================================================

ctx["BVG_AB_TICKET"] = fail_on("2026-12-31", Decimal(_v["BVG_AB_TICKET"]))
ctx["BVG_ABC_TICKET"] = fail_on("2026-12-31", Decimal(_v["BVG_ABC_TICKET"]))
ctx["BVG_FINE"] = fail_on("2026-12-31", _v["BVG_FINE"])
ctx["BVG_REDUCED_FINE"] = fail_on("2026-12-31", _v["BVG_REDUCED_FINE"])
ctx["DEUTSCHLAND_TICKET_PRICE"] = fail_on("2026-12-31", _v["DEUTSCHLAND_TICKET_PRICE"])


# ==============================================================================
# IMMIGRATION
# ==============================================================================

# Minimum income (€/y) to get a Blue Card - § 18g AufenthG
ctx["BLUE_CARD_MIN_INCOME"] = round(Decimal("0.5") * ctx["BEITRAGSBEMESSUNGSGRENZE"])

# Minimum income (€/y) to get a Blue Card in shortage fields - § 18g AufenthG
ctx["BLUE_CARD_SHORTAGE_MIN_INCOME"] = round(Decimal("0.453") * ctx["BEITRAGSBEMESSUNGSGRENZE"])


# Visa fees (€) - § 44, § 45, § 45c and § 47 AufenthV
ctx["SCHENGEN_VISA_FEE"] = _v["SCHENGEN_VISA_FEE"]
ctx["NATIONAL_VISA_FEE"] = _v["NATIONAL_VISA_FEE"]
ctx["NATIONAL_VISA_RENEWAL_FEE"] = _v["NATIONAL_VISA_RENEWAL_FEE"]
ctx["RESIDENCE_PERMIT_REPLACEMENT_FEE"] = _v[
    "RESIDENCE_PERMIT_REPLACEMENT_FEE"
]  # After a passport change (€) - § 45c AufenthG
ctx["MIN_PERMANENT_RESIDENCE_FEE"] = _v["MIN_PERMANENT_RESIDENCE_FEE"]  # For Turkish citizens
ctx["MAX_PERMANENT_RESIDENCE_FEE"] = _v["MAX_PERMANENT_RESIDENCE_FEE"]  # § 44 AufenthG
ctx["FAST_TRACK_FEE"] = _v["FAST_TRACK_FEE"]  # § 47 AufenthG

# Minimum guaranteed pension payment (€/m) to get a freelance visa above age 45
# VAB, https://www.bmas.de/DE/Soziales/Rente-und-Altersvorsorge/rentenversicherungsbericht-art.html
ctx["FREELANCE_VISA_MIN_MONTHLY_PENSION"] = fail_on("2027-02-01", Decimal(_v["FREELANCE_VISA_MIN_MONTHLY_PENSION"]))
ctx["FREELANCE_VISA_MIN_PENSION"] = round(ctx["FREELANCE_VISA_MIN_MONTHLY_PENSION"] * 144)

# Minimum income (€/mth) before health insurance and rent to get a freelance visa - Anlage SGB 12 (Regelbedarfsstufe 1)
ctx["FREELANCE_VISA_MIN_INCOME"] = fail_on("2026-12-31", _v["FREELANCE_VISA_MIN_INCOME"])

# Minimum gross income (€/y) to get a work visa above age 45 - service.berlin.de/dienstleistung/305304
ctx["WORK_VISA_MIN_INCOME"] = ctx["BEITRAGSBEMESSUNGSGRENZE"] * Decimal("0.55")

# Not watched - https://www.berlin.de/vhs-tempelhof-schoeneberg/kurse/deutsch-als-zweitsprache/pruefungen-und-abschluesse/einbuergerung/
ctx["CITIZENSHIP_TEST_FEE"] = fail_on("2026-12-31", _v["CITIZENSHIP_TEST_FEE"])

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

ctx["BESCHEINIGUNG_IN_STEUERSACHEN_FEE"] = fail_on(
    "2026-12-31", Decimal(_v["BESCHEINIGUNG_IN_STEUERSACHEN_FEE"])
)  # dienstleistung/324713
ctx["ERWEITERTE_MELDEBESCHEINIGUNG_FEE"] = fail_on(
    "2026-12-31", _v["ERWEITERTE_MELDEBESCHEINIGUNG_FEE"]
)  # (€) - service.berlin.de/dienstleistung/120702
ctx["GEWERBEANMELDUNG_FEE"] = fail_on(
    "2026-12-31", _v["GEWERBEANMELDUNG_FEE"]
)  # € - service.berlin.de/dienstleistung/121921
ctx["HUNDEREGISTER_FEE"] = fail_on("2026-12-31", Decimal(_v["HUNDEREGISTER_FEE"]))  # € - hunderegister.berlin.de
ctx["HUNDESTEUER_FIRST_DOG"] = fail_on("2026-12-31", _v["HUNDESTEUER_FIRST_DOG"])  # §4 HuStG BE, (€/y)
ctx["HUNDESTEUER_MORE_DOGS"] = fail_on("2026-12-31", _v["HUNDESTEUER_MORE_DOGS"])  # §4 HuStG BE, (€/y)

# Maximum income from employment to stay a member of the KSK (€/y)
ctx["KSK_MAX_EMPLOYMENT_INCOME"] = ctx["BEITRAGSBEMESSUNGSGRENZE"] / 2  # § 4 KSVG
ctx["KSK_MIN_INCOME"] = fail_on("2026-12-31", _v["KSK_MIN_INCOME"])  # (€/y) - §3 Abs. 1 KSVG

# Minimum income used to calculate cost of health insurance and Pflegeversicherung
# https://www.kuenstlersozialkasse.de/service-und-medien/ksk-in-zahlen
ctx["KSK_MIN_HEALTH_INSURANCE_INCOME"] = fail_on(
    "2026-12-31", _v["KSK_MIN_HEALTH_INSURANCE_INCOME"]
)  # Mindestbeitragsberechnungsgrundlage (€/y)

ctx["ORDNUNGSAMT_DANGEROUS_DOG_FEE"] = fail_on(
    "2026-12-31", _v["ORDNUNGSAMT_DANGEROUS_DOG_FEE"]
)  # service.berlin.de/dienstleistung/326263
ctx["RUNDFUNKBEITRAG_FEE"] = fail_on("2026-12-31", Decimal(_v["RUNDFUNKBEITRAG_FEE"]))
ctx["SCHUFA_REPORT_FEE"] = fail_on("2026-12-31", Decimal(_v["SCHUFA_REPORT_FEE"]))  # TODO: Not watched
ctx["VEHICLE_UMMELDUNG_FEE"] = fail_on(
    "2026-12-31", Decimal(_v["VEHICLE_UMMELDUNG_FEE"])
)  # service.berlin.de/dienstleistung/120658
ctx["LICENSE_PLATE_COST"] = fail_on("2027-12-31", _v["LICENSE_PLATE_COST"])  # Cost of making license plates

ctx["FIRST_AID_COURSE_COST"] = fail_on(
    "2027-12-31", _v["FIRST_AID_COURSE_COST"]
)  # Cost of a first aid course for a driver's licence
ctx["DRIVING_LICENCE_CONVERSION_FEE"] = fail_on(
    "2026-12-31", Decimal(_v["DRIVING_LICENCE_CONVERSION_FEE"])
)  # (€) - /dienstleistung/327537
ctx["DRIVING_LICENCE_FEE"] = Decimal(_v["DRIVING_LICENCE_FEE"])  # (€) - service.berlin.de/dienstleistung/121627
ctx["FIRST_AID_COURSE_FEE"] = fail_on("2026-12-31", Decimal(_v["FIRST_AID_COURSE_FEE"]))
ctx["DRIVING_SCHOOL_FEE"] = fail_on("2026-12-31", Decimal(_v["DRIVING_SCHOOL_FEE"]))
ctx["DRIVING_PRACTICE_FEE"] = fail_on("2026-12-31", Decimal(_v["DRIVING_PRACTICE_FEE"]))  # per 45-minute lesson
ctx["DRIVING_THEORY_EXAM_FEE"] = fail_on("2026-12-31", Decimal(_v["DRIVING_THEORY_EXAM_FEE"]))  # Dekra/TÜV fee
ctx["DRIVING_PRACTICAL_EXAM_FEE"] = fail_on("2026-12-31", Decimal(_v["DRIVING_PRACTICAL_EXAM_FEE"]))  # Dekra/TÜV fee

ctx["LEGAL_HOTLINE_COST_PER_MINUTE"] = fail_on(
    "2026-03-20", _v["LEGAL_HOTLINE_COST_PER_MINUTE"]
)  # https://www.vonengelhardt.com/en/helpnowen

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
