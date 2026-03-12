from playwright.sync_api import expect
import pytest


@pytest.fixture
def pension_refund_question_form(page):
    page.goto("/tests/tools/pension-refund-question-form")
    return page.get_by_role("group", name="Pension refund question form")


def test_snapshot(page, pension_refund_question_form, test_screenshot):
    tool = pension_refund_question_form
    test_screenshot(page, tool)
    tool.get_by_label("Your question").fill("Can I get a pension refund")
    tool.get_by_label("Name").fill("John Smith")
    tool.get_by_label("Email address").fill("j.smith@gmail.com")
    tool.get_by_label("Nationality").select_option("Canada")
    expect(tool).not_to_contain_text("You do not qualify for a pension refund.")

    tool.get_by_label("Where do you live").select_option("Canada")
    expect(tool).not_to_contain_text("You do not qualify for a pension refund.")

    tool.get_by_label("Where do you live").select_option("France")
    expect(tool).to_contain_text("You do not qualify for a pension refund.")

    with page.expect_response("**/api/forms/pension-refund-question") as api_response:
        tool.get_by_role("button", name="Send question").click()

    assert api_response.value.ok
    response_data = api_response.value.json()
    assert response_data["email"] == "j.smith@gmail.com"
    assert response_data["name"] == "John Smith"
    assert response_data["nationality"] == "CA"
    assert response_data["country_of_residence"] == "FR"
    assert response_data["question"] == "Can I get a pension refund"

    expect(tool).to_contain_text("Message sent")

    test_screenshot(page, tool)
