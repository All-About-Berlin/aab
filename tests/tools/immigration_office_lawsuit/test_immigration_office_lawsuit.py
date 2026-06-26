from playwright.sync_api import expect
import pytest
import re


@pytest.fixture
def lawsuit_form(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/immigration-office-lawsuit")
    return page.get_by_role("group", name="Sue the Ausländerbehörde")


def assert_stage(lawsuit_form, expected_stage: str):
    stage = lawsuit_form.get_attribute("data-stage")
    assert stage == expected_stage, f"Expected stage '{expected_stage}', got '{stage}'"


def fill_questions(lawsuit_form):
    lawsuit_form.get_by_label("Application date").fill("2025-11-01")
    lawsuit_form.get_by_label("Application type").select_option("BLUE_CARD")
    lawsuit_form.get_by_label("Application city").fill("Berlin")


def test_snapshot_intro(lawsuit_form, test_screenshot):
    test_screenshot(lawsuit_form.page, lawsuit_form)


def test_validation(lawsuit_form, test_screenshot):
    lawsuit_form.get_by_role("button", name="Continue").click()  # intro → questions

    lawsuit_form.get_by_role("button", name="Continue").click()  # questions → contact
    test_screenshot(lawsuit_form.page, lawsuit_form)
    fill_questions(lawsuit_form)
    lawsuit_form.get_by_role("button", name="Continue").click()  # questions → contact

    expect(lawsuit_form).not_to_have_class(re.compile(r".*show-errors.*"))
    lawsuit_form.get_by_role("button", name="Send").click()
    expect(lawsuit_form).to_have_class(re.compile(r".*show-errors.*"))
    test_screenshot(lawsuit_form.page, lawsuit_form)


def test_submit(lawsuit_form, test_screenshot):
    page = lawsuit_form.page

    lawsuit_form.get_by_role("button", name="Continue").click()
    fill_questions(lawsuit_form)
    lawsuit_form.get_by_label("Comments").fill("Some extra details")

    lawsuit_form.get_by_role("button", name="Continue").click()
    assert_stage(lawsuit_form, "contact")
    lawsuit_form.get_by_label("Full name").fill("John Doe")
    lawsuit_form.get_by_label("Email address").fill("contact@nicolasbouliane.com")

    with page.expect_response("**/api/forms/immigration-office-lawsuit") as api_response:
        lawsuit_form.get_by_role("button", name="Send").click()

    assert api_response.value.ok
    response_data = api_response.value.json()
    assert response_data["name"] == "John Doe"
    assert response_data["email"] == "contact@nicolasbouliane.com"
    assert response_data["application_type"] == "BLUE_CARD"
    assert response_data["city"] == "Berlin"
    assert response_data["application_date"] == "2025-11-01"
    assert response_data["message"] == "Some extra details"

    test_screenshot(page, lawsuit_form)
    assert_stage(lawsuit_form, "thank-you")

    lawsuit_form.get_by_label("Go back").click()
    assert_stage(lawsuit_form, "intro")


def test_application_date_too_recent(lawsuit_form, test_screenshot):
    lawsuit_form.get_by_role("button", name="Continue").click()
    assert_stage(lawsuit_form, "questions")

    lawsuit_form.get_by_label("Application date").fill("2025-11-23")  # 3 months - 1 day ago
    test_screenshot(lawsuit_form.page, lawsuit_form)
    lawsuit_form.get_by_role("button", name="Continue").click()  # questions → contact
    lawsuit_form.get_by_label("Application date").fill("2025-11-23")  # 3 months - 1 day ago
    lawsuit_form.get_by_role("button", name="Continue").click()  # questions → contact

    lawsuit_form.get_by_label("Application type").select_option("BLUE_CARD")
    lawsuit_form.get_by_label("Application city").fill("Berlin")
    lawsuit_form.get_by_role("button", name="Continue").click()
    assert_stage(lawsuit_form, "questions")
