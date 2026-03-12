from playwright.sync_api import expect
import pytest


@pytest.fixture
def citizenship_feedback_form(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/citizenship-feedback-form")
    return page.get_by_role("group", name="Feedback form")


application_label = "I have applied in Berlin"
reply_label = "I got a reply"
appointment_label = "I got an appointment"


def test_checkboxes(page, citizenship_feedback_form):
    tool = citizenship_feedback_form

    expect(tool.get_by_label(application_label)).not_to_be_checked()
    expect(tool.get_by_label(reply_label)).not_to_be_checked()
    expect(tool.get_by_label(appointment_label)).not_to_be_checked()

    tool.get_by_label(appointment_label).check()

    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label(reply_label)).to_be_checked()
    expect(tool.get_by_label(appointment_label)).to_be_checked()

    tool.get_by_label(reply_label).uncheck()

    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label(reply_label)).not_to_be_checked()
    expect(tool.get_by_label(appointment_label)).not_to_be_checked()


def test_form_validation(page, citizenship_feedback_form, test_screenshot):
    tool = citizenship_feedback_form
    tool.get_by_label(appointment_label).check()
    tool.get_by_label("First response date", exact=True).fill("2020-02-01")
    tool.get_by_label("Appointment date", exact=True).fill("2020-01-01")

    assert tool.get_by_label("Application date", exact=True).evaluate("e => !e.validity.valid")  # Required but empty
    assert tool.get_by_label("Appointment date", exact=True).evaluate("e => !e.validity.valid")  # Date too small
    assert tool.get_by_label("Department", exact=True).evaluate("e => !e.validity.valid")  # Required but empty
    assert tool.get_by_label("Notes and advice").evaluate("e => e.validity.valid")  # Not required

    tool.get_by_role("button", name="Send feedback").click()

    test_screenshot(page, tool)


def test_partial_submission(page, citizenship_feedback_form, test_screenshot):
    tool = citizenship_feedback_form

    tool.get_by_label(appointment_label).check()
    tool.get_by_label("Application date", exact=True).fill("2020-01-01")
    tool.get_by_label("First response date", exact=True).fill("2020-02-01")

    # If the appointment step is checked, filled, then unchecked, the appointment date must not be submitted
    tool.get_by_label("Appointment date", exact=True).fill("2020-03-01")
    tool.get_by_label(appointment_label).uncheck()

    tool.get_by_label("Department").select_option("S3 — Asia")

    with page.expect_response("**/api/forms/citizenship-feedback") as first_api_response:
        tool.get_by_role("button", name="Send feedback").click()
    first_expected_response = {
        "application_date": "2020-01-01",
        "first_response_date": "2020-02-01",
        "department": "S3",
        "appointment_date": None,
        "email": None,
        "notes": "",
    }
    assert first_api_response.value.ok
    first_response_data = first_api_response.value.json()
    for key, value in first_expected_response.items():
        assert first_response_data[key] == value

    modification_key = first_response_data["modification_key"]
    assert page.evaluate("localStorage.getItem('citizenshipModificationKey')") == modification_key

    test_screenshot(page, tool)
    tool.get_by_label("Email address").fill("j.smith@gmail.com")

    # Feedback is updated with the email address
    with page.expect_response(f"**/api/forms/citizenship-feedback/{modification_key}") as second_api_response:
        tool.get_by_role("button", name="Remind me").click()
    second_expected_response = {
        **first_expected_response,
        "email": "j.smith@gmail.com",
    }
    assert second_api_response.value.ok
    response_data = second_api_response.value.json()
    for key, value in second_expected_response.items():
        assert response_data[key] == value

    expect(tool).to_contain_text("Support this website")
    assert page.evaluate("localStorage.getItem('citizenshipModificationKey')") == modification_key

    # Test that the modification key works properly, and that the feedback can be ammended
    page.reload()
    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label("Application date", exact=True)).to_have_value("2020-01-01")
    expect(tool.get_by_label(reply_label)).to_be_checked()
    expect(tool.get_by_label("First response date", exact=True)).to_have_value("2020-02-01")
    expect(tool.get_by_label(appointment_label)).not_to_be_checked()
    tool.get_by_label("First response date", exact=True).fill("2020-03-05")

    with page.expect_response(f"**/api/forms/citizenship-feedback/{modification_key}") as third_api_response:
        tool.get_by_role("button", name="Update feedback").click()
    third_expected_response = {
        **second_expected_response,
        "first_response_date": "2020-03-05",
    }
    assert third_api_response.value.ok

    response_data = third_api_response.value.json()
    for key, value in third_expected_response.items():
        assert response_data[key] == value

    # Email is already set, so skip asking for email
    expect(tool).to_contain_text("Support this website")
    assert page.evaluate("localStorage.getItem('citizenshipModificationKey')") == modification_key

    # Load modification key from URL, instead of localStorage
    page.evaluate("localStorage.setItem('citizenshipModificationKey', 'invalid')")
    page.goto(f"/tests/tools/citizenship-feedback-form#feedbackKey={modification_key}")
    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label("Application date", exact=True)).to_have_value("2020-01-01")
    expect(tool.get_by_label(reply_label)).to_be_checked()
    expect(tool.get_by_label("First response date", exact=True)).to_have_value("2020-03-05")
    expect(tool.get_by_label(appointment_label)).not_to_be_checked()


def test_full_submission(page, citizenship_feedback_form, test_screenshot):
    tool = citizenship_feedback_form
    test_screenshot(page, tool)

    tool.get_by_label(appointment_label).check()
    tool.get_by_label("Application date", exact=True).fill("2020-01-01")
    tool.get_by_label("First response date", exact=True).fill("2020-02-01")
    tool.get_by_label("Appointment date", exact=True).fill("2020-04-01")
    tool.get_by_label("Department").select_option("S3")
    tool.get_by_label("Notes and advice").fill("I followed the instructions and everything went smoothly")

    test_screenshot(page, tool)

    with page.expect_response("**/api/forms/citizenship-feedback") as api_response:
        tool.get_by_role("button", name="Send feedback").click()

    expected_response = {
        "email": None,
        "application_date": "2020-01-01",
        "first_response_date": "2020-02-01",
        "appointment_date": "2020-04-01",
        "department": "S3",
        "notes": "I followed the instructions and everything went smoothly",
    }

    assert api_response.value.ok

    response_data = api_response.value.json()
    for key, value in expected_response.items():
        assert response_data[key] == value

    test_screenshot(page, tool)
    expect(tool).to_contain_text("Thank you")

    # No modification key for complete feedback
    assert page.evaluate("localStorage.getItem('citizenshipModificationKey')") is None
