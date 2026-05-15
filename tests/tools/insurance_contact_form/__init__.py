def get_form(page):
    return page.get_by_role("group", name="Insurance contact form")


def load_form(page):
    page.goto("/tests/tools/insurance-contact-form?ref=test-referrer")


def assert_stage(page, expected_stage: str):
    stage = get_form(page).get_attribute("data-stage")
    assert stage == expected_stage, f"Expected stage '{expected_stage}', got '{stage}'"
