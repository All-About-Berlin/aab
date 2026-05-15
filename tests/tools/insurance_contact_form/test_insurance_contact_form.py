import re
from playwright.sync_api import expect
from . import assert_stage, get_form, load_form


def test_snapshot(page, test_screenshot):
    load_form(page)
    assert_stage(page, "contact")
    test_screenshot(page, get_form(page))


def test_snapshot_whatsapp(page, test_screenshot):
    load_form(page)
    page.click("text=WhatsApp")
    test_screenshot(page, get_form(page))


def test_snapshot_email(page, test_screenshot):
    load_form(page)
    page.click("text=Email")
    test_screenshot(page, get_form(page))


def test_by_whatsapp(page, test_screenshot):
    load_form(page)
    page.click("text=WhatsApp")

    expect(get_form(page)).not_to_have_class(re.compile(r".*show-errors.*"))
    page.locator(".button.whatsapp").click()
    expect(get_form(page)).to_have_class(re.compile(r".*show-errors.*"))
    test_screenshot(page, get_form(page))
    assert_stage(page, "contact")

    page.get_by_label("Your name").fill("John Doe")

    with page.expect_response("**/api/insurance/case") as api_response:
        page.locator(".button.whatsapp").click()

    assert api_response.value.ok
    response_data = api_response.value.json()
    assert response_data["name"] == "John Doe"
    assert response_data["email"] == ""
    assert response_data["contact_method"] == "WHATSAPP"
    assert response_data["referrer"] == "test-referrer"

    test_screenshot(page, get_form(page))
    assert_stage(page, "thank-you")

    page.get_by_label("Go back").click()
    assert_stage(page, "contact")


def test_by_email(page, test_screenshot):
    load_form(page)
    page.click("text=Email")

    expect(get_form(page)).not_to_have_class(re.compile(r".*show-errors.*"))
    page.get_by_role("button", name="Ask Seamus").click()
    expect(get_form(page)).to_have_class(re.compile(r".*show-errors.*"))
    test_screenshot(page, get_form(page))
    assert_stage(page, "contact")

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

    test_screenshot(page, get_form(page))
    assert_stage(page, "thank-you")

    page.get_by_label("Go back").click()
    assert_stage(page, "contact")
