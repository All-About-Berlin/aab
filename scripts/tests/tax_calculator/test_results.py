from decimal import Decimal
import pytest
import re


def fill_calculator(
    page,
    income=25000,
    occupation="employee",
    age=25,
    tax_class=1,
    children_count=0,
    is_married=False,
    zusatzbeitrag=1.5,
    religion=None,
    region="be-east",
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


def verify_results(
    page,
    health_insurance=None,
    public_pension=None,
    unemployment_insurance=None,
    income_tax=None,
    solidarity_surcharge=None,
    church_tax=None,
):
    def get_numerical_value(collapsible_title):
        content = page.locator("summary", has_text=collapsible_title).locator("output").text_content()
        return Decimal(re.sub(r'[^0-9\.]', '', content))

    if health_insurance is not None:
        actual = Decimal(round(health_insurance))
        expected = get_numerical_value("Health insurance")
        assert (actual - expected < 2), f"Health insurance: {actual} != {expected}"
    if public_pension is not None:
        actual = Decimal(round(public_pension))
        expected = get_numerical_value("Public pension")
        assert (actual - expected < 2), f"Public pension: {actual} != {expected}"
    if unemployment_insurance is not None:
        actual = Decimal(round(unemployment_insurance))
        expected = get_numerical_value("Unemployment insurance")
        assert (actual - expected < 2), f"Unemployment insurance: {actual} != {expected}"
    if income_tax is not None:
        actual = Decimal(round(income_tax))
        expected = get_numerical_value("Income tax")
        assert (actual - expected < 2), f"Income tax: {actual} != {expected}"
    if solidarity_surcharge is not None:
        actual = Decimal(round(solidarity_surcharge))
        expected = get_numerical_value("Solidarity surcharge")
        assert (actual - expected < 2), f"Solidarity surcharge: {actual} != {expected}"
    if church_tax is not None:
        actual = Decimal(round(church_tax))
        expected = get_numerical_value("Church tax")
        assert (actual - expected < 2), f"Church tax: {actual} != {expected}"


def get_external_results(
    page,
    income=25000,
    occupation="employee",
    age=25,
    tax_class=1,
    children_count=0,
    is_married=False,
    zusatzbeitrag=1.5,
    religion=None,
    region="be-east",
):
    def get_numerical_value(row_title):
        content = page.locator("#s_r_de_lohnsteuer_result tr", has_text=row_title).locator("td:last-child").first.text_content()
        return Decimal(re.sub(r'[^0-9\,]', '', content).replace(',', '.'))

    # Income
    page.locator("#s_r_de_lohnsteuer_bruttolohn").fill(str(income))

    # Tax class
    tax_class_label = [None, 'I', 'II', 'III', 'IV', 'V', 'VI'][tax_class]
    page.get_by_role("button", name=tax_class_label, exact=True).click()

    # Children
    page.locator("#s_r_de_lohnsteuer_kinderanzahl-button").click()
    if children_count == 0:
        if age >= 23:
            page.get_by_role("option", name="Kinderlos, mind. 23").click()
        else:
            page.get_by_role("option", name="Kinderlos, unter 23").click()
    elif children_count == 1:
        page.get_by_role("option", name="1 Kind").click()
    elif children_count in [2, 3, 4]:
        page.get_by_role("option", name=f"{children_count} Kinder").click()
    elif children_count > 4:
        page.get_by_role("option", name="5 oder mehr Kinder").click()

    # Region
    bundesland = {
        "bb": "Brandenburg",
        "by": "Bayern",
        "be-west": "Berlin‑West",  # Note: hyphen is non-standard character
        "be-east": "Berlin‑Ost",
    }
    page.locator("#s_r_de_lohnsteuer_bundesland-button").click()
    page.get_by_role("option", name=bundesland[region]).click()

    # Church tax
    page.locator("#s_r_de_lohnsteuer_kirchensteuer").get_by_role("button", name="Ja" if religion else "Nein").click()

    # Health insurance
    page.get_by_label("Zusatzbeitrag Krankenvers. in %").fill(str(zusatzbeitrag).replace('.', ','))

    page.get_by_role("button", name="Berechnen").click()

    values = dict(
        health_insurance=(
            get_numerical_value("% Krankenversicherung")
            + get_numerical_value("% KV Zusatzbeitrag")
            + get_numerical_value("% Pflegeversicherung")
        ),
        public_pension=get_numerical_value("% Rentenversicherung"),
        unemployment_insurance=get_numerical_value("% Arbeitslosenversicherung"),
        income_tax=get_numerical_value("Lohnsteuer"),
        solidarity_surcharge=get_numerical_value("Solidaritätszuschlag") or None,
        church_tax=get_numerical_value("Kirchensteuer") if religion else None,
    )

    # Remove the old calculation
    page.locator("#s_r_de_lohnsteuer_result .ui-myresult-close").click()

    return values


@pytest.fixture(scope="session")
def context(browser, browser_context_args):
    new_context = browser.new_context(**browser_context_args)
    yield new_context
    new_context.close()


@pytest.fixture(scope="session")
def external_calc_page(context):
    page = context.new_page()
    page.set_default_timeout(5000)
    page.goto("https://www.smart-rechner.de/lohnsteuer/rechner.php")

    # Cookie banner
    page.frame_locator("iframe[title=\"SP Consent Message\"]").get_by_label("Akzeptieren").click()

    # Yearly calculation
    page.locator("#s_r_de_lohnsteuer_lohnzahlungszeitraum-button").get_by_text("Monatsbrutto").click()
    page.get_by_role("option", name="Jahresbrutto").click()

    return page


@pytest.fixture(scope="session")
def calc_page(context):
    page = context.new_page()
    page.set_default_timeout(10000)
    page.goto("/tools/tax-calculator")
    page.get_by_role("link", name="Show options").click()
    return page


@pytest.mark.parametrize("age", [21, 22, 26, 30, 31])
@pytest.mark.parametrize("income", [25000, 35000, 45000, 65000, 85000, 100000, 250000, 1000000])
@pytest.mark.parametrize("is_married", [False, ])  # [True, False]
@pytest.mark.parametrize("children_count", [0, 1, 2, 6])
@pytest.mark.parametrize("region", ['be-east', 'be-west'])  # ['be-east', 'be-west', 'by', 'bb']
@pytest.mark.parametrize("tax_class", [1, ])  # [1, 2, 3, 4, 5, 6]
@pytest.mark.parametrize("zusatzbeitrag", [1.5, ])
@pytest.mark.browser_context_args(timezone_id="Europe/Berlin", locale="en-GB")  # Affects number formatting
def test_results(calc_page, external_calc_page, age, children_count, income, is_married, region, tax_class, zusatzbeitrag):
    if is_married and tax_class in (1, 2):
        return
    elif not is_married:
        if tax_class in (3, 4, 5):
            return
        if not children_count and tax_class == 2:
            return

    calc_params = dict(
        income=income,
        occupation="employee",
        age=age,
        tax_class=tax_class,
        children_count=children_count,
        is_married=is_married,
        zusatzbeitrag=zusatzbeitrag,
        religion=None,
        region=region,
    )
    print(calc_params)

    if is_married and tax_class in (1, 2, 6):
        return
    if not is_married and tax_class in (3, 4, 5):
        return

    fill_calculator(calc_page, **calc_params)
    expected = get_external_results(external_calc_page, **calc_params)
    verify_results(calc_page, **expected)
