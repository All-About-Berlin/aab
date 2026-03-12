import pytest


@pytest.fixture
def bescheinigung_in_steuersachen_email_generator(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/bescheinigung-in-steuersachen-email")
    return page.get_by_role("group", name="Bescheinigung in Steuersachen email generator")


def test_snapshot(page, bescheinigung_in_steuersachen_email_generator, test_screenshot):
    tool = bescheinigung_in_steuersachen_email_generator
    test_screenshot(page, tool)
    tool.get_by_role("button", name="Customize").click()

    tool.get_by_label("Your full name").fill("John Smith")
    tool.get_by_label("Your address").fill("Pasewalker Str. 65\n13127 Berlin")
    tool.get_by_label("Date of birth").fill("1993-04-05")
    tool.get_by_label("Tax ID").fill("23 456 789 012")

    tool.get_by_role("button", name="Preview").click()
    test_screenshot(page, tool)
