from playwright.sync_api import expect
from . import assert_stage, cases, get_calculator, fill_calculator_until
import re


def test_snapshot(page, test_screenshot):
    fill_calculator_until(page, "askABroker", **cases["employee-100k"])
    test_screenshot(page, get_calculator(page))


def test_by_whatsapp(page, test_screenshot):
    case = cases["employee-100k"]

    fill_calculator_until(page, "askABroker", **case)
    page.click("text=WhatsApp")
    expect(get_calculator(page)).not_to_have_class(re.compile(r".*show-errors.*"))
    page.locator(".button.whatsapp").click()
    expect(get_calculator(page)).to_have_class(re.compile(r".*show-errors.*"))
    test_screenshot(page, get_calculator(page))
    assert_stage(page, "askABroker")

    page.get_by_label("Your name").fill("John Doe")

    with page.expect_response("**/api/insurance/case") as api_response:
        page.locator(".button.whatsapp").click()

    expected_response = {
        **case,
        "name": "John Doe",
        "email": "",
        "question": "",
        "referrer": "test-referrer",
        "contact_method": "WHATSAPP",
        "broker": "seamus-wolf",
    }
    expected_response.pop("can_have_private")
    assert api_response.value.ok

    response_data = api_response.value.json()
    for key, value in expected_response.items():
        assert response_data[key] == value

    test_screenshot(page, get_calculator(page))
    assert_stage(page, "thank-you")

    page.get_by_label("Go back").click()
    assert_stage(page, "occupation")


def test_by_email(page, test_screenshot):
    case = cases["employee-100k"]

    fill_calculator_until(page, "askABroker", **case)
    page.click("text=Email")
    expect(get_calculator(page)).not_to_have_class(re.compile(r".*show-errors.*"))
    page.get_by_role("button", name="Ask Seamus").click()
    expect(get_calculator(page)).to_have_class(re.compile(r".*show-errors.*"))
    test_screenshot(page, get_calculator(page))
    assert_stage(page, "askABroker")

    page.get_by_label("Your name").fill("John Doe")
    page.get_by_label("Email address").fill("j.doe@example.com")
    page.get_by_label("Question").fill("This is a question\nPlease answer soon")

    with page.expect_response("**/api/insurance/case") as api_response:
        page.get_by_role("button", name="Ask Seamus").click()

    expected_response = {
        **case,
        "name": "John Doe",
        "email": "j.doe@example.com",
        "question": "This is a question\nPlease answer soon",
        "referrer": "test-referrer",
        "contact_method": "EMAIL",
        "broker": "seamus-wolf",
    }
    expected_response.pop("can_have_private")

    assert api_response.value.ok

    response_data = api_response.value.json()
    for key, value in expected_response.items():
        assert response_data[key] == value

    test_screenshot(page, get_calculator(page))
    assert_stage(page, "thank-you")

    page.get_by_label("Go back").click()
    assert_stage(page, "occupation")
