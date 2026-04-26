from playwright.sync_api import expect
import pytest


@pytest.fixture
def suggestion_form(page):
    page.goto("/tests/tools/place-suggestion-form")
    return page.get_by_label("Recommend a vet")


def select_place(page, suggestion_form):
    """Type a query into the autocomplete input and select the first result."""
    input = suggestion_form.get_by_label("Business name").first
    input.fill("Tierarztpraxis Anne Gamalski")
    page.locator(".pac-item").first.click()


def test_place_selection(page, suggestion_form, test_screenshot):
    test_screenshot(page, suggestion_form)
    select_place(page, suggestion_form)
    expect(suggestion_form.locator(".input-instructions").first).to_be_visible()
    test_screenshot(page, suggestion_form)


def test_category_display(page, suggestion_form):
    expect(suggestion_form).to_contain_text("Recommend a vet")


def test_extra_fields_shown_after_place_selected(page, suggestion_form):
    expect(suggestion_form.get_by_label("Languages spoken")).not_to_be_visible()
    expect(suggestion_form.get_by_label("Notes")).not_to_be_visible()

    select_place(page, suggestion_form)

    expect(suggestion_form.get_by_label("Languages spoken")).to_be_visible()
    expect(suggestion_form.get_by_label("Notes")).to_be_visible()


def test_address_shown_after_place_selected(page, suggestion_form):
    select_place(page, suggestion_form)
    expect(suggestion_form.locator(".input-instructions").first).to_contain_text("Greifenhagener Str.")


def test_owner_checkbox_shows_email(page, suggestion_form):
    select_place(page, suggestion_form)

    expect(suggestion_form.get_by_label("Email address")).not_to_be_visible()
    suggestion_form.get_by_label("I work for this business").check()
    expect(suggestion_form.get_by_label("Email address")).to_be_visible()


def test_form_submission(page, suggestion_form, test_screenshot):
    select_place(page, suggestion_form)

    suggestion_form.get_by_label("Languages spoken").fill("English")
    suggestion_form.get_by_label("I work for this business").check()
    suggestion_form.get_by_label("Email address").fill("tests@allaboutberlin.com")

    with page.expect_response("**/api/forms/place-suggestion") as api_response:
        suggestion_form.get_by_role("button", name="Submit").click()

    assert api_response.value.ok
    response_data = api_response.value.json()
    assert response_data["business_name"] == "Tierarztpraxis Anne Gamalski an den Allee-Arcaden"
    assert response_data["google_maps_id"]
    assert response_data["languages"] == "English"
    assert response_data["is_owner"] is True
    assert response_data["email"] == "tests@allaboutberlin.com"
    assert response_data["category"] == "veterinarians"

    expect(suggestion_form).to_contain_text("Thank you")
    test_screenshot(page, suggestion_form)


def test_error_go_back(page, suggestion_form, test_screenshot):
    select_place(page, suggestion_form)

    page.route(
        "**/api/forms/place-suggestion",
        lambda route: route.fulfill(status=400, content_type="application/json"),
    )

    suggestion_form.get_by_role("button", name="Submit").click()
    expect(suggestion_form).to_contain_text("An error occurred")
    test_screenshot(page, suggestion_form)

    suggestion_form.get_by_role("button", name="Go back").click()
    expect(suggestion_form).to_contain_text("Recommend a vet")
