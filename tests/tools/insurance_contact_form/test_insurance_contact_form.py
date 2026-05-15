import re
import pytest
from playwright.sync_api import expect


@pytest.fixture
def insurance_form(page):
    page.goto("/tests/tools/insurance-contact-form?ref=test-referrer")
    return page.get_by_role("group", name="Insurance contact form")


def assert_stage(form, expected_stage: str):
    stage = form.get_attribute("data-stage")
    assert stage == expected_stage, f"Expected stage '{expected_stage}', got '{stage}'"


def test_snapshot(insurance_form, test_screenshot):
    assert_stage(insurance_form, "contact")
    test_screenshot(insurance_form.page, insurance_form)


def test_snapshot_whatsapp(insurance_form, test_screenshot):
    insurance_form.page.click("text=WhatsApp")
    test_screenshot(insurance_form.page, insurance_form)


def test_snapshot_email(insurance_form, test_screenshot):
    insurance_form.page.click("text=Email")
    test_screenshot(insurance_form.page, insurance_form)


def test_by_whatsapp(insurance_form, test_screenshot):
    page = insurance_form.page
    page.click("text=WhatsApp")

    expect(insurance_form).not_to_have_class(re.compile(r".*show-errors.*"))
    page.locator(".button.whatsapp").click()
    expect(insurance_form).to_have_class(re.compile(r".*show-errors.*"))
    test_screenshot(page, insurance_form)
    assert_stage(insurance_form, "contact")

    page.get_by_label("Your name").fill("John Doe")

    with page.expect_response("**/api/insurance/case") as api_response:
        page.locator(".button.whatsapp").click()

    assert api_response.value.ok
    response_data = api_response.value.json()
    assert response_data["name"] == "John Doe"
    assert response_data["email"] == ""
    assert response_data["contact_method"] == "WHATSAPP"
    assert response_data["referrer"] == "test-referrer"

    test_screenshot(page, insurance_form)
    assert_stage(insurance_form, "thank-you")

    page.get_by_label("Go back").click()
    assert_stage(insurance_form, "contact")


def test_by_email(insurance_form, test_screenshot):
    page = insurance_form.page
    page.click("text=Email")

    expect(insurance_form).not_to_have_class(re.compile(r".*show-errors.*"))
    page.get_by_role("button", name="Ask Seamus").click()
    expect(insurance_form).to_have_class(re.compile(r".*show-errors.*"))
    test_screenshot(page, insurance_form)
    assert_stage(insurance_form, "contact")

    page.get_by_label("Your name").fill("John Doe")
    page.get_by_label("Email address").fill("j.doe@example.com")
    page.get_by_label("Your question").fill("This is a question")

    with page.expect_response("**/api/insurance/case") as api_response:
        page.get_by_role("button", name="Ask Seamus").click()

    assert api_response.value.ok
    response_data = api_response.value.json()
    assert response_data["name"] == "John Doe"
    assert response_data["email"] == "j.doe@example.com"
    assert response_data["question"] == "This is a question"
    assert response_data["contact_method"] == "EMAIL"
    assert response_data["referrer"] == "test-referrer"

    test_screenshot(page, insurance_form)
    assert_stage(insurance_form, "thank-you")

    page.get_by_label("Go back").click()
    assert_stage(insurance_form, "contact")
