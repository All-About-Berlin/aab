from playwright.sync_api import expect
from . import cases, assert_stage, fill_calculator_until, get_calculator
import pytest


@pytest.mark.parametrize("case", cases.values(), ids=cases.keys())
def test_options(page, test_screenshot, case):
    fill_calculator_until(page, "options", **case)
    test_screenshot(page, get_calculator(page))

    page.get_by_label("Go back").click()
    assert_stage(page, "questions")


@pytest.mark.parametrize("case", cases.values(), ids=cases.keys())
def test_option_ask_a_broker(page, case):
    fill_calculator_until(page, "options", **case)
    page.get_by_label("Ask our expert", exact=True).click()
    assert_stage(page, "askABroker")

    page.click("text=WhatsApp")
    page.get_by_label("Go back").click()
    assert_stage(page, "options")


def test_option_private_quote(page, test_screenshot):
    case = cases["employee-100k"]

    fill_calculator_until(page, "options", **case)

    if case["can_have_private"]:
        page.get_by_label("Private health insurance").click()
        assert_stage(page, "privateOptions")
        test_screenshot(page, get_calculator(page))

        page.get_by_role("button", name="Get insured").click()
        assert_stage(page, "askABroker")
        page.click("text=WhatsApp")
        page.get_by_label("Go back").click()
    else:
        expect(page.get_by_label("Private health insurance")).to_have_count(0)

    assert_stage(page, "options")
