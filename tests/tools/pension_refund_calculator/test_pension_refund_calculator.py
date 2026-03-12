from playwright.sync_api import expect

import pytest


@pytest.fixture
def pension_refund_calculator(page):
    page.goto("/tests/tools/pension-refund-calculator")
    return page.get_by_role("group", name="Pension refund calculator")


def fill_calculator(page):
    page.get_by_label("Nationality").select_option("Canada")
    page.get_by_label("Where do you live?").select_option("United States")
    page.get_by_label("First month of work in Germany").select_option("January")
    page.get_by_label("First year of work in Germany").select_option("2020")
    page.get_by_label("Last month of work in Germany").select_option("February")
    page.get_by_label("Last year of work in Germany").select_option("2022")
    page.get_by_label("Salary in Germany").fill("50000")


def test_default_state(page, pension_refund_calculator, test_screenshot):
    test_screenshot(page, pension_refund_calculator)


def test_eligible(page, pension_refund_calculator, test_screenshot):
    fill_calculator(page)
    test_screenshot(page, pension_refund_calculator)


def test_apply_for_refund(page, pension_refund_calculator, test_screenshot):
    fill_calculator(page)
    page.get_by_role("button", name="Apply for a refund").click()
    test_screenshot(page, pension_refund_calculator)
    page.get_by_label("FundsBack").click()
    page.get_by_role("button", name="Request a refund").click()
    page.get_by_role("button", name="Send request").click()  # Form error
    test_screenshot(page, pension_refund_calculator)
    page.get_by_label("Full name").fill("John Smith")
    page.get_by_label("Email address").fill("testaccount@gmail.com")
    page.get_by_label("Date of birth").fill("1995-09-03")

    with page.expect_response("**/api/forms/pension-refund-request") as api_response:
        page.get_by_role("button", name="Send request").click()
    assert api_response.value.ok

    expected_response = {
        "arrival_date": "2020-01-01",
        "departure_date": "2022-02-01",
        "birth_date": "1995-09-03",
        "nationality": "CA",
        "country_of_residence": "US",
        "email": "testaccount@gmail.com",
        "name": "John Smith",
        "partner": "fundsback",
    }
    response_data = api_response.value.json()
    for key, value in expected_response.items():
        assert response_data[key] == value

    expect(pension_refund_calculator).to_contain_text("Request sent")
    test_screenshot(page, pension_refund_calculator)


def test_diy_refund(page, pension_refund_calculator, test_screenshot):
    fill_calculator(page)
    page.get_by_role("button", name="Apply for a refund").click()
    page.get_by_label("Do it yourself").click()
    test_screenshot(page, pension_refund_calculator)


def test_east_west_germany(page, pension_refund_calculator, test_screenshot):
    fill_calculator(page)
    page.get_by_label("Salary in Germany").fill("150000")
    page.get_by_label("Where did you work?").select_option("Brandenburg")
    refund_east = pension_refund_calculator.locator(".price.large").text_content()
    page.get_by_label("Where did you work?").select_option("Bavaria")
    refund_west = pension_refund_calculator.locator(".price.large").text_content()
    assert refund_east != refund_west
    test_screenshot(page, pension_refund_calculator)


def test_not_eligible_month(page, pension_refund_calculator, test_screenshot):
    fill_calculator(page)
    page.get_by_label("First year of work in Germany").select_option("2000")
    expect(pension_refund_calculator).to_contain_text("You can't get a pension refund")
    test_screenshot(page, pension_refund_calculator)


def test_not_eligible_country_of_residence(page, pension_refund_calculator, test_screenshot):
    page.get_by_label("Nationality").select_option("Canada")
    page.get_by_label("Where do you live?").select_option("France")
    test_screenshot(page, pension_refund_calculator)


def test_not_eligible_nationality(page, pension_refund_calculator, test_screenshot):
    page.get_by_label("Nationality").select_option("France")
    page.get_by_label("Where do you live?").select_option("Canada")
    test_screenshot(page, pension_refund_calculator)
