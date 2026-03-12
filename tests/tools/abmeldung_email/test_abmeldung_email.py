import pytest


@pytest.fixture
def abmeldung_email_generator(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/abmeldung-email")
    return page.get_by_role("group", name="Letter generator to deregister your address")


def test_snapshot(page, abmeldung_email_generator, test_screenshot):
    tool = abmeldung_email_generator
    test_screenshot(page, tool)
    tool.get_by_role("button", name="Customize").click()
    tool.get_by_label("Your full name").fill("John Smith")
    tool.get_by_label("Your new address").fill("123 Maple Street\nMontreal, Quebec\nCanada")
    tool.get_by_label("Backup recipient").fill("Bella Johnson")
    tool.get_by_label("Backup address").fill("Wohnungstr. 123\n13122 Berlin")
    tool.get_by_role("button", name="Preview").click()
    test_screenshot(page, tool)
