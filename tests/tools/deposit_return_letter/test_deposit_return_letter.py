import pytest


@pytest.fixture
def deposit_return_letter_generator(page):
    page.clock.set_fixed_time("2026-02-22T10:00:00")
    page.goto("/tests/tools/apartment-deposit-return-letter")
    return page.get_by_role("group", name="Letter generator to ask for your apartment deposit back")


def test_snapshot(page, deposit_return_letter_generator, test_screenshot):
    tool = deposit_return_letter_generator
    test_screenshot(page, tool)
    tool.get_by_role("button", name="Customize").click()

    tool.get_by_label("Your full name").fill("John Smith")
    tool.get_by_label("Old address").fill("Alte Straße 65\n13127 Berlin")

    tool.get_by_label("Move-out date").fill("2022-03-04")
    tool.get_by_label("Current address").fill("Neue Straße 78\n12345 Berlin")

    tool.get_by_label("Deposit amount").fill("1234.56")
    tool.get_by_label("I already got part of my deposit back").check()
    tool.get_by_label("Remaining deposit").fill("78.90")

    tool.get_by_label("Company name").fill("Hausverwaltung Geiz")
    tool.get_by_label("Address", exact=True).fill("Vermieter Str. 333\n10115 Berlin")

    tool.get_by_label("Time to respond", exact=True).select_option("6 weeks")

    tool.get_by_label("Bank account holder").fill("John Bartholomy Smith")
    tool.get_by_label("IBAN").fill("DE75512108001245126199")

    tool.get_by_role("button", name="Preview").click()
    test_screenshot(page, tool)
