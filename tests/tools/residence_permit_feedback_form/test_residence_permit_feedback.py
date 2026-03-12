from playwright.sync_api import expect
import pytest


@pytest.fixture
def residence_permit_feedback_form(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/residence-permit-feedback-form")
    return page.get_by_role("group", name="Feedback form")


@pytest.fixture
def blue_card_feedback_form(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/residence-permit-feedback-form-blue-card")
    return page.get_by_role("group", name="Feedback form: Blue Card processing time")


application_label = "I have applied in Berlin"
reply_label = "The immigration office has replied"
appointment_label = "I have an appointment"
pick_up_date_label = "I have a pick-up date for the residence card"


def test_checkboxes(page, residence_permit_feedback_form):
    tool = residence_permit_feedback_form

    expect(tool.get_by_label(application_label)).not_to_be_checked()
    expect(tool.get_by_label(reply_label)).not_to_be_checked()
    expect(tool.get_by_label(appointment_label)).not_to_be_checked()
    expect(tool.get_by_label(pick_up_date_label)).not_to_be_checked()

    tool.get_by_label(pick_up_date_label).check()

    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label(reply_label)).to_be_checked()
    expect(tool.get_by_label(appointment_label)).to_be_checked()
    expect(tool.get_by_label(pick_up_date_label)).to_be_checked()

    tool.get_by_label(reply_label).uncheck()

    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label(reply_label)).not_to_be_checked()
    expect(tool.get_by_label(appointment_label)).not_to_be_checked()
    expect(tool.get_by_label(pick_up_date_label)).not_to_be_checked()


def test_form_validation(page, residence_permit_feedback_form, test_screenshot):
    tool = residence_permit_feedback_form
    tool.get_by_label(pick_up_date_label).check()
    tool.get_by_label("First response date", exact=True).fill("2020-02-01")
    tool.get_by_label("Appointment date", exact=True).fill("2020-01-01")

    assert tool.get_by_label("Application date", exact=True).evaluate("e => !e.validity.valid")  # Required but empty
    assert tool.get_by_label("Appointment date", exact=True).evaluate("e => !e.validity.valid")  # Date too small
    assert tool.get_by_label("Pick-up date", exact=True).evaluate("e => !e.validity.valid")  # Required but empty
    assert tool.get_by_label("Residence permit", exact=True).evaluate("e => !e.validity.valid")  # Required but empty
    assert tool.get_by_label("Department", exact=True).evaluate("e => !e.validity.valid")  # Required but empty
    assert tool.get_by_label("Permit validity").evaluate("e => e.validity.valid")  # Not required
    assert tool.get_by_label("Notes and advice").evaluate("e => e.validity.valid")  # Not required

    tool.get_by_role("button", name="Send feedback").click()

    test_screenshot(page, tool)


def test_partial_submission(page, residence_permit_feedback_form, test_screenshot):
    tool = residence_permit_feedback_form

    tool.get_by_label(appointment_label).check()
    tool.get_by_label("Application date", exact=True).fill("2020-01-01")
    tool.get_by_label("First response date", exact=True).fill("2020-02-01")

    # If the appointment step is checked, filled, then unchecked, the appointment date must not be submitted
    tool.get_by_label("Appointment date", exact=True).fill("2020-03-01")
    tool.get_by_label(appointment_label).uncheck()

    tool.get_by_label("Residence permit").select_option("Blue Card")
    tool.get_by_role("heading", name="How is your Blue Card application going?")
    tool.get_by_label("Department").select_option("BIS — Business Immigration Service")

    # This field is hidden if the feedback is not complete
    expect(tool.get_by_label("Permit validity")).to_have_count(0)

    with page.expect_response("**/api/forms/residence-permit-feedback") as first_api_response:
        tool.get_by_role("button", name="Send feedback").click()
    first_expected_response = {
        "application_date": "2020-01-01",
        "first_response_date": "2020-02-01",
        "department": "B6",
        "residence_permit_type": "BLUE_CARD",
        "appointment_date": None,
        "pick_up_date": None,
        "email": None,
        "validity_in_months": None,
        "notes": "",
    }
    assert first_api_response.value.ok
    first_response_data = first_api_response.value.json()
    for key, value in first_expected_response.items():
        assert first_response_data[key] == value

    modification_key = first_response_data["modification_key"]
    assert page.evaluate("localStorage.getItem('modificationKey')") == f"{modification_key}~BLUE_CARD"

    test_screenshot(page, tool)
    tool.get_by_label("Email address").fill("j.smith@gmail.com")

    # Feedback is updated with the email address
    with page.expect_response(f"**/api/forms/residence-permit-feedback/{modification_key}") as second_api_response:
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
    assert page.evaluate("localStorage.getItem('modificationKey')") == f"{modification_key}~BLUE_CARD"

    # Test that the modification key works properly, and that the feedback can be ammended
    page.reload()
    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label("Application date", exact=True)).to_have_value("2020-01-01")
    expect(tool.get_by_label(reply_label)).to_be_checked()
    expect(tool.get_by_label("First response date", exact=True)).to_have_value("2020-02-01")
    expect(tool.get_by_label(appointment_label)).not_to_be_checked()
    expect(tool.get_by_label(pick_up_date_label)).not_to_be_checked()

    tool.get_by_label(appointment_label).check()
    tool.get_by_label("Appointment date", exact=True).fill("2020-03-05")

    with page.expect_response(f"**/api/forms/residence-permit-feedback/{modification_key}") as third_api_response:
        tool.get_by_role("button", name="Update feedback").click()
    third_expected_response = {
        **second_expected_response,
        "appointment_date": "2020-03-05",
    }
    assert third_api_response.value.ok
    response_data = third_api_response.value.json()
    for key, value in third_expected_response.items():
        assert response_data[key] == value

    # Email is already set, so skip asking for email
    expect(tool).to_contain_text("Support this website")
    assert page.evaluate("localStorage.getItem('modificationKey')") == f"{modification_key}~BLUE_CARD"

    # Load modification key from URL, instead of localStorage
    page.evaluate("localStorage.setItem('modificationKey', 'invalid~BLUE_CARD')")
    page.goto(f"/tests/tools/residence-permit-feedback-form-blue-card#feedbackKey={modification_key}~BLUE_CARD")
    expect(tool.get_by_label(application_label)).to_be_checked()
    expect(tool.get_by_label("Application date", exact=True)).to_have_value("2020-01-01")
    expect(tool.get_by_label(reply_label)).to_be_checked()
    expect(tool.get_by_label("First response date", exact=True)).to_have_value("2020-02-01")
    expect(tool.get_by_label(appointment_label)).to_be_checked()
    expect(tool.get_by_label("Appointment date", exact=True)).to_have_value("2020-03-05")


def test_full_submission(page, residence_permit_feedback_form, test_screenshot):
    tool = residence_permit_feedback_form
    test_screenshot(page, tool)

    tool.get_by_role("heading", name="How is your residence permit application going?")

    tool.get_by_label(pick_up_date_label).check()
    tool.get_by_label("Application date", exact=True).fill("2020-01-01")
    tool.get_by_label("First response date", exact=True).fill("2020-02-01")
    tool.get_by_label("Appointment date", exact=True).fill("2020-04-01")
    tool.get_by_label("Pick-up date", exact=True).fill("2020-08-01")

    expect(tool.get_by_label("Health insurance")).to_have_count(0)
    expect(tool.get_by_label("Permit validity")).to_have_count(1)

    tool.get_by_label("Residence permit").select_option("Permanent residence")
    tool.get_by_role("heading", name="How is your permanent residence application going?")

    # Don't ask for permit validity with PR
    expect(tool.get_by_label("Permit validity")).to_have_count(0)

    tool.get_by_label("Department").select_option("M1")

    # Ask for insurer name, but only for some types of insurance
    tool.get_by_label("Health insurance").select_option("Public health insurance")
    expect(tool.get_by_placeholder("Name of health insurance")).to_have_count(0)
    tool.get_by_label("Health insurance").select_option("Other")
    expect(tool.get_by_placeholder("Name of health insurance")).to_have_count(1)
    tool.get_by_label("Health insurance").select_option("Private health insurance")
    expect(tool.get_by_placeholder("Name of health insurance")).to_have_count(1)
    tool.get_by_label("Health insurance").select_option("Expat health insurance")
    expect(tool.get_by_placeholder("Name of health insurance")).to_have_count(1)

    tool.get_by_placeholder("Name of health insurance").fill("Mawista")

    tool.get_by_label("Notes and advice").fill("I followed the instructions and everything went smoothly")

    test_screenshot(page, tool)

    with page.expect_response("**/api/forms/residence-permit-feedback") as api_response:
        tool.get_by_role("button", name="Send feedback").click()

    expected_response = {
        "email": None,
        "validity_in_months": None,
        "health_insurance_type": "EXPAT",
        "health_insurance_name": "Mawista",
        "application_date": "2020-01-01",
        "first_response_date": "2020-02-01",
        "appointment_date": "2020-04-01",
        "pick_up_date": "2020-08-01",
        "department": "M1",
        "notes": "I followed the instructions and everything went smoothly",
        "residence_permit_type": "PERMANENT_RESIDENCE",
    }

    assert api_response.value.ok

    response_data = api_response.value.json()
    for key, value in expected_response.items():
        assert response_data[key] == value

    test_screenshot(page, tool)
    expect(tool).to_contain_text("Thank you")

    # No modification key for complete feedback
    assert page.evaluate("localStorage.getItem('modificationKey')") is None


def test_preset_residence_permit_type(page, blue_card_feedback_form):
    tool = blue_card_feedback_form

    tool.get_by_role("heading", name="How is your Blue Card application going?")

    tool.get_by_label(pick_up_date_label).check()

    # No residence permit selection
    expect(tool.get_by_label("Residence permit")).to_have_count(0)

    # No health insurance field
    expect(tool.get_by_label("Health insurance")).to_have_count(0)

    # Filtered departments
    expect(tool.get_by_label("Department").locator("option[value='B6']")).to_have_count(1)
    expect(tool.get_by_label("Department").locator("option[value='M1']")).to_have_count(0)
