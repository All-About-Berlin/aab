from decimal import Decimal
import pytest
import re


@pytest.fixture(scope="session")
def session_context(browser):
    new_context = browser.new_context(ignore_https_errors=True)
    yield new_context
    new_context.close()


@pytest.fixture(scope="session")  # Reuse the same page for multiple calculations
def external_tax_calculator(session_context):
    page = session_context.new_page()
    page.set_default_timeout(5000)
    page.goto("https://www.tk-lex.tk.de/web/guest/rechner/-/ideskproductresources/2006/MIME/7546978/HI7546978.html")
    yield page
    page.close()


@pytest.fixture(scope="session")  # Reuse the same page for multiple calculations
def local_tax_calculator(session_context, base_url):
    page = session_context.new_page()
    page.set_default_timeout(2000)
    page.goto(f"{base_url}/tests/tools/tax-calculator")
    page.get_by_role("link", name="Show options").click()
    yield page
    page.close()


def get_external_results(
    page, income, occupation, age, tax_class, children_count, is_married, zusatzbeitrag, religion, region
):
    def get_numerical_value(row_title):
        content = page.locator("table.table", has_text=row_title).locator("td:last-child").first.text_content()
        return Decimal(re.sub(r"[^0-9\,]", "", content).replace(",", ".")).quantize(Decimal("0.01"))

    # Period
    period_selector = page.locator("select#gwt-debug-inPeriod")
    if period_selector.is_enabled():
        period_selector.select_option("Jahr")

    # Income
    page.locator("input#gwt-debug-inBrutto").fill(str(income))

    # Tax class
    tax_class_label = [None, "I", "II", "III", "IV", "V", "VI"][tax_class]
    page.locator("select#gwt-debug-inTaxSteuerKlasse").select_option(tax_class_label)

    # Children
    page.locator("select#gwt-debug-inTaxKFB").select_option()

    pays_more_for_pflegeversicherung = age >= 23 and children_count == 0
    if page.locator("input#gwt-debug-inTaxUsePVZ-input").is_checked() != pays_more_for_pflegeversicherung:
        page.locator("input#gwt-debug-inTaxUsePVZ-input").click()

    children_count_selector = page.locator("select#gwt-debug-inTaxPVKinder")
    if children_count_selector.is_enabled():
        if children_count >= 5:
            children_count_selector.select_option("5 oder mehr")
        elif children_count == 0:
            children_count_selector.select_option("0 (Arbeitnehmer < 23 Jahre)")
        else:
            children_count_selector.select_option(str(children_count))

    # Region
    page.locator("select#gwt-debug-inTaxBula").select_option(
        {"bb": "Brandenburg", "by": "Bayern", "be-west": "Berlin-West", "be-east": "Berlin-Ost"}[region]
    )

    # Church tax
    if page.locator("input#gwt-debug-inTaxUseKiSt-input").is_checked() != bool(religion):
        page.locator("input#gwt-debug-inTaxUseKiSt-input").click()

    # Health insurance
    page.locator("input#gwt-debug-inTaxKVZusatzbeitrag").fill(str(zusatzbeitrag).replace(".", ","))

    return {
        "health_insurance": (get_numerical_value("Krankenversicherung") + get_numerical_value("Pflegeversicherung")),
        "public_pension": get_numerical_value("Rentenversicherung"),
        "unemployment_insurance": get_numerical_value("Arbeitslosenversicherung"),
        "income_tax": get_numerical_value("Lohnsteuer"),
        "solidarity_surcharge": get_numerical_value("Solidaritätszuschlag"),
        "church_tax": get_numerical_value("Kirchensteuer"),
    }


def get_local_results(
    page, income, occupation, age, tax_class, children_count, is_married, zusatzbeitrag, religion, region
):
    page.get_by_label("Salary").fill(str(income))
    page.get_by_label("Occupation").select_option(occupation)
    page.get_by_label("Where do you work?").select_option(region)
    page.get_by_label("Age", exact=True).fill(str(age))
    page.get_by_label("Religion").select_option(religion or "other")
    page.get_by_label("Health insurance").select_option("public-custom")
    page.get_by_label("Insurer surcharge").fill(str(zusatzbeitrag))
    page.get_by_text("Married", exact=True).set_checked(is_married)
    page.get_by_role("combobox", name="Children").select_option(str(children_count))
    page.get_by_text(f"Tax class {tax_class}").click()

    def get_numerical_value(collapsible_title):
        if page.locator("summary", has_text=collapsible_title).is_visible(timeout=0):
            value = page.locator("summary", has_text=collapsible_title).locator(".currency").text_content()
            return Decimal(re.sub(r"[^0-9\.]", "", value)).quantize(Decimal("0.01"))
        else:
            return Decimal(0).quantize(Decimal("0.01"))

    return {
        "health_insurance": get_numerical_value("Health insurance"),
        "public_pension": get_numerical_value("Public pension"),
        "unemployment_insurance": get_numerical_value("Unemployment insurance"),
        "income_tax": get_numerical_value("Income tax"),
        "solidarity_surcharge": get_numerical_value("Solidarity surcharge"),
        "church_tax": get_numerical_value("Church tax"),
    }


def compare_results(actual: dict, expected: dict, tax_calculator_params: dict):
    keys = set([*actual.keys(), *expected.keys()])

    errors = ""
    for key in keys:
        act = actual.get(key)
        exp = expected.get(key)
        if act != exp:
            if isinstance(act, Decimal) and isinstance(exp, Decimal):
                if act - exp > 2:
                    errors += f"\n\t{key:<25}: {act or '':<8} != {exp or '':<8}"
            else:
                errors += f"\n\t{key:<25}: {act or '':<8} != {exp or '':<8}"

    if errors:
        params = "".join([f"\n\t{key:<25}: {value}" for key, value in tax_calculator_params.items()])
        pytest.fail(f"PARAMS:{params}\n\nDIFF:{errors}", pytrace=False)


@pytest.mark.parametrize("age", [21, 23, 31])
@pytest.mark.parametrize("income", [10000, 20000, 50000, 110000, 500000])
@pytest.mark.parametrize("children_count", [0, 1, 2, 6])
@pytest.mark.parametrize("region", ["be-east", "be-west"])  # ['be-east', 'be-west', 'by', 'bb']
def test_results(local_tax_calculator, external_tax_calculator, age, children_count, income, region):
    tax_calculator_params = {
        "age": age,
        "children_count": children_count,
        "income": income,
        "is_married": False,
        "occupation": "employee",
        "region": region,
        "religion": None,
        "tax_class": 1,
        "zusatzbeitrag": 2.9,
    }
    compare_results(
        actual=get_local_results(local_tax_calculator, **tax_calculator_params),
        expected=get_external_results(external_tax_calculator, **tax_calculator_params),
        tax_calculator_params=tax_calculator_params,
    )
